/**
 * Morning briefing composer.
 *
 * Assembles the daily narrative: current Life Score, why it moved,
 * today's highest-impact actions, and the freshest personal insights.
 */

import type { Briefing, DayRecord, LifeScoreResult, UserProfile } from './types';
import { computeLifeScore } from './lifeScore';
import { discoverInsights } from './insights';
import { recommendActions } from './recommendations';

function scoreNarrative(result: LifeScoreResult, today: DayRecord): string {
  const movers = [...result.pillars].sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
  const top = movers[0];
  const second = movers[1];

  const dir = (d: number) => (d > 0 ? 'up' : 'down');
  const parts: string[] = [];

  if (Math.abs(result.delta) < 0.5) {
    parts.push('Your Life Score is holding steady.');
    if (Math.abs(top.delta) >= 2 && second && Math.sign(second.delta) !== Math.sign(top.delta)) {
      parts.push(
        `Under the surface, ${top.label} moved ${dir(top.delta)} ${Math.abs(top.delta)} while ${second.label} offset it (${second.delta > 0 ? '+' : ''}${second.delta}).`,
      );
    }
  } else {
    parts.push(
      `Your Life Score is ${dir(result.delta)} ${Math.abs(result.delta).toFixed(1)} points, driven mostly by ${top.label} (${top.delta > 0 ? '+' : ''}${top.delta}).`,
    );
    if (second && Math.abs(second.delta) >= 1) {
      parts.push(`${second.label} also moved ${dir(second.delta)} ${Math.abs(second.delta)}.`);
    }
  }
  if (today.recoveryScore >= 85) {
    parts.push(`Recovery is excellent today (${today.recoveryScore}) — a green-light day.`);
  } else if (today.recoveryScore < 45) {
    parts.push(`Recovery is low (${today.recoveryScore}) — protect your energy today.`);
  }
  return parts.join(' ');
}

function greeting(name: string, hourUTC = 13): string {
  if (hourUTC < 12) return `Good morning, ${name}`;
  if (hourUTC < 18) return `Good afternoon, ${name}`;
  return `Good evening, ${name}`;
}

export function composeBriefing(records: DayRecord[], profile: UserProfile): Briefing {
  const result = computeLifeScore(records, profile);
  const today = records[records.length - 1];
  const insights = discoverInsights(records);
  const actions = recommendActions(records, profile);

  const date = new Date(today.date + 'T00:00:00Z');
  const dateLabel = date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  });

  return {
    dateLabel,
    greeting: greeting(profile.name),
    score: result.score,
    delta: result.delta,
    scoreNarrative: scoreNarrative(result, today),
    pillars: result.pillars,
    actions,
    insights: insights.slice(0, 3),
  };
}
