import { useEffect, useMemo, useState } from 'react';
import type { CheckInInput, Goal, UserProfile } from './engine/types';
import { assembleCustomRecords, generateHistory, isFreshStart, realDays } from './data/generator';
import { PERSONAS, getPersona } from './data/personas';
import { computeLifeScore } from './engine/lifeScore';
import { composeBriefing } from './engine/briefing';
import { discoverInsights } from './engine/insights';
import { assessGoals } from './engine/goals';
import { buildWeeklyReview, computeMomentum, detectAccomplishments, potentialGaps } from './engine/journey';
import { OnboardingView } from './views/OnboardingView';
import { CheckInView } from './views/CheckInView';
import { Segments } from './components/Segments';
import { TodayView } from './views/TodayView';
import { GoalsView } from './views/GoalsView';
import { JourneyView } from './views/JourneyView';
import { DashboardView } from './views/DashboardView';
import { SimulatorView } from './views/SimulatorView';
import { InsightsView } from './views/InsightsView';
import { IntegrationsView } from './views/IntegrationsView';
import { ProfileView } from './views/ProfileView';
import { ScienceView } from './views/ScienceView';

type Tab = 'today' | 'checkin' | 'goals' | 'journey' | 'me';
type GoalsSeg = 'goals' | 'future';
type JourneySeg = 'journey' | 'patterns';
type MeSeg = 'profile' | 'dashboard' | 'science' | 'connect';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'today', label: 'Today', icon: '☀️' },
  { id: 'goals', label: 'Goals', icon: '🎯' },
  { id: 'checkin', label: 'Check in', icon: '＋' },
  { id: 'journey', label: 'Journey', icon: '🧭' },
  { id: 'me', label: 'Me', icon: '👤' },
];

type Mode = 'onboarding' | 'custom' | 'demo';

interface LoggedDay {
  date: string;
  input: CheckInInput;
}

interface SavedState {
  mode: Mode;
  personaId: string;
  overrides: Partial<UserProfile>;
  customProfile?: UserProfile;
  loggedDays?: LoggedDay[];
}

/** Real device date — custom mode lives on the actual calendar. */
function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
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
  const [goalsSeg, setGoalsSeg] = useState<GoalsSeg>('goals');
  const [journeySeg, setJourneySeg] = useState<JourneySeg>('journey');
  const [meSeg, setMeSeg] = useState<MeSeg>('profile');
  const [mode, setMode] = useState<Mode>(initial.mode);
  const [personaId, setPersonaId] = useState(initial.personaId);
  const [overrides, setOverrides] = useState<Partial<UserProfile>>(initial.overrides);
  const [customProfile, setCustomProfile] = useState<UserProfile | undefined>(initial.customProfile);
  const [loggedDays, setLoggedDays] = useState<LoggedDay[]>(initial.loggedDays ?? []);
  const [saveToast, setSaveToast] = useState<{ before: number; after?: number } | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, personaId, overrides, customProfile, loggedDays }));
    } catch {
      // storage unavailable (private mode) — persistence is best-effort
    }
  }, [mode, personaId, overrides, customProfile, loggedDays]);


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

  // In production this is the sync + scoring pipeline. A custom user's
  // records = their baseline runway + every day they've actually logged
  // (real calendar dates); demo mode uses full persona datasets.
  const records = useMemo(
    () =>
      mode === 'custom'
        ? assembleCustomRecords(profile, loggedDays, todayISO())
        : generateHistory(profile, seed),
    [mode, profile, seed, loggedDays],
  );
  const fresh = isFreshStart(records);
  const realCount = mode === 'custom' ? realDays(records).length : records.length;
  const realRecords = useMemo(() => (mode === 'custom' ? realDays(records) : records), [mode, records]);
  const scoreResult = useMemo(() => computeLifeScore(records, profile), [records, profile]);

  // Complete the save toast once the score has recomputed from the new log.
  useEffect(() => {
    setSaveToast((t) => (t && t.after === undefined ? { ...t, after: scoreResult.score } : t));
  }, [scoreResult.score]);
  const briefing = useMemo(() => composeBriefing(records, profile), [records, profile]);
  // Patterns come only from REAL days, and need ~3 weeks of them.
  const insights = useMemo(
    () => (mode === 'custom' && realCount < 21 ? [] : discoverInsights(realRecords)),
    [mode, realCount, realRecords],
  );
  const assessments = useMemo(() => assessGoals(records, profile), [records, profile]);
  const momentum = useMemo(() => computeMomentum(records, profile), [records, profile]);
  // Wins come only from REAL days — never from baseline estimates.
  const accomplishments = useMemo(
    () => (realCount < 7 ? [] : detectAccomplishments(realRecords, profile)),
    [realCount, realRecords, profile],
  );
  const gaps = useMemo(
    () => (realCount < 14 ? [] : potentialGaps(realRecords, profile)),
    [realCount, realRecords, profile],
  );
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

  const saveCheckIn = (input: CheckInInput) => {
    const date = todayISO();
    setSaveToast({ before: scoreResult.score });
    setTab('today');
    setLoggedDays((prev) => [...prev.filter((l) => l.date !== date), { date, input }]);
    if (mode === 'custom' && customProfile) {
      const prevSaved = loggedDays.find((l) => l.date === date)?.input.saved ?? 0;
      setCustomProfile({
        ...customProfile,
        // Savings balance moves by what you actually transferred today.
        savingsBalance: Math.max(0, customProfile.savingsBalance + input.saved - prevSaved),
        // A logged weigh-in becomes the profile's current weight.
        weightLbs: input.weightLbs ?? customProfile.weightLbs,
      });
    }
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
        <div className="sidebar-score">
          <div className="sidebar-score-value">{scoreResult.score}</div>
          <div className="sidebar-score-label">Life Score</div>
        </div>
      </aside>

      <header className="appbar">
        <span className="appbar-brand">◉ LifeOS</span>
        <span className="appbar-score">{scoreResult.score}</span>
      </header>

      <main className="main">
        {mode === 'demo' && (
          <div className="demo-banner">
            Exploring a demo life ({profile.name}).{' '}
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

        {tab === 'today' && (
          <>
            {saveToast?.after !== undefined && (
              <div className="save-toast" onClick={() => setSaveToast(null)}>
                ✓ Day logged — Life Score{' '}
                {saveToast.after === saveToast.before
                  ? `steady at ${saveToast.after}`
                  : `${saveToast.before} → ${saveToast.after}`}
                . Every number below just updated from your real day.
              </div>
            )}
            {mode === 'custom' && !loggedDays.some((l) => l.date === todayISO()) && (
              <div className="checkin-nudge" onClick={() => setTab('checkin')}>
                ✍️ 30 seconds keeps your data real — <strong>check in →</strong>
              </div>
            )}
            <TodayView briefing={briefing} assessments={assessments} momentum={momentum} fresh={fresh} />
          </>
        )}

        {tab === 'checkin' &&
          (mode === 'custom' ? (
            <CheckInView
              profile={profile}
              todayISO={todayISO()}
              existing={loggedDays.find((l) => l.date === todayISO())?.input}
              realDayCount={realCount}
              onSave={saveCheckIn}
            />
          ) : (
            <div className="view">
              <header>
                <h1>Daily check-in</h1>
                <p className="muted">Check-ins are for your own LifeOS. Set yours up from the Me tab.</p>
              </header>
            </div>
          ))}

        {tab === 'goals' && (
          <div className="view">
            <Segments<GoalsSeg>
              options={[
                { id: 'goals', label: 'My goals' },
                { id: 'future', label: 'What if…' },
              ]}
              value={goalsSeg}
              onChange={setGoalsSeg}
            />
            {goalsSeg === 'goals' ? (
              <GoalsView records={records} profile={profile} assessments={assessments} onChangeGoal={patchGoal} fresh={fresh} />
            ) : (
              <SimulatorView records={records} profile={profile} />
            )}
          </div>
        )}

        {tab === 'journey' && (
          <div className="view">
            <Segments<JourneySeg>
              options={[
                { id: 'journey', label: 'Journey' },
                { id: 'patterns', label: 'Patterns' },
              ]}
              value={journeySeg}
              onChange={setJourneySeg}
            />
            {journeySeg === 'journey' ? (
              <JourneyView accomplishments={accomplishments} momentum={momentum} gaps={gaps} review={review} fresh={fresh} />
            ) : (
              <InsightsView insights={insights} fresh={mode === 'custom' && realCount < 21} />
            )}
          </div>
        )}

        {tab === 'me' && (
          <div className="view">
            <Segments<MeSeg>
              options={[
                { id: 'profile', label: 'Profile' },
                { id: 'dashboard', label: 'Stats' },
                { id: 'science', label: 'Science' },
                { id: 'connect', label: 'Connect' },
              ]}
              value={meSeg}
              onChange={setMeSeg}
            />
            {meSeg === 'profile' && (
              <ProfileView
                personaId={mode === 'demo' ? personaId : ''}
                profile={profile}
                onSelectPersona={selectPersona}
                onChange={patchProfile}
                onReset={resetApp}
              />
            )}
            {meSeg === 'dashboard' && <DashboardView records={records} result={scoreResult} profile={profile} />}
            {meSeg === 'science' && <ScienceView />}
            {meSeg === 'connect' && <IntegrationsView />}
          </div>
        )}
      </main>

      <nav className="bottom-nav">
        {TABS.map((t) =>
          t.id === 'checkin' ? (
            <button key={t.id} className="bn-checkin" onClick={() => setTab('checkin')} aria-label="Check in">
              ＋
            </button>
          ) : (
            <button key={t.id} className={`bn-item ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
              <span className="bn-icon">{t.icon}</span>
              <span className="bn-label">{t.label}</span>
            </button>
          ),
        )}
      </nav>
    </div>
  );
}
