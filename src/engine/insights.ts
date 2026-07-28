/**
 * Personal pattern discovery.
 *
 * This is the "learns your cause-and-effect" layer. It scans the user's
 * unified history for statistically meaningful relationships — including
 * lagged ones (last night's sleep → today's spending) — and turns the
 * strongest into plain-language insights. Nothing here is hard-coded
 * advice: every insight is backed by a correlation computed from the
 * user's own data, with the r-value and sample size attached.
 */

import type { DayRecord, Insight, PillarKey } from './types';

function pearson(xs: number[], ys: number[]): number {
  const n = Math.min(xs.length, ys.length);
  if (n < 3) return 0;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0;
  let dx = 0;
  let dy = 0;
  for (let i = 0; i < n; i++) {
    const a = xs[i] - mx;
    const b = ys[i] - my;
    num += a * b;
    dx += a * a;
    dy += b * b;
  }
  const den = Math.sqrt(dx * dy);
  return den === 0 ? 0 : num / den;
}

/** Mean of `values` where mask is true vs. false — for effect sizes in copy. */
function splitMeans(records: DayRecord[], mask: (r: DayRecord) => boolean, value: (r: DayRecord) => number) {
  const a: number[] = [];
  const b: number[] = [];
  for (const r of records) (mask(r) ? a : b).push(value(r));
  const mean = (v: number[]) => (v.length ? v.reduce((x, y) => x + y, 0) / v.length : 0);
  return { yes: mean(a), no: mean(b), nYes: a.length, nNo: b.length };
}

function confidence(r: number, n: number): Insight['confidence'] {
  const strength = Math.abs(r) * Math.sqrt(n / 60);
  if (strength > 0.45) return 'strong';
  if (strength > 0.3) return 'moderate';
  return 'emerging';
}

interface PatternProbe {
  id: string;
  pillars: PillarKey[];
  /** Predictor series, may be lagged relative to outcome */
  x: (records: DayRecord[]) => number[];
  y: (records: DayRecord[]) => number[];
  /** Copy builder given r and the full history */
  build: (r: number, records: DayRecord[]) => { title: string; detail: string } | null;
  /** Expected sign; probes with the wrong sign are discarded */
  sign: 1 | -1;
}

const fmt = (v: number, digits = 0) => v.toFixed(digits);
const pct = (a: number, b: number) => Math.round(((a - b) / Math.max(b, 0.001)) * 100);

const PROBES: PatternProbe[] = [
  {
    id: 'sleep-focus',
    pillars: ['health', 'productivity'],
    sign: 1,
    x: (rs) => rs.map((r) => r.sleepHours),
    y: (rs) => rs.map((r) => r.focusScore),
    build: (r, rs) => {
      const s = splitMeans(rs, (d) => d.sleepHours > 7.5, (d) => d.focusScore);
      if (s.nYes < 5 || s.nNo < 5) return null;
      return {
        title: 'You perform better after 7.5+ hours of sleep',
        detail: `On nights you sleep more than 7.5h, next-day focus averages ${fmt(s.yes)} vs ${fmt(s.no)} otherwise — a ${pct(s.yes, s.no)}% lift (r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'sleep-spend',
    pillars: ['health', 'wealth'],
    sign: -1,
    x: (rs) => rs.map((r) => r.sleepHours),
    y: (rs) => rs.map((r) => r.discretionarySpend),
    build: (r, rs) => {
      const s = splitMeans(rs, (d) => d.sleepHours < 6.5, (d) => d.discretionarySpend);
      if (s.nYes < 5) return null;
      return {
        title: 'You overspend after poor sleep',
        detail: `On days following under 6.5h of sleep you spend $${fmt(s.yes)} on average vs $${fmt(s.no)} when rested — ${pct(s.yes, s.no)}% more impulse spending (r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'morning-workout-productivity',
    pillars: ['health', 'productivity'],
    sign: 1,
    x: (rs) => rs.map((r) => (r.workoutTime === 'morning' ? 1 : 0)),
    y: (rs) => rs.map((r) => r.focusScore),
    build: (r, rs) => {
      const s = splitMeans(rs, (d) => d.workoutTime === 'morning', (d) => d.focusScore);
      if (s.nYes < 5) return null;
      return {
        title: 'Morning workouts lead to your most productive days',
        detail: `Days that start with a workout average a focus score of ${fmt(s.yes)} vs ${fmt(s.no)} on other days (+${pct(s.yes, s.no)}%, r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'mealprep-nutrition',
    pillars: ['habits', 'health'],
    sign: 1,
    x: (rs) => rs.map((r) => (r.mealPrepped ? 1 : 0)),
    y: (rs) => rs.map((r) => r.nutritionScore),
    build: (r, rs) => {
      const s = splitMeans(rs, (d) => d.mealPrepped, (d) => d.nutritionScore);
      if (s.nYes < 5) return null;
      const takeout = splitMeans(rs, (d) => d.mealPrepped, (d) => (d.ateTakeout ? 1 : 0));
      return {
        title: 'Sunday meal prep transforms your week',
        detail: `Meal-prepped days score ${fmt(s.yes)} on nutrition vs ${fmt(s.no)} otherwise, and takeout drops from ${fmt(takeout.no * 100)}% to ${fmt(takeout.yes * 100)}% of days (r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'alcohol-recovery',
    pillars: ['health'],
    sign: -1,
    x: (rs) => rs.slice(0, -1).map((r) => r.alcoholDrinks),
    y: (rs) => rs.slice(1).map((r) => r.recoveryScore),
    build: (r, rs) => {
      const pairs = rs.slice(0, -1).map((d, i) => ({ drinks: d.alcoholDrinks, rec: rs[i + 1].recoveryScore }));
      const yes = pairs.filter((p) => p.drinks > 0).map((p) => p.rec);
      const no = pairs.filter((p) => p.drinks === 0).map((p) => p.rec);
      if (yes.length < 5) return null;
      const mean = (v: number[]) => v.reduce((a, b) => a + b, 0) / v.length;
      return {
        title: 'Alcohol quietly taxes your next day',
        detail: `Recovery the morning after drinking averages ${fmt(mean(yes))} vs ${fmt(mean(no))} after alcohol-free nights — a ${fmt(mean(no) - mean(yes))}-point recovery cost per occasion (r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'bedtime-energy',
    pillars: ['health', 'productivity'],
    sign: -1,
    // A record's bedtime is the night that produced that day's sleep and
    // energy, so this pair is same-index (already effectively lagged).
    x: (rs) => rs.map((r) => r.bedtime),
    y: (rs) => rs.map((r) => r.energy),
    build: (r, rs) => {
      const pairs = rs.map((d) => ({ bed: d.bedtime, e: d.energy }));
      const early = pairs.filter((p) => p.bed <= 22.75).map((p) => p.e);
      const late = pairs.filter((p) => p.bed > 23.5).map((p) => p.e);
      if (early.length < 5 || late.length < 5) return null;
      const mean = (v: number[]) => v.reduce((a, b) => a + b, 0) / v.length;
      return {
        title: 'Your energy is made the night before',
        detail: `Bedtimes before 10:45 PM give you ${mean(early).toFixed(1)}/10 energy the next day vs ${mean(late).toFixed(1)}/10 after nights past 11:30 PM (r = ${r.toFixed(2)}).`,
      };
    },
  },
  {
    id: 'social-mood',
    pillars: ['relationships'],
    sign: 1,
    x: (rs) => rs.map((r) => r.socialTouchpoints),
    y: (rs) => rs.map((r) => r.mood),
    build: (r, rs) => {
      const s = splitMeans(rs, (d) => d.socialTouchpoints > 0, (d) => d.mood);
      if (s.nYes < 5) return null;
      return {
        title: 'Connection is your mood multiplier',
        detail: `Days with at least one meaningful social touchpoint average ${s.yes.toFixed(1)}/10 mood vs ${s.no.toFixed(1)}/10 without (r = ${r.toFixed(2)}).`,
      };
    },
  },
];

export function discoverInsights(records: DayRecord[]): Insight[] {
  const insights: Insight[] = [];
  for (const probe of PROBES) {
    const xs = probe.x(records);
    const ys = probe.y(records);
    const r = pearson(xs, ys);
    if (Math.sign(r) !== probe.sign || Math.abs(r) < 0.15) continue;
    const copy = probe.build(r, records);
    if (!copy) continue;
    insights.push({
      id: probe.id,
      title: copy.title,
      detail: copy.detail,
      correlation: Math.round(r * 100) / 100,
      sampleSize: Math.min(xs.length, ys.length),
      confidence: confidence(r, records.length),
      pillars: probe.pillars,
    });
  }
  return insights.sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation));
}
