/**
 * Journey engine — the long-duration retention layer.
 *
 * Built on what the behavior-change evidence says keeps people engaged
 * for years, not weeks:
 *
 *   • Visible small wins beat distant outcomes (progress-principle) →
 *     auto-detected accomplishments and personal records.
 *   • Broken streaks are the #1 quit moment; rewarding the COMEBACK beat
 *     53 other interventions in the largest exercise study ever run
 *     (streak-recovery) → repair tokens + comeback detection, zero guilt.
 *   • Goals must stay attainable to stay motivating (goal-setting-theory)
 *     → adaptive weekly micro-targets tuned to the recent hit rate.
 *   • Momentum, not perfection: an EWMA of process adherence that shows
 *     direction — because trend is the honest unit of self-improvement.
 *   • Your own best weeks are the proof of your potential (potential gap)
 *     — comparison to self, never to others (baseline-relative-scoring).
 */

import type {
  Accomplishment,
  DayRecord,
  GoalAssessment,
  Momentum,
  PotentialGap,
  UserProfile,
  WeeklyReview,
} from './types';
import { deriveTargets } from './personalize';
import { processAdherence } from './lifeScore';

const mean = (v: number[]) => (v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0);

function fmtDate(iso: string): string {
  return new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  });
}

// ── Accomplishments: auto-detected wins from the data ─────────────────────

export function detectAccomplishments(records: DayRecord[], profile: UserProfile): Accomplishment[] {
  const t = deriveTargets(profile);
  const out: Accomplishment[] = [];

  // Longest sleep-in-range streak (and whether it's recent).
  let best = 0;
  let cur = 0;
  let bestEnd = 0;
  records.forEach((r, i) => {
    if (r.sleepHours >= t.sleepRange[0] - 0.2) {
      cur++;
      if (cur > best) {
        best = cur;
        bestEnd = i;
      }
    } else cur = 0;
  });
  if (best >= 4) {
    out.push({
      id: 'sleep-streak',
      date: records[bestEnd].date,
      emoji: '🌙',
      title: `${best}-night sleep streak`,
      detail: `${best} consecutive nights at or near your ${t.sleepRange[0]}–${t.sleepRange[1]}h range — your personal best this quarter.`,
      kind: 'streak',
    });
  }

  // Best deep-work week.
  let bestWeek = 0;
  let bestWeekEnd = 0;
  for (let i = 7; i <= records.length; i += 7) {
    const w = records.slice(i - 7, i).reduce((a, r) => a + r.deepWorkHours, 0);
    if (w > bestWeek) {
      bestWeek = w;
      bestWeekEnd = i - 1;
    }
  }
  if (bestWeek > 0) {
    out.push({
      id: 'deepwork-pr',
      date: records[bestWeekEnd].date,
      emoji: '🎯',
      title: `Deep-work PR: ${bestWeek.toFixed(1)}h in one week`,
      detail: 'Your most focused week on record. That capacity is yours — you\'ve already proven it.',
      kind: 'record',
    });
  }

  // Biggest single-day step count.
  const stepPR = records.reduce((a, r) => (r.steps > a.steps ? r : a), records[0]);
  if (stepPR.steps > t.stepsTarget * 1.3) {
    out.push({
      id: 'steps-pr',
      date: stepPR.date,
      emoji: '👟',
      title: `Step record: ${stepPR.steps.toLocaleString()} in a day`,
      detail: `${Math.round((stepPR.steps / t.stepsTarget) * 100)}% of your daily target in one day.`,
      kind: 'record',
    });
  }

  // Budget weeks won (spend under budget).
  let budgetWeeks = 0;
  for (let i = records.length; i >= 7; i -= 7) {
    const spend = records.slice(Math.max(0, i - 7), i).reduce((a, r) => a + r.discretionarySpend, 0);
    if (spend <= t.weeklyDiscretionary) budgetWeeks++;
  }
  if (budgetWeeks >= 3) {
    out.push({
      id: 'budget-wins',
      date: records[records.length - 1].date,
      emoji: '💰',
      title: `${budgetWeeks} budget weeks won`,
      detail: `${budgetWeeks} of the last ${Math.floor(records.length / 7)} weeks came in under your $${t.weeklyDiscretionary} discretionary budget.`,
      kind: 'milestone',
    });
  }

  // Comeback detection: a bad patch followed by recovery — celebrated,
  // never shamed (streak-recovery: rewarding the return works).
  const half = Math.floor(records.length / 2);
  for (let i = half; i < records.length - 10; i += 7) {
    const rough = records.slice(i - 7, i).filter((r) => r.sleepHours < t.sleepRange[0] - 0.7).length;
    const recovered = records.slice(i, i + 7).filter((r) => r.sleepHours >= t.sleepRange[0] - 0.2).length;
    if (rough >= 4 && recovered >= 5) {
      out.push({
        id: `comeback-${i}`,
        date: records[i + 6].date,
        emoji: '🔥',
        title: 'The comeback week',
        detail: 'A rough sleep week followed by five strong nights. Returning is the skill that actually predicts long-term success.',
        kind: 'comeback',
      });
      break;
    }
  }

  return out.sort((a, b) => b.date.localeCompare(a.date));
}

// ── Momentum ──────────────────────────────────────────────────────────────

export function computeMomentum(records: DayRecord[], profile: UserProfile): Momentum {
  const n = records.length - 1;
  const recent = processAdherence(records, profile, n);
  const prior = processAdherence(records, profile, Math.max(6, n - 14));
  const diff = recent - prior;
  const direction = diff > 2 ? 'rising' : diff < -2 ? 'falling' : 'steady';
  const narrative =
    direction === 'rising'
      ? `Your daily execution is up ${Math.abs(diff).toFixed(0)} points over two weeks — momentum is compounding in your favor.`
      : direction === 'falling'
        ? `Execution has slipped ${Math.abs(diff).toFixed(0)} points in two weeks. Not a crisis — one good day starts the turn.`
        : 'Execution is steady. Consistency is the quiet superpower — boring on any day, unbeatable over a year.';
  return {
    direction,
    recent: Math.round(recent),
    prior: Math.round(prior),
    narrative,
  };
}

// ── Potential gap: your own best weeks are the proof ──────────────────────

export function potentialGaps(records: DayRecord[], profile: UserProfile): PotentialGap[] {
  void profile;
  const out: PotentialGap[] = [];
  const weeks: DayRecord[][] = [];
  for (let i = records.length; i >= 7; i -= 7) weeks.push(records.slice(Math.max(0, i - 7), i));

  const bestBy = (f: (w: DayRecord[]) => number) => Math.max(...weeks.map(f));
  const currentBy = (f: (w: DayRecord[]) => number) => f(weeks[0]);

  const sleepF = (w: DayRecord[]) => mean(w.map((r) => r.sleepHours));
  const deepF = (w: DayRecord[]) => w.reduce((a, r) => a + r.deepWorkHours, 0);
  const stepF = (w: DayRecord[]) => mean(w.map((r) => r.steps));

  const sleepBest = bestBy(sleepF);
  const sleepNow = currentBy(sleepF);
  if (sleepBest - sleepNow > 0.4) {
    out.push({
      metricLabel: 'Sleep',
      currentAvg: `${sleepNow.toFixed(1)}h`,
      bestAvg: `${sleepBest.toFixed(1)}h`,
      message: `Your best week averaged ${sleepBest.toFixed(1)}h. That wasn't luck — it's your proven capacity.`,
    });
  }
  const deepBest = bestBy(deepF);
  const deepNow = currentBy(deepF);
  if (deepBest - deepNow > 2) {
    out.push({
      metricLabel: 'Deep work',
      currentAvg: `${deepNow.toFixed(1)}h/wk`,
      bestAvg: `${deepBest.toFixed(1)}h/wk`,
      message: `You've already done a ${deepBest.toFixed(1)}h week. The gap to your best self is ${(deepBest - deepNow).toFixed(1)}h — real, and closable.`,
    });
  }
  const stepBest = bestBy(stepF);
  const stepNow = currentBy(stepF);
  if (stepBest - stepNow > 1200) {
    out.push({
      metricLabel: 'Movement',
      currentAvg: `${Math.round(stepNow).toLocaleString()}/day`,
      bestAvg: `${Math.round(stepBest).toLocaleString()}/day`,
      message: `Best week: ${Math.round(stepBest).toLocaleString()} steps/day. Your own history is the evidence it fits your life.`,
    });
  }
  return out;
}

// ── Weekly review ─────────────────────────────────────────────────────────

export function buildWeeklyReview(
  records: DayRecord[],
  profile: UserProfile,
  assessments: GoalAssessment[],
  scoreHistory: number[],
): WeeklyReview {
  const t = deriveTargets(profile);
  const week = records.slice(-7);
  const prevWeek = records.slice(-14, -7);

  const scoreChange = scoreHistory[scoreHistory.length - 1] - scoreHistory[Math.max(0, scoreHistory.length - 8)];
  const bestDay = week.reduce((a, r) => (r.focusScore + r.recoveryScore > a.focusScore + a.recoveryScore ? r : a), week[0]);

  const recap: string[] = [];
  const sleepAvg = mean(week.map((r) => r.sleepHours));
  const sleepPrev = mean(prevWeek.map((r) => r.sleepHours));
  recap.push(
    `Sleep averaged ${sleepAvg.toFixed(1)}h (${sleepAvg >= sleepPrev ? '+' : ''}${(sleepAvg - sleepPrev).toFixed(1)}h vs last week).`,
  );
  const spend = week.reduce((a, r) => a + r.discretionarySpend, 0);
  recap.push(
    spend <= t.weeklyDiscretionary
      ? `Budget week won: $${Math.round(spend)} of $${t.weeklyDiscretionary}.`
      : `Spent $${Math.round(spend)} vs the $${t.weeklyDiscretionary} budget — worth one look at where.`,
  );
  const deep = week.reduce((a, r) => a + r.deepWorkHours, 0);
  recap.push(`${deep.toFixed(1)}h of deep work, ${week.filter((r) => r.didWorkout).length} workouts.`);

  const behind = assessments.filter((a) => a.paceRatio < 0.9);
  const nextFocus: string[] = [];
  if (behind.length) {
    const worst = behind.sort((a, b) => a.paceRatio - b.paceRatio)[0];
    nextFocus.push(`Close the gap on "${worst.goal.label}" — it's the furthest behind pace.`);
  }
  if (sleepAvg < t.sleepRange[0]) {
    nextFocus.push(`One earlier night than usual: your data says everything else follows sleep.`);
  }
  nextFocus.push('Protect the streaks you already have — maintenance beats heroics.');

  const end = new Date(records[records.length - 1].date + 'T00:00:00Z');
  const startD = new Date(end.getTime() - 6 * 86_400_000);
  const weekLabel = `${startD.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })} – ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })}`;

  return {
    weekLabel,
    scoreChange: Math.round(scoreChange),
    bestDay: `${fmtDate(bestDay.date)} — recovery ${bestDay.recoveryScore}, focus ${bestDay.focusScore}`,
    recap,
    nextFocus: nextFocus.slice(0, 3),
  };
}

// ── Adaptive weekly micro-targets ─────────────────────────────────────────

export interface MicroTarget {
  label: string;
  thisWeek: string;
  note: string;
}

/**
 * Tune this week's micro-targets to the recent hit rate so they sit in
 * the attainable-but-challenging band (goal-setting-theory): ease off
 * after a rough stretch, nudge up after a dominant one.
 */
export function adaptiveTargets(records: DayRecord[], profile: UserProfile): MicroTarget[] {
  const t = deriveTargets(profile);
  const last14 = records.slice(-14);

  const tune = (hitRate: number) => (hitRate < 0.45 ? 0.92 : hitRate > 0.85 ? 1.06 : 1.0);
  const note = (hitRate: number) =>
    hitRate < 0.45
      ? 'eased after a tough stretch — win this, then re-climb'
      : hitRate > 0.85
        ? 'nudged up — you\'ve outgrown the old bar'
        : 'holding steady in your challenge zone';

  const stepHit = last14.filter((r) => r.steps >= t.stepsTarget).length / 14;
  const sleepHit = last14.filter((r) => r.sleepHours >= t.sleepRange[0]).length / 14;
  const spendDays = last14.filter((r) => r.discretionarySpend <= t.weeklyDiscretionary / 7).length / 14;

  return [
    {
      label: 'Steps',
      thisWeek: `${Math.round((t.stepsTarget * tune(stepHit)) / 100) * 100} / day`,
      note: note(stepHit),
    },
    {
      label: 'Sleep floor',
      thisWeek: `${(t.sleepRange[0] * (tune(sleepHit) === 1.06 ? 1 : tune(sleepHit))).toFixed(1)}h+`,
      note: note(Math.min(sleepHit, 0.85)), // sleep floor never gets raised
    },
    {
      label: 'Daily spend',
      thisWeek: `≤ $${Math.round((t.weeklyDiscretionary / 7) * (2 - tune(spendDays)))}`,
      note: note(spendDays),
    },
  ];
}
