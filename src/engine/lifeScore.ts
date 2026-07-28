/**
 * Life Score engine v2 — individualized, goal-anchored.
 *
 * Your score is not a comparison to anyone else. Each pillar blends:
 *
 *   • PROCESS (55%): did you do the controllable daily behaviors, scored
 *     against YOUR personalized targets (sleep range for your age,
 *     chronotype-consistent bedtime, income-derived budget, …)? Process
 *     dominates because it's what you control today, and visible progress
 *     on controllables is the strongest motivator (progress-principle).
 *
 *   • OUTCOME (45%): are you on pace toward YOUR goals from YOUR baseline
 *     (goal engine paceScore)? On-pace = 75, ahead climbs toward 100,
 *     behind decays — measured against your own baseline→target line,
 *     never a universal standard (baseline-relative-scoring).
 *
 * Pillar weights come from the user's stated priorities. Three pillars:
 * Health · Wealth · Productivity.
 */

import type {
  DayRecord,
  GoalAssessment,
  LifeScoreResult,
  PersonalTargets,
  PillarKey,
  PillarScore,
  UserProfile,
} from './types';
import { deriveTargets } from './personalize';
import { assessGoals } from './goals';

const PILLAR_LABELS: Record<PillarKey, string> = {
  health: 'Health',
  wealth: 'Wealth',
  productivity: 'Productivity',
};

const PROCESS_WEIGHT = 0.55;
const OUTCOME_WEIGHT = 0.45;

const clamp = (v: number, lo = 0, hi = 100) => Math.min(hi, Math.max(lo, v));

/** Recency-weighted mean over a window (most recent last). */
function recencyMean(values: number[], halfLife = 3): number {
  let sum = 0;
  let wsum = 0;
  const n = values.length;
  for (let i = 0; i < n; i++) {
    const age = n - 1 - i;
    const w = Math.pow(0.5, age / halfLife);
    sum += values[i] * w;
    wsum += w;
  }
  return wsum ? sum / wsum : 0;
}

function window(records: DayRecord[], endIndex: number, size: number): DayRecord[] {
  return records.slice(Math.max(0, endIndex - size + 1), endIndex + 1);
}

/**
 * Sleep-duration score against the personal range: 100 inside the
 * recommended band (nsf-sleep-duration), tapering outside — short sleep
 * costs more than long sleep.
 */
function sleepDurationScore(hours: number, [lo, hi]: [number, number]): number {
  if (hours >= lo && hours <= hi) return 100;
  const dist = hours < lo ? lo - hours : hours - hi;
  return clamp(100 - dist * (hours < lo ? 22 : 12));
}

/**
 * Sleep regularity: deviation from the person's own median bedtime
 * (sleep-regularity-mortality, social-jetlag). Shift workers are scored
 * against their two anchor clusters (night sleeps vs day sleeps).
 */
function regularityScore(win: DayRecord[]): number {
  const groups = new Map<string, number[]>();
  for (const r of win) {
    const key = r.workedShift ? 'day-sleep' : 'night-sleep';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(r.bedtime);
  }
  let totalDev = 0;
  let n = 0;
  for (const values of groups.values()) {
    if (values.length < 2) continue;
    const sorted = [...values].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    for (const v of values) {
      totalDev += Math.abs(v - median);
      n++;
    }
  }
  if (!n) return 70;
  return clamp(100 - (totalDev / n) * 38);
}

// ── Process scorers (controllable daily behavior vs personal targets) ────

function healthProcess(win: DayRecord[], t: PersonalTargets): number {
  const sleep = recencyMean(win.map((r) => sleepDurationScore(r.sleepHours, t.sleepRange)));
  const quality = recencyMean(win.map((r) => r.sleepQuality));
  const recovery = recencyMean(win.map((r) => r.recoveryScore));
  const movement = recencyMean(win.map((r) => clamp((r.steps / t.stepsTarget) * 100)));
  const nutrition = recencyMean(win.map((r) => r.nutritionScore));
  const regularity = regularityScore(win);
  const drinks7 = win.slice(-7).reduce((a, r) => a + r.alcoholDrinks, 0);
  const alcoholPenalty = Math.max(0, drinks7 - t.maxDrinksWeekly) * 4 + drinks7 * 1.2;
  return clamp(
    0.2 * sleep +
      0.13 * quality +
      0.19 * recovery +
      0.18 * movement +
      0.15 * nutrition +
      0.15 * regularity -
      alcoholPenalty,
  );
}

function wealthProcess(win: DayRecord[], profile: UserProfile, t: PersonalTargets): number {
  const dailyBudget = t.weeklyDiscretionary / 7;
  const spendDiscipline = recencyMean(
    win.map((r) => clamp(100 - ((r.discretionarySpend - dailyBudget) / Math.max(dailyBudget, 1)) * 100, 0, 100)),
  );
  if (profile.lifeStage === 'retired') return spendDiscipline;
  const actualRate = profile.monthlyIncome > 0 ? profile.monthlyInvestment / profile.monthlyIncome : 0;
  const savingsExecution = t.savingsRateTarget > 0 ? clamp((actualRate / t.savingsRateTarget) * 100) : 100;
  return clamp(0.6 * spendDiscipline + 0.4 * savingsExecution);
}

function productivityProcess(win: DayRecord[], profile: UserProfile): number {
  const deepCeiling = profile.lifeStage === 'retired' ? 2.5 : 4;
  const weekendAware = profile.workPattern === 'standard' || profile.workPattern === 'flexible';
  let sum = 0;
  let wsum = 0;
  win.forEach((r, i) => {
    const recency = Math.pow(0.5, (win.length - 1 - i) / 3);
    const isOff = weekendAware ? r.dayOfWeek === 0 || r.dayOfWeek === 6 : r.workedShift === true;
    const dayWeight = isOff ? 0.25 : 1;
    const completion = r.tasksPlanned ? (r.tasksCompleted / r.tasksPlanned) * 100 : 60;
    const deep = clamp((r.deepWorkHours / deepCeiling) * 100);
    const day = 0.4 * r.focusScore + 0.35 * deep + 0.25 * completion;
    sum += day * recency * dayWeight;
    wsum += recency * dayWeight;
  });
  return clamp(wsum ? sum / wsum : 0);
}

// ── Outcome: pace toward the user's own goals ─────────────────────────────

function outcomeScore(pillar: PillarKey, assessments: GoalAssessment[]): number | null {
  const relevant = assessments.filter((a) => a.goal.pillar === pillar);
  if (!relevant.length) return null;
  // Priority-weighted mean of pace scores.
  let sum = 0;
  let wsum = 0;
  for (const a of relevant) {
    sum += a.paceScore * a.goal.priority;
    wsum += a.goal.priority;
  }
  return sum / wsum;
}

// ── Composite ─────────────────────────────────────────────────────────────

function pillarProcessAt(
  records: DayRecord[],
  endIndex: number,
  profile: UserProfile,
  t: PersonalTargets,
): Record<PillarKey, number> {
  const win7 = window(records, endIndex, 7);
  const win14 = window(records, endIndex, 14);
  return {
    health: healthProcess(win7, t),
    wealth: wealthProcess(win14, profile, t),
    productivity: productivityProcess(win7, profile),
  };
}

function blend(process: number, outcome: number | null): number {
  return outcome === null ? process : PROCESS_WEIGHT * process + OUTCOME_WEIGHT * outcome;
}

function composite(p: Record<PillarKey, number>, weights: Record<PillarKey, number>): number {
  return (Object.keys(weights) as PillarKey[]).reduce((acc, k) => acc + p[k] * weights[k], 0);
}

function pillarDriver(
  key: PillarKey,
  records: DayRecord[],
  t: PersonalTargets,
  assessments: GoalAssessment[],
): string {
  const today = records[records.length - 1];
  const goals = assessments.filter((a) => a.goal.pillar === key);
  const behind = goals.filter((a) => a.paceRatio < 0.9).sort((a, b) => a.paceRatio - b.paceRatio)[0];
  const ahead = goals.filter((a) => a.paceRatio >= 1.05).sort((a, b) => b.paceRatio - a.paceRatio)[0];

  switch (key) {
    case 'health':
      if (today.recoveryScore >= 85) return `Recovery at ${today.recoveryScore} — best in weeks`;
      if (today.recoveryScore <= 45) return `Recovery low (${today.recoveryScore}) — rest matters today`;
      if (behind) return `"${behind.goal.label}" is at ${Math.round(behind.paceRatio * 100)}% of pace`;
      if (ahead) return `"${ahead.goal.label}" is ahead of pace`;
      return `${today.sleepHours}h sleep · recovery ${today.recoveryScore}`;
    case 'wealth': {
      const spend7 = records.slice(-7).reduce((a, r) => a + r.discretionarySpend, 0);
      if (behind) return `"${behind.goal.label}" needs $${Math.round(behind.requiredWeeklyRate)}/wk from here`;
      return `$${Math.round(spend7)} of your $${t.weeklyDiscretionary} weekly budget`;
    }
    case 'productivity':
      if (behind) return `"${behind.goal.label}" at ${Math.round(behind.paceRatio * 100)}% of target level`;
      return `${today.deepWorkHours}h deep work · ${today.tasksCompleted}/${today.tasksPlanned} tasks yesterday`;
  }
}

export function computeLifeScore(records: DayRecord[], profile: UserProfile): LifeScoreResult {
  const targets = deriveTargets(profile);
  const w = targets.weights;
  const assessments = assessGoals(records, profile);

  const outcomes: Record<PillarKey, number | null> = {
    health: outcomeScore('health', assessments),
    wealth: outcomeScore('wealth', assessments),
    productivity: outcomeScore('productivity', assessments),
  };

  // History: process varies daily; outcome (goal pace) is evaluated at the
  // end state — a simplification that keeps the 30-day trend meaningful.
  const history: number[] = records.map((_, i) => {
    const proc = pillarProcessAt(records, Math.max(i, 6), profile, targets);
    const blended = {
      health: blend(proc.health, outcomes.health),
      wealth: blend(proc.wealth, outcomes.wealth),
      productivity: blend(proc.productivity, outcomes.productivity),
    };
    return composite(blended, w);
  });

  const todayIdx = records.length - 1;
  const procToday = pillarProcessAt(records, todayIdx, profile, targets);
  const procYesterday = pillarProcessAt(records, todayIdx - 1, profile, targets);

  const pillars: PillarScore[] = (Object.keys(w) as PillarKey[]).map((key) => {
    const score = blend(procToday[key], outcomes[key]);
    const yScore = blend(procYesterday[key], outcomes[key]);
    return {
      key,
      label: PILLAR_LABELS[key],
      score: Math.round(score),
      delta: Math.round((score - yScore) * 10) / 10,
      weight: Math.round(w[key] * 1000) / 1000,
      driver: pillarDriver(key, records, targets, assessments),
    };
  });

  const todayBlend = {
    health: blend(procToday.health, outcomes.health),
    wealth: blend(procToday.wealth, outcomes.wealth),
    productivity: blend(procToday.productivity, outcomes.productivity),
  };
  const yesterdayBlend = {
    health: blend(procYesterday.health, outcomes.health),
    wealth: blend(procYesterday.wealth, outcomes.wealth),
    productivity: blend(procYesterday.productivity, outcomes.productivity),
  };

  const score = composite(todayBlend, w);
  const delta = score - composite(yesterdayBlend, w);

  return {
    score: Math.round(score),
    delta: Math.round(delta * 10) / 10,
    pillars,
    history: history.map((h) => Math.round(h)),
  };
}

/** Pure process adherence (0–100) over a window — used by momentum. */
export function processAdherence(records: DayRecord[], profile: UserProfile, endIndex: number): number {
  const targets = deriveTargets(profile);
  const p = pillarProcessAt(records, endIndex, profile, targets);
  return composite(p, targets.weights);
}
