import type { Briefing, GoalAssessment, Momentum } from '../engine/types';
import { ScoreRing } from '../components/ScoreRing';

const PILLAR_ICONS: Record<string, string> = {
  health: '💪',
  wealth: '💰',
  productivity: '🎯',
};

const MOMENTUM_ICON = { rising: '📈', steady: '➡️', falling: '📉' } as const;

interface TodayProps {
  briefing: Briefing;
  assessments: GoalAssessment[];
  momentum: Momentum;
  fresh?: boolean;
}

export function TodayView({ briefing, assessments, momentum, fresh }: TodayProps) {
  const topOdds = briefing.actions.find((a) => a.goalOdds)?.goalOdds;
  return (
    <div className="view">
      <header className="today-header">
        <div>
          <h1>{briefing.greeting}</h1>
          <p className="muted">{briefing.dateLabel} · Morning Briefing</p>
        </div>
      </header>

      {briefing.situationNote && <div className="situation-banner">{briefing.situationNote}</div>}

      {topOdds && (
        <div className="forecast-banner">
          🔮 Today's #1 action moves your odds on "{topOdds.goalLabel}" from{' '}
          <strong>{Math.round(topOdds.from * 100)}%</strong> to <strong>{Math.round(topOdds.to * 100)}%</strong> — the
          single highest-leverage move available to you today.
        </div>
      )}

      <div className="today-grid">
        <section className="card score-card">
          <ScoreRing score={briefing.score} delta={briefing.delta} />
          <p className="score-narrative">{briefing.scoreNarrative}</p>
        </section>

        <section className="card">
          <h2>Pillars</h2>
          <div className="pillar-list">
            {briefing.pillars.map((p) => (
              <div key={p.key} className="pillar-row">
                <span className="pillar-icon">{PILLAR_ICONS[p.key]}</span>
                <div className="pillar-info">
                  <div className="pillar-top">
                    <span className="pillar-name">{p.label}</span>
                    <span className="pillar-score">
                      {p.score}
                      <span className={`pillar-delta ${p.delta >= 0 ? 'up' : 'down'}`}>
                        {p.delta >= 0 ? '+' : ''}
                        {p.delta}
                      </span>
                    </span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${p.score}%` }} data-level={p.score >= 75 ? 'good' : p.score >= 55 ? 'ok' : 'low'} />
                  </div>
                  <div className="pillar-driver">{p.driver}</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="card">
        <div className="section-head">
          <h2>Your goals at a glance</h2>
          {fresh ? (
            <span className="momentum-chip">🌱 day 1 — momentum starts today</span>
          ) : (
            <span className={`momentum-chip ${momentum.direction}`}>
              {MOMENTUM_ICON[momentum.direction]} momentum {momentum.direction}
            </span>
          )}
        </div>
        <div className="goal-strip">
          {assessments.map((a) => (
            <div key={a.goal.id} className="goal-mini">
              <div className="goal-mini-label">{a.goal.label}</div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.round(a.progressPct * 100)}%` }}
                  data-level={a.paceRatio >= 0.95 ? 'good' : a.paceRatio >= 0.7 ? 'ok' : 'low'}
                />
              </div>
              <div className="goal-mini-pace muted small">
                {a.goal.kind === 'reach'
                  ? fresh
                    ? 'just set — on pace'
                    : `${Math.round(a.paceRatio * 100)}% of pace`
                  : `${Math.round(a.paceRatio * 100)}% of target`}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="section-head">
          <h2>Do these today</h2>
          <span className="muted small">Ranked by predicted Life Score impact</span>
        </div>
        <div className="action-list">
          {briefing.actions.map((a, i) => (
            <div key={a.id} className="action-card">
              <div className="action-rank">#{i + 1}</div>
              <div className="action-body">
                <div className="action-title">{a.title}</div>
                <p className="action-detail">{a.detail}</p>
                <p className="action-prediction">🔮 {a.prediction}</p>
                {a.goalOdds && (
                  <p className="action-odds">
                    "{a.goalOdds.goalLabel}": {Math.round(a.goalOdds.from * 100)}% →{' '}
                    <strong>{Math.round(a.goalOdds.to * 100)}%</strong> odds if this becomes your default
                  </p>
                )}
                <p className="action-because">Why now: {a.because}</p>
              </div>
              <div className="action-impact">
                <span className="impact-value">+{a.impactPoints.toFixed(1)}</span>
                <span className="impact-label">pts</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {briefing.insights.length > 0 && (
        <section className="card">
          <div className="section-head">
            <h2>Patterns LifeOS has learned about you</h2>
            <span className="muted small">From your own data — not generic advice</span>
          </div>
          <div className="insight-strip">
            {briefing.insights.map((ins) => (
              <div key={ins.id} className="insight-mini">
                <div className="insight-title">{ins.title}</div>
                <div className="insight-detail">{ins.detail}</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
