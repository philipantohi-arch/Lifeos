/**
 * Goal engine — the anchor of the individualized Life Score.
 *
 * Progress is measured against YOUR baseline → YOUR target at YOUR
 * feasible pace. Three questions per goal:
 *
 *   1. Where are you vs. the straight line from baseline to deadline?
 *      (paceRatio — the honest "am I on track")
 *   2. Is the remaining rate physically/financially possible for you?
 *      (capacity check — income, time budget, safe physiological rates)
 *   3. If it isn't, what's the honest alternative? (suggestion — LifeOS
 *      renegotiates targets instead of letting users silently fail;
 *      goal-setting theory: goals must stay accepted & attainable)
 */

import type {
  Capacity,
  DayRecord,
  Goal,
  GoalAssessment,
  MetricKey,
  UserProfile,
} from './types';
import { deriveTargets } from './personalize';

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export const METRIC_META: Record<
  MetricKey,
  { label: string; unit: string; kind: 'reach' | 'sustain'; decimals: number }
> = {
  weightLbs: { label: 'Body weight', unit: 'lbs', kind: 'reach', decimals: 1 },
  savingsBalance: { label: 'Savings balance', unit: '$', kind: 'reach', decimals: 0 },
  sleepAvg: { label: 'Average sleep', unit: 'h/night', kind: 'sustain', decimals: 1 },
  stepsAvg: { label: 'Average steps', unit: '/day', kind: 'sustain', decimals: 0 },
  deepWorkWeekly: { label: 'Deep work', unit: 'h/week', kind: 'sustain', decimals: 1 },
  workoutsWeekly: { label: 'Workouts', unit: '/week', kind: 'sustain', decimals: 1 },
};

/** What this user can realistically output, from profile + research bands. */
export function deriveCapacity(profile: UserProfile): Capacity {
  const t = deriveTargets(profile);
  const surplus = profile.monthlyIncome - profile.monthlyEssentials;
  return {
    // Leave ~25% of surplus as slack — budgets with zero slack fail.
    maxMonthlySavings: Math.max(0, Math.round(surplus * 0.75)),
    safeWeightLossLbPerWeek: t.weightLossLbPerWeek,
    weeklyDeepWorkCeiling:
      profile.situation === 'new-baby' || profile.situation === 'sick'
        ? 10
        : profile.workPattern === 'shift'
          ? 15
          : profile.lifeStage === 'retired'
            ? 14
            : 25,
    dailyStepsCeiling: profile.age >= 65 ? 12000 : 16000,
  };
}

/** Current value of a goal metric from the unified history. */
export function currentMetric(metric: MetricKey, records: DayRecord[], profile: UserProfile): number {
  const last14 = records.slice(-14);
  const last7 = records.slice(-7);
  const mean = (v: number[]) => (v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0);
  switch (metric) {
    case 'weightLbs':
      // Smoothed: mean of last 7 daily readings beats a single noisy weigh-in.
      return Math.round(mean(last7.map((r) => r.weightLbs)) * 10) / 10;
    case 'savingsBalance':
      return profile.savingsBalance;
    case 'sleepAvg':
      return Math.round(mean(last14.map((r) => r.sleepHours)) * 10) / 10;
    case 'stepsAvg':
      return Math.round(mean(last14.map((r) => r.steps)));
    case 'deepWorkWeekly':
      return Math.round(last7.reduce((a, r) => a + r.deepWorkHours, 0) * 10) / 10;
    case 'workoutsWeekly':
      return last7.filter((r) => r.didWorkout).length;
  }
}

/** Max sustainable weekly rate toward a reach goal, from capacity. */
function capacityRate(goal: Goal, cap: Capacity, profile: UserProfile): number {
  switch (goal.metric) {
    case 'weightLbs':
      return cap.safeWeightLossLbPerWeek[1]; // lb/week (loss expressed as positive)
    case 'savingsBalance':
      // Contributions the budget can sustain + expected growth on what's
      // already invested (6% nominal — see researchBase: equity-returns).
      return cap.maxMonthlySavings / 4.33 + (profile.savingsBalance * 0.06) / 52;
    default:
      return Infinity; // sustain goals have no accumulation rate
  }
}

function fmtValue(metric: MetricKey, v: number): string {
  const meta = METRIC_META[metric];
  const num = meta.decimals === 0 ? Math.round(v).toLocaleString() : v.toFixed(meta.decimals);
  return meta.unit === '$' ? `$${num}` : `${num} ${meta.unit}`;
}

const DAY_MS = 86_400_000;

/**
 * Assess one goal: pace vs the baseline→deadline line, capacity
 * feasibility, and an honest suggestion when the math doesn't work.
 * `today` is the last record's date (deterministic, not wall-clock).
 */
export function assessGoal(
  goal: Goal,
  records: DayRecord[],
  profile: UserProfile,
): GoalAssessment {
  const cap = deriveCapacity(profile);
  const current = currentMetric(goal.metric, records, profile);
  const today = new Date(records[records.length - 1].date + 'T00:00:00Z').getTime();

  if (goal.kind === 'sustain') {
    // Sustain goals: how close is the current level to the target level,
    // and how far have you come from your baseline?
    const covered = (current - goal.baseline) / (goal.target - goal.baseline || 1);
    const level = clamp(current / (goal.target || 1), 0, 1.4);
    const paceScore = clamp(25 + 50 * level, 15, 100);
    return {
      goal,
      current,
      progressPct: clamp(covered, 0, 1),
      expectedPct: 1,
      paceRatio: Math.round(level * 100) / 100,
      paceScore: Math.round(paceScore),
      requiredWeeklyRate: Math.max(0, goal.target - current),
      capacityWeeklyRate: Infinity,
      feasibility: feasibilitySustain(goal, cap),
      suggestion: suggestionSustain(goal, cap),
    };
  }

  // Reach goals: distance covered vs distance expected by today.
  const start = goalStartDate(goal, records);
  const deadline = new Date((goal.deadline ?? records[records.length - 1].date) + 'T00:00:00Z').getTime();
  const totalDays = Math.max(1, (deadline - start) / DAY_MS);
  const elapsedDays = clamp((today - start) / DAY_MS, 0, totalDays);
  const remainingWeeks = Math.max(0.2, (deadline - today) / DAY_MS / 7);

  const span = goal.target - goal.baseline; // signed (negative for weight loss)
  const covered = span === 0 ? 1 : (current - goal.baseline) / span;
  const expected = elapsedDays / totalDays;
  const paceRatio = expected > 0.02 ? covered / expected : 1;

  const remaining = Math.abs(goal.target - current);
  const requiredWeeklyRate = remaining / remainingWeeks;
  const capRate = capacityRate(goal, cap, profile);

  let feasibility: GoalAssessment['feasibility'];
  if (requiredWeeklyRate <= capRate * 0.7) feasibility = 'comfortable';
  else if (requiredWeeklyRate <= capRate * 1.05) feasibility = 'stretch';
  else feasibility = 'unrealistic';

  let suggestion: string | undefined;
  if (feasibility === 'unrealistic' && Number.isFinite(capRate)) {
    const weeksNeeded = remaining / (capRate * 0.85);
    const newDeadline = new Date(today + weeksNeeded * 7 * DAY_MS);
    const reachableBydeadline =
      goal.metric === 'weightLbs'
        ? current - capRate * 0.85 * remainingWeeks
        : current + capRate * 0.85 * remainingWeeks;
    suggestion = `At your sustainable pace (${fmtValue(goal.metric, capRate)}/week), this lands ~${newDeadline.toLocaleDateString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' })}. Either move the deadline, or aim for ${fmtValue(goal.metric, reachableBydeadline)} by the current one — both are wins worth having.`;
  }

  const paceScore = clamp(25 + 50 * clamp(paceRatio, 0, 1.5), 15, 100);

  return {
    goal,
    current,
    progressPct: clamp(covered, 0, 1),
    expectedPct: clamp(expected, 0, 1),
    paceRatio: Math.round(paceRatio * 100) / 100,
    paceScore: Math.round(paceScore),
    requiredWeeklyRate: Math.round(requiredWeeklyRate * 100) / 100,
    capacityWeeklyRate: Math.round(capRate * 100) / 100,
    feasibility,
    suggestion,
  };
}

function feasibilitySustain(goal: Goal, cap: Capacity): GoalAssessment['feasibility'] {
  if (goal.metric === 'deepWorkWeekly' && goal.target > cap.weeklyDeepWorkCeiling) return 'unrealistic';
  if (goal.metric === 'stepsAvg' && goal.target > cap.dailyStepsCeiling) return 'unrealistic';
  if (goal.metric === 'deepWorkWeekly' && goal.target > cap.weeklyDeepWorkCeiling * 0.8) return 'stretch';
  return 'comfortable';
}

function suggestionSustain(goal: Goal, cap: Capacity): string | undefined {
  if (goal.metric === 'deepWorkWeekly' && goal.target > cap.weeklyDeepWorkCeiling) {
    return `Given your current work pattern and situation, ~${Math.round(cap.weeklyDeepWorkCeiling * 0.8)}h/week is the honest ceiling. Winning at a real target beats losing at a fantasy one.`;
  }
  if (goal.metric === 'stepsAvg' && goal.target > cap.dailyStepsCeiling) {
    return `${goal.target.toLocaleString()} steps daily exceeds a sustainable ceiling; ${Math.round(cap.dailyStepsCeiling * 0.7).toLocaleString()} would still capture nearly all the health benefit.`;
  }
  return undefined;
}

/**
 * Goal start date: 90 days before the last record (the demo assumes goals
 * were set at history start). In production this is stored per goal.
 */
function goalStartDate(goal: Goal, records: DayRecord[]): number {
  void goal;
  const first = new Date(records[0].date + 'T00:00:00Z').getTime();
  return first;
}

export function assessGoals(records: DayRecord[], profile: UserProfile): GoalAssessment[] {
  return profile.goals.map((g) => assessGoal(g, records, profile));
}
