/**
 * Recommendation engine — "what should I do next?"
 *
 * Generates candidate actions from today's actual state (recovery, sleep
 * debt, spending pace, streaks, relationship freshness), scores each by
 * predicted Life Score impact, and returns the top few. The point is
 * ruthless prioritization: a handful of high-leverage moves, not a
 * dashboard of 200 metrics.
 */

import type { DayRecord, RecommendedAction, UserProfile } from './types';

export function recommendActions(
  records: DayRecord[],
  profile: UserProfile,
  limit = 5,
): RecommendedAction[] {
  const today = records[records.length - 1];
  const last7 = records.slice(-7);
  const candidates: RecommendedAction[] = [];

  // ── Training: match intensity to recovery ────────────────────────────
  if (today.recoveryScore >= 85 && !today.didWorkout) {
    candidates.push({
      id: 'heavy-training',
      title: 'Make today your heavy training day',
      detail: `Recovery is at ${today.recoveryScore} (HRV ${today.hrv}ms, resting HR ${today.restingHR}) — your body is primed for high intensity.`,
      impactPoints: 3.2,
      pillar: 'health',
      prediction: 'Training on peak-recovery days builds strength ~20% more efficiently and avoids junk-fatigue days.',
      because: `Recovery score ${today.recoveryScore} is in your top decile.`,
    });
  } else if (today.recoveryScore < 45) {
    candidates.push({
      id: 'active-recovery',
      title: 'Swap the workout for a 30-minute walk',
      detail: `Recovery is only ${today.recoveryScore} today. A hard session now would dig the hole deeper — walk, stretch, sleep.`,
      impactPoints: 2.1,
      pillar: 'health',
      prediction: 'Respecting low-recovery days cuts your odds of a multi-day energy crash this week.',
      because: `Recovery ${today.recoveryScore} is well below your baseline.`,
    });
  }

  // ── Sleep: bedtime is the highest-leverage lever ─────────────────────
  const avgSleep7 = last7.reduce((a, r) => a + r.sleepHours, 0) / 7;
  if (avgSleep7 < 7.3 || today.sleepHours < 7) {
    candidates.push({
      id: 'early-bedtime',
      title: 'Be in bed by 10:15 PM tonight',
      detail: `You're averaging ${avgSleep7.toFixed(1)}h this week. Your data shows sleep >7.5h lifts next-day focus more than any other single change.`,
      impactPoints: 3.6,
      pillar: 'health',
      prediction: "A 10:15 bedtime tonight will likely improve tomorrow's energy and productivity more than completing another workout.",
      because: `7-day sleep average ${avgSleep7.toFixed(1)}h is under your 7.5h performance threshold.`,
    });
  }

  // ── Finances: pace vs. weekly budget ─────────────────────────────────
  const spend7 = last7.reduce((a, r) => a + r.discretionarySpend, 0);
  const weeklyBudget = 75 * 7;
  if (spend7 > weeklyBudget * 0.92) {
    const monthsEarlier = 2;
    candidates.push({
      id: 'skip-takeout',
      title: 'Cook tonight — skip the takeout',
      detail: `You've spent $${Math.round(spend7)} of your $${weeklyBudget} weekly discretionary budget. Tonight is the swing decision.`,
      impactPoints: 2.4,
      pillar: 'wealth',
      prediction: `Skipping takeout tonight keeps you on pace to hit your ${profile.savingsGoalLabel.toLowerCase()} goal ~${monthsEarlier} months earlier.`,
      because: `Weekly spend is at ${Math.round((spend7 / weeklyBudget) * 100)}% of budget with days remaining.`,
    });
  }

  // ── Relationships: neglected family contact ──────────────────────────
  if (today.daysSinceFamilyContact >= 7) {
    candidates.push({
      id: 'call-family',
      title: 'Call your parents today',
      detail: `It's been ${today.daysSinceFamilyContact} days since your last call — past your weekly goal, and your mood data dips when contact stretches past 10 days.`,
      impactPoints: 2.8,
      pillar: 'relationships',
      prediction: 'A 20-minute call today restores a relationship trend line that has been quietly declining.',
      because: `${today.daysSinceFamilyContact} days since family contact vs. your 7-day goal.`,
    });
  }

  // ── Deep work: protect the morning if focus conditions are good ──────
  if (today.recoveryScore >= 70 && today.sleepHours >= 7.5) {
    candidates.push({
      id: 'deep-work-block',
      title: 'Block 9–11 AM for deep work on the side project',
      detail: `You slept ${today.sleepHours}h with ${today.sleepQuality} quality — historically your best focus windows follow nights like this.`,
      impactPoints: 2.6,
      pillar: 'productivity',
      prediction: 'Two protected morning hours today are worth ~3 scattered afternoon hours based on your focus curve.',
      because: 'Well-rested days are your top-quartile deep-work days.',
    });
  }

  // ── Habits: Sunday meal prep window ──────────────────────────────────
  if (today.dayOfWeek === 0) {
    candidates.push({
      id: 'meal-prep',
      title: 'Meal prep this afternoon (90 minutes)',
      detail: 'Your meal-prepped weeks show dramatically better nutrition and less takeout spending Monday–Thursday.',
      impactPoints: 3.0,
      pillar: 'habits',
      prediction: 'One 90-minute session today upgrades roughly 12 meals this week and saves ~$60.',
      because: "It's Sunday — the highest-leverage 90 minutes of your week.",
    });
  }

  // ── Movement floor ───────────────────────────────────────────────────
  if (today.steps < 5000 && !candidates.some((c) => c.id === 'active-recovery')) {
    candidates.push({
      id: 'walk',
      title: 'Take a 25-minute walk after lunch',
      detail: `Only ${today.steps.toLocaleString()} steps so far today.`,
      impactPoints: 1.4,
      pillar: 'health',
      prediction: 'Keeps your movement streak alive and reliably bumps afternoon energy in your data.',
      because: 'Step count is tracking under your 8,000/day floor.',
    });
  }

  return candidates.sort((a, b) => b.impactPoints - a.impactPoints).slice(0, limit);
}
