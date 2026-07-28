import type { DayRecord, LifeScoreResult, UserProfile } from '../engine/types';
import { deriveTargets } from '../engine/personalize';
import { TrendChart } from '../components/TrendChart';

interface Props {
  records: DayRecord[];
  result: LifeScoreResult;
  profile: UserProfile;
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

export function DashboardView({ records, result, profile }: Props) {
  const t = deriveTargets(profile);
  const last30 = records.slice(-30);
  const today = records[records.length - 1];
  const avg = (f: (r: DayRecord) => number) => last30.reduce((a, r) => a + f(r), 0) / last30.length;

  const monthLabels = [last30[0], last30[14], last30[29]].map((r) =>
    new Date(r.date + 'T00:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }),
  );

  const spend7 = records.slice(-7).reduce((a, r) => a + r.discretionarySpend, 0);
  const goalPct = Math.round((profile.savingsBalance / profile.savingsGoal) * 100);

  return (
    <div className="view">
      <header>
        <h1>Dashboard</h1>
        <p className="muted">Everything LifeOS is tracking, in one place.</p>
      </header>

      <section className="card">
        <h2>Life Score — last 30 days</h2>
        <TrendChart
          series={[{ values: result.history.slice(-30), color: 'var(--accent)', label: 'Life Score', fill: true }]}
          xLabels={monthLabels}
          min={40}
          max={100}
        />
      </section>

      <div className="stat-grid">
        <Stat
          label="Sleep (30d avg)"
          value={`${avg((r) => r.sleepHours).toFixed(1)}h`}
          sub={`Your range: ${t.sleepRange[0]}–${t.sleepRange[1]}h`}
        />
        <Stat label="Recovery today" value={String(today.recoveryScore)} sub={`HRV ${today.hrv}ms · RHR ${today.restingHR}`} />
        <Stat
          label="Steps (30d avg)"
          value={Math.round(avg((r) => r.steps)).toLocaleString()}
          sub={`Target: ${t.stepsTarget.toLocaleString()}/day`}
        />
        <Stat label="Deep work (30d avg)" value={`${avg((r) => r.deepWorkHours).toFixed(1)}h`} sub={`Focus score ${today.focusScore}`} />
        <Stat label="Spend this week" value={`$${Math.round(spend7)}`} sub={`Budget: $${t.weeklyDiscretionary}/wk`} />
        <Stat
          label={profile.savingsGoalLabel}
          value={`${goalPct}%`}
          sub={`$${profile.savingsBalance.toLocaleString()} of $${profile.savingsGoal.toLocaleString()}`}
        />
      </div>

      <div className="two-col">
        <section className="card">
          <h2>Sleep vs. Focus</h2>
          <p className="muted small">The relationship the recommendation engine leans on most.</p>
          <TrendChart
            height={190}
            series={[
              { values: last30.map((r) => r.sleepHours * 10), color: 'var(--blue)', label: 'Sleep (h ×10)' },
              { values: last30.map((r) => r.focusScore), color: 'var(--green)', label: 'Focus score' },
            ]}
            xLabels={monthLabels}
          />
        </section>
        <section className="card">
          <h2>Discretionary spend</h2>
          <p className="muted small">Spikes cluster after short-sleep nights.</p>
          <TrendChart
            height={190}
            series={[{ values: last30.map((r) => r.discretionarySpend), color: 'var(--amber)', label: '$ / day', fill: true }]}
            xLabels={monthLabels}
            yFormat={(v) => `$${Math.round(v)}`}
          />
        </section>
      </div>
    </div>
  );
}
