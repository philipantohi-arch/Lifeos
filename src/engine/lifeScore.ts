/**
 * Life Score engine.
 *
 * Each pillar is scored 0–100 from a rolling window of DayRecords, then
 * combined into a single weighted composite. Every threshold comes from
 * the user's PersonalTargets (derived from the research base + profile),
 * and pillar weights reflect the user's stated priorities. Recent days
 * matter more (exponential recency weighting inside each window).
 */

import type {
  DayRecord,
  LifeScoreResult,
  PersonalTargets,
  PillarKey,
  PillarScore,
  UserProfile,
} from './types';
import { deriveTargets } from './personalize';

const PILLAR_LABELS: Record<PillarKey, string> = {
  health: 'Health',
  wealth: 'Wealth',
  productivity: 'Productivity',
  relationships: 'Relationships',
  habits: 'Habits & Goals',
};

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
 * recommended band (nsf-sleep-duration), tapering ~18 pts/hour outside.
 */
function sleepDurationScore(hours: number, [lo, hi]: [number, number]): number {
  if (hours >= lo && hours <= hi) return 100;
  const dist = hours < lo ? lo - hours : hours - hi;
  return clamp(100 - dist * (hours < lo ? 22 : 12)); // short sleep costs more
}

/**
 * Sleep regularity: deviation from the person's own median bedtime.
 * Regularity predicts outcomes beyond duration (sleep-regularity-mortality,
 * social-jetlag). Shift workers are scored against their two anchor
 * clusters (night sleeps vs day sleeps) rather than a single median.
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
  const meanDev = totalDev / n; // hours from personal median
  return clamp(100 - meanDev * 38);
}

// ── Pillar scorers ────────────────────────────────────────────────────────

function healthScore(win: DayRecord[], t: PersonalTargets): number {
  const sleep = recencyMean(win.map((r) => sleepDurationScore(r.sleepHours, t.sleepRange)));
  const quality = recencyMean(win.map((r) => r.sleepQuality));
  const recovery = recencyMean(win.map((r) => r.recoveryScore));
  const movement = recencyMean(win.map((r) => clamp((r.steps / t.stepsTarget) * 100)));
  const nutrition = recencyMean(win.map((r) => r.nutritionScore));
  // Weekly drinks vs the personal (sex-specific) ceiling.
  const drinks7 = win.slice(-7).reduce((a, r) => a + r.alcoholDrinks, 0);
  const alcoholPenalty = Math.max(0, drinks7 - t.maxDrinksWeekly) * 4 + drinks7 * 1.2;
  return clamp(
    0.24 * sleep + 0.16 * quality + 0.22 * recovery + 0.2 * movement + 0.18 * nutrition - alcoholPenalty,
  );
}

function wealthScore(win: DayRecord[], profile: UserProfile, t: PersonalTargets): number {
  const dailyBudget = t.weeklyDiscretionary / 7;
  const spendDiscipline = recencyMean(
    win.map((r) => clamp(100 - ((r.discretionarySpend - dailyBudget) / Math.max(dailyBudget, 1)) * 100, 0, 100)),
  );
  if (profile.lifeStage === 'retired') {
    // Drawdown phase: discipline + nest-egg preservation, not savings rate.
    const preservation = clamp((profile.savingsBalance / profile.savingsGoal) * 100);
    return clamp(0.55 * spendDiscipline + 0.45 * preservation);
  }
  const actualRate = profile.monthlyIncome > 0 ? profile.monthlyInvestment / profile.monthlyIncome : 0;
  const savingsRate = t.savingsRateTarget > 0 ? clamp((actualRate / t.savingsRateTarget) * 100) : 100;
  const goalProgress = clamp((profile.savingsBalance / profile.savingsGoal) * 100);
  return clamp(0.45 * spendDiscipline + 0.3 * savingsRate + 0.25 * goalProgress);
}

function productivityScore(win: DayRecord[], profile: UserProfile): number {
  // Deep-work expectations differ: retirees' "engaged hours" target is
  // lower; everyone else is scored against a 4h ceiling.
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

function relationshipsScore(win: DayRecord[], t: PersonalTargets): number {
  const touch = recencyMean(win.map((r) => clamp(r.socialTouchpoints * 40, 0, 100)));
  const last = win[win.length - 1];
  // Freshness decays over 3× the personal cadence (holt-lunstad,
  // surgeon-general-loneliness justify never letting this silently decay).
  const cadence = t.familyContactCadenceDays;
  const familyFreshness = clamp(100 - (last.daysSinceFamilyContact / (cadence * 3)) * 100);
  const moodSocial = recencyMean(win.map((r) => r.mood * 10));
  return clamp(0.4 * touch + 0.35 * familyFreshness + 0.25 * moodSocial);
}

function habitsScore(win: DayRecord[], t: PersonalTargets): number {
  // Workouts vs the personal weekly structure (who-activity-2020).
  const workouts7 = win.slice(-7).filter((r) => r.didWorkout).length;
  const workoutTargetWeekly = Math.max(t.strengthSessionsWeekly, 3);
  const workoutScore = clamp((workouts7 / workoutTargetWeekly) * 100);
  const prep = recencyMean(win.map((r) => (r.mealPrepped ? 100 : 45)));
  const regularity = regularityScore(win);
  return clamp(0.35 * workoutScore + 0.25 * prep + 0.4 * regularity);
}

// ── Composite ─────────────────────────────────────────────────────────────

function pillarScoresAt(
  records: DayRecord[],
  endIndex: number,
  profile: UserProfile,
  t: PersonalTargets,
): Record<PillarKey, number> {
  const win7 = window(records, endIndex, 7);
  const win14 = window(records, endIndex, 14);
  return {
    health: healthScore(win7, t),
    wealth: wealthScore(win14, profile, t),
    productivity: productivityScore(win7, profile),
    relationships: relationshipsScore(win14, t),
    habits: habitsScore(win14, t),
  };
}

function composite(p: Record<PillarKey, number>, weights: Record<PillarKey, number>): number {
  return (Object.keys(weights) as PillarKey[]).reduce((acc, k) => acc + p[k] * weights[k], 0);
}

function pillarDriver(key: PillarKey, records: DayRecord[], t: PersonalTargets): string {
  const today = records[records.length - 1];
  switch (key) {
    case 'health':
      if (today.recoveryScore >= 85) return `Recovery at ${today.recoveryScore} — best in weeks`;
      if (today.recoveryScore <= 45) return `Recovery low (${today.recoveryScore}) — rest matters today`;
      if (today.sleepHours < t.sleepRange[0] - 0.5)
        return `${today.sleepHours}h sleep vs your ${t.sleepRange[0]}–${t.sleepRange[1]}h target`;
      return `${today.sleepHours}h sleep · recovery ${today.recoveryScore}`;
    case 'wealth': {
      const spend7 = records.slice(-7).reduce((a, r) => a + r.discretionarySpend, 0);
      return `$${Math.round(spend7)} of your $${t.weeklyDiscretionary} weekly budget`;
    }
    case 'productivity':
      return `${today.deepWorkHours}h deep work · ${today.tasksCompleted}/${today.tasksPlanned} tasks yesterday`;
    case 'relationships':
      return today.daysSinceFamilyContact > t.familyContactCadenceDays
        ? `${today.daysSinceFamilyContact} days since close contact (your cadence: ${t.familyContactCadenceDays})`
        : `Social contact steady this week`;
    case 'habits': {
      const workouts = records.slice(-7).filter((r) => r.didWorkout).length;
      return `${workouts} workout${workouts === 1 ? '' : 's'} in the last 7 days`;
    }
  }
}

export function computeLifeScore(records: DayRecord[], profile: UserProfile): LifeScoreResult {
  const targets = deriveTargets(profile);
  const w = targets.weights;

  const history: number[] = records.map((_, i) =>
    composite(pillarScoresAt(records, Math.max(i, 6), profile, targets), w),
  );

  const todayIdx = records.length - 1;
  const todayPillars = pillarScoresAt(records, todayIdx, profile, targets);
  const yesterdayPillars = pillarScoresAt(records, todayIdx - 1, profile, targets);

  const pillars: PillarScore[] = (Object.keys(w) as PillarKey[]).map((key) => ({
    key,
    label: PILLAR_LABELS[key],
    score: Math.round(todayPillars[key]),
    delta: Math.round((todayPillars[key] - yesterdayPillars[key]) * 10) / 10,
    weight: Math.round(w[key] * 1000) / 1000,
    driver: pillarDriver(key, records, targets),
  }));

  const score = composite(todayPillars, w);
  const delta = score - composite(yesterdayPillars, w);

  return {
    score: Math.round(score),
    delta: Math.round(delta * 10) / 10,
    pillars,
    history: history.map((h) => Math.round(h)),
  };
}
