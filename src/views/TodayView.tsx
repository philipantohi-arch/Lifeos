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
        <h1>{briefing.greeting}</h1>
        <p className="muted">{briefing.dateLabel}</p>
      </header>

      {briefing.situationNote && <div className="situation-banner">{briefing.situationNote}</div>}

      <section className="hero-card card">
        <ScoreRing score={briefing.score} delta={briefing.delta} />
        <p className="score-narrative">{briefing.scoreNarrative}</p>
        <div className="pillar-tiles">
          {briefing.pillars.map((p) => (
            <div key={p.key} className="pillar-tile">
              <span className="pillar-tile-icon">{PILLAR_ICONS[p.key]}</span>
              <span className="pillar-tile-score">{p.score}</span>
              <span className={`pillar-tile-delta ${p.delta >= 0 ? 'up' : 'down'}`}>
                {p.delta >= 0 ? '▲' : '▼'} {Math.abs(p.delta)}
              </span>
              <span className="pillar-tile-label">{p.label}</span>
              {p.process !== undefined && (
                <span className="pillar-tile-sub">
                  habits {p.process}
                  {p.outcome !== undefined ? ` · pace ${p.outcome}` : ''}
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      {topOdds && (
        <div className="forecast-banner">
          Today's #1 action: "{topOdds.goalLabel}" odds {Math.round(topOdds.from * 100)}% →{' '}
          <strong>{Math.round(topOdds.to * 100)}%</strong>
        </div>
      )}

      <section className="card">
        <div className="section-head">
          <h2>Do these today</h2>
          {fresh ? (
            <span className="momentum-chip">🌱 day 1</span>
          ) : (
            <span className={`momentum-chip ${momentum.direction}`}>
              {MOMENTUM_ICON[momentum.direction]} {momentum.direction}
            </span>
          )}
        </div>
        <div className="action-list">
          {briefing.actions.slice(0, 4).map((a, i) => (
            <div key={a.id} className="action-card">
              <div className="action-top">
                <div className="action-rank">{i + 1}</div>
                <div className="action-main">
                  <div className="action-title">{a.title}</div>
                  {a.goalOdds && (
                    <div className="action-odds">
                      {a.goalOdds.goalLabel}: {Math.round(a.goalOdds.from * 100)}% →{' '}
                      <strong>{Math.round(a.goalOdds.to * 100)}%</strong>
                    </div>
                  )}
                </div>
                <div className="action-impact">
                  <span className="impact-value">+{a.impactPoints.toFixed(1)}</span>
                </div>
              </div>
              <details className="action-details">
                <summary>Why this, why now</summary>
                <p className="action-detail">{a.detail}</p>
                <p className="action-prediction">🔮 {a.prediction}</p>
                <p className="action-because">{a.because}</p>
              </details>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Goals</h2>
        <div className="goal-strip">
          {assessments.map((a) => (
            <div key={a.goal.id} className="goal-mini">
              <div className="goal-mini-label">{a.goal.label}</div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.max(4, Math.round(a.progressPct * 100))}%` }}
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

      {briefing.insights.length > 0 && (
        <section className="card">
          <h2>Patterns in your data</h2>
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
