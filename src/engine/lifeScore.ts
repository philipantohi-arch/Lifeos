/**
 * Life Score engine.
 *
 * Each pillar is scored 0–100 from a rolling window of DayRecords, then
 * combined into a single weighted composite. Recent days matter more
 * (exponential recency weighting inside each pillar window).
 */

import type { DayRecord, LifeScoreResult, PillarKey, PillarScore, UserProfile } from './types';

const PILLAR_WEIGHTS: Record<PillarKey, number> = {
  health: 0.3,
  wealth: 0.2,
  productivity: 0.2,
  relationships: 0.15,
  habits: 0.15,
};

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

// ── Pillar scorers ────────────────────────────────────────────────────────

function healthScore(win: DayRecord[]): number {
  const sleep = recencyMean(win.map((r) => clamp((r.sleepHours / 8) * 100)));
  const quality = recencyMean(win.map((r) => r.sleepQuality));
  const recovery = recencyMean(win.map((r) => r.recoveryScore));
  const movement = recencyMean(win.map((r) => clamp((r.steps / 9000) * 100)));
  const nutrition = recencyMean(win.map((r) => r.nutritionScore));
  const alcoholPenalty = recencyMean(win.map((r) => r.alcoholDrinks * 6));
  return clamp(
    0.24 * sleep + 0.18 * quality + 0.22 * recovery + 0.18 * movement + 0.18 * nutrition - alcoholPenalty,
  );
}

function wealthScore(win: DayRecord[], profile: UserProfile): number {
  const dailyBudget = 75; // discretionary target per day
  const spendDiscipline = recencyMean(
    win.map((r) => clamp(100 - ((r.discretionarySpend - dailyBudget) / dailyBudget) * 100, 0, 100)),
  );
  const savingsRate = clamp((profile.monthlyInvestment / profile.monthlyIncome) * 100 * 5); // 20% rate → 100
  const goalProgress = clamp((profile.savingsBalance / profile.savingsGoal) * 100);
  return clamp(0.45 * spendDiscipline + 0.3 * savingsRate + 0.25 * goalProgress);
}

function productivityScore(win: DayRecord[]): number {
  // Weekends shouldn't drag the score; weight weekdays 4x.
  let sum = 0;
  let wsum = 0;
  win.forEach((r, i) => {
    const recency = Math.pow(0.5, (win.length - 1 - i) / 3);
    const dayWeight = r.dayOfWeek === 0 || r.dayOfWeek === 6 ? 0.25 : 1;
    const completion = r.tasksPlanned ? (r.tasksCompleted / r.tasksPlanned) * 100 : 60;
    const deep = clamp((r.deepWorkHours / 4) * 100);
    const day = 0.4 * r.focusScore + 0.35 * deep + 0.25 * completion;
    sum += day * recency * dayWeight;
    wsum += recency * dayWeight;
  });
  return clamp(wsum ? sum / wsum : 0);
}

function relationshipsScore(win: DayRecord[]): number {
  const touch = recencyMean(win.map((r) => clamp(r.socialTouchpoints * 40, 0, 100)));
  const last = win[win.length - 1];
  const familyFreshness = clamp(100 - last.daysSinceFamilyContact * 9);
  const moodSocial = recencyMean(win.map((r) => r.mood * 10));
  return clamp(0.4 * touch + 0.35 * familyFreshness + 0.25 * moodSocial);
}

function habitsScore(win: DayRecord[]): number {
  const workoutStreak = recencyMean(win.map((r) => (r.didWorkout ? 100 : 30)));
  const prep = recencyMean(win.map((r) => (r.mealPrepped ? 100 : 45)));
  const bedtimeConsistency = recencyMean(win.map((r) => clamp(100 - Math.max(0, r.bedtime - 23) * 35)));
  return clamp(0.4 * workoutStreak + 0.25 * prep + 0.35 * bedtimeConsistency);
}

// ── Composite ─────────────────────────────────────────────────────────────

function pillarScoresAt(records: DayRecord[], endIndex: number, profile: UserProfile): Record<PillarKey, number> {
  const win7 = window(records, endIndex, 7);
  const win14 = window(records, endIndex, 14);
  return {
    health: healthScore(win7),
    wealth: wealthScore(win14, profile),
    productivity: productivityScore(win7),
    relationships: relationshipsScore(win14),
    habits: habitsScore(win14),
  };
}

function composite(p: Record<PillarKey, number>): number {
  return (Object.keys(PILLAR_WEIGHTS) as PillarKey[]).reduce(
    (acc, k) => acc + p[k] * PILLAR_WEIGHTS[k],
    0,
  );
}

function pillarDriver(key: PillarKey, records: DayRecord[]): string {
  const t = records[records.length - 1];
  switch (key) {
    case 'health':
      if (t.recoveryScore >= 85) return `Recovery at ${t.recoveryScore} — best in weeks`;
      if (t.sleepHours < 6.5) return `Only ${t.sleepHours}h of sleep last night`;
      return `${t.sleepHours}h sleep · recovery ${t.recoveryScore}`;
    case 'wealth': {
      const spend7 = records.slice(-7).reduce((a, r) => a + r.discretionarySpend, 0);
      return `$${Math.round(spend7)} discretionary spend this week`;
    }
    case 'productivity':
      return `${t.deepWorkHours}h deep work · ${t.tasksCompleted}/${t.tasksPlanned} tasks yesterday`;
    case 'relationships':
      return t.daysSinceFamilyContact > 7
        ? `${t.daysSinceFamilyContact} days since you called family`
        : `Social contact steady this week`;
    case 'habits': {
      const workouts = records.slice(-7).filter((r) => r.didWorkout).length;
      return `${workouts} workouts in the last 7 days`;
    }
  }
}

export function computeLifeScore(records: DayRecord[], profile: UserProfile): LifeScoreResult {
  const history: number[] = records.map((_, i) => {
    if (i < 6) return composite(pillarScoresAt(records, Math.max(i, 6), profile));
    return composite(pillarScoresAt(records, i, profile));
  });

  const todayIdx = records.length - 1;
  const todayPillars = pillarScoresAt(records, todayIdx, profile);
  const yesterdayPillars = pillarScoresAt(records, todayIdx - 1, profile);

  const pillars: PillarScore[] = (Object.keys(PILLAR_WEIGHTS) as PillarKey[]).map((key) => ({
    key,
    label: PILLAR_LABELS[key],
    score: Math.round(todayPillars[key]),
    delta: Math.round((todayPillars[key] - yesterdayPillars[key]) * 10) / 10,
    weight: PILLAR_WEIGHTS[key],
    driver: pillarDriver(key, records),
  }));

  const score = composite(todayPillars);
  const delta = score - composite(yesterdayPillars);

  return {
    score: Math.round(score),
    delta: Math.round(delta * 10) / 10,
    pillars,
    history: history.map((h) => Math.round(h)),
  };
}
