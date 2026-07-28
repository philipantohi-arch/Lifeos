/**
 * LifeOS core domain model.
 *
 * A DayRecord is the unified, normalized view of one day of a user's life,
 * merged from every connected source (wearables, bank, calendar, tasks).
 * Everything downstream — Life Score, insights, recommendations, the
 * Future Simulator — operates on this single schema.
 */

export interface DayRecord {
  /** ISO date, e.g. "2026-07-28" */
  date: string;
  /** 0 = Sunday … 6 = Saturday */
  dayOfWeek: number;

  // ── Sleep (Oura / Apple Health / Whoop) ────────────────────────────────
  sleepHours: number;
  /** 0–100, from wearable sleep staging */
  sleepQuality: number;
  /** Decimal hour bedtime, e.g. 23.25 = 11:15 PM */
  bedtime: number;

  // ── Recovery & activity (Whoop / Garmin / Fitbit) ──────────────────────
  /** 0–100 readiness/recovery composite */
  recoveryScore: number;
  hrv: number;
  restingHR: number;
  steps: number;
  activeMinutes: number;
  didWorkout: boolean;
  workoutTime: 'morning' | 'evening' | null;

  // ── Nutrition & substances ─────────────────────────────────────────────
  /** 0–100 estimated diet quality for the day */
  nutritionScore: number;
  ateTakeout: boolean;
  /** Standard drinks */
  alcoholDrinks: number;
  /** True on days covered by a Sunday meal prep */
  mealPrepped: boolean;

  // ── Finances (Plaid-style aggregation) ─────────────────────────────────
  /** Discretionary spending for the day, USD */
  discretionarySpend: number;
  /** Amount moved to savings/investments that day, USD */
  savedToday: number;

  // ── Productivity (calendar + task manager) ─────────────────────────────
  deepWorkHours: number;
  tasksCompleted: number;
  tasksPlanned: number;
  /** 0–100 subjective+derived focus composite */
  focusScore: number;

  // ── Body & self-report ─────────────────────────────────────────────────
  /** True on days a shift worker worked a night/rotating shift */
  workedShift?: boolean;

  /** Morning weight, lbs (smoothed scale reading) */
  weightLbs: number;
  /** 1–10 */
  mood: number;
  /** 1–10 */
  energy: number;
  /** True for baseline-derived placeholder days (not lived/logged data).
   *  Estimated days never produce accomplishments, patterns, or records. */
  estimated?: boolean;
}

/** What a user enters in the ~30-second daily check-in. */
export interface CheckInInput {
  sleepHours: number;
  /** Decimal hour bedtime (values ≥24 = past midnight) */
  bedtime: number;
  steps: number;
  didWorkout: boolean;
  ateTakeout: boolean;
  drinks: number;
  /** Discretionary spend today, $ */
  spend: number;
  /** Moved to savings/investments today, $ */
  saved: number;
  deepWorkHours: number;
  /** Optional morning weigh-in; omit to carry the last known weight */
  weightLbs?: number;
  /** 1–10 */
  mood: number;
}

export type PillarKey = 'health' | 'wealth' | 'productivity';

export interface PillarScore {
  key: PillarKey;
  label: string;
  /** 0–100 */
  score: number;
  /** Score change vs. previous day */
  delta: number;
  /** Weight used in the Life Score composite (sums to 1 across pillars) */
  weight: number;
  /** Short human explanation of the day's main driver */
  driver: string;
  /** 0–100 daily-habits component (55% of the pillar) */
  process?: number;
  /** 0–100 goal-pace component (45%), absent if the pillar has no goals */
  outcome?: number;
}

export interface LifeScoreResult {
  /** 0–100 composite */
  score: number;
  delta: number;
  pillars: PillarScore[];
  /** 0–100 score for each day, aligned with the input records */
  history: number[];
}

// ── Personalization model ─────────────────────────────────────────────────
// Everything the engines adapt to. Each dimension is grounded in the
// research knowledge base (src/engine/researchBase.ts).

export type Sex = 'male' | 'female' | 'other';
/** Morningness–eveningness, per MEQ/MCTQ chronotype research */
export type Chronotype = 'morning' | 'intermediate' | 'evening';
export type WorkPattern = 'standard' | 'flexible' | 'shift' | 'not-working';
export type LifeStage =
  | 'student'
  | 'early-career'
  | 'parent-young-kids'
  | 'midlife'
  | 'pre-retirement'
  | 'retired';
export type FitnessLevel = 'beginner' | 'intermediate' | 'advanced';
/** Temporary contexts that change what good coaching looks like today */
export type Situation = 'normal' | 'sick' | 'travel' | 'crunch' | 'new-baby' | 'injury';

/**
 * Self-reported typical week, captured at onboarding. Until live
 * connectors accumulate real data, the engines model the user's life
 * from these baselines — their numbers, not a demo persona's.
 */
export interface BaselineHabits {
  typicalSleepHours: number;
  /** Decimal hour, e.g. 23.5 = 11:30 PM */
  typicalBedtime: number;
  typicalSteps: number;
  workoutsPerWeek: number;
  deepWorkHoursPerDay: number;
  takeoutMealsPerWeek: number;
  drinksPerWeek: number;
  mealPreps: boolean;
}

export interface UserProfile {
  name: string;
  age: number;
  sex: Sex;
  weightLbs: number;
  chronotype: Chronotype;
  lifeStage: LifeStage;
  workPattern: WorkPattern;
  fitnessLevel: FitnessLevel;
  situation: Situation;
  /** Income is variable/irregular (gig, commission, freelance) */
  variableIncome: boolean;
  savingsBalance: number;
  monthlyIncome: number;
  monthlyInvestment: number;
  /** Rough monthly essential expenses (rent, bills, groceries) */
  monthlyEssentials: number;
  /** 1–5 importance per pillar; personalizes Life Score weights */
  priorities: Record<PillarKey, number>;
  /** The user's own goals — the anchor of their individualized Life Score */
  goals: Goal[];
  /** Self-reported typical week (set during onboarding for real users) */
  baseline?: BaselineHabits;
}

// ── Goals: the anchor of the individualized Life Score ───────────────────
//
// LifeOS scores progress against YOUR goals from YOUR baseline at YOUR
// feasible pace — not against universal standards. A goal is either a
// level to REACH by a deadline (lose 17 lbs, save $40k) or a habit level
// to SUSTAIN (average 7.5h sleep, 15h deep work weekly).

export type MetricKey =
  | 'weightLbs'
  | 'savingsBalance'
  | 'sleepAvg'
  | 'stepsAvg'
  | 'deepWorkWeekly'
  | 'workoutsWeekly';

export interface Goal {
  id: string;
  pillar: PillarKey;
  label: string;
  metric: MetricKey;
  kind: 'reach' | 'sustain';
  /** Metric value when the goal was set — progress is measured from here */
  baseline: number;
  target: number;
  /** ISO deadline (reach goals only) */
  deadline?: string;
  /** ISO date the goal was set; pace is measured from here (defaults to
   *  history start for demo personas) */
  startDate?: string;
  /** 1–5, how much this goal matters to the user */
  priority: number;
}

export type Feasibility = 'comfortable' | 'stretch' | 'unrealistic';

/** A goal evaluated against current data, capacity, and simulated odds. */
export interface GoalAssessment {
  goal: Goal;
  /** Current metric value (rolling average for sustain metrics) */
  current: number;
  /** 0–1 share of baseline→target distance covered (reach goals) */
  progressPct: number;
  /** 0–1 share expected by today on a straight baseline→deadline line */
  expectedPct: number;
  /** actual/expected progress; 1.0 = exactly on pace */
  paceRatio: number;
  /** 0–100 score used in the Life Score outcome component */
  paceScore: number;
  /** Required rate to hit the deadline from here (units/week) */
  requiredWeeklyRate: number;
  /** Max sustainable rate given the user's capacity (units/week) */
  capacityWeeklyRate: number;
  feasibility: Feasibility;
  /** When infeasible/stretch: an honest alternative target or deadline */
  suggestion?: string;
}

/** What this user can realistically output, derived from profile + research. */
export interface Capacity {
  /** Max sustainable monthly savings, $ (income − essentials, cushioned) */
  maxMonthlySavings: number;
  /** Safe weight-change band, lb/week (age-adjusted) */
  safeWeightLossLbPerWeek: [number, number];
  /** Realistic weekly deep-work ceiling, hours (work pattern + situation) */
  weeklyDeepWorkCeiling: number;
  /** Realistic daily step ceiling for sustained habit (fitness-adjusted) */
  dailyStepsCeiling: number;
}

// ── Probability simulation (Monte Carlo on the user's own data) ──────────

export interface InterventionEffect {
  /** Lift low sleep nights by up to this many hours (bedtime discipline) */
  sleepFloorLift?: number;
  /** Multiply discretionary spend samples */
  spendMult?: number;
  /** Add to weekly savings contributions, $ */
  extraWeeklySavings?: number;
  /** Add to deep-work hours on workdays */
  deepWorkBoost?: number;
  /** Add to daily steps */
  stepsBoost?: number;
  /** Shift weekly weight drift, lb/week (negative = losing) */
  weightDriftShift?: number;
  /** Add workouts per week */
  workoutsBoost?: number;
}

export interface GoalForecast {
  goalId: string;
  /** Probability (0–1) of hitting the goal by its deadline / sustaining 4 weeks */
  pHit: number;
  /** Median projected completion date (reach goals, if ever hit in ≤600d) */
  medianCompletion?: string;
  /** Fan chart: per checkpoint, percentile values of the metric */
  fan: { dayOffset: number; p10: number; p50: number; p90: number }[];
  runs: number;
}

// ── Journey: long-term retention layer ───────────────────────────────────

export interface Accomplishment {
  id: string;
  date: string;
  emoji: string;
  title: string;
  detail: string;
  kind: 'streak' | 'record' | 'milestone' | 'comeback';
}

export interface Momentum {
  /** 'rising' | 'steady' | 'falling' */
  direction: 'rising' | 'steady' | 'falling';
  /** Recent process adherence 0–100 vs the prior period */
  recent: number;
  prior: number;
  narrative: string;
}

export interface PotentialGap {
  metricLabel: string;
  currentAvg: string;
  bestAvg: string;
  message: string;
}

export interface WeeklyReview {
  weekLabel: string;
  scoreChange: number;
  bestDay: string;
  recap: string[];
  nextFocus: string[];
}

/**
 * Personal targets derived from the research base + profile.
 * Every number here traces to citations in researchBase.ts.
 */
export interface PersonalTargets {
  /** Recommended nightly sleep range in hours for this age band */
  sleepRange: [number, number];
  /** Ideal in-bed time (decimal hour) given chronotype + work pattern */
  bedtimeIdeal: number;
  /** Daily step target adjusted for age (mortality-benefit plateau) */
  stepsTarget: number;
  /** Weekly moderate-intensity aerobic minutes (WHO/HHS) */
  activeMinutesWeekly: number;
  /** Weekly muscle-strengthening sessions (WHO/HHS; higher priority 65+) */
  strengthSessionsWeekly: number;
  /** Weekly discretionary budget derived from income (50/30/20) */
  weeklyDiscretionary: number;
  /** Target savings rate as a share of gross income */
  savingsRateTarget: number;
  /** Emergency fund size in months of expenses */
  emergencyFundMonths: number;
  /** Weekly low-risk alcohol ceiling (drinks), sex-specific */
  maxDrinksWeekly: number;
  /** Safe sustained weight-loss band, lb/week */
  weightLossLbPerWeek: [number, number];
  /** Best deep-work window [startHour, endHour) from chronotype synchrony */
  deepWorkWindow: [number, number];
  /** Max NEW habits to push simultaneously (behavior-change research) */
  simultaneousHabitLimit: number;
  /** Life Score pillar weights after applying user priorities */
  weights: Record<PillarKey, number>;
}

export interface Insight {
  id: string;
  title: string;
  detail: string;
  /** Pearson r that backs this insight */
  correlation: number;
  /** Number of days of evidence */
  sampleSize: number;
  confidence: 'emerging' | 'moderate' | 'strong';
  pillars: PillarKey[];
}

export interface RecommendedAction {
  id: string;
  title: string;
  detail: string;
  /** Predicted Life Score impact if done today, in points */
  impactPoints: number;
  pillar: PillarKey;
  /** Forward-looking consequence statement */
  prediction: string;
  /** Why the engine chose it today, tied to actual data */
  because: string;
  /** Simulated effect of adopting this action on a goal's odds */
  goalOdds?: { goalLabel: string; from: number; to: number };
}

export interface Briefing {
  dateLabel: string;
  greeting: string;
  score: number;
  delta: number;
  /** Explanation of why the score moved */
  scoreNarrative: string;
  /** Banner text when a non-normal situation reshapes today's coaching */
  situationNote?: string;
  pillars: PillarScore[];
  actions: RecommendedAction[];
  insights: Insight[];
}

export interface SimulationPoint {
  /** Months from now */
  month: number;
  lifeScore: number;
  health: number;
  wealth: number;
  productivity: number;
  /** Net worth / savings trajectory in USD where relevant */
  dollars?: number;
}

export interface SimulationResult {
  scenarioId: string;
  title: string;
  summary: string;
  horizonMonths: number;
  baseline: SimulationPoint[];
  simulated: SimulationPoint[];
  highlights: string[];
  /** How this change moves the odds on each affected goal (Monte Carlo) */
  goalOdds: { goalLabel: string; from: number; to: number }[];
  /** Fan chart for the primary affected reach goal, with the change applied */
  goalFan?: { goal: Goal; forecast: GoalForecast; unit: string };
}

export interface Scenario {
  id: string;
  question: string;
  emoji: string;
  description: string;
}
