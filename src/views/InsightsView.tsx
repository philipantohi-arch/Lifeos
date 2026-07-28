import type { Insight } from '../engine/types';

const CONF_LABEL: Record<Insight['confidence'], string> = {
  strong: 'Strong pattern',
  moderate: 'Moderate pattern',
  emerging: 'Emerging pattern',
};

export function InsightsView({ insights, fresh }: { insights: Insight[]; fresh?: boolean }) {
  if (fresh || insights.length === 0) {
    return (
      <div className="view">
        <header>
          <h1>Your Patterns</h1>
          <p className="muted">
            LifeOS mines your history for personal cause-and-effect — statistically, from your own days, never from
            generic advice.
          </p>
        </header>
        <section className="card note-card">
          <h2>🔓 Unlocks after ~2–3 weeks of data</h2>
          <p className="muted">
            Pattern discovery needs variation to find truth in: nights you slept more and less, weeks you cooked and
            weeks you didn't. Once enough real days accumulate, LifeOS starts surfacing findings like "you focus 40%
            better after 7.5h+ sleep" or "your spending jumps after short nights" — each one shown with the
            correlation strength and sample size behind it, so you can judge the evidence yourself.
          </p>
        </section>
      </div>
    );
  }
  return (
    <div className="view">
      <header>
        <h1>Your Patterns</h1>
        <p className="muted">
          LifeOS continuously mines your unified history for personal cause-and-effect. Every insight below was discovered
          statistically from your data — the correlation and sample size are shown so you can judge the evidence yourself.
        </p>
      </header>

      <div className="insight-grid">
        {insights.map((ins) => (
          <div key={ins.id} className={`card insight-card conf-${ins.confidence}`}>
            <div className="insight-head">
              <span className={`conf-badge ${ins.confidence}`}>{CONF_LABEL[ins.confidence]}</span>
              <span className="muted small">
                r = {ins.correlation.toFixed(2)} · {ins.sampleSize} days
              </span>
            </div>
            <h3>{ins.title}</h3>
            <p>{ins.detail}</p>
            <div className="insight-pillars">
              {ins.pillars.map((p) => (
                <span key={p} className="pill">
                  {p}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <section className="card note-card">
        <h2>How this works</h2>
        <p className="muted">
          The pattern engine runs correlation probes — including time-lagged ones (last night's sleep → today's spending) —
          across every pair of signals in your unified data. Relationships that clear statistical thresholds become insights;
          the strongest ones feed directly into your daily recommendations. As more days of data arrive, confidence labels
          upgrade from <em>emerging</em> to <em>strong</em>.
        </p>
      </section>
    </div>
  );
}
