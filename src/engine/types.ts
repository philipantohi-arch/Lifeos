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

  // ── Relationships & self-report ────────────────────────────────────────
  /** True on days a shift worker worked a night/rotating shift */
  workedShift?: boolean;

  /** Meaningful social touchpoints (calls, meals, time together) */
  socialTouchpoints: number;
  /** Days since last contact with family as of this day */
  daysSinceFamilyContact: number;
  /** 1–10 */
  mood: number;
  /** 1–10 */
  energy: number;
}

export type PillarKey =
  | 'health'
  | 'wealth'
  | 'productivity'
  | 'relationships'
  | 'habits';

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
  savingsGoal: number;
  savingsGoalLabel: string;
  /** 1–5 importance per pillar; personalizes Life Score weights */
  priorities: Record<PillarKey, number>;
  goals: string[];
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
  /** Days between meaningful family/close-tie contact before nudging */
  familyContactCadenceDays: number;
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
}

export interface Scenario {
  id: string;
  question: string;
  emoji: string;
  description: string;
}
