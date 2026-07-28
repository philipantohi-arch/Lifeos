import { useMemo, useState } from 'react';
import type { UserProfile } from './engine/types';
import { generateHistory } from './data/generator';
import { PERSONAS, getPersona } from './data/personas';
import { computeLifeScore } from './engine/lifeScore';
import { composeBriefing } from './engine/briefing';
import { discoverInsights } from './engine/insights';
import { TodayView } from './views/TodayView';
import { DashboardView } from './views/DashboardView';
import { SimulatorView } from './views/SimulatorView';
import { InsightsView } from './views/InsightsView';
import { IntegrationsView } from './views/IntegrationsView';
import { ProfileView } from './views/ProfileView';
import { ScienceView } from './views/ScienceView';

type Tab = 'today' | 'dashboard' | 'simulator' | 'insights' | 'profile' | 'science' | 'integrations';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'today', label: 'Today', icon: '☀️' },
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'simulator', label: 'Future Simulator', icon: '🔮' },
  { id: 'insights', label: 'Your Patterns', icon: '🧠' },
  { id: 'profile', label: 'Profile', icon: '👤' },
  { id: 'science', label: 'The Science', icon: '🔬' },
  { id: 'integrations', label: 'Integrations', icon: '🔌' },
];

export default function App() {
  const [tab, setTab] = useState<Tab>('today');
  const [personaId, setPersonaId] = useState(PERSONAS[0].id);
  const [overrides, setOverrides] = useState<Partial<UserProfile>>({});

  const persona = getPersona(personaId);
  const profile: UserProfile = useMemo(
    () => ({ ...persona.profile, ...overrides, priorities: { ...persona.profile.priorities, ...(overrides.priorities ?? {}) } }),
    [persona, overrides],
  );

  // In production this is the sync + scoring pipeline; here each persona's
  // demo dataset flows through the exact same engines. History regenerates
  // when profile changes that shape behavior (work pattern, situation, …).
  const records = useMemo(() => generateHistory(profile, persona.seed), [profile, persona.seed]);
  const scoreResult = useMemo(() => computeLifeScore(records, profile), [records, profile]);
  const briefing = useMemo(() => composeBriefing(records, profile), [records, profile]);
  const insights = useMemo(() => discoverInsights(records), [records]);

  const selectPersona = (id: string) => {
    setPersonaId(id);
    setOverrides({});
  };

  const patchProfile = (patch: Partial<UserProfile>) =>
    setOverrides((prev) => ({ ...prev, ...patch, priorities: { ...(prev.priorities ?? {}), ...(patch.priorities ?? {}) } as UserProfile['priorities'] }));

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
        <div className="sidebar-persona">
          <span className="persona-chip" onClick={() => setTab('profile')}>
            {profile.name} · {profile.age}
          </span>
        </div>
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
        {tab === 'profile' && (
          <ProfileView personaId={personaId} profile={profile} onSelectPersona={selectPersona} onChange={patchProfile} />
        )}
        {tab === 'science' && <ScienceView />}
        {tab === 'integrations' && <IntegrationsView />}
      </main>
    </div>
  );
}
