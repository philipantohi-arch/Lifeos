import { useEffect, useMemo, useState } from 'react';
import type { Goal, UserProfile } from './engine/types';
import { generateHistory } from './data/generator';
import { PERSONAS, getPersona } from './data/personas';
import { computeLifeScore } from './engine/lifeScore';
import { composeBriefing } from './engine/briefing';
import { discoverInsights } from './engine/insights';
import { assessGoals } from './engine/goals';
import { buildWeeklyReview, computeMomentum, detectAccomplishments, potentialGaps } from './engine/journey';
import { TodayView } from './views/TodayView';
import { GoalsView } from './views/GoalsView';
import { JourneyView } from './views/JourneyView';
import { DashboardView } from './views/DashboardView';
import { SimulatorView } from './views/SimulatorView';
import { InsightsView } from './views/InsightsView';
import { IntegrationsView } from './views/IntegrationsView';
import { ProfileView } from './views/ProfileView';
import { ScienceView } from './views/ScienceView';

type Tab =
  | 'today'
  | 'goals'
  | 'journey'
  | 'dashboard'
  | 'simulator'
  | 'insights'
  | 'profile'
  | 'science'
  | 'integrations';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'today', label: 'Today', icon: '☀️' },
  { id: 'goals', label: 'Goals', icon: '🏁' },
  { id: 'journey', label: 'Journey', icon: '🧭' },
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'simulator', label: 'Future Simulator', icon: '🔮' },
  { id: 'insights', label: 'Your Patterns', icon: '🧠' },
  { id: 'profile', label: 'Profile', icon: '👤' },
  { id: 'science', label: 'The Science', icon: '🔬' },
  { id: 'integrations', label: 'Integrations', icon: '🔌' },
];

/** Restore persona + profile edits across reloads. */
function loadSaved(): { personaId: string; overrides: Partial<UserProfile> } {
  try {
    const raw = localStorage.getItem('lifeos-profile-v2');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (PERSONAS.some((p) => p.id === parsed.personaId)) return parsed;
    }
  } catch {
    // corrupt/absent storage — fall through to defaults
  }
  return { personaId: PERSONAS[0].id, overrides: {} };
}

export default function App() {
  const saved = useMemo(loadSaved, []);
  const [tab, setTab] = useState<Tab>('today');
  const [personaId, setPersonaId] = useState(saved.personaId);
  const [overrides, setOverrides] = useState<Partial<UserProfile>>(saved.overrides);

  useEffect(() => {
    try {
      localStorage.setItem('lifeos-profile-v2', JSON.stringify({ personaId, overrides }));
    } catch {
      // storage unavailable (private mode) — persistence is best-effort
    }
  }, [personaId, overrides]);

  const persona = getPersona(personaId);
  const profile: UserProfile = useMemo(
    () => ({
      ...persona.profile,
      ...overrides,
      priorities: { ...persona.profile.priorities, ...(overrides.priorities ?? {}) },
      goals: overrides.goals ?? persona.profile.goals,
    }),
    [persona, overrides],
  );

  // In production this is the sync + scoring pipeline; here each persona's
  // demo dataset flows through the exact same engines.
  const records = useMemo(() => generateHistory(profile, persona.seed), [profile, persona.seed]);
  const scoreResult = useMemo(() => computeLifeScore(records, profile), [records, profile]);
  const briefing = useMemo(() => composeBriefing(records, profile), [records, profile]);
  const insights = useMemo(() => discoverInsights(records), [records]);
  const assessments = useMemo(() => assessGoals(records, profile), [records, profile]);
  const momentum = useMemo(() => computeMomentum(records, profile), [records, profile]);
  const accomplishments = useMemo(() => detectAccomplishments(records, profile), [records, profile]);
  const gaps = useMemo(() => potentialGaps(records, profile), [records, profile]);
  const review = useMemo(
    () => buildWeeklyReview(records, profile, assessments, scoreResult.history),
    [records, profile, assessments, scoreResult],
  );

  const selectPersona = (id: string) => {
    setPersonaId(id);
    setOverrides({});
  };

  const patchProfile = (patch: Partial<UserProfile>) =>
    setOverrides((prev) => ({
      ...prev,
      ...patch,
      priorities: { ...(prev.priorities ?? {}), ...(patch.priorities ?? {}) } as UserProfile['priorities'],
    }));

  const patchGoal = (goalId: string, patch: Partial<Goal>) => {
    const nextGoals = profile.goals.map((g) => (g.id === goalId ? { ...g, ...patch } : g));
    setOverrides((prev) => ({ ...prev, goals: nextGoals }));
  };

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
        {tab === 'today' && <TodayView briefing={briefing} assessments={assessments} momentum={momentum} />}
        {tab === 'goals' && (
          <GoalsView records={records} profile={profile} assessments={assessments} onChangeGoal={patchGoal} />
        )}
        {tab === 'journey' && (
          <JourneyView accomplishments={accomplishments} momentum={momentum} gaps={gaps} review={review} />
        )}
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
