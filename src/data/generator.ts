/**
 * Synthetic life-data generator, parameterized by user profile.
 *
 * Produces a deterministic, realistic 120-day history whose *shape* follows
 * the profile: chronotype sets bedtime center of mass, shift work creates
 * rotating sleep blocks, a new baby fragments sleep, fitness level drives
 * training frequency, income scales money flows, and life stage shapes the
 * week's rhythm. It also embeds real causal structure — the same kinds of
 * patterns LifeOS discovers in real user data:
 *
 *   • More sleep → better next-day focus.
 *   • Short sleep → inflated impulse spending.
 *   • Chronotype-aligned workouts → higher focus.
 *   • Meal prep → better nutrition, less takeout.
 *   • Alcohol tonight → degraded sleep quality and tomorrow's recovery.
 *
 * The insights engine does NOT know these rules — it rediscovers them from
 * the numbers, exactly as it would against live wearable/finance data.
 */

import type { DayRecord, UserProfile } from '../engine/types';
import { deriveTargets } from '../engine/personalize';

/** Deterministic PRNG (mulberry32) so each persona is stable across reloads. */
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

interface GenParams {
  bedtimeBase: number;
  bedtimeJitter: number;
  lateNightProb: (isWeekend: boolean) => number;
  sleepInterruption: number; // hours randomly lost (new baby, on-call)
  workoutProb: number;
  morningWorkoutBias: number; // 0..1 chance a workout lands in the morning
  stepsBase: number;
  stepsShiftBonus: number;
  deepWorkBase: number; // typical productive-hours scale
  weekendMatters: boolean; // weekday/weekend rhythm exists
  takeoutProb: number;
  mealPrepProb: number;
  alcoholWeekendProb: number;
  alcoholWeekdayProb: number;
  dailyWantsBudget: number;
  weeklyTransfer: number;
  shiftPattern: boolean;
}

function paramsFor(profile: UserProfile): GenParams {
  const t = deriveTargets(profile);
  const dailyWants = (profile.monthlyIncome * 0.3) / 30;

  const p: GenParams = {
    bedtimeBase: Math.min(t.bedtimeIdeal + 0.4, 25.5),
    bedtimeJitter: 0.9,
    lateNightProb: (w) => (w ? 0.45 : 0.2),
    sleepInterruption: 0,
    workoutProb:
      profile.fitnessLevel === 'beginner' ? 0.25 : profile.fitnessLevel === 'advanced' ? 0.6 : 0.45,
    morningWorkoutBias:
      profile.chronotype === 'morning' ? 0.8 : profile.chronotype === 'evening' ? 0.2 : 0.5,
    stepsBase: 4200,
    stepsShiftBonus: 0,
    deepWorkBase: 1.2,
    weekendMatters: profile.workPattern === 'standard' || profile.workPattern === 'flexible',
    takeoutProb: 0.38,
    mealPrepProb: 0.55,
    alcoholWeekendProb: 0.5,
    alcoholWeekdayProb: 0.12,
    dailyWantsBudget: dailyWants,
    weeklyTransfer: Math.round((profile.monthlyInvestment * 12) / 52),
    shiftPattern: profile.workPattern === 'shift',
  };

  switch (profile.lifeStage) {
    case 'student':
      p.bedtimeJitter = 1.5;
      p.lateNightProb = (w) => (w ? 0.7 : 0.45);
      p.takeoutProb = 0.55;
      p.mealPrepProb = 0.2;
      p.stepsBase = 7000; // campus walking
      p.deepWorkBase = 1.6;
      break;
    case 'parent-young-kids':
      p.lateNightProb = () => 0.15; // in bed early, just not asleep long
      p.alcoholWeekendProb = 0.2;
      p.alcoholWeekdayProb = 0.05;
      p.takeoutProb = 0.5; // survival mode
      p.mealPrepProb = 0.25; // partner + baby count
      p.deepWorkBase = 0.9;
      break;
    case 'retired':
      p.stepsBase = 6200;
      p.deepWorkBase = 1.4; // hobbies, volunteering, gardening
      p.takeoutProb = 0.18;
      p.mealPrepProb = 0.75;
      p.alcoholWeekendProb = 0.25;
      p.lateNightProb = () => 0.08;
      break;
    default:
      break;
  }

  if (profile.situation === 'new-baby') p.sleepInterruption = 1.4;
  if (profile.workPattern === 'shift') {
    p.stepsShiftBonus = 5500; // on your feet all shift
    p.bedtimeJitter = 0.7;
  }

  return p;
}

export function generateHistory(profile: UserProfile, seed: number, days = 120): DayRecord[] {
  const rand = mulberry32(seed);
  const P = paramsFor(profile);
  const records: DayRecord[] = [];

  const today = new Date('2026-07-28T00:00:00Z');
  let prevAlcohol = 0;
  let prevSleepHours = 7.4;
  let mealPrepActive = false;
  // Weight series: random walk with a drift driven by nutrition + movement
  // (embedded causal structure the pattern engine can rediscover).
  let weight = profile.weightLbs + 2.5;

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setUTCDate(d.getUTCDate() - i);
    const dow = d.getUTCDay();
    const isWeekend = dow === 0 || dow === 6;
    const dayIndex = days - 1 - i;

    // Shift workers rotate: 3 nights on, 3 off (ignores weekday rhythm).
    const onShift = P.shiftPattern && dayIndex % 6 < 3;

    // ── Sleep ──────────────────────────────────────────────────────────
    const lateNight = rand() < P.lateNightProb(isWeekend);
    let bedtime: number;
    if (onShift) {
      // Day sleep after a night shift: "bedtime" ~8:30 AM (32.5 in prev-day hours).
      bedtime = 8.2 + rand() * 1.2;
    } else {
      bedtime = P.bedtimeBase - 0.4 + (lateNight ? 1.3 + rand() * 1.5 : rand() * P.bedtimeJitter);
    }
    let sleepHours = clamp(
      (onShift ? 6.6 : 8.7 - (bedtime - 22.5) * 0.85) + (rand() - 0.5) * 1.6,
      4.2,
      9.3,
    );
    // Fragmentation (new baby, on-call): lose a random chunk most nights.
    if (P.sleepInterruption > 0 && rand() < 0.75) {
      sleepHours = clamp(sleepHours - rand() * P.sleepInterruption * 1.6, 3.8, 9);
    }
    const daySleepPenalty = onShift ? 12 : 0; // circadian-misaligned sleep is lighter
    const fragmentationPenalty = P.sleepInterruption > 0 ? 10 : 0;
    const sleepQuality = clamp(
      55 + (sleepHours - 6.5) * 11 - prevAlcohol * 9 - daySleepPenalty - fragmentationPenalty + (rand() - 0.5) * 14,
      22,
      98,
    );

    // ── Recovery ───────────────────────────────────────────────────────
    // Age drags maximal HRV down (hrv-individual); trends stay personal.
    const ageHrvOffset = Math.max(0, (profile.age - 30) * 0.45);
    const recoveryScore = clamp(
      0.55 * sleepQuality + 0.25 * (prevSleepHours * 10) - prevAlcohol * 6 + rand() * 18,
      20,
      99,
    );
    const hrv = Math.round(clamp(30 + recoveryScore * 0.45 - ageHrvOffset + (rand() - 0.5) * 10, 14, 95));
    const restingHR = Math.round(
      clamp(
        68 - recoveryScore * 0.12 + prevAlcohol * 2 + (profile.sex === 'female' ? 2.5 : 0) + (rand() - 0.5) * 4,
        46,
        82,
      ),
    );

    // ── Movement ───────────────────────────────────────────────────────
    const didWorkout = !onShift && rand() < (recoveryScore > 60 ? P.workoutProb + 0.1 : P.workoutProb * 0.6);
    const workoutTime: DayRecord['workoutTime'] = didWorkout
      ? rand() < P.morningWorkoutBias
        ? 'morning'
        : 'evening'
      : null;
    const steps = Math.round(
      clamp(
        P.stepsBase +
          (onShift ? P.stepsShiftBonus : 0) +
          (didWorkout ? 3500 : 0) +
          (isWeekend && P.weekendMatters ? 1200 : 0) +
          rand() * 4500,
        1500,
        22000,
      ),
    );
    const activeMinutes = Math.round(clamp((didWorkout ? 45 : onShift ? 25 : 8) + rand() * 30, 0, 130));

    // ── Nutrition & substances ─────────────────────────────────────────
    if (dow === 0) mealPrepActive = rand() < P.mealPrepProb;
    const mealPrepped = mealPrepActive && dow >= 1 && dow <= 4;
    const ateTakeout = rand() < (mealPrepped ? 0.12 : isWeekend ? P.takeoutProb + 0.15 : P.takeoutProb);
    const nutritionScore = clamp(
      58 + (mealPrepped ? 18 : 0) - (ateTakeout ? 14 : 0) + (rand() - 0.5) * 16,
      20,
      98,
    );
    // Weekends, plus the first off-day after a shift block (post-block unwind).
    const drinkDay = isWeekend || (P.shiftPattern && !onShift && dayIndex % 6 === 3);
    const alcoholDrinks =
      drinkDay && rand() < P.alcoholWeekendProb
        ? Math.ceil(rand() * 3)
        : rand() < P.alcoholWeekdayProb
          ? 1
          : 0;

    // ── Finances ───────────────────────────────────────────────────────
    // Embedded pattern: the shorter the sleep, the more impulse spending
    // (≈ +45% per hour under 7.2h — tired brains reach for the card).
    let discretionarySpend =
      P.dailyWantsBudget * (0.45 + rand() * 0.75) +
      (ateTakeout ? Math.min(26, P.dailyWantsBudget * 0.35) : 0) +
      (isWeekend && P.weekendMatters ? P.dailyWantsBudget * 0.3 : 0);
    discretionarySpend *= 1 + Math.max(0, 7.2 - sleepHours) * 0.45;
    discretionarySpend = Math.round(discretionarySpend * 100) / 100;
    const savedToday = dow === 5 ? P.weeklyTransfer : 0;

    // ── Productivity ───────────────────────────────────────────────────
    // Embedded patterns: sleep and chronotype-aligned workouts lift focus.
    const wellRested = sleepHours > 7.5;
    const alignedWorkout =
      (profile.chronotype === 'evening' && workoutTime === 'evening') ||
      (profile.chronotype !== 'evening' && workoutTime === 'morning');
    let focusScore = clamp(
      50 +
        (wellRested ? 16 : sleepHours < 6.5 ? -12 : 0) +
        (alignedWorkout ? 10 : 0) -
        prevAlcohol * 5 -
        (onShift ? 14 : 0) +
        (rand() - 0.5) * 18,
      15,
      99,
    );
    if (isWeekend && P.weekendMatters) focusScore = clamp(focusScore - 15, 10, 99);
    const offDay = P.weekendMatters ? isWeekend : onShift;
    const deepWorkHours = offDay
      ? Math.round(rand() * 15) / 10
      : Math.round(clamp(P.deepWorkBase + (focusScore - 50) * 0.045 + rand() * 1.4, 0, 7) * 10) / 10;
    const tasksPlanned = offDay ? 3 : 6 + Math.round(rand() * 3);
    const tasksCompleted = Math.round(
      clamp(tasksPlanned * (0.35 + (focusScore / 100) * 0.6 + (rand() - 0.5) * 0.15), 0, tasksPlanned),
    );

    // ── Body & self-report ─────────────────────────────────────────────
    // Daily weight drift: better nutrition and more movement pull it down,
    // takeout/short-sleep push it up — plus scale noise.
    const drift =
      (58 - nutritionScore) * 0.0022 +
      (7500 - Math.min(steps, 14000)) * 0.000012 +
      (ateTakeout ? 0.03 : 0) +
      (sleepHours < 6.5 ? 0.02 : 0);
    weight = clamp(weight + drift + (rand() - 0.5) * 0.5, profile.weightLbs - 30, profile.weightLbs + 15);
    const energy = clamp(Math.round(3 + sleepQuality / 20 + recoveryScore / 40 + (rand() - 0.5) * 2), 1, 10);
    const mood = clamp(Math.round(4 + energy * 0.5 + (rand() - 0.5) * 2), 1, 10);

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
      workedShift: P.shiftPattern ? onShift : undefined,
      weightLbs: Math.round(weight * 10) / 10,
      mood,
      energy,
    });

    prevAlcohol = alcoholDrinks;
    prevSleepHours = sleepHours;
  }

  shapeDemoDay(records, profile);
  return records;
}

/**
 * Make "today" a compelling demo day per situation, so each persona's
 * briefing has a clear story: green-light recovery for a healthy day,
 * honest fatigue for a new parent, crunch-mode sleep debt for finals.
 */
function shapeDemoDay(records: DayRecord[], profile: UserProfile): void {
  const t = records[records.length - 1];

  switch (profile.situation) {
    case 'new-baby':
      t.sleepHours = 5.6;
      t.sleepQuality = 48;
      t.recoveryScore = 41;
      t.hrv = 38;
      t.alcoholDrinks = 0;
      t.didWorkout = false;
      t.workoutTime = null;
      break;
    case 'crunch':
      t.sleepHours = 6.1;
      t.sleepQuality = 61;
      t.recoveryScore = 54;
      t.deepWorkHours = 5.5;
      t.didWorkout = false;
      t.workoutTime = null;
      break;
    case 'sick':
      t.sleepHours = 8.4;
      t.recoveryScore = 35;
      t.restingHR += 7;
      t.didWorkout = false;
      t.workoutTime = null;
      break;
    default:
      t.sleepHours = 7.9;
      t.sleepQuality = 88;
      t.bedtime = t.workedShift ? t.bedtime : 22.5;
      t.recoveryScore = 91;
      t.hrv = Math.max(t.hrv, Math.round(72 - Math.max(0, (profile.age - 30) * 0.45)));
      t.restingHR = Math.min(t.restingHR, profile.sex === 'female' ? 56 : 52);
      t.alcoholDrinks = 0;
      t.didWorkout = false;
      t.workoutTime = null;
      break;
  }

}
