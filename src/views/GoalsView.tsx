import { useMemo } from 'react';
import type { DayRecord, Goal, GoalAssessment, UserProfile } from '../engine/types';
import { METRIC_META } from '../engine/goals';
import { forecastGoal } from '../engine/montecarlo';
import { adaptiveTargets } from '../engine/journey';
import { FanChart } from '../components/FanChart';

interface Props {
  records: DayRecord[];
  profile: UserProfile;
  assessments: GoalAssessment[];
  onChangeGoal: (goalId: string, patch: Partial<Goal>) => void;
}

const FEAS_LABEL = {
  comfortable: { text: 'On solid ground', cls: 'good' },
  stretch: { text: 'Stretch — doable, not free', cls: 'warn' },
  unrealistic: { text: 'Math needs renegotiating', cls: 'bad' },
} as const;

function fmtMetric(goal: Goal, v: number): string {
  const meta = METRIC_META[goal.metric];
  const num = meta.decimals === 0 ? Math.round(v).toLocaleString() : v.toFixed(meta.decimals);
  return meta.unit === '$' ? `$${num}` : `${num} ${meta.unit}`;
}

function OddsBadge({ p }: { p: number }) {
  const pct = Math.round(p * 100);
  const cls = pct >= 70 ? 'good' : pct >= 40 ? 'warn' : 'bad';
  return <span className={`odds-badge ${cls}`}>{pct}% odds</span>;
}

export function GoalsView({ records, profile, assessments, onChangeGoal }: Props) {
  const forecasts = useMemo(
    () => new Map(profile.goals.map((g) => [g.id, forecastGoal(g, records, profile, { runs: 800 })])),
    [profile, records],
  );
  const micro = useMemo(() => adaptiveTargets(records, profile), [records, profile]);

  return (
    <div className="view">
      <header>
        <h1>Your Goals</h1>
        <p className="muted">
          Your Life Score is anchored here: progress is measured from your own baseline toward your own targets, at a
          pace your capacity can actually sustain. Odds come from {(800).toLocaleString()} simulated futures built from
          your real day-to-day variability — not wishful straight lines.
        </p>
      </header>

      {assessments.map((a) => {
        const g = a.goal;
        const fc = forecasts.get(g.id);
        const feas = FEAS_LABEL[a.feasibility];
        return (
          <section key={g.id} className="card goal-card">
            <div className="goal-head">
              <div>
                <h2>{g.label}</h2>
                <span className="muted small">
                  {g.kind === 'reach'
                    ? `${fmtMetric(g, g.baseline)} → ${fmtMetric(g, g.target)} by ${new Date(
                        (g.deadline ?? '') + 'T00:00:00Z',
                      ).toLocaleDateString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' })}`
                    : `Sustain ${fmtMetric(g, g.target)} (started at ${fmtMetric(g, g.baseline)})`}
                </span>
              </div>
              <div className="goal-badges">
                {fc && <OddsBadge p={fc.pHit} />}
                <span className={`feas-badge ${feas.cls}`}>{feas.text}</span>
              </div>
            </div>

            <div className="goal-progress">
              <div className="goal-progress-labels">
                <span>
                  Now: <strong>{fmtMetric(g, a.current)}</strong>
                </span>
                <span className={a.paceRatio >= 0.95 ? 'pace good' : a.paceRatio >= 0.7 ? 'pace warn' : 'pace bad'}>
                  {g.kind === 'reach'
                    ? `${Math.round(a.paceRatio * 100)}% of expected pace`
                    : `${Math.round(a.paceRatio * 100)}% of target level`}
                </span>
              </div>
              <div className="bar-track tall">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.round(a.progressPct * 100)}%` }}
                  data-level={a.paceRatio >= 0.95 ? 'good' : a.paceRatio >= 0.7 ? 'ok' : 'low'}
                />
                {g.kind === 'reach' && (
                  <div className="bar-expected" style={{ left: `${Math.round(a.expectedPct * 100)}%` }} title="Where the plan says you should be today" />
                )}
              </div>
              {g.kind === 'reach' && (
                <div className="muted small">
                  Requires {fmtMetric(g, a.requiredWeeklyRate)}/week from here
                  {Number.isFinite(a.capacityWeeklyRate) && ` · your sustainable ceiling ≈ ${fmtMetric(g, a.capacityWeeklyRate)}/week`}
                  {fc?.medianCompletion &&
                    ` · median finish ${new Date(fc.medianCompletion + 'T00:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })}`}
                </div>
              )}
            </div>

            {a.suggestion && <div className="suggestion-box">🎯 {a.suggestion}</div>}
            {!a.suggestion && fc && fc.pHit < 0.35 && a.feasibility === 'comfortable' && (
              <div className="suggestion-box">
                💡 The capacity is there — these odds reflect your <em>current</em> behavior, not your limits. The
                Today tab ranks the exact actions that move this number.
              </div>
            )}

            {fc && g.kind === 'reach' && (
              <FanChart forecast={fc} startValue={a.current} target={g.target} unit={METRIC_META[g.metric].unit} height={200} />
            )}

            <div className="goal-edit">
              <label className="field inline">
                <span className="field-label">Target</span>
                <input
                  type="number"
                  value={g.target}
                  onChange={(e) => onChangeGoal(g.id, { target: Number(e.target.value) || g.target })}
                />
              </label>
              {g.kind === 'reach' && (
                <label className="field inline">
                  <span className="field-label">Deadline</span>
                  <input
                    type="date"
                    value={g.deadline}
                    onChange={(e) => e.target.value && onChangeGoal(g.id, { deadline: e.target.value })}
                  />
                </label>
              )}
              <label className="field inline">
                <span className="field-label">Priority (1–5)</span>
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={g.priority}
                  onChange={(e) => onChangeGoal(g.id, { priority: Math.min(5, Math.max(1, Number(e.target.value) || 3)) })}
                />
              </label>
            </div>
          </section>
        );
      })}

      <section className="card">
        <div className="section-head">
          <h2>This week's micro-targets</h2>
          <span className="muted small">Auto-tuned to your recent hit rate — hard enough to matter, close enough to win</span>
        </div>
        <div className="micro-grid">
          {micro.map((m) => (
            <div key={m.label} className="micro-target">
              <div className="micro-label">{m.label}</div>
              <div className="micro-value">{m.thisWeek}</div>
              <div className="micro-note">{m.note}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
