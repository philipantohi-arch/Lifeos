/**
 * Daily check-in: ~30 seconds each evening. Every saved day becomes a
 * REAL data point — your streaks, patterns, momentum, and goal odds grow
 * from these, not from estimates. Until device integrations arrive, this
 * is how your individual data accumulates.
 */

import { useState } from 'react';
import type { CheckInInput, UserProfile } from '../engine/types';

interface Props {
  profile: UserProfile;
  todayISO: string;
  /** Existing log for today, if re-editing */
  existing?: CheckInInput;
  realDayCount: number;
  onSave: (input: CheckInInput) => void;
}

const BEDTIMES: { v: number; label: string }[] = [
  { v: 21, label: '9:00 PM' },
  { v: 21.5, label: '9:30 PM' },
  { v: 22, label: '10:00 PM' },
  { v: 22.5, label: '10:30 PM' },
  { v: 23, label: '11:00 PM' },
  { v: 23.5, label: '11:30 PM' },
  { v: 24, label: 'Midnight' },
  { v: 24.75, label: '12:45 AM' },
  { v: 25.5, label: '1:30 AM' },
  { v: 26.5, label: '2:30 AM or later' },
];

export function CheckInView({ profile, todayISO, existing, realDayCount, onSave }: Props) {
  const b = profile.baseline;
  const [form, setForm] = useState<CheckInInput>(
    existing ?? {
      sleepHours: b?.typicalSleepHours ?? 7,
      bedtime: b?.typicalBedtime ?? 23,
      steps: b?.typicalSteps ?? 6000,
      didWorkout: false,
      ateTakeout: false,
      drinks: 0,
      spend: Math.round(((profile.monthlyIncome * 0.3) / 30) * 0.7),
      saved: 0,
      deepWorkHours: b?.deepWorkHoursPerDay ?? 2,
      weightLbs: undefined,
      mood: 6,
    },
  );
  const [saved, setSaved] = useState(false);

  const set = <K extends keyof CheckInInput>(k: K, v: CheckInInput[K]) => {
    setForm((f) => ({ ...f, [k]: v }));
    setSaved(false);
  };

  const dateLabel = new Date(todayISO + 'T00:00:00Z').toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  });

  return (
    <div className="view">
      <header>
        <h1>Daily check-in</h1>
        <p className="muted">
          {dateLabel} · ~30 seconds. Every day you log is a real data point — {realDayCount} logged so far
          {realDayCount < 7 ? `, ${7 - realDayCount} until your first weekly review` : ''}
          {realDayCount >= 7 && realDayCount < 21 ? `, ${21 - realDayCount} until pattern discovery unlocks` : ''}.
        </p>
      </header>

      <section className="card">
        <h2>😴 Last night</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Hours slept</span>
            <input type="number" step={0.5} min={0} max={14} value={form.sleepHours} onChange={(e) => set('sleepHours', Number(e.target.value) || 0)} />
          </label>
          <label className="field">
            <span className="field-label">When you got in bed</span>
            <select value={form.bedtime} onChange={(e) => set('bedtime', Number(e.target.value))}>
              {BEDTIMES.map((o) => (
                <option key={o.v} value={o.v}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="card">
        <h2>🏃 Today's movement</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Steps (check your phone)</span>
            <input type="number" step={500} min={0} value={form.steps} onChange={(e) => set('steps', Number(e.target.value) || 0)} />
          </label>
          <label className="field">
            <span className="field-label">Did you work out?</span>
            <select value={form.didWorkout ? 'yes' : 'no'} onChange={(e) => set('didWorkout', e.target.value === 'yes')}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </label>
          <label className="field">
            <span className="field-label">Morning weight (optional, lbs)</span>
            <input
              type="number"
              step={0.1}
              placeholder="skip if you didn't weigh in"
              value={form.weightLbs ?? ''}
              onChange={(e) => set('weightLbs', e.target.value === '' ? undefined : Number(e.target.value))}
            />
          </label>
        </div>
      </section>

      <section className="card">
        <h2>🍽️ Food & drink</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Takeout / delivery today?</span>
            <select value={form.ateTakeout ? 'yes' : 'no'} onChange={(e) => set('ateTakeout', e.target.value === 'yes')}>
              <option value="no">No — cooked / home food</option>
              <option value="yes">Yes</option>
            </select>
          </label>
          <label className="field">
            <span className="field-label">Alcoholic drinks</span>
            <input type="number" min={0} max={20} value={form.drinks} onChange={(e) => set('drinks', Number(e.target.value) || 0)} />
          </label>
        </div>
      </section>

      <section className="card">
        <h2>💰 Money</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Fun/extra spending today ($)</span>
            <input type="number" min={0} value={form.spend} onChange={(e) => set('spend', Number(e.target.value) || 0)} />
          </label>
          <label className="field">
            <span className="field-label">Moved to savings today ($)</span>
            <input type="number" min={0} value={form.saved} onChange={(e) => set('saved', Number(e.target.value) || 0)} />
          </label>
        </div>
      </section>

      <section className="card">
        <h2>🎯 Work & mood</h2>
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Focused work hours</span>
            <input type="number" step={0.5} min={0} max={16} value={form.deepWorkHours} onChange={(e) => set('deepWorkHours', Number(e.target.value) || 0)} />
          </label>
          <label className="field">
            <span className="field-label">Mood today: {form.mood}/10</span>
            <input type="range" min={1} max={10} value={form.mood} onChange={(e) => set('mood', Number(e.target.value))} />
          </label>
        </div>
      </section>

      <div className="checkin-save">
        <button
          className="btn primary"
          onClick={() => {
            onSave(form);
            setSaved(true);
          }}
        >
          {existing ? 'Update today' : 'Save today'}
        </button>
        {saved && <span className="checkin-saved">✓ Saved — everything just recalibrated</span>}
      </div>
    </div>
  );
}
