/**
 * Monte Carlo probability engine.
 *
 * "What are the odds I actually hit this goal?" — answered honestly, by
 * resampling the user's OWN recent history (bootstrap) instead of assuming
 * smooth average progress. This is an outside-view forecast by
 * construction (planning-fallacy): if your real weeks vary wildly, the fan
 * of futures is wide and the odds say so.
 *
 * Interventions (adopting a habit) shift the sampled distributions — the
 * cause-and-effect layer. Effect sizes come from the user's own measured
 * patterns where possible (e.g. their sleep→focus lift), bounded by
 * research priors.
 *
 * Deterministic: seeded PRNG, seeded per (goal, intervention), so the UI
 * is stable across renders.
 */

import type {
  DayRecord,
  Goal,
  GoalForecast,
  InterventionEffect,
  UserProfile,
} from './types';
import { deriveTargets } from './personalize';

function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Stable numeric seed from a string. */
function hashSeed(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

const DAY_MS = 86_400_000;

/** Sample from an empirical array with replacement. */
function pick<T>(arr: T[], rand: () => number): T {
  return arr[Math.floor(rand() * arr.length)];
}

/** Approximate normal sample via Box–Muller. */
function gaussian(rand: () => number, mean: number, sd: number): number {
  const u = Math.max(rand(), 1e-9);
  const v = rand();
  return mean + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function stdev(arr: number[]): number {
  if (arr.length < 2) return 0;
  const m = arr.reduce((a, b) => a + b, 0) / arr.length;
  return Math.sqrt(arr.reduce((a, b) => a + (b - m) * (b - m), 0) / (arr.length - 1));
}

/**
 * Fresh users have a flat self-reported baseline — zero measured
 * variance would make every forecast a fake-certain single line. Until
 * real data accumulates, inject typical human day-to-day variability
 * around THEIR mean (labeled as such in the UI). Once their history has
 * real spread, the empirical distribution takes over untouched.
 */
function varianceFloor(samples: number[], floor: number, defaultSd: number): number {
  return stdev(samples) < floor ? defaultSd : 0;
}

// ── Empirical samplers per metric ─────────────────────────────────────────

/**
 * Weekly net savings flow observed in history: transfers made plus budget
 * under/overshoot (overspending a week eats into what gets saved).
 */
function weeklySavingsSamples(records: DayRecord[], profile: UserProfile): number[] {
  const t = deriveTargets(profile);
  const weekly: number[] = [];
  for (let i = records.length; i >= 7; i -= 7) {
    const week = records.slice(Math.max(0, i - 7), i);
    const saved = week.reduce((a, r) => a + r.savedToday, 0);
    const spend = week.reduce((a, r) => a + r.discretionarySpend, 0);
    // Half of any budget overshoot ultimately comes out of savings.
    const overshoot = Math.max(0, spend - t.weeklyDiscretionary);
    weekly.push(saved - overshoot * 0.5);
  }
  return weekly.length ? weekly : [profile.monthlyInvestment / 4.33];
}

/** Weekly weight deltas observed in history (lb/week, signed). */
function weeklyWeightDeltaSamples(records: DayRecord[]): number[] {
  const out: number[] = [];
  for (let i = 7; i < records.length; i += 7) {
    out.push(records[i].weightLbs - records[i - 7].weightLbs);
  }
  return out.length ? out : [0];
}

// ── Forecast: reach goals ─────────────────────────────────────────────────

interface SimOpts {
  runs?: number;
  intervention?: InterventionEffect;
  /** Extra sim label so seeds differ between baseline and intervention */
  seedTag?: string;
}

export function forecastGoal(
  goal: Goal,
  records: DayRecord[],
  profile: UserProfile,
  opts: SimOpts = {},
): GoalForecast {
  const runs = opts.runs ?? 1000;
  const iv = opts.intervention ?? {};
  const rand = mulberry32(hashSeed(goal.id + (opts.seedTag ?? '') + 'lifeos'));

  if (goal.kind === 'sustain') return forecastSustain(goal, records, profile, runs, iv, rand);

  const today = new Date(records[records.length - 1].date + 'T00:00:00Z').getTime();
  const deadline = new Date((goal.deadline ?? records[records.length - 1].date) + 'T00:00:00Z').getTime();
  const horizonWeeks = Math.max(1, Math.round((deadline - today) / DAY_MS / 7));
  // Fan checkpoints: ~8 evenly spaced points across the horizon.
  const checkpointEvery = Math.max(1, Math.round(horizonWeeks / 8));

  const isWeight = goal.metric === 'weightLbs';
  const samples = isWeight ? weeklyWeightDeltaSamples(records) : weeklySavingsSamples(records, profile);
  const start = isWeight
    ? records[records.length - 1].weightLbs
    : profile.savingsBalance;
  const meanAbs = Math.abs(samples.reduce((a, b) => a + b, 0) / samples.length);
  const extraSd = isWeight
    ? varianceFloor(samples, 0.15, 0.55) // typical scale-weight weekly noise, lb
    : varianceFloor(samples, Math.max(15, meanAbs * 0.1), Math.max(30, meanAbs * 0.35));

  // Interventions shift each sampled week.
  const weeklyShift = isWeight ? (iv.weightDriftShift ?? 0) : (iv.extraWeeklySavings ?? 0);
  const spendRelief = !isWeight && iv.spendMult ? weeklySpendRelief(records, profile, iv.spendMult) : 0;

  const trajectories: number[][] = [];
  let hits = 0;
  const hitWeek: number[] = [];
  const goalDown = goal.target < goal.baseline; // e.g. weight loss

  for (let run = 0; run < runs; run++) {
    let v = start;
    let hit = false;
    const traj: number[] = [];
    for (let w = 1; w <= horizonWeeks; w++) {
      let step = pick(samples, rand) + weeklyShift + spendRelief;
      if (extraSd > 0) step += gaussian(rand, 0, extraSd);
      if (!isWeight) {
        // Market movement on invested balance: ~6%/yr nominal, ~13%/yr vol.
        step += v * gaussian(rand, 0.06 / 52, 0.13 / Math.sqrt(52));
      }
      v += step;
      // Weight goals switch to maintenance once the target is reached —
      // nobody keeps cutting past their goal.
      if (isWeight && goalDown && v < goal.target) v = goal.target;
      if (w % checkpointEvery === 0 || w === horizonWeeks) traj.push(v);
      if (!hit && (goalDown ? v <= goal.target : v >= goal.target)) {
        hit = true;
        hitWeek.push(w);
      }
    }
    if (hit) hits++;
    trajectories.push(traj);
  }

  const nPoints = trajectories[0].length;
  const fan = Array.from({ length: nPoints }, (_, pi) => {
    const vals = trajectories.map((t) => t[pi]).sort((a, b) => a - b);
    const q = (p: number) => vals[Math.min(vals.length - 1, Math.floor(p * vals.length))];
    return {
      dayOffset: (pi + 1) * checkpointEvery * 7,
      p10: Math.round(q(0.1) * 10) / 10,
      p50: Math.round(q(0.5) * 10) / 10,
      p90: Math.round(q(0.9) * 10) / 10,
    };
  });

  // Median completion: the week by which half of ALL runs have hit.
  let medianCompletion: string | undefined;
  if (hitWeek.length >= runs / 2) {
    const sorted = [...hitWeek].sort((a, b) => a - b);
    const med = sorted[Math.min(sorted.length - 1, Math.ceil(runs / 2) - 1)];
    medianCompletion = new Date(today + med * 7 * DAY_MS).toISOString().slice(0, 10);
  }

  return { goalId: goal.id, pHit: hits / runs, medianCompletion, fan, runs };
}

/** $/week freed by a sustained spend-multiplier intervention. */
function weeklySpendRelief(records: DayRecord[], profile: UserProfile, mult: number): number {
  void profile;
  const weekly = records.slice(-28).reduce((a, r) => a + r.discretionarySpend, 0) / 4;
  return weekly * (1 - mult) * 0.8; // most (not all) of the saving is banked
}

// ── Forecast: sustain goals ───────────────────────────────────────────────

/**
 * Sustain goals ask: "over the next 4 weeks, will your average hold at or
 * above target?" Bootstrap 28-day windows from history, apply intervention
 * shifts, count the share of futures that clear the bar.
 */
function forecastSustain(
  goal: Goal,
  records: DayRecord[],
  profile: UserProfile,
  runs: number,
  iv: InterventionEffect,
  rand: () => number,
): GoalForecast {
  const t = deriveTargets(profile);
  const recent = records.slice(-60);

  const dailyValue = (r: DayRecord): number => {
    switch (goal.metric) {
      case 'sleepAvg': {
        let v = r.sleepHours;
        // Bedtime discipline lifts short nights toward the range floor.
        if (iv.sleepFloorLift && v < t.sleepRange[0]) {
          v = Math.min(t.sleepRange[0], v + iv.sleepFloorLift);
        }
        return v;
      }
      case 'stepsAvg':
        return r.steps + (iv.stepsBoost ?? 0);
      case 'deepWorkWeekly': {
        const isWorkday = !(r.dayOfWeek === 0 || r.dayOfWeek === 6) && !r.workedShift;
        return r.deepWorkHours + (isWorkday ? (iv.deepWorkBoost ?? 0) : 0);
      }
      case 'workoutsWeekly':
        return (r.didWorkout ? 1 : 0) + (iv.workoutsBoost ?? 0) / 7;
      default:
        return 0;
    }
  };

  const pool = recent.map(dailyValue);
  const weeklyGoal = goal.metric === 'deepWorkWeekly' || goal.metric === 'workoutsWeekly';
  const target = goal.target;

  // Typical daily variability per metric, applied only when the pool is
  // flat (fresh users) — see varianceFloor.
  const poolMean = pool.reduce((a, b) => a + b, 0) / Math.max(pool.length, 1);
  const extraSd = (() => {
    switch (goal.metric) {
      case 'sleepAvg':
        return varianceFloor(pool, 0.25, 0.85);
      case 'stepsAvg':
        return varianceFloor(pool, 400, Math.max(800, poolMean * 0.28));
      case 'deepWorkWeekly':
        return varianceFloor(pool, 0.3, poolMean * 0.45 + 0.3);
      case 'workoutsWeekly':
        return varianceFloor(pool, 0.12, 0.28);
      default:
        return 0;
    }
  })();

  // Block bootstrap: sample four CONTIGUOUS 7-day blocks instead of 28
  // i.i.d. days. Real weeks are autocorrelated (a bad stretch is a bad
  // stretch); i.i.d. sampling collapses the variance and makes odds look
  // artificially binary.
  const maxBlockStart = Math.max(1, pool.length - 7);
  let hits = 0;
  const outcomes: number[] = [];
  for (let run = 0; run < runs; run++) {
    let sum = 0;
    for (let b = 0; b < 4; b++) {
      const start = Math.floor(rand() * maxBlockStart);
      for (let d = 0; d < 7; d++) {
        let v = pool[Math.min(start + d, pool.length - 1)];
        if (extraSd > 0) v += gaussian(rand, 0, extraSd);
        sum += v;
      }
    }
    const avg = weeklyGoal ? sum / 4 : sum / 28; // per-week or per-day average
    outcomes.push(avg);
    if (avg >= target) hits++;
  }

  outcomes.sort((a, b) => a - b);
  const q = (p: number) => outcomes[Math.min(outcomes.length - 1, Math.floor(p * outcomes.length))];
  const fan = [7, 14, 21, 28].map((dayOffset) => ({
    dayOffset,
    p10: Math.round(q(0.1) * 10) / 10,
    p50: Math.round(q(0.5) * 10) / 10,
    p90: Math.round(q(0.9) * 10) / 10,
  }));

  return { goalId: goal.id, pHit: hits / runs, fan, runs };
}

/**
 * Odds delta from adopting an intervention, for one goal.
 * Fewer runs (fast path) — used to rank recommendations by ΔP.
 */
export function oddsDelta(
  goal: Goal,
  records: DayRecord[],
  profile: UserProfile,
  intervention: InterventionEffect,
  runs = 300,
): { from: number; to: number } {
  const base = forecastGoal(goal, records, profile, { runs, seedTag: 'base' });
  const withIv = forecastGoal(goal, records, profile, { runs, intervention, seedTag: 'iv' });
  return { from: base.pHit, to: withIv.pHit };
}
