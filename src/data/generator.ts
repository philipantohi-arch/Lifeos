/**
 * Synthetic life-data generator.
 *
 * Produces a deterministic, realistic 120-day history for the demo user.
 * Crucially, it embeds real causal structure — the same kinds of patterns
 * LifeOS is designed to discover in real user data:
 *
 *   • Sleeping > 7.5h lifts next-day focus and deep work.
 *   • Sleeping < 6.5h inflates same-day discretionary spending (~40%).
 *   • Morning workouts lift same-day focus.
 *   • Sunday meal prep improves nutrition and cuts takeout Mon–Thu.
 *   • Alcohol tonight degrades tonight's sleep quality and tomorrow's recovery.
 *
 * The insights engine does NOT know about these rules — it rediscovers them
 * from the numbers via correlation analysis, which is exactly the pipeline
 * that runs against real wearable/finance data in production.
 */

import type { DayRecord, UserProfile } from '../engine/types';

/** Deterministic PRNG (mulberry32) so the demo is stable across reloads. */
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

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export const DEMO_PROFILE: UserProfile = {
  name: 'Philip',
  age: 34,
  weightLbs: 192,
  savingsBalance: 28400,
  monthlyIncome: 7800,
  monthlyInvestment: 800,
  savingsGoal: 40000,
  savingsGoalLabel: 'House down payment',
  goals: [
    'Reach 175 lbs by next summer',
    'Save $40k for a house down payment',
    'Ship the side project',
    'Call parents at least weekly',
  ],
};

export function generateHistory(days = 120, seed = 20260728): DayRecord[] {
  const rand = mulberry32(seed);
  const records: DayRecord[] = [];

  const today = new Date('2026-07-28T00:00:00Z');
  let daysSinceFamilyContact = 2;
  let prevAlcohol = 0;
  let prevSleepHours = 7.4;
  let mealPrepActive = false;

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setUTCDate(d.getUTCDate() - i);
    const dow = d.getUTCDay();
    const isWeekend = dow === 0 || dow === 6;

    // ── Sleep ──────────────────────────────────────────────────────────
    // Weekends: later bedtime. Alcohol last night: worse quality tonight.
    const lateNight = rand() < (isWeekend ? 0.45 : 0.2);
    const bedtime = 22.5 + (lateNight ? 1.5 + rand() * 1.5 : rand() * 0.9);
    const sleepHours = clamp(8.7 - (bedtime - 22.5) * 0.85 + (rand() - 0.5) * 1.6, 4.8, 9.3);
    const sleepQuality = clamp(
      55 + (sleepHours - 6.5) * 11 - prevAlcohol * 9 + (rand() - 0.5) * 14,
      25,
      98,
    );

    // ── Recovery ───────────────────────────────────────────────────────
    const recoveryScore = clamp(
      0.55 * sleepQuality + 0.25 * (prevSleepHours * 10) - prevAlcohol * 6 + rand() * 18,
      20,
      99,
    );
    const hrv = Math.round(clamp(30 + recoveryScore * 0.45 + (rand() - 0.5) * 10, 22, 95));
    const restingHR = Math.round(clamp(68 - recoveryScore * 0.12 + prevAlcohol * 2 + (rand() - 0.5) * 4, 48, 74));

    // ── Movement ───────────────────────────────────────────────────────
    const didWorkout = rand() < (recoveryScore > 60 ? 0.55 : 0.3);
    const workoutTime: DayRecord['workoutTime'] = didWorkout
      ? rand() < 0.5
        ? 'morning'
        : 'evening'
      : null;
    const steps = Math.round(
      clamp(4200 + (didWorkout ? 3500 : 0) + (isWeekend ? 1200 : 0) + rand() * 4500, 1800, 18000),
    );
    const activeMinutes = Math.round(clamp((didWorkout ? 45 : 8) + rand() * 30, 0, 130));

    // ── Nutrition & substances ─────────────────────────────────────────
    if (dow === 0) mealPrepActive = rand() < 0.55; // Sunday meal prep decision
    const mealPrepped = mealPrepActive && dow >= 1 && dow <= 4;
    const ateTakeout = rand() < (mealPrepped ? 0.12 : isWeekend ? 0.55 : 0.38);
    const nutritionScore = clamp(
      58 + (mealPrepped ? 18 : 0) - (ateTakeout ? 14 : 0) + (rand() - 0.5) * 16,
      20,
      98,
    );
    const alcoholDrinks = isWeekend && rand() < 0.5 ? Math.ceil(rand() * 3) : rand() < 0.12 ? 1 : 0;

    // ── Finances ───────────────────────────────────────────────────────
    // Embedded pattern: the shorter the sleep, the more impulse spending
    // (≈ +45% per hour under 7.2h — tired brains reach for the card).
    let discretionarySpend =
      28 + (ateTakeout ? 26 : 0) + (isWeekend ? 30 : 0) + rand() * 40;
    discretionarySpend *= 1 + Math.max(0, 7.2 - sleepHours) * 0.45;
    discretionarySpend = Math.round(discretionarySpend * 100) / 100;
    const savedToday = dow === 5 ? 200 : 0; // weekly auto-transfer

    // ── Productivity ───────────────────────────────────────────────────
    // Embedded patterns: >7.5h sleep and morning workouts lift focus.
    const wellRested = sleepHours > 7.5;
    let focusScore = clamp(
      50 +
        (wellRested ? 16 : sleepHours < 6.5 ? -12 : 0) +
        (workoutTime === 'morning' ? 10 : 0) -
        prevAlcohol * 5 +
        (rand() - 0.5) * 18,
      15,
      99,
    );
    if (isWeekend) focusScore = clamp(focusScore - 15, 10, 99);
    const deepWorkHours = isWeekend
      ? Math.round(rand() * 15) / 10
      : Math.round(clamp(1.2 + (focusScore - 50) * 0.045 + rand() * 1.4, 0, 6.5) * 10) / 10;
    const tasksPlanned = isWeekend ? 3 : 6 + Math.round(rand() * 3);
    const tasksCompleted = Math.round(
      clamp(tasksPlanned * (0.35 + (focusScore / 100) * 0.6 + (rand() - 0.5) * 0.15), 0, tasksPlanned),
    );

    // ── Relationships & self-report ────────────────────────────────────
    const calledFamily = rand() < (daysSinceFamilyContact >= 6 ? 0.4 : 0.12);
    daysSinceFamilyContact = calledFamily ? 0 : daysSinceFamilyContact + 1;
    const socialTouchpoints = (calledFamily ? 1 : 0) + (isWeekend ? Math.round(rand() * 3) : rand() < 0.35 ? 1 : 0);
    const energy = clamp(Math.round(3 + sleepQuality / 20 + recoveryScore / 40 + (rand() - 0.5) * 2), 1, 10);
    const mood = clamp(
      Math.round(4 + energy * 0.35 + socialTouchpoints * 0.5 - (daysSinceFamilyContact > 10 ? 1 : 0) + (rand() - 0.5) * 2),
      1,
      10,
    );

    records.push({
      date: d.toISOString().slice(0, 10),
      dayOfWeek: dow,
      sleepHours: Math.round(sleepHours * 10) / 10,
      sleepQuality: Math.round(sleepQuality),
      bedtime: Math.round(bedtime * 4) / 4,
      recoveryScore: Math.round(recoveryScore),
      hrv,
      restingHR,
      steps,
      activeMinutes,
      didWorkout,
      workoutTime,
      nutritionScore: Math.round(nutritionScore),
      ateTakeout,
      alcoholDrinks,
      mealPrepped,
      discretionarySpend,
      savedToday,
      deepWorkHours,
      tasksCompleted,
      tasksPlanned,
      focusScore: Math.round(focusScore),
      socialTouchpoints,
      daysSinceFamilyContact,
      mood,
      energy,
    });

    prevAlcohol = alcoholDrinks;
    prevSleepHours = sleepHours;
  }

  // Make "today" a compelling demo day: excellent recovery, good sleep,
  // family contact overdue — so the briefing has a clear story to tell.
  const t = records[records.length - 1];
  t.sleepHours = 7.9;
  t.sleepQuality = 88;
  t.bedtime = 22.5;
  t.recoveryScore = 91;
  t.hrv = 72;
  t.restingHR = 52;
  t.alcoholDrinks = 0;
  t.didWorkout = false;
  t.workoutTime = null;

  // Family contact drifted for the last 9 days (gradually, so the
  // relationships pillar declines rather than cliff-dropping today).
  for (let k = 0; k <= 9 && k < records.length; k++) {
    records[records.length - 1 - k].daysSinceFamilyContact = 9 - k;
  }

  return records;
}
