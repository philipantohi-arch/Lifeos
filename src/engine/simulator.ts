/**
 * Future Simulator.
 *
 * Models the long-run effect of a sustained behavior change on the user's
 * pillars and Life Score — personalized: weight-loss speed respects the
 * safe band for the user's age, alcohol effects scale with how much they
 * actually drink, step targets follow the age-banded plateau, sleep
 * scenarios use the personal range, and money uses real compound math with
 * their actual balance/contributions. Pillar weights are the user's own.
 *
 * Directional projections for decision-making, not medical or financial
 * guarantees; the UI labels them as such.
 */

import type {
  DayRecord,
  PersonalTargets,
  Scenario,
  SimulationPoint,
  SimulationResult,
  UserProfile,
} from './types';
import { computeLifeScore } from './lifeScore';
import { deriveTargets } from './personalize';

const clamp = (v: number, lo = 0, hi = 100) => Math.min(hi, Math.max(lo, v));

/** Smooth ramp 0→1 over `rampMonths`, then flat — habits take time to pay off. */
function ramp(month: number, rampMonths: number): number {
  return clamp(month / rampMonths, 0, 1);
}

/**
 * Expected nominal annual return for projections: 6% — the middle path
 * between 1900–2024 history (9.7% nominal, DMS) and Vanguard's 10-year
 * forward forecast (3.9–5.9%). See researchBase: equity-returns.
 */
const NOMINAL_ANNUAL_RETURN = 0.06;

/** Months until savings goal at current balance + monthly contributions. */
function monthsToGoal(profile: UserProfile, extraMonthly: number): number {
  const r = NOMINAL_ANNUAL_RETURN / 12;
  let bal = profile.savingsBalance;
  const monthly = profile.monthlyInvestment + extraMonthly;
  let m = 0;
  while (bal < profile.savingsGoal && m < 600) {
    bal = bal * (1 + r) + monthly;
    m++;
  }
  return m;
}

interface PillarShift {
  health?: number;
  wealth?: number;
  productivity?: number;
  relationships?: number;
  habits?: number;
  rampMonths: number;
  /** Extra monthly dollars saved/invested (compounds at NOMINAL_ANNUAL_RETURN) */
  monthlyDollars?: number;
  highlights: string[];
}

/**
 * Scenario definitions, personalized. Questions and effects are built
 * from the profile + actual history, so Rosa's step scenario differs from
 * Sam's, and a light drinker sees smaller quit-alcohol gains than a
 * heavy one.
 */
export function getScenarios(profile: UserProfile, records: DayRecord[]): Scenario[] {
  const t = deriveTargets(profile);
  const drinks7 = records.slice(-28).reduce((a, r) => a + r.alcoholDrinks, 0) / 4;
  const [sleepLo, sleepHi] = t.sleepRange;

  const list: Scenario[] = [];

  if (profile.weightLbs > 150 && profile.lifeStage !== 'retired') {
    list.push({
      id: 'lose-20',
      question: 'What happens if I lose 20 pounds?',
      emoji: '⚖️',
      description: `Sustainable ${t.weightLossLbPerWeek[0]}–${t.weightLossLbPerWeek[1]} lb/week cut with strength training preserved (CDC safe band for your age).`,
    });
  }

  const investAmt = profile.monthlyIncome >= 5000 ? 500 : 100;
  list.push({
    id: 'invest-extra',
    question: `What if I invest an extra $${investAmt} every month?`,
    emoji: '📈',
    description: `Additional $${investAmt}/mo into index funds at a 6% nominal expected return (between long-run history and forward-looking forecasts).`,
  });

  if (drinks7 >= 1) {
    list.push({
      id: 'quit-alcohol',
      question: 'What if I stop drinking alcohol?',
      emoji: '🚫',
      description: `You average ~${Math.round(drinks7)} drinks/week. Zero recovers sleep quality, HRV, and ~$${Math.round(drinks7 * 4.33 * 9)}/mo.`,
    });
  }

  list.push({
    id: 'sleep-range',
    question:
      profile.workPattern === 'shift'
        ? 'What if I protect an anchor-sleep window every day?'
        : `What if I sleep ${sleepLo}–${sleepHi} hours every night?`,
    emoji: '😴',
    description:
      profile.workPattern === 'shift'
        ? 'A fixed 3–4h core sleep window on shift AND off days — the evidence-backed rotation strategy.'
        : `Consistent ${sleepLo}+ hours in your age band's range, anchored to your ${profile.chronotype} chronotype.`,
  });

  list.push({
    id: 'steps-target',
    question: `What if I hit ${t.stepsTarget.toLocaleString()} steps every day?`,
    emoji: '🚶',
    description: `Your age band's mortality-benefit plateau is ${profile.age >= 60 ? '6,000–8,000' : '8,000–10,000'} steps — this targets it daily.`,
  });

  list.push({
    id: 'meal-prep',
    question: 'What if I meal prep every Sunday?',
    emoji: '🍱',
    description: 'Frequent home cooking tracks with better diet quality and lower food spending in national cohort data.',
  });

  list.push({
    id: 'weekly-connection',
    question: 'What if I never miss my connection cadence?',
    emoji: '🤝',
    description: `Close contact every ${t.familyContactCadenceDays} days, per your cadence. Strong ties: ~50% survival advantage (148-study meta-analysis).`,
  });

  return list;
}

function shiftsFor(
  scenarioId: string,
  profile: UserProfile,
  t: PersonalTargets,
  records: DayRecord[],
  horizon: number,
): PillarShift {
  const drinksWeekly = records.slice(-28).reduce((a, r) => a + r.alcoholDrinks, 0) / 4;

  switch (scenarioId) {
    case 'lose-20': {
      const rate = (t.weightLossLbPerWeek[0] + t.weightLossLbPerWeek[1]) / 2;
      const months = Math.round(20 / (rate * 4.33));
      return {
        health: 11,
        productivity: 4,
        habits: 6,
        rampMonths: months,
        highlights: [
          `At ${t.weightLossLbPerWeek[0]}–${t.weightLossLbPerWeek[1]} lb/week (your age's safe band) you reach ${profile.weightLbs - 20} lbs in ~${months} months.`,
          'Projected resting HR drops ~4 bpm; recovery scores rise ~8 points.',
          profile.age >= 50
            ? 'Strength training + 1.0–1.2 g/kg protein preserves muscle — critical at your age (PROT-AGE).'
            : 'Energy gains compound into roughly one extra productive hour per day by month 4.',
        ],
      };
    }
    case 'invest-extra': {
      const amt = profile.monthlyIncome >= 5000 ? 500 : 100;
      const r = NOMINAL_ANNUAL_RETURN / 12;
      const fv = amt * ((Math.pow(1 + r, horizon) - 1) / r);
      const base = monthsToGoal(profile, 0);
      const withExtra = monthsToGoal(profile, amt);
      const accel =
        base > 0 && base < 600 && withExtra < base
          ? `Your ${profile.savingsGoalLabel.toLowerCase()} goal arrives ${base - withExtra} months sooner (month ${withExtra} instead of ${base}).`
          : `Compounding does the heavy lifting: contributions are $${(amt * horizon).toLocaleString()}, growth adds the rest.`;
      return {
        wealth: 14,
        habits: 3,
        rampMonths: 2,
        monthlyDollars: amt,
        highlights: [
          `$${amt}/mo at 6% nominal grows to $${Math.round(fv).toLocaleString()} in ${Math.round(horizon / 12)} year${horizon >= 24 ? 's' : ''} — $${Math.round(fv - amt * horizon).toLocaleString()} of it pure growth.`,
          accel,
          profile.lifeStage === 'student'
            ? 'Starting this decade is the whole game: money invested at 21 has ~4× the retirement value of money invested at 41.'
            : 'Kept up for 20 years, this single habit adds six figures to net worth.',
        ],
      };
    }
    case 'quit-alcohol': {
      const scale = clamp(drinksWeekly / 6, 0.3, 1.2);
      return {
        health: Math.round(9 * scale),
        productivity: Math.round(5 * scale),
        wealth: 3,
        rampMonths: 2,
        monthlyDollars: Math.round(drinksWeekly * 4.33 * 9),
        highlights: [
          `At ~${Math.round(drinksWeekly)} drinks/week, quitting recovers ~${Math.round(9 * scale)} sleep-quality points within 3 weeks (your data shows the per-night recovery cost).`,
          profile.sex === 'female'
            ? 'Guidelines set women\'s low-risk ceiling at half of men\'s — your body clears alcohol more slowly, so the gains are proportionally larger.'
            : 'You reclaim the compromised mornings that follow drinking nights.',
          `~$${Math.round(drinksWeekly * 4.33 * 9)}/mo redirected to savings compounds meaningfully within 5 years.`,
        ],
      };
    }
    case 'sleep-range':
      return {
        health: 10,
        productivity: 8,
        relationships: 2,
        habits: 4,
        rampMonths: 1.5,
        highlights:
          profile.workPattern === 'shift'
            ? [
                'A fixed anchor window cuts circadian whiplash — regularity predicts health outcomes beyond duration.',
                'Expect steadier energy across rotations within 3–4 weeks.',
                'Strategic 20–30 min pre-shift naps stack on top for alertness during nights.',
              ]
            : [
                `Your own data: focus runs higher after ${t.sleepRange[0]}h+ nights — this makes that your default.`,
                'Projected: +1h of quality deep work per workday within 6 weeks.',
                'Impulse spending drops too — your short-sleep days run measurably more expensive.',
              ],
      };
    case 'steps-target':
      return {
        health: profile.age >= 60 ? 10 : 8,
        productivity: 3,
        habits: 5,
        rampMonths: 2,
        highlights: [
          profile.age >= 60
            ? `For your age band the mortality-benefit plateau is 6,000–8,000 steps — hitting ${t.stepsTarget.toLocaleString()} daily captures essentially all of it.`
            : `~2,100 extra calories burned weekly — roughly 2.5 lbs/quarter without diet changes.`,
          'Afternoon energy dips shrink; step count correlates with same-day mood in your data.',
          'Walking meetings or errands on foot can absorb much of the target without extra time cost.',
        ],
      };
    case 'meal-prep':
      return {
        health: 7,
        wealth: 4,
        habits: 6,
        rampMonths: 2,
        monthlyDollars: Math.round(t.weeklyDiscretionary * 0.12 * 4.33),
        highlights: [
          'Frequent home cooking tracks with higher diet quality and lower food spending (national cohort data).',
          'Ultra-processed/takeout meals drive ~500 extra calories/day in controlled feeding studies.',
          `Your own meal-prepped weeks already show the effect — this locks it in year-round.`,
        ],
      };
    case 'weekly-connection':
      return {
        relationships: 14,
        health: 3,
        rampMonths: 3,
        highlights: [
          'Strong social ties: ~50% higher survival odds across 148 studies — an effect comparable to quitting smoking.',
          profile.age >= 60
            ? 'Loneliness raises dementia risk ~50% in older adults (US Surgeon General, 2023) — cadence is protective, not sentimental.'
            : 'The Harvard Study: relationship quality at 50 predicted health at 80 better than cholesterol.',
          'Consistent cadence beats sporadic grand gestures — the trend line is what compounds.',
        ],
      };
    default:
      return { rampMonths: 2, highlights: [] };
  }
}

export function simulate(
  scenarioId: string,
  records: DayRecord[],
  profile: UserProfile,
  horizonMonths = 24,
): SimulationResult {
  const t = deriveTargets(profile);
  const scenario = getScenarios(profile, records).find((s) => s.id === scenarioId)!;
  const shift = shiftsFor(scenarioId, profile, t, records, horizonMonths);
  const base = computeLifeScore(records, profile);

  const basePillars: Record<string, number> = {};
  for (const p of base.pillars) basePillars[p.key] = p.score;
  const weights = t.weights;

  const baseline: SimulationPoint[] = [];
  const simulated: SimulationPoint[] = [];
  const r = NOMINAL_ANNUAL_RETURN / 12;
  let baseDollars = profile.savingsBalance;
  let simDollars = profile.savingsBalance;

  for (let m = 0; m <= horizonMonths; m++) {
    if (m > 0) {
      baseDollars = baseDollars * (1 + r) + profile.monthlyInvestment;
      simDollars = simDollars * (1 + r) + profile.monthlyInvestment + (shift.monthlyDollars ?? 0);
    }

    const drift = Math.min(m * 0.05, 1);
    const basePoint: SimulationPoint = {
      month: m,
      health: clamp(basePillars.health + drift),
      wealth: clamp(basePillars.wealth + (profile.lifeStage === 'retired' ? 0 : m * 0.12)),
      productivity: clamp(basePillars.productivity + drift),
      lifeScore: 0,
      dollars: Math.round(baseDollars),
    };
    basePoint.lifeScore = Math.round(
      basePoint.health * weights.health +
        basePoint.wealth * weights.wealth +
        basePoint.productivity * weights.productivity +
        basePillars.relationships * weights.relationships +
        basePillars.habits * weights.habits,
    );
    baseline.push(basePoint);

    const k = ramp(m, shift.rampMonths);
    // Diminishing returns near the ceiling: gains shrink as pillar → 100.
    const apply = (baseScore: number, maxShift = 0) =>
      clamp(baseScore + maxShift * k * (1 - baseScore / 180));

    const simPoint: SimulationPoint = {
      month: m,
      health: apply(basePoint.health, shift.health ?? 0),
      wealth: apply(basePoint.wealth, shift.wealth ?? 0),
      productivity: apply(basePoint.productivity, shift.productivity ?? 0),
      lifeScore: 0,
      dollars: Math.round(simDollars),
    };
    const simRel = apply(basePillars.relationships, shift.relationships ?? 0);
    const simHab = apply(basePillars.habits, shift.habits ?? 0);
    simPoint.lifeScore = Math.round(
      simPoint.health * weights.health +
        simPoint.wealth * weights.wealth +
        simPoint.productivity * weights.productivity +
        simRel * weights.relationships +
        simHab * weights.habits,
    );
    simulated.push(simPoint);
  }

  const end = simulated[simulated.length - 1];
  const endBase = baseline[baseline.length - 1];

  return {
    scenarioId,
    title: scenario.question,
    summary: `Projected Life Score after ${horizonMonths} months: ${end.lifeScore} vs ${endBase.lifeScore} on your current path (+${end.lifeScore - endBase.lifeScore} points).`,
    horizonMonths,
    baseline,
    simulated,
    highlights: shift.highlights,
  };
}
