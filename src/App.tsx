import { useEffect, useMemo, useState } from 'react';
import type { Goal, UserProfile } from './engine/types';
import { generateBaselineHistory, generateHistory, isFreshStart } from './data/generator';
import { PERSONAS, getPersona } from './data/personas';
import { computeLifeScore } from './engine/lifeScore';
import { composeBriefing } from './engine/briefing';
import { discoverInsights } from './engine/insights';
import { assessGoals } from './engine/goals';
import { buildWeeklyReview, computeMomentum, detectAccomplishments, potentialGaps } from './engine/journey';
import { OnboardingView } from './views/OnboardingView';
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

type Mode = 'onboarding' | 'custom' | 'demo';

interface SavedState {
  mode: Mode;
  personaId: string;
  overrides: Partial<UserProfile>;
  customProfile?: UserProfile;
}

const STORAGE_KEY = 'lifeos-state-v3';

/** New users start at onboarding — no pre-filled demo data. */
function loadSaved(): SavedState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as SavedState;
      if (parsed.mode === 'custom' && parsed.customProfile) return parsed;
      if (parsed.mode === 'demo' && PERSONAS.some((p) => p.id === parsed.personaId)) return parsed;
    }
  } catch {
    // corrupt/absent storage — fall through to onboarding
  }
  return { mode: 'onboarding', personaId: PERSONAS[0].id, overrides: {} };
}

/** Stable per-user seed so a custom profile gets its own consistent data. */
function seedFor(profile: UserProfile): number {
  let h = 2166136261;
  const s = `${profile.name}|${profile.age}|${profile.weightLbs}`;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export default function App() {
  const initial = useMemo(loadSaved, []);
  const [tab, setTab] = useState<Tab>('today');
  const [mode, setMode] = useState<Mode>(initial.mode);
  const [personaId, setPersonaId] = useState(initial.personaId);
  const [overrides, setOverrides] = useState<Partial<UserProfile>>(initial.overrides);
  const [customProfile, setCustomProfile] = useState<UserProfile | undefined>(initial.customProfile);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, personaId, overrides, customProfile }));
    } catch {
      // storage unavailable (private mode) — persistence is best-effort
    }
  }, [mode, personaId, overrides, customProfile]);

  const persona = getPersona(personaId);
  const profile: UserProfile = useMemo(() => {
    if (mode === 'custom' && customProfile) return customProfile;
    return {
      ...persona.profile,
      ...overrides,
      priorities: { ...persona.profile.priorities, ...(overrides.priorities ?? {}) },
      goals: overrides.goals ?? persona.profile.goals,
    };
  }, [mode, customProfile, persona, overrides]);

  const seed = mode === 'custom' && customProfile ? seedFor(customProfile) : persona.seed;

  // In production this is the sync + scoring pipeline. A fresh user gets
  // ONLY a deterministic baseline window built from their own inputs — no
  // invented past. Demo mode uses full persona datasets.
  const records = useMemo(
    () => (mode === 'custom' ? generateBaselineHistory(profile) : generateHistory(profile, seed)),
    [mode, profile, seed],
  );
  const fresh = isFreshStart(records);
  const scoreResult = useMemo(() => computeLifeScore(records, profile), [records, profile]);
  const briefing = useMemo(() => composeBriefing(records, profile), [records, profile]);
  const insights = useMemo(() => discoverInsights(records), [records]);
  const assessments = useMemo(() => assessGoals(records, profile), [records, profile]);
  const momentum = useMemo(() => computeMomentum(records, profile), [records, profile]);
  // Fresh users have no lived history — never fabricate wins from it.
  const accomplishments = useMemo(
    () => (fresh ? [] : detectAccomplishments(records, profile)),
    [fresh, records, profile],
  );
  const gaps = useMemo(() => (fresh ? [] : potentialGaps(records, profile)), [fresh, records, profile]);
  const review = useMemo(
    () => buildWeeklyReview(records, profile, assessments, scoreResult.history),
    [records, profile, assessments, scoreResult],
  );

  if (mode === 'onboarding') {
    return (
      <OnboardingView
        onComplete={(p) => {
          setCustomProfile(p);
          setMode('custom');
          setTab('today');
        }}
        onExploreDemo={() => {
          setMode('demo');
          setPersonaId(PERSONAS[0].id);
          setTab('today');
        }}
      />
    );
  }

  const selectPersona = (id: string) => {
    setMode('demo');
    setPersonaId(id);
    setOverrides({});
  };

  const patchProfile = (patch: Partial<UserProfile>) => {
    if (mode === 'custom' && customProfile) {
      setCustomProfile({
        ...customProfile,
        ...patch,
        priorities: { ...customProfile.priorities, ...(patch.priorities ?? {}) },
        baseline: patch.baseline ?? customProfile.baseline,
        goals: patch.goals ?? customProfile.goals,
      });
    } else {
      setOverrides((prev) => ({
        ...prev,
        ...patch,
        priorities: { ...(prev.priorities ?? {}), ...(patch.priorities ?? {}) } as UserProfile['priorities'],
      }));
    }
  };

  const patchGoal = (goalId: string, patch: Partial<Goal>) => {
    const nextGoals = profile.goals.map((g) => (g.id === goalId ? { ...g, ...patch } : g));
    patchProfile({ goals: nextGoals });
  };

  const resetApp = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
    setCustomProfile(undefined);
    setOverrides({});
    setMode('onboarding');
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
            {mode === 'demo' ? `Demo: ${profile.name}` : profile.name} · {profile.age}
          </span>
        </div>
        <div className="sidebar-score">
          <div className="sidebar-score-value">{scoreResult.score}</div>
          <div className="sidebar-score-label">Life Score</div>
        </div>
      </aside>

      <main className="main">
        {mode === 'demo' && (
          <div className="demo-banner">
            You're exploring a demo life ({profile.name}).{' '}
            {customProfile ? (
              <button className="link-btn" onClick={() => setMode('custom')}>
                Back to my LifeOS
              </button>
            ) : (
              <button className="link-btn" onClick={resetApp}>
                Set up my own
              </button>
            )}
          </div>
        )}
        {tab === 'today' && <TodayView briefing={briefing} assessments={assessments} momentum={momentum} fresh={fresh} />}
        {tab === 'goals' && (
          <GoalsView records={records} profile={profile} assessments={assessments} onChangeGoal={patchGoal} fresh={fresh} />
        )}
        {tab === 'journey' && (
          <JourneyView accomplishments={accomplishments} momentum={momentum} gaps={gaps} review={review} fresh={fresh} />
        )}
        {tab === 'dashboard' && <DashboardView records={records} result={scoreResult} profile={profile} />}
        {tab === 'simulator' && <SimulatorView records={records} profile={profile} />}
        {tab === 'insights' && <InsightsView insights={insights} fresh={fresh} />}
        {tab === 'profile' && (
          <ProfileView
            personaId={mode === 'demo' ? personaId : ''}
            profile={profile}
            onSelectPersona={selectPersona}
            onChange={patchProfile}
            onReset={resetApp}
          />
        )}
        {tab === 'science' && <ScienceView />}
        {tab === 'integrations' && <IntegrationsView />}
      </main>
    </div>
  );
}
