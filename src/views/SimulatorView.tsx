import { useEffect, useMemo, useState } from 'react';
import type { DayRecord, UserProfile } from '../engine/types';
import { getScenarios, simulate } from '../engine/simulator';
import { METRIC_META, currentMetric } from '../engine/goals';
import { TrendChart } from '../components/TrendChart';
import { FanChart } from '../components/FanChart';

interface Props {
  records: DayRecord[];
  profile: UserProfile;
}

const HORIZONS = [
  { months: 6, label: '6 months' },
  { months: 12, label: '1 year' },
  { months: 24, label: '2 years' },
  { months: 60, label: '5 years' },
];

export function SimulatorView({ records, profile }: Props) {
  const scenarios = useMemo(() => getScenarios(profile, records), [profile, records]);
  const [scenarioId, setScenarioId] = useState(scenarios[0].id);
  const [horizon, setHorizon] = useState(24);

  // Scenario list is personalized; if a profile change removed the selected
  // one (e.g. quit-alcohol for a non-drinker), fall back to the first.
  useEffect(() => {
    if (!scenarios.some((s) => s.id === scenarioId)) setScenarioId(scenarios[0].id);
  }, [scenarios, scenarioId]);

  const activeId = scenarios.some((s) => s.id === scenarioId) ? scenarioId : scenarios[0].id;
  const result = useMemo(
    () => simulate(activeId, records, profile, horizon),
    [activeId, records, profile, horizon],
  );

  const showDollars = activeId === 'invest-extra' || activeId === 'quit-alcohol' || activeId === 'meal-prep';
  const fan = result.goalFan;
  const xLabels = ['Now', `${Math.round(horizon / 2)} mo`, `${horizon} mo`];
  const endSim = result.simulated[result.simulated.length - 1];
  const endBase = result.baseline[result.baseline.length - 1];

  return (
    <div className="view">
      <header>
        <h1>Future Simulator</h1>
        <p className="muted">
          Ask "what if" — LifeOS projects the compounding effect of a decision across your whole life, not just one app's metric.
        </p>
      </header>

      <div className="scenario-grid">
        {scenarios.map((s) => (
          <button
            key={s.id}
            className={`scenario-btn ${s.id === activeId ? 'active' : ''}`}
            onClick={() => setScenarioId(s.id)}
          >
            <span className="scenario-emoji">{s.emoji}</span>
            <span className="scenario-q">{s.question}</span>
            <span className="scenario-desc">{s.description}</span>
          </button>
        ))}
      </div>

      <section className="card">
        <div className="section-head">
          <h2>{result.title}</h2>
          <div className="horizon-picker">
            {HORIZONS.map((h) => (
              <button
                key={h.months}
                className={`chip ${horizon === h.months ? 'active' : ''}`}
                onClick={() => setHorizon(h.months)}
              >
                {h.label}
              </button>
            ))}
          </div>
        </div>

        <p className="sim-summary">{result.summary}</p>

        <TrendChart
          series={[
            { values: result.baseline.map((p) => p.lifeScore), color: 'var(--muted-line)', label: 'Current path' },
            { values: result.simulated.map((p) => p.lifeScore), color: 'var(--accent)', label: 'With this change', fill: true },
          ]}
          xLabels={xLabels}
          min={Math.min(...result.baseline.map((p) => p.lifeScore)) - 4}
          max={Math.max(...result.simulated.map((p) => p.lifeScore)) + 4}
        />

        {showDollars && endSim.dollars !== undefined && endBase.dollars !== undefined && (
          <div className="dollars-strip">
            <div>
              <div className="stat-label">Savings on current path</div>
              <div className="stat-value">${endBase.dollars.toLocaleString()}</div>
            </div>
            <div>
              <div className="stat-label">Savings with this change</div>
              <div className="stat-value accent">${endSim.dollars.toLocaleString()}</div>
            </div>
            <div>
              <div className="stat-label">Difference</div>
              <div className="stat-value green">+${(endSim.dollars - endBase.dollars).toLocaleString()}</div>
            </div>
          </div>
        )}

        {result.goalOdds.length > 0 && (
          <div className="odds-panel">
            <h3>What this does to YOUR goal odds</h3>
            <p className="muted small">Monte Carlo on your own history — 500 simulated futures per goal.</p>
            {result.goalOdds.map((o) => (
              <div key={o.goalLabel} className="odds-row">
                <span className="odds-goal">{o.goalLabel}</span>
                <div className="odds-bars">
                  <div className="odds-bar-track">
                    <div className="odds-bar base" style={{ width: `${Math.round(o.from * 100)}%` }} />
                  </div>
                  <div className="odds-bar-track">
                    <div className="odds-bar boosted" style={{ width: `${Math.round(o.to * 100)}%` }} />
                  </div>
                </div>
                <span className="odds-numbers">
                  {Math.round(o.from * 100)}% → <strong>{Math.round(o.to * 100)}%</strong>
                </span>
              </div>
            ))}
          </div>
        )}

        {fan && (
          <div className="fan-section">
            <h3>
              "{fan.goal.label}" — {fan.forecast.runs.toLocaleString()} futures with this change
            </h3>
            <FanChart
              forecast={fan.forecast}
              startValue={currentMetric(fan.goal.metric, records, profile)}
              target={fan.goal.target}
              unit={METRIC_META[fan.goal.metric].unit}
            />
          </div>
        )}

        <div className="highlights">
          {result.highlights.map((h, i) => (
            <div key={i} className="highlight-row">
              <span className="highlight-bullet">→</span>
              {h}
            </div>
          ))}
        </div>

        <p className="disclaimer">
          Projections are directional models based on your history and published behavioral research — for decision support, not
          medical or financial advice.
        </p>
      </section>
    </div>
  );
}
