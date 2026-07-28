import { useMemo, useState } from 'react';
import { generateHistory, DEMO_PROFILE } from './data/generator';
import { computeLifeScore } from './engine/lifeScore';
import { composeBriefing } from './engine/briefing';
import { discoverInsights } from './engine/insights';
import { TodayView } from './views/TodayView';
import { DashboardView } from './views/DashboardView';
import { SimulatorView } from './views/SimulatorView';
import { InsightsView } from './views/InsightsView';
import { IntegrationsView } from './views/IntegrationsView';

type Tab = 'today' | 'dashboard' | 'simulator' | 'insights' | 'integrations';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'today', label: 'Today', icon: '☀️' },
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'simulator', label: 'Future Simulator', icon: '🔮' },
  { id: 'insights', label: 'Your Patterns', icon: '🧠' },
  { id: 'integrations', label: 'Integrations', icon: '🔌' },
];

export default function App() {
  const [tab, setTab] = useState<Tab>('today');

  // In production this is the sync + scoring pipeline; here the demo
  // dataset flows through the exact same engines.
  const records = useMemo(() => generateHistory(), []);
  const profile = DEMO_PROFILE;
  const scoreResult = useMemo(() => computeLifeScore(records, profile), [records, profile]);
  const briefing = useMemo(() => composeBriefing(records, profile), [records, profile]);
  const insights = useMemo(() => discoverInsights(records), [records]);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">◉</span>
          <div>
            <div className="brand-name">LifeOS</div>
            <div className="brand-tag">One score. One coach.</div>
          </div>
        </div>
        <nav>
          {TABS.map((t) => (
            <button key={t.id} className={`nav-item ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
              <span className="nav-icon">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-score">
          <div className="sidebar-score-value">{scoreResult.score}</div>
          <div className="sidebar-score-label">Life Score</div>
        </div>
      </aside>

      <main className="main">
        {tab === 'today' && <TodayView briefing={briefing} />}
        {tab === 'dashboard' && <DashboardView records={records} result={scoreResult} profile={profile} />}
        {tab === 'simulator' && <SimulatorView records={records} profile={profile} />}
        {tab === 'insights' && <InsightsView insights={insights} />}
        {tab === 'integrations' && <IntegrationsView />}
      </main>
    </div>
  );
}
