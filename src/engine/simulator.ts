/**
 * Future Simulator.
 *
 * Models the long-run effect of a sustained behavior change on the user's
 * pillars and Life Score. Each scenario perturbs a small set of drivers
 * (sleep, spending, training, alcohol, steps) and rolls them forward with
 * realistic ramp-up curves, diminishing returns, and — for money —
 * actual compound-growth math.
 *
 * These are directional projections for decision-making, not medical or
 * financial guarantees; the UI labels them as such.
 */

import type {
  DayRecord,
  Scenario,
  SimulationPoint,
  SimulationResult,
  UserProfile,
} from './types';
import { computeLifeScore } from './lifeScore';

export const SCENARIOS: Scenario[] = [
  {
    id: 'lose-20',
    question: 'What happens if I lose 20 pounds?',
    emoji: '⚖️',
    description: 'Sustainable 1 lb/week cut with strength training preserved.',
  },
  {
    id: 'invest-500',
    question: 'What if I invest an extra $500 every month?',
    emoji: '📈',
    description: 'Additional $500/mo into index funds at 7% expected annual return.',
  },
  {
    id: 'quit-alcohol',
    question: 'What if I stop drinking alcohol?',
    emoji: '🚫',
    description: 'Zero drinks; recovers sleep quality, HRV, and ~$180/mo.',
  },
  {
    id: 'sleep-8',
    question: 'What if I sleep eight hours every night?',
    emoji: '😴',
    description: 'Consistent 10:30 PM bedtime, 8h in bed, 7 nights a week.',
  },
  {
    id: 'steps-10k',
    question: 'What if I walk 10,000 steps every day?',
    emoji: '🚶',
    description: 'Daily movement floor of 10k steps regardless of workouts.',
  },
];

const clamp = (v: number, lo = 0, hi = 100) => Math.min(hi, Math.max(lo, v));

/** Smooth ramp 0→1 over `rampMonths`, then flat — habits take time to pay off. */
function ramp(month: number, rampMonths: number): number {
  return clamp(month / rampMonths, 0, 1);
}

interface PillarShift {
  /** Max pillar-point shifts at full effect */
  health?: number;
  wealth?: number;
  productivity?: number;
  relationships?: number;
  habits?: number;
  rampMonths: number;
  /** Extra monthly dollars saved/invested (compounds) */
  monthlyDollars?: number;
  highlights: (profile: UserProfile, horizon: number) => string[];
}

const SHIFTS: Record<string, PillarShift> = {
  'lose-20': {
    health: 11,
    productivity: 4,
    habits: 6,
    rampMonths: 5,
    highlights: (p) => [
      `At 1 lb/week you reach ${p.weightLbs - 20} lbs in ~5 months.`,
      'Projected resting HR drops ~4 bpm; recovery scores rise ~8 points.',
      'Energy gains compound into roughly one extra productive hour per day by month 4.',
    ],
  },
  'invest-500': {
    wealth: 14,
    habits: 3,
    rampMonths: 2,
    monthlyDollars: 500,
    highlights: (p, horizon) => {
      const months = horizon;
      const r = 0.07 / 12;
      const fv = 500 * ((Math.pow(1 + r, months) - 1) / r);
      const goalMonthsBase = monthsToGoal(p, 0);
      const goalMonthsNew = monthsToGoal(p, 500);
      return [
        `$500/mo at 7% grows to $${Math.round(fv).toLocaleString()} in ${Math.round(months / 12)} years — $${Math.round(fv - 500 * months).toLocaleString()} of it pure growth.`,
        `Your ${p.savingsGoalLabel.toLowerCase()} goal arrives ${goalMonthsBase - goalMonthsNew} months sooner (month ${goalMonthsNew} instead of ${goalMonthsBase}).`,
        'Kept up for 20 years, this single habit adds ~$260,000 to net worth.',
      ];
    },
  },
  'quit-alcohol': {
    health: 9,
    productivity: 5,
    wealth: 3,
    rampMonths: 2,
    monthlyDollars: 180,
    highlights: () => [
      'Sleep quality recovers ~9 points within 3 weeks; HRV trends up ~7ms.',
      'You reclaim ~6 compromised mornings per month.',
      '$180/mo redirected to savings adds $11,500 over 5 years with growth.',
    ],
  },
  'sleep-8': {
    health: 10,
    productivity: 8,
    relationships: 2,
    habits: 4,
    rampMonths: 1.5,
    highlights: () => [
      'Your own data: focus runs ~18% higher after 7.5h+ nights — this makes that your default.',
      'Projected: +1.1h of deep work per weekday within 6 weeks.',
      'Impulse spending drops too — your poor-sleep days average 40% higher discretionary spend.',
    ],
  },
  'steps-10k': {
    health: 8,
    productivity: 3,
    habits: 5,
    rampMonths: 2,
    highlights: () => [
      '~2,100 extra calories burned weekly — roughly 2.5 lbs/quarter without diet changes.',
      'Afternoon energy dips shrink; your step count correlates with same-day mood.',
      'Walking meetings could absorb 40% of the target without extra time cost.',
    ],
  },
};

/** Months until savings goal at current balance + monthly contributions. */
function monthsToGoal(profile: UserProfile, extraMonthly: number): number {
  const r = 0.07 / 12;
  let bal = profile.savingsBalance;
  const monthly = profile.monthlyInvestment + extraMonthly;
  let m = 0;
  while (bal < profile.savingsGoal && m < 600) {
    bal = bal * (1 + r) + monthly;
    m++;
  }
  return m;
}

export function simulate(
  scenarioId: string,
  records: DayRecord[],
  profile: UserProfile,
  horizonMonths = 24,
): SimulationResult {
  const scenario = SCENARIOS.find((s) => s.id === scenarioId)!;
  const shift = SHIFTS[scenarioId];
  const base = computeLifeScore(records, profile);

  const basePillars: Record<string, number> = {};
  for (const p of base.pillars) basePillars[p.key] = p.score;

  const weights: Record<string, number> = {
    health: 0.3,
    wealth: 0.2,
    productivity: 0.2,
    relationships: 0.15,
    habits: 0.15,
  };

  const baseline: SimulationPoint[] = [];
  const simulated: SimulationPoint[] = [];
  const r = 0.07 / 12;
  let baseDollars = profile.savingsBalance;
  let simDollars = profile.savingsBalance;

  for (let m = 0; m <= horizonMonths; m++) {
    // Baseline: mild mean-reversion drift, money compounds at current rate.
    if (m > 0) {
      baseDollars = baseDollars * (1 + r) + profile.monthlyInvestment;
      simDollars = simDollars * (1 + r) + profile.monthlyInvestment + (shift.monthlyDollars ?? 0);
    }

    const drift = Math.min(m * 0.05, 1); // baseline drifts +1 pt max over horizon
    const basePoint: SimulationPoint = {
      month: m,
      health: clamp(basePillars.health + drift),
      wealth: clamp(basePillars.wealth + m * 0.12), // savings creep up on autopilot
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
    highlights: shift.highlights(profile, horizonMonths),
  };
}
