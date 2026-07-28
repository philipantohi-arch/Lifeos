import { CONNECTORS } from '../data/connectors';

export function IntegrationsView() {
  const categories = ['Wearables', 'Finance', 'Productivity', 'Lifestyle'] as const;

  return (
    <div className="view">
      <header>
        <h1>Integrations</h1>
        <p className="muted">
          LifeOS unifies every source into one schema, so sleep, money, tasks, and relationships can finally talk to each other.
        </p>
      </header>

      {categories.map((cat) => (
        <section key={cat} className="card">
          <h2>{cat}</h2>
          <div className="connector-grid">
            {CONNECTORS.filter((c) => c.category === cat).map((c) => (
              <div key={c.id} className={`connector ${c.status}`}>
                <div className="connector-head">
                  <span className="connector-icon">{c.icon}</span>
                  <span className="connector-name">{c.name}</span>
                  {c.status === 'connected' ? (
                    <span className="status-dot connected" title="Connected" />
                  ) : (
                    <button className="connect-btn">Connect</button>
                  )}
                </div>
                <div className="connector-provides">
                  {c.provides.map((p) => (
                    <span key={p} className="pill">
                      {p}
                    </span>
                  ))}
                </div>
                {c.lastSync && <div className="muted small">Last sync {c.lastSync}</div>}
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
