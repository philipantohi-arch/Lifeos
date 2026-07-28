/**
 * First-run onboarding: the user enters who they are, their money, their
 * typical week, and their goals — and LifeOS builds everything from those
 * inputs. No demo data unless they explicitly ask to explore a demo life.
 */

import { useState } from 'react';
import type {
  BaselineHabits,
  Chronotype,
  FitnessLevel,
  Goal,
  LifeStage,
  PillarKey,
  Sex,
  Situation,
  UserProfile,
  WorkPattern,
} from '../engine/types';

interface Props {
  onComplete: (profile: UserProfile) => void;
  onExploreDemo: () => void;
}

/** The app's deterministic "today" (matches the data generator). */
const TODAY = new Date('2026-07-28T00:00:00Z');

function isoMonthsFromNow(months: number): string {
  const d = new Date(TODAY);
  d.setUTCMonth(d.getUTCMonth() + months);
  return d.toISOString().slice(0, 10);
}

interface GoalTemplate {
  id: string;
  emoji: string;
  title: string;
  pillar: PillarKey;
  build: (about: AboutState, money: MoneyState, week: WeekState) => Goal;
  /** Editable fields shown when selected */
  fields: ('target' | 'deadline')[];
  unit: string;
}

interface AboutState {
  name: string;
  age: number;
  sex: Sex;
  weightLbs: number;
  chronotype: Chronotype;
  lifeStage: LifeStage;
  workPattern: WorkPattern;
  fitnessLevel: FitnessLevel;
  situation: Situation;
}

interface MoneyState {
  monthlyIncome: number;
  monthlyEssentials: number;
  savingsBalance: number;
  monthlyInvestment: number;
  variableIncome: boolean;
}

type WeekState = BaselineHabits;

const GOAL_TEMPLATES: GoalTemplate[] = [
  {
    id: 'goal-weight',
    emoji: '⚖️',
    title: 'Reach a target weight',
    pillar: 'health',
    unit: 'lbs',
    fields: ['target', 'deadline'],
    build: (about) => ({
      id: 'goal-weight',
      pillar: 'health',
      label: `Reach ${Math.max(90, about.weightLbs - 15)} lbs`,
      metric: 'weightLbs',
      kind: 'reach',
      baseline: about.weightLbs,
      target: Math.max(90, about.weightLbs - 15),
      deadline: isoMonthsFromNow(9),
      priority: 4,
    }),
  },
  {
    id: 'goal-savings',
    emoji: '💰',
    title: 'Grow my savings',
    pillar: 'wealth',
    unit: '$',
    fields: ['target', 'deadline'],
    build: (_a, money) => ({
      id: 'goal-savings',
      pillar: 'wealth',
      label: `Save $${(money.savingsBalance + 10000).toLocaleString()}`,
      metric: 'savingsBalance',
      kind: 'reach',
      baseline: money.savingsBalance,
      target: money.savingsBalance + 10000,
      deadline: isoMonthsFromNow(18),
      priority: 4,
    }),
  },
  {
    id: 'goal-sleep',
    emoji: '😴',
    title: 'Sleep more, consistently',
    pillar: 'health',
    unit: 'h/night',
    fields: ['target'],
    build: (_a, _m, week) => ({
      id: 'goal-sleep',
      pillar: 'health',
      label: 'Average 7.5h sleep',
      metric: 'sleepAvg',
      kind: 'sustain',
      baseline: week.typicalSleepHours,
      target: 7.5,
      priority: 4,
    }),
  },
  {
    id: 'goal-steps',
    emoji: '🚶',
    title: 'Move more every day',
    pillar: 'health',
    unit: 'steps/day',
    fields: ['target'],
    build: (about, _m, week) => ({
      id: 'goal-steps',
      pillar: 'health',
      label: `Average ${about.age >= 60 ? '7,000' : '8,500'} steps/day`,
      metric: 'stepsAvg',
      kind: 'sustain',
      baseline: week.typicalSteps,
      target: about.age >= 60 ? 7000 : 8500,
      priority: 3,
    }),
  },
  {
    id: 'goal-deepwork',
    emoji: '🎯',
    title: 'More focused work hours',
    pillar: 'productivity',
    unit: 'h/week',
    fields: ['target'],
    build: (_a, _m, week) => ({
      id: 'goal-deepwork',
      pillar: 'productivity',
      label: `${Math.round(week.deepWorkHoursPerDay * 5 * 1.3)}h/week of deep work`,
      metric: 'deepWorkWeekly',
      kind: 'sustain',
      baseline: Math.round(week.deepWorkHoursPerDay * 5 * 10) / 10,
      target: Math.round(week.deepWorkHoursPerDay * 5 * 1.3),
      priority: 4,
    }),
  },
  {
    id: 'goal-workouts',
    emoji: '💪',
    title: 'Train regularly',
    pillar: 'health',
    unit: '/week',
    fields: ['target'],
    build: (_a, _m, week) => ({
      id: 'goal-workouts',
      pillar: 'health',
      label: '3 workouts a week',
      metric: 'workoutsWeekly',
      kind: 'sustain',
      baseline: week.workoutsPerWeek,
      target: 3,
      priority: 3,
    }),
  },
];

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

export function OnboardingView({ onComplete, onExploreDemo }: Props) {
  const [step, setStep] = useState(0);

  const [about, setAbout] = useState<AboutState>({
    name: '',
    age: 30,
    sex: 'other',
    weightLbs: 170,
    chronotype: 'intermediate',
    lifeStage: 'early-career',
    workPattern: 'standard',
    fitnessLevel: 'beginner',
    situation: 'normal',
  });
  const [money, setMoney] = useState<MoneyState>({
    monthlyIncome: 0,
    monthlyEssentials: 0,
    savingsBalance: 0,
    monthlyInvestment: 0,
    variableIncome: false,
  });
  const [week, setWeek] = useState<WeekState>({
    typicalSleepHours: 7,
    typicalBedtime: 23,
    typicalSteps: 6000,
    workoutsPerWeek: 1,
    deepWorkHoursPerDay: 2,
    takeoutMealsPerWeek: 3,
    drinksPerWeek: 0,
    mealPreps: false,
  });
  const [selectedGoals, setSelectedGoals] = useState<Record<string, Goal>>({});

  const toggleGoal = (t: GoalTemplate) => {
    setSelectedGoals((prev) => {
      const next = { ...prev };
      if (next[t.id]) delete next[t.id];
      else next[t.id] = t.build(about, money, week);
      return next;
    });
  };

  const patchGoal = (id: string, patch: Partial<Goal>) =>
    setSelectedGoals((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }));

  const finish = () => {
    const goals = Object.values(selectedGoals).map((g) => {
      // Keep labels honest if the user edited targets.
      if (g.metric === 'weightLbs') return { ...g, label: `Reach ${g.target} lbs` };
      if (g.metric === 'savingsBalance') return { ...g, label: `Save $${g.target.toLocaleString()}` };
      if (g.metric === 'sleepAvg') return { ...g, label: `Average ${g.target}h sleep` };
      if (g.metric === 'stepsAvg') return { ...g, label: `Average ${g.target.toLocaleString()} steps/day` };
      if (g.metric === 'deepWorkWeekly') return { ...g, label: `${g.target}h/week of deep work` };
      if (g.metric === 'workoutsWeekly') return { ...g, label: `${g.target} workouts a week` };
      return g;
    });
    onComplete({
      ...about,
      name: about.name.trim() || 'You',
      ...money,
      priorities: { health: 4, wealth: 3, productivity: 3 },
      // Goals start TODAY: day one is "on pace", never "already behind".
      goals: goals.map((g) => ({ ...g, startDate: TODAY.toISOString().slice(0, 10) })),
      baseline: week,
    });
  };

  const steps = ['About you', 'Your money', 'Your typical week', 'Your goals'];
  const canContinue =
    step === 0
      ? about.age > 0 && about.weightLbs > 0
      : step === 1
        ? money.monthlyIncome >= 0
        : step === 2
          ? true
          : Object.keys(selectedGoals).length > 0;

  return (
    <div className="onboarding">
      <div className="onboarding-card">
        <div className="brand onboarding-brand">
          <span className="brand-mark">◉</span>
          <div>
            <div className="brand-name">LifeOS</div>
            <div className="brand-tag">One score. One coach. Built from your inputs.</div>
          </div>
        </div>

        <div className="onboarding-steps">
          {steps.map((s, i) => (
            <span key={s} className={`onboarding-step ${i === step ? 'active' : i < step ? 'done' : ''}`}>
              {i < step ? '✓' : i + 1}. {s}
            </span>
          ))}
        </div>

        {step === 0 && (
          <>
            <h1>Tell LifeOS who you are</h1>
            <p className="muted">
              Every target in the app — sleep range, step counts, budgets, training — is derived from these answers
              and the research behind them. Nothing is compared to anyone else.
            </p>
            <div className="field-grid">
              <Field label="First name">
                <input
                  type="text"
                  placeholder="Your name"
                  value={about.name}
                  onChange={(e) => setAbout({ ...about, name: e.target.value })}
                />
              </Field>
              <Field label="Age">
                <input type="number" value={about.age || ''} placeholder="e.g. 34" onChange={(e) => setAbout({ ...about, age: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Sex">
                <select value={about.sex} onChange={(e) => setAbout({ ...about, sex: e.target.value as Sex })}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other / prefer not to say</option>
                </select>
              </Field>
              <Field label="Current weight (lbs)">
                <input type="number" value={about.weightLbs || ''} placeholder="e.g. 180" onChange={(e) => setAbout({ ...about, weightLbs: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Are you a morning or evening person?">
                <select value={about.chronotype} onChange={(e) => setAbout({ ...about, chronotype: e.target.value as Chronotype })}>
                  <option value="morning">Morning person</option>
                  <option value="intermediate">Somewhere in between</option>
                  <option value="evening">Night owl</option>
                </select>
              </Field>
              <Field label="Life stage">
                <select value={about.lifeStage} onChange={(e) => setAbout({ ...about, lifeStage: e.target.value as LifeStage })}>
                  <option value="student">Student</option>
                  <option value="early-career">Early career</option>
                  <option value="parent-young-kids">Parent of young kids</option>
                  <option value="midlife">Midlife</option>
                  <option value="pre-retirement">Pre-retirement</option>
                  <option value="retired">Retired</option>
                </select>
              </Field>
              <Field label="Work pattern">
                <select value={about.workPattern} onChange={(e) => setAbout({ ...about, workPattern: e.target.value as WorkPattern })}>
                  <option value="standard">Standard 9–5</option>
                  <option value="flexible">Flexible / remote</option>
                  <option value="shift">Shift / rotating</option>
                  <option value="not-working">Not working</option>
                </select>
              </Field>
              <Field label="Fitness level">
                <select value={about.fitnessLevel} onChange={(e) => setAbout({ ...about, fitnessLevel: e.target.value as FitnessLevel })}>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </Field>
              <Field label="Anything going on right now?">
                <select value={about.situation} onChange={(e) => setAbout({ ...about, situation: e.target.value as Situation })}>
                  <option value="normal">Life as usual</option>
                  <option value="sick">I'm sick</option>
                  <option value="travel">Traveling</option>
                  <option value="crunch">Work/exam crunch</option>
                  <option value="new-baby">New baby</option>
                  <option value="injury">Injured</option>
                </select>
              </Field>
            </div>
          </>
        )}

        {step === 1 && (
          <>
            <h1>Your money, roughly</h1>
            <p className="muted">
              Ballpark numbers are fine — they set your personal budget (50/30/20 on your real income) and what
              savings pace is actually sustainable for you. Everything stays on your device.
            </p>
            <div className="field-grid">
              <Field label="Monthly take-home income ($)">
                <input type="number" value={money.monthlyIncome || ''} placeholder="e.g. 4500" onChange={(e) => setMoney({ ...money, monthlyIncome: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Monthly essentials — rent, bills, groceries ($)">
                <input type="number" value={money.monthlyEssentials || ''} placeholder="e.g. 2800" onChange={(e) => setMoney({ ...money, monthlyEssentials: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Current savings ($)">
                <input type="number" value={money.savingsBalance || ''} placeholder="e.g. 5000" onChange={(e) => setMoney({ ...money, savingsBalance: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Monthly saving/investing ($)">
                <input type="number" value={money.monthlyInvestment || ''} placeholder="e.g. 300" onChange={(e) => setMoney({ ...money, monthlyInvestment: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Is your income irregular?">
                <select
                  value={money.variableIncome ? 'yes' : 'no'}
                  onChange={(e) => setMoney({ ...money, variableIncome: e.target.value === 'yes' })}
                >
                  <option value="no">No — steady paycheck</option>
                  <option value="yes">Yes — gig / commission / freelance</option>
                </select>
              </Field>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h1>Your typical week, honestly</h1>
            <p className="muted">
              This is your starting line. LifeOS measures progress from here — so honest answers beat impressive
              ones. (Once real device data connects, it replaces these estimates.)
            </p>
            <div className="field-grid">
              <Field label="Typical night's sleep (hours)">
                <input type="number" step={0.5} value={week.typicalSleepHours} onChange={(e) => setWeek({ ...week, typicalSleepHours: Number(e.target.value) || 7 })} />
              </Field>
              <Field label="Usual bedtime">
                <select value={week.typicalBedtime} onChange={(e) => setWeek({ ...week, typicalBedtime: Number(e.target.value) })}>
                  <option value={21.5}>9:30 PM</option>
                  <option value={22}>10:00 PM</option>
                  <option value={22.5}>10:30 PM</option>
                  <option value={23}>11:00 PM</option>
                  <option value={23.5}>11:30 PM</option>
                  <option value={24}>Midnight</option>
                  <option value={24.75}>12:45 AM</option>
                  <option value={25.5}>1:30 AM or later</option>
                </select>
              </Field>
              <Field label="Steps on a normal day">
                <input type="number" step={500} value={week.typicalSteps} onChange={(e) => setWeek({ ...week, typicalSteps: Number(e.target.value) || 5000 })} />
              </Field>
              <Field label="Workouts per week">
                <input type="number" value={week.workoutsPerWeek} onChange={(e) => setWeek({ ...week, workoutsPerWeek: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Focused work hours per day">
                <input type="number" step={0.5} value={week.deepWorkHoursPerDay} onChange={(e) => setWeek({ ...week, deepWorkHoursPerDay: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Takeout / delivery meals per week">
                <input type="number" value={week.takeoutMealsPerWeek} onChange={(e) => setWeek({ ...week, takeoutMealsPerWeek: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Alcoholic drinks per week">
                <input type="number" value={week.drinksPerWeek} onChange={(e) => setWeek({ ...week, drinksPerWeek: Number(e.target.value) || 0 })} />
              </Field>
              <Field label="Do you meal prep?">
                <select value={week.mealPreps ? 'yes' : 'no'} onChange={(e) => setWeek({ ...week, mealPreps: e.target.value === 'yes' })}>
                  <option value="no">Rarely / never</option>
                  <option value="yes">Most weeks</option>
                </select>
              </Field>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h1>What are you working toward?</h1>
            <p className="muted">
              Pick at least one. Your Life Score will measure pace toward these — from your baseline, at a pace your
              capacity supports. You can edit targets, deadlines, and priorities anytime.
            </p>
            <div className="goal-template-list">
              {GOAL_TEMPLATES.map((t) => {
                const sel = selectedGoals[t.id];
                return (
                  <div key={t.id} className={`goal-template ${sel ? 'selected' : ''}`}>
                    <button className="goal-template-head" onClick={() => toggleGoal(t)}>
                      <span className="goal-template-emoji">{t.emoji}</span>
                      <span className="goal-template-title">{t.title}</span>
                      <span className={`goal-template-check ${sel ? 'on' : ''}`}>{sel ? '✓' : '+'}</span>
                    </button>
                    {sel && (
                      <div className="goal-template-fields">
                        {t.fields.includes('target') && (
                          <Field label={`Target (${t.unit})`}>
                            <input
                              type="number"
                              value={sel.target}
                              onChange={(e) => patchGoal(t.id, { target: Number(e.target.value) || sel.target })}
                            />
                          </Field>
                        )}
                        {t.fields.includes('deadline') && (
                          <Field label="By when">
                            <input
                              type="date"
                              value={sel.deadline}
                              onChange={(e) => e.target.value && patchGoal(t.id, { deadline: e.target.value })}
                            />
                          </Field>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}

        <div className="onboarding-nav">
          {step > 0 ? (
            <button className="btn ghost" onClick={() => setStep(step - 1)}>
              Back
            </button>
          ) : (
            <button className="btn ghost" onClick={onExploreDemo}>
              Just exploring? Try a demo life
            </button>
          )}
          {step < 3 ? (
            <button className="btn primary" disabled={!canContinue} onClick={() => setStep(step + 1)}>
              Continue
            </button>
          ) : (
            <button className="btn primary" disabled={!canContinue} onClick={finish}>
              Build my LifeOS
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
