import type { Chronotype, FitnessLevel, LifeStage, PillarKey, Sex, Situation, UserProfile, WorkPattern } from '../engine/types';
import { deriveTargets, fmtHour } from '../engine/personalize';
import { PERSONAS } from '../data/personas';

interface Props {
  personaId: string;
  profile: UserProfile;
  onSelectPersona: (id: string) => void;
  onChange: (patch: Partial<UserProfile>) => void;
}

const PILLAR_LABELS: Record<PillarKey, string> = {
  health: 'Health',
  wealth: 'Wealth',
  productivity: 'Productivity',
};

function Select<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value as T)}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberField({
  label,
  value,
  step = 1,
  onChange,
}: {
  label: string;
  value: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        type="number"
        value={value}
        step={step}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
      />
    </label>
  );
}

export function ProfileView({ personaId, profile, onSelectPersona, onChange }: Props) {
  const t = deriveTargets(profile);

  return (
    <div className="view">
      <header>
        <h1>Profile & Personalization</h1>
        <p className="muted">
          LifeOS adapts every target, recommendation, and simulation to who you are and what's happening in your life
          right now. Change anything below — the whole system recalibrates instantly.
        </p>
      </header>

      <section className="card">
        <h2>Try a different life</h2>
        <p className="muted small">Five demo lives, each exercising different research-backed adaptations.</p>
        <div className="persona-grid">
          {PERSONAS.map((p) => (
            <button
              key={p.id}
              className={`persona-btn ${p.id === personaId ? 'active' : ''}`}
              onClick={() => onSelectPersona(p.id)}
            >
              <span className="persona-name">{p.profile.name}</span>
              <span className="persona-meta">
                {p.profile.age} · {p.profile.chronotype} type · {p.profile.workPattern.replace('-', ' ')}
              </span>
              <span className="persona-tagline">{p.tagline}</span>
            </button>
          ))}
        </div>
      </section>

      <div className="two-col">
        <section className="card">
          <h2>Who you are</h2>
          <div className="field-grid">
            <NumberField label="Age" value={profile.age} onChange={(v) => onChange({ age: v })} />
            <Select<Sex>
              label="Sex"
              value={profile.sex}
              options={[
                { value: 'male', label: 'Male' },
                { value: 'female', label: 'Female' },
                { value: 'other', label: 'Other / prefer not to say' },
              ]}
              onChange={(v) => onChange({ sex: v })}
            />
            <Select<Chronotype>
              label="Chronotype"
              value={profile.chronotype}
              options={[
                { value: 'morning', label: 'Morning lark' },
                { value: 'intermediate', label: 'Intermediate' },
                { value: 'evening', label: 'Night owl' },
              ]}
              onChange={(v) => onChange({ chronotype: v })}
            />
            <Select<LifeStage>
              label="Life stage"
              value={profile.lifeStage}
              options={[
                { value: 'student', label: 'Student' },
                { value: 'early-career', label: 'Early career' },
                { value: 'parent-young-kids', label: 'Parent (young kids)' },
                { value: 'midlife', label: 'Midlife' },
                { value: 'pre-retirement', label: 'Pre-retirement' },
                { value: 'retired', label: 'Retired' },
              ]}
              onChange={(v) => onChange({ lifeStage: v })}
            />
            <Select<WorkPattern>
              label="Work pattern"
              value={profile.workPattern}
              options={[
                { value: 'standard', label: 'Standard 9–5' },
                { value: 'flexible', label: 'Flexible / remote' },
                { value: 'shift', label: 'Shift / rotating' },
                { value: 'not-working', label: 'Not working' },
              ]}
              onChange={(v) => onChange({ workPattern: v })}
            />
            <Select<FitnessLevel>
              label="Fitness level"
              value={profile.fitnessLevel}
              options={[
                { value: 'beginner', label: 'Beginner' },
                { value: 'intermediate', label: 'Intermediate' },
                { value: 'advanced', label: 'Advanced' },
              ]}
              onChange={(v) => onChange({ fitnessLevel: v })}
            />
            <Select<Situation>
              label="Current situation"
              value={profile.situation}
              options={[
                { value: 'normal', label: 'Normal' },
                { value: 'sick', label: 'Sick' },
                { value: 'travel', label: 'Traveling' },
                { value: 'crunch', label: 'Crunch / exam period' },
                { value: 'new-baby', label: 'New baby' },
                { value: 'injury', label: 'Injured' },
              ]}
              onChange={(v) => onChange({ situation: v })}
            />
            <NumberField
              label="Monthly income ($)"
              value={profile.monthlyIncome}
              step={100}
              onChange={(v) => onChange({ monthlyIncome: v })}
            />
            <NumberField
              label="Monthly investing ($)"
              value={profile.monthlyInvestment}
              step={50}
              onChange={(v) => onChange({ monthlyInvestment: v })}
            />
          </div>

          <h2 style={{ marginTop: 20 }}>What matters most to you</h2>
          <p className="muted small">Priorities reweight your Life Score — your score measures *your* definition of a good life.</p>
          <div className="priority-list">
            {(Object.keys(PILLAR_LABELS) as PillarKey[]).map((k) => (
              <label key={k} className="priority-row">
                <span className="priority-name">{PILLAR_LABELS[k]}</span>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={profile.priorities[k]}
                  onChange={(e) =>
                    onChange({ priorities: { ...profile.priorities, [k]: Number(e.target.value) } })
                  }
                />
                <span className="priority-weight">{Math.round(t.weights[k] * 100)}%</span>
              </label>
            ))}
          </div>
        </section>

        <section className="card">
          <h2>Your personalized targets</h2>
          <p className="muted small">
            Derived from your profile via the research base — tap Science in the sidebar for every citation.
          </p>
          <div className="target-list">
            <div className="target-row">
              <span>Sleep range</span>
              <strong>
                {t.sleepRange[0]}–{t.sleepRange[1]}h
              </strong>
              <span className="target-src">NSF age bands</span>
            </div>
            <div className="target-row">
              <span>{profile.workPattern === 'shift' ? 'Anchor sleep start' : 'Ideal bedtime'}</span>
              <strong>{fmtHour(t.bedtimeIdeal)}</strong>
              <span className="target-src">chronotype + work pattern</span>
            </div>
            <div className="target-row">
              <span>Daily steps</span>
              <strong>{t.stepsTarget.toLocaleString()}</strong>
              <span className="target-src">Paluch 2022 age plateau</span>
            </div>
            <div className="target-row">
              <span>Aerobic minutes / week</span>
              <strong>{t.activeMinutesWeekly}</strong>
              <span className="target-src">WHO 2020</span>
            </div>
            <div className="target-row">
              <span>Strength sessions / week</span>
              <strong>
                {t.strengthSessionsWeekly}
                {profile.age >= 65 ? ' + balance' : ''}
              </strong>
              <span className="target-src">WHO 2020{profile.age >= 65 ? ' (65+)' : ''}</span>
            </div>
            <div className="target-row">
              <span>Deep-work window</span>
              <strong>
                {fmtHour(t.deepWorkWindow[0])}–{fmtHour(t.deepWorkWindow[1])}
              </strong>
              <span className="target-src">chronotype synchrony</span>
            </div>
            <div className="target-row">
              <span>Weekly discretionary budget</span>
              <strong>${t.weeklyDiscretionary}</strong>
              <span className="target-src">50/30/20 on your income</span>
            </div>
            <div className="target-row">
              <span>Savings-rate target</span>
              <strong>{Math.round(t.savingsRateTarget * 100)}%</strong>
              <span className="target-src">life-stage adjusted</span>
            </div>
            <div className="target-row">
              <span>Emergency fund</span>
              <strong>{t.emergencyFundMonths} months</strong>
              <span className="target-src">CFPB{profile.variableIncome ? ' (variable income)' : ''}</span>
            </div>
            <div className="target-row">
              <span>Alcohol ceiling / week</span>
              <strong>{t.maxDrinksWeekly} drinks</strong>
              <span className="target-src">sex-specific guidelines</span>
            </div>
            <div className="target-row">
              <span>New habits at once</span>
              <strong>max {t.simultaneousHabitLimit}</strong>
              <span className="target-src">behavior-change limit</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
