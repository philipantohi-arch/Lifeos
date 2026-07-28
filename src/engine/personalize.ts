/**
 * Personalization engine.
 *
 * Derives every target the scoring/recommendation/simulation engines use
 * from the user's profile, with each rule traceable to the research base.
 * This is the single place where "who you are" becomes "what good looks
 * like for you" — no other module hard-codes a universal number.
 */

import type { PersonalTargets, PillarKey, UserProfile } from './types';

const BASE_WEIGHTS: Record<PillarKey, number> = {
  health: 0.4,
  wealth: 0.3,
  productivity: 0.3,
};

/** Sleep need range by age band — NSF consensus (nsf-sleep-duration). */
function sleepRange(age: number): [number, number] {
  if (age < 18) return [8, 10];
  if (age >= 65) return [7, 8];
  return [7, 9];
}

/**
 * Daily step target — Paluch et al. 2022 (paluch-steps-2022): the
 * mortality-benefit plateau is ~6–8k for 60+, ~8–10k under 60. Beginners
 * start at the low end of their band (acsm-progression).
 */
function stepsTarget(profile: UserProfile): number {
  const band: [number, number] = profile.age >= 60 ? [6000, 8000] : [8000, 10000];
  switch (profile.fitnessLevel) {
    case 'beginner':
      return band[0];
    case 'intermediate':
      return Math.round((band[0] + band[1]) / 2);
    case 'advanced':
      return band[1];
  }
}

/**
 * Ideal in-bed time by chronotype (chronotype-distribution,
 * synchrony-effect), shifted for work pattern. Decimal hours, 24h clock
 * (values ≥24 mean past midnight).
 */
function bedtimeIdeal(profile: UserProfile): number {
  let base: number;
  switch (profile.chronotype) {
    case 'morning':
      base = 21.75; // 9:45 PM
      break;
    case 'intermediate':
      base = 22.5; // 10:30 PM
      break;
    case 'evening':
      base = 23.75; // 11:45 PM
      break;
  }
  // Students & evening types skew later naturally (latest chronotype ~20).
  if (profile.lifeStage === 'student') base += 0.5;
  // Shift work: clock bedtime is meaningless — anchor sleep matters
  // (shift-anchor-sleep). We still return a nominal anchor start.
  if (profile.workPattern === 'shift') base = 25.0; // 1:00 AM nominal anchor
  return base;
}

/** Deep-work window from chronotype synchrony (synchrony-effect). */
function deepWorkWindow(profile: UserProfile): [number, number] {
  switch (profile.chronotype) {
    case 'morning':
      return [8, 11];
    case 'intermediate':
      return [9, 12];
    case 'evening':
      return [15, 18];
  }
}

/**
 * Savings-rate target by life stage — anchored on the ~15% retirement
 * guideline (fidelity-milestones) and 20% total savings in 50/30/20
 * (fifty-thirty-twenty), softened for students/new parents.
 */
function savingsRateTarget(profile: UserProfile): number {
  switch (profile.lifeStage) {
    case 'student':
      return 0.05;
    case 'parent-young-kids':
      return 0.12;
    case 'pre-retirement':
      return 0.2;
    case 'retired':
      return 0; // drawdown phase — measured by withdrawal discipline instead
    default:
      return 0.15;
  }
}

/** Emergency fund months — CFPB (emergency-fund); more if income varies. */
function emergencyFundMonths(profile: UserProfile): number {
  if (profile.lifeStage === 'student') return 1; // starter fund
  return profile.variableIncome ? 9 : profile.lifeStage === 'parent-young-kids' ? 6 : 4;
}

/**
 * Weekly low-risk alcohol ceiling. US guidelines are daily caps
 * (≤2 men / ≤1 women); Canada 2023 flags risk above 2/week
 * (us-alcohol-guidelines). LifeOS coaches toward the conservative
 * midpoint: well under the US weekly implication, sex-adjusted.
 */
function maxDrinksWeekly(profile: UserProfile): number {
  return profile.sex === 'female' ? 4 : 6;
}

/** Safe weight-loss band, lb/week — CDC (cdc-weight-loss), gentler 65+. */
function weightLossBand(profile: UserProfile): [number, number] {
  if (profile.age >= 65) return [0.5, 1]; // preserve lean mass (protein-older-adults)
  return [1, 2];
}

/** Personalized pillar weights: base × user priority (1–5), normalized. */
function personalWeights(profile: UserProfile): Record<PillarKey, number> {
  const keys = Object.keys(BASE_WEIGHTS) as PillarKey[];
  const raw = keys.map((k) => BASE_WEIGHTS[k] * (profile.priorities[k] ?? 3));
  const total = raw.reduce((a, b) => a + b, 0);
  const out = {} as Record<PillarKey, number>;
  keys.forEach((k, i) => {
    out[k] = raw[i] / total;
  });
  return out;
}

export function deriveTargets(profile: UserProfile): PersonalTargets {
  const [lo, hi] = sleepRange(profile.age);
  return {
    sleepRange: [lo, hi],
    bedtimeIdeal: bedtimeIdeal(profile),
    stepsTarget: stepsTarget(profile),
    // WHO 2020 (who-activity-2020): 150–300 min moderate weekly; aim
    // mid-band, low end for beginners/65+.
    activeMinutesWeekly:
      profile.fitnessLevel === 'beginner' || profile.age >= 65 ? 150 : 225,
    strengthSessionsWeekly: profile.age >= 65 ? 3 : 2, // + balance work 65+ (WHO)
    weeklyDiscretionary: Math.round(((profile.monthlyIncome * 0.3) / 30) * 7), // 30% wants band
    savingsRateTarget: savingsRateTarget(profile),
    emergencyFundMonths: emergencyFundMonths(profile),
    maxDrinksWeekly: maxDrinksWeekly(profile),
    weightLossLbPerWeek: weightLossBand(profile),
    deepWorkWindow: deepWorkWindow(profile),
    // one-habit-at-a-time: cap concurrent NEW habit pushes.
    simultaneousHabitLimit: profile.situation === 'normal' ? 2 : 1,
    weights: personalWeights(profile),
  };
}

/** Format a decimal hour as a clock string, handling past-midnight. */
export function fmtHour(h: number): string {
  const wrapped = ((h % 24) + 24) % 24;
  const hh = Math.floor(wrapped);
  const mm = Math.round((wrapped - hh) * 60);
  const ampm = hh >= 12 ? 'PM' : 'AM';
  const h12 = hh % 12 === 0 ? 12 : hh % 12;
  return `${h12}:${mm.toString().padStart(2, '0')} ${ampm}`;
}
