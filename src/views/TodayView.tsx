import type { Briefing } from '../engine/types';
import { ScoreRing } from '../components/ScoreRing';

const PILLAR_ICONS: Record<string, string> = {
  health: '💪',
  wealth: '💰',
  productivity: '🎯',
  relationships: '🤝',
  habits: '🔁',
};

export function TodayView({ briefing }: { briefing: Briefing }) {
  return (
    <div className="view">
      <header className="today-header">
        <div>
          <h1>{briefing.greeting}</h1>
          <p className="muted">{briefing.dateLabel} · Morning Briefing</p>
        </div>
      </header>

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
