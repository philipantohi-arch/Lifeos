import type { Accomplishment, Momentum, PotentialGap, WeeklyReview } from '../engine/types';

interface Props {
  accomplishments: Accomplishment[];
  momentum: Momentum;
  gaps: PotentialGap[];
  review: WeeklyReview;
  fresh: boolean;
}

const MOMENTUM_ICON = { rising: '📈', steady: '➡️', falling: '📉' } as const;

export function JourneyView({ accomplishments, momentum, gaps, review, fresh }: Props) {
  if (fresh) {
    return (
      <div className="view">
        <header>
          <p className="muted small">Day 1. Your story starts now — nothing here is invented.</p>
        </header>
        <section className="card momentum-card">
          <div className="momentum-head">
            <span className="momentum-icon">🌱</span>
            <div>
              <h2>This page fills itself as you live it</h2>
              <p className="muted small">Everything below unlocks from real days, never fabricated ones.</p>
            </div>
          </div>
          <div className="unlock-list">
            <div className="unlock-row"><span className="unlock-when">After ~3 days</span> Momentum — whether your daily execution is rising or slipping.</div>
            <div className="unlock-row"><span className="unlock-when">After 7 days</span> Your first weekly review, and your first streaks and records.</div>
            <div className="unlock-row"><span className="unlock-when">After ~2–3 weeks</span> Personal patterns — the cause-and-effect LifeOS statistically discovers in YOUR data.</div>
            <div className="unlock-row"><span className="unlock-when">Always</span> Comebacks count double here. Miss a day, come back, get celebrated — never guilted.</div>
          </div>
        </section>
        <section className="card">
          <h2>Meanwhile: today is the only day that matters</h2>
          <p className="muted">
            The Today tab already ranks your highest-leverage actions, and the Goals tab shows your odds. Do one thing
            today; the Journey writes itself.
          </p>
        </section>
      </div>
    );
  }
  return (
    <div className="view">
      <header>
        <p className="muted small">Small wins, comebacks, momentum — compared to one person only: past you.</p>
      </header>

      <section className={`card momentum-card ${momentum.direction}`}>
        <div className="momentum-head">
          <span className="momentum-icon">{MOMENTUM_ICON[momentum.direction]}</span>
          <div>
            <h2>Momentum: {momentum.direction}</h2>
            <p className="muted small">
              Daily execution {momentum.recent}/100 now vs {momentum.prior}/100 two weeks ago
            </p>
          </div>
        </div>
        <p className="momentum-narrative">{momentum.narrative}</p>
      </section>

      <div className="two-col">
        <section className="card">
          <h2>Weekly review · {review.weekLabel}</h2>
          <p className={`review-score ${review.scoreChange >= 0 ? 'up' : 'down'}`}>
            Life Score {review.scoreChange >= 0 ? '+' : ''}
            {review.scoreChange} this week · best day {review.bestDay}
          </p>
          <div className="review-block">
            <h3>What happened</h3>
            <ul>
              {review.recap.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
          <div className="review-block">
            <h3>Next week, focus on</h3>
            <ul>
              {review.nextFocus.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="card">
          <h2>Your proven potential</h2>
          <p className="muted small">Not aspirations — your own best weeks, on record.</p>
          <div className="gap-list">
            {gaps.length === 0 && <p className="muted">You're currently running at your recorded best. New records ahead.</p>}
            {gaps.map((g) => (
              <div key={g.metricLabel} className="gap-row">
                <div className="gap-metric">{g.metricLabel}</div>
                <div className="gap-values">
                  <span className="gap-now">{g.currentAvg}</span>
                  <span className="gap-arrow">→</span>
                  <span className="gap-best">{g.bestAvg}</span>
                </div>
                <p className="gap-msg">{g.message}</p>
              </div>
            ))}
          </div>
          <div className="repair-tokens">
            <span className="token-icons">🛡️ 🛡️</span>
            <div>
              <div className="token-title">2 streak repair tokens available</div>
              <div className="muted small">
                Miss a day? Spend a token and the streak lives. Rewarding the comeback — not punishing the miss — was
                the single best-performing intervention in the largest exercise study ever run.
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="card">
        <div className="section-head">
          <h2>Accomplishments</h2>
          <span className="muted small">Auto-detected from your data — no self-reporting theater</span>
        </div>
        <div className="accomplishment-list">
          {accomplishments.map((a) => (
            <div key={a.id} className={`accomplishment kind-${a.kind}`}>
              <span className="acc-emoji">{a.emoji}</span>
              <div className="acc-body">
                <div className="acc-title">
                  {a.title}
                  <span className="acc-date">
                    {new Date(a.date + 'T00:00:00Z').toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      timeZone: 'UTC',
                    })}
                  </span>
                </div>
                <div className="acc-detail">{a.detail}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
