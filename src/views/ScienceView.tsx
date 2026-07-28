import { RESEARCH } from '../engine/researchBase';

const DOMAIN_ICONS: Record<string, string> = {
  Sleep: '😴',
  'Physical activity': '🏃',
  'Cardio norms': '❤️',
  Finance: '💰',
  'Behavior change': '🧩',
  'Chronotype & work': '🕐',
  'Nutrition & substances': '🥗',
  'Goals & motivation': '🏁',
};

const STRENGTH_LABEL: Record<string, string> = {
  guideline: 'Official guideline',
  'meta-analysis': 'Meta-analysis',
  rct: 'Randomized trial',
  cohort: 'Cohort study',
  expert: 'Expert consensus',
};

export function ScienceView() {
  const domains = [...new Set(RESEARCH.map((r) => r.domain))];

  return (
    <div className="view">
      <header>
        <h1>The Science</h1>
        <p className="muted">
          Every personalized target and recommendation in LifeOS traces to a source below — official guidelines,
          meta-analyses, and landmark studies. No number in the engine is made up, and each entry says exactly how it's
          used. Evidence changes; so does LifeOS.
        </p>
      </header>

      {domains.map((domain) => (
        <section key={domain} className="card">
          <h2>
            {DOMAIN_ICONS[domain]} {domain}
          </h2>
          <div className="research-list">
            {RESEARCH.filter((r) => r.domain === domain).map((r) => (
              <div key={r.id} className="research-row">
                <div className="research-main">
                  <div className="research-claim">{r.claim}</div>
                  <div className="research-numbers">{r.numbers}</div>
                  <div className="research-source">
                    <a href={r.url} target="_blank" rel="noreferrer">
                      {r.source}
                    </a>{' '}
                    ({r.year}) · {r.population}
                  </div>
                  <div className="research-used">↳ Used for: {r.usedFor}</div>
                </div>
                <span className={`strength-badge s-${r.strength}`}>{STRENGTH_LABEL[r.strength]}</span>
              </div>
            ))}
          </div>
        </section>
      ))}

      <section className="card note-card">
        <h2>Honest limits</h2>
        <p className="muted">
          Guidelines describe populations; you are a sample size of one. LifeOS uses this research to set starting
          targets, then personalizes further from your own data (the Patterns tab). Correlations in your data are not
          proof of causation, projections are directional models, and none of this is medical or financial advice —
          for diagnoses and portfolios, see professionals.
        </p>
      </section>
    </div>
  );
}
