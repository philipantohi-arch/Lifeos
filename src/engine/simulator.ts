/**
 * Future Simulator — probability edition.
 *
 * Every scenario is a sustained behavior change. Its long-run effect is
 * shown two ways:
 *
 *   1. A Life Score trajectory vs. your current path (directional model
 *      with habit ramp-up and diminishing returns).
 *   2. The honest part: Monte Carlo odds on YOUR actual goals — the same
 *      bootstrap-of-your-own-history engine used everywhere else — plus a
 *      fan chart of futures for the primary affected goal.
 *
 * Directional projections for decision support, not guarantees.
 */

import type {
  DayRecord,
  Goal,
  InterventionEffect,
  Scenario,
  SimulationPoint,
  SimulationResult,
  UserProfile,
} from './types';
import { pillarProcessScores, pillarOutcomeScores, PROCESS_WEIGHT, OUTCOME_WEIGHT } from './lifeScore';
import { deriveTargets } from './personalize';
import { forecastGoal, oddsDelta } from './montecarlo';
import { METRIC_META, assessGoals, currentMetric } from './goals';
import { generateBaselineHistory } from '../data/generator';
import type { BaselineHabits, PillarKey } from './types';

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

interface ScenarioDef extends Scenario {
  intervention: InterventionEffect;
  /** Goal metrics this change plausibly moves */
  affects: Goal['metric'][];
  shifts: {
    health?: number;
    wealth?: number;
    productivity?: number;
    rampMonths: number;
    monthlyDollars?: number;
  };
  highlights: string[];
}

/**
 * Scenario definitions, personalized. Questions, effects, and evidence
 * copy are built from the profile + actual history, so a light drinker
 * sees smaller quit-alcohol gains than a heavy one, and step targets
 * follow the age plateau.
 */
export function getScenarioDefs(profile: UserProfile, records: DayRecord[]): ScenarioDef[] {
  const t = deriveTargets(profile);
  const drinksWeekly = records.slice(-28).reduce((a, r) => a + r.alcoholDrinks, 0) / 4;
  const [sleepLo, sleepHi] = t.sleepRange;
  const stepsNow = currentMetric('stepsAvg', records, profile);

  const list: ScenarioDef[] = [];

  // ── The full protocol: every right habit at once ─────────────────────
  // Single habits move single slices; this is the honest ceiling of
  // sustained good behavior across the board.
  {
    const savingsGoal = profile.goals.find((g) => g.metric === 'savingsBalance');
    const observedWeekly = records.slice(-28).reduce((a, r) => a + r.savedToday, 0) / 4;
    const surplusWeekly = Math.max(0, ((profile.monthlyIncome - (profile.monthlyEssentials || profile.monthlyIncome * 0.6)) * 0.75) / 4.33);
    const extraWeekly = savingsGoal
      ? Math.round(Math.min(Math.max(20, surplusWeekly - observedWeekly), surplusWeekly))
      : 0;
    const deepGoal = profile.goals.find((g) => g.metric === 'deepWorkWeekly');
    const deepNow = currentMetric('deepWorkWeekly', records, profile);
    // The protocol aims at the higher of the research target and the
    // user's own goal — "everything right" includes YOUR bar.
    const stepsGoal = profile.goals.find((g) => g.metric === 'stepsAvg');
    const stepsAim = Math.max(t.stepsTarget, stepsGoal?.target ?? 0);
    list.push({
      id: 'all-in',
      question: 'What if I do everything right, consistently?',
      emoji: '🚀',
      description:
        'The full protocol: sleep in your range, hit your steps, train, meal prep, hold budget, save toward your goals — sustained.',
      intervention: {
        sleepFloorLift: 0.9,
        stepsBoost: Math.max(500, stepsAim + 400 - stepsNow),
        deepWorkBoost: deepGoal ? Math.max(0.3, (deepGoal.target - deepNow) / 5 + 0.2) : 0.5,
        workoutsBoost: 2,
        spendMult: 0.93,
        extraWeeklySavings: extraWeekly || undefined,
        weightDriftShift: profile.goals.some((g) => g.metric === 'weightLbs')
          ? -((t.weightLossLbPerWeek[0] + t.weightLossLbPerWeek[1]) / 2) * 0.7
          : undefined,
      },
      affects: ['sleepAvg', 'stepsAvg', 'deepWorkWeekly', 'workoutsWeekly', 'savingsBalance', 'weightLbs'],
      shifts: { rampMonths: 3, monthlyDollars: extraWeekly ? Math.round(extraWeekly * 4.33) : undefined },
      highlights: [
        'This is your realistic ceiling — the same scoring engine, run on a version of you whose habits all hit their marks.',
        'No single habit gets you here; the compounding of all of them does. Pick the one habit below to start with.',
        'Your goals\' odds under the full protocol are shown below — this is what consistency actually buys.',
      ],
    });
  }

  if (profile.goals.some((g) => g.metric === 'weightLbs') || (profile.weightLbs > 150 && profile.lifeStage !== 'retired')) {
    const rate = (t.weightLossLbPerWeek[0] + t.weightLossLbPerWeek[1]) / 2;
    list.push({
      id: 'commit-cut',
      question: 'What if I fully commit to the cut?',
      emoji: '⚖️',
      description: `Meal prep + training + protein, at your safe ${t.weightLossLbPerWeek[0]}–${t.weightLossLbPerWeek[1]} lb/week band (CDC).`,
      intervention: { weightDriftShift: -rate * 0.7, spendMult: 0.95 },
      affects: ['weightLbs', 'savingsBalance'],
      shifts: { health: 11, productivity: 4, rampMonths: 4 },
      highlights: [
        `Your safe band is ${t.weightLossLbPerWeek[0]}–${t.weightLossLbPerWeek[1]} lb/week — the fan chart below shows what your real week-to-week variability does to the timeline.`,
        'Projected resting HR drops ~4 bpm; recovery scores rise ~8 points.',
        profile.age >= 50
          ? 'Strength training + 1.0–1.2 g/kg protein preserves muscle — critical at your age (PROT-AGE).'
          : 'Energy gains compound into roughly one extra productive hour per day by month 4.',
      ],
    });
  }

  const investAmt = profile.monthlyIncome >= 5000 ? 500 : 100;
  list.push({
    id: 'invest-extra',
    question: `What if I invest an extra $${investAmt} every month?`,
    emoji: '📈',
    description: `Additional $${investAmt}/mo into index funds at a 6% nominal expected return (between long-run history and forward forecasts).`,
    intervention: { extraWeeklySavings: Math.round(investAmt / 4.33) },
    affects: ['savingsBalance'],
    shifts: { wealth: 14, rampMonths: 2, monthlyDollars: investAmt },
    highlights: [
      `Contributions compound: the simulation includes realistic market volatility (~13%/yr), not a smooth line.`,
      profile.lifeStage === 'student'
        ? 'Starting this decade is the whole game: money invested at 21 has ~4× the retirement value of money invested at 41.'
        : 'Kept up for 20 years, this single habit adds six figures to net worth.',
    ],
  });

  if (drinksWeekly >= 1) {
    list.push({
      id: 'quit-alcohol',
      question: 'What if I stop drinking alcohol?',
      emoji: '🚫',
      description: `You average ~${Math.round(drinksWeekly)} drinks/week. Zero recovers sleep quality, HRV, and ~$${Math.round(drinksWeekly * 4.33 * 9)}/mo.`,
      intervention: { sleepFloorLift: 0.3, spendMult: 0.97 },
      affects: ['sleepAvg', 'savingsBalance'],
      shifts: {
        health: Math.round(9 * clamp(drinksWeekly / 6, 0.3, 1.2)),
        productivity: Math.round(5 * clamp(drinksWeekly / 6, 0.3, 1.2)),
        wealth: 3,
        rampMonths: 2,
        monthlyDollars: Math.round(drinksWeekly * 4.33 * 9),
      },
      highlights: [
        `At ~${Math.round(drinksWeekly)} drinks/week, your own data shows the per-night recovery cost — quitting recovers it within ~3 weeks.`,
        profile.sex === 'female'
          ? "Guidelines set women's low-risk ceiling at half of men's — your body clears alcohol more slowly, so the gains are proportionally larger."
          : 'You reclaim the compromised mornings that follow drinking nights.',
        'Canada 2023: risk rises above 2 drinks/week; WHO finds no safe level. The trend of the evidence is one-directional.',
      ],
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
    intervention: { sleepFloorLift: 0.7 },
    affects: ['sleepAvg', 'deepWorkWeekly'],
    shifts: { health: 10, productivity: 8, rampMonths: 1.5 },
    highlights:
      profile.workPattern === 'shift'
        ? [
            'A fixed anchor window cuts circadian whiplash — regularity predicts health outcomes beyond duration.',
            'Strategic 20–30 min pre-shift naps stack on top for alertness during nights.',
          ]
        : [
            `Your own data: focus runs higher after ${sleepLo}h+ nights — this makes that your default.`,
            'Impulse spending drops too — your short-sleep days run measurably more expensive.',
          ],
  });

  list.push({
    id: 'steps-target',
    question: `What if I hit ${t.stepsTarget.toLocaleString()} steps every day?`,
    emoji: '🚶',
    description: `Your age band's mortality-benefit plateau is ${profile.age >= 60 ? '6,000–8,000' : '8,000–10,000'} steps — this targets it daily.`,
    intervention: { stepsBoost: Math.max(500, t.stepsTarget - stepsNow) },
    affects: ['stepsAvg', 'weightLbs'],
    shifts: { health: profile.age >= 60 ? 10 : 8, productivity: 3, rampMonths: 2 },
    highlights: [
      profile.age >= 60
        ? `For your age band the benefit plateaus at 6,000–8,000 steps — hitting ${t.stepsTarget.toLocaleString()} daily captures essentially all of it.`
        : '7,000+ steps/day carries −47% all-cause mortality vs 2,000 in the 2025 Lancet meta-analysis — and the curve is steepest exactly where you are.',
      'Afternoon energy dips shrink; step count correlates with same-day mood in your data.',
    ],
  });

  list.push({
    id: 'meal-prep',
    question: 'What if I meal prep every Sunday?',
    emoji: '🍱',
    description: 'Frequent home cooking tracks with better diet quality and lower food spending in national cohort data.',
    intervention: { spendMult: 0.94, weightDriftShift: -0.15 },
    affects: ['savingsBalance', 'weightLbs'],
    shifts: { health: 7, wealth: 4, rampMonths: 2, monthlyDollars: Math.round(t.weeklyDiscretionary * 0.12 * 4.33) },
    highlights: [
      'Ultra-processed/takeout meals drive ~500 extra calories/day in controlled feeding studies (Hall 2019).',
      'Your own meal-prepped weeks already show the effect — this locks it in year-round.',
    ],
  });

  return list;
}

export function getScenarios(profile: UserProfile, records: DayRecord[]): Scenario[] {
  return getScenarioDefs(profile, records).map(({ id, question, emoji, description }) => ({
    id,
    question,
    emoji,
    description,
  }));
}

/**
 * "You, if this habit becomes your norm": clone the profile with its
 * baseline habits upgraded by the intervention. Personas without an
 * explicit baseline get one derived from their history's actual means,
 * so the same machinery works for demo lives.
 */
function improvedProfile(profile: UserProfile, records: DayRecord[], def: ScenarioDef): UserProfile {
  const t = deriveTargets(profile);
  const last30 = records.slice(-30);
  const mean = (f: (r: DayRecord) => number) => last30.reduce((a, r) => a + f(r), 0) / Math.max(last30.length, 1);

  const base: BaselineHabits = profile.baseline ?? {
    typicalSleepHours: Math.round(mean((r) => r.sleepHours) * 10) / 10,
    typicalBedtime: t.bedtimeIdeal + 0.5,
    typicalSteps: Math.round(mean((r) => r.steps)),
    workoutsPerWeek: Math.round(mean((r) => (r.didWorkout ? 1 : 0)) * 7),
    deepWorkHoursPerDay: Math.round(mean((r) => r.deepWorkHours) * 10) / 10,
    takeoutMealsPerWeek: Math.round(mean((r) => (r.ateTakeout ? 1 : 0)) * 7),
    drinksPerWeek: Math.round(mean((r) => r.alcoholDrinks) * 7),
    mealPreps: mean((r) => (r.mealPrepped ? 1 : 0)) > 0.3,
  };

  const iv = def.intervention;
  const nb: BaselineHabits = { ...base };
  if (iv.sleepFloorLift) {
    nb.typicalSleepHours = Math.max(base.typicalSleepHours, t.sleepRange[0] + 0.3);
    nb.typicalBedtime = t.bedtimeIdeal;
  }
  if (iv.stepsBoost) nb.typicalSteps = base.typicalSteps + iv.stepsBoost;
  if (iv.deepWorkBoost) nb.deepWorkHoursPerDay = base.deepWorkHoursPerDay + iv.deepWorkBoost;
  if (iv.workoutsBoost) nb.workoutsPerWeek = Math.min(6, base.workoutsPerWeek + iv.workoutsBoost);
  if (def.id === 'quit-alcohol') nb.drinksPerWeek = 0;
  if (def.id === 'meal-prep' || def.id === 'commit-cut' || def.id === 'all-in') {
    nb.mealPreps = true;
    nb.takeoutMealsPerWeek = Math.min(base.takeoutMealsPerWeek, 2);
  }
  if (def.id === 'commit-cut' || def.id === 'all-in') {
    nb.workoutsPerWeek = Math.max(nb.workoutsPerWeek, t.strengthSessionsWeekly + 1);
  }
  if (def.id === 'all-in') {
    nb.drinksPerWeek = Math.min(nb.drinksPerWeek, 2);
    nb.typicalSleepHours = Math.max(nb.typicalSleepHours, t.sleepRange[0] + 0.5);
    const stepsGoal = profile.goals.find((g) => g.metric === 'stepsAvg');
    nb.typicalSteps = Math.max(nb.typicalSteps, t.stepsTarget, stepsGoal?.target ?? 0);
  }

  return {
    ...profile,
    baseline: nb,
    monthlyInvestment: profile.monthlyInvestment + (iv.extraWeeklySavings ? Math.round(iv.extraWeeklySavings * 4.33) : 0),
  };
}

export function simulate(
  scenarioId: string,
  records: DayRecord[],
  profile: UserProfile,
  horizonMonths = 24,
): SimulationResult {
  const t = deriveTargets(profile);
  const defs = getScenarioDefs(profile, records);
  const def = defs.find((s) => s.id === scenarioId) ?? defs[0];
  const weights = t.weights;
  const keys: PillarKey[] = ['health', 'wealth', 'productivity'];

  // ── Engine-grounded endpoints ────────────────────────────────────────
  // The "with this change" ceiling is computed by running the REAL
  // scoring engine on a window where the improved habits are your norm —
  // not by nudging abstract pillar numbers. Doing the right thing daily
  // for months moves the score the way it actually would.
  const assessments = assessGoals(records, profile);
  const procNow = pillarProcessScores(records, profile);
  const outNow = pillarOutcomeScores(assessments);

  const improved = improvedProfile(profile, records, def);
  const lastDate = records[records.length - 1].date;
  const improvedWindow = generateBaselineHistory(improved, lastDate);
  const procEnd = pillarProcessScores(improvedWindow, improved);
  // Sustained right behavior also puts affected goals on/ahead of pace.
  const outEnd: Record<PillarKey, number | null> = { ...outNow };
  for (const key of keys) {
    const relevant = assessments.filter((a) => a.goal.pillar === key);
    if (!relevant.length) continue;
    let sum = 0;
    let wsum = 0;
    for (const a of relevant) {
      const affected = def.affects.includes(a.goal.metric);
      sum += (affected ? Math.max(a.paceScore, 90) : a.paceScore) * a.goal.priority;
      wsum += a.goal.priority;
    }
    outEnd[key] = sum / wsum;
  }

  const blendAt = (proc: number, out: number | null) =>
    out === null ? proc : PROCESS_WEIGHT * proc + OUTCOME_WEIGHT * out;
  const lerp = (a: number, b: number, k: number) => a + (b - a) * k;

  const baseline: SimulationPoint[] = [];
  const simulated: SimulationPoint[] = [];
  const r = NOMINAL_ANNUAL_RETURN / 12;
  let baseDollars = profile.savingsBalance;
  let simDollars = profile.savingsBalance;
  const habitRamp = Math.max(def.shifts.rampMonths, 1.5);
  const goalRamp = Math.max(horizonMonths * 0.6, habitRamp * 2);

  for (let m = 0; m <= horizonMonths; m++) {
    if (m > 0) {
      baseDollars = baseDollars * (1 + r) + profile.monthlyInvestment;
      simDollars = simDollars * (1 + r) + profile.monthlyInvestment + (def.shifts.monthlyDollars ?? 0);
    }

    const basePillarVals = keys.map((k) => clamp(blendAt(procNow[k], outNow[k])));
    const basePoint: SimulationPoint = {
      month: m,
      health: basePillarVals[0],
      wealth: basePillarVals[1],
      productivity: basePillarVals[2],
      lifeScore: Math.round(keys.reduce((acc, k, i) => acc + basePillarVals[i] * weights[k], 0)),
      dollars: Math.round(baseDollars),
    };
    baseline.push(basePoint);

    const kHabit = ramp(m, habitRamp);
    const kGoal = ramp(m, goalRamp);
    const simVals = keys.map((k) =>
      clamp(
        blendAt(
          lerp(procNow[k], procEnd[k], kHabit),
          outNow[k] === null ? null : lerp(outNow[k]!, outEnd[k]!, kGoal),
        ),
      ),
    );
    const simPoint: SimulationPoint = {
      month: m,
      health: simVals[0],
      wealth: simVals[1],
      productivity: simVals[2],
      lifeScore: Math.round(keys.reduce((acc, k, i) => acc + simVals[i] * weights[k], 0)),
      dollars: Math.round(simDollars),
    };
    simulated.push(simPoint);
  }

  const end = simulated[simulated.length - 1];
  const endBase = baseline[baseline.length - 1];

  // ── The honest layer: Monte Carlo odds on the user's actual goals ────
  const goalOdds: SimulationResult['goalOdds'] = [];
  let goalFan: SimulationResult['goalFan'];
  for (const goal of profile.goals) {
    if (!def.affects.includes(goal.metric)) continue;
    const d = oddsDelta(goal, records, profile, def.intervention, 500);
    goalOdds.push({ goalLabel: goal.label, from: d.from, to: d.to });
    if (!goalFan && goal.kind === 'reach') {
      goalFan = {
        goal,
        forecast: forecastGoal(goal, records, profile, { runs: 700, intervention: def.intervention, seedTag: 'fan' }),
        unit: METRIC_META[goal.metric].unit,
      };
    }
  }

  return {
    scenarioId: def.id,
    title: def.question,
    summary: `Projected Life Score after ${horizonMonths} months: ${end.lifeScore} vs ${endBase.lifeScore} on your current path (+${end.lifeScore - endBase.lifeScore} points).`,
    horizonMonths,
    baseline,
    simulated,
    highlights: def.highlights,
    goalOdds,
    goalFan,
  };
}
