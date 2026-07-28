/**
 * Recommendation engine — "what should I do next?"
 *
 * Candidate actions are generated from today's actual state — every
 * threshold personal (chronotype windows, income budgets, age-banded
 * steps, fitness-level training, situation modes) — then each candidate
 * that maps to a measurable intervention is run through the Monte Carlo
 * engine against the user's own goals. The result: actions ranked not by
 * generic "points" alone but by how much they move YOUR goal odds.
 *
 * Tone follows self-determination theory (sdt-motivation): explain why,
 * offer choices, never command. Behavior-change guardrail: at most
 * `simultaneousHabitLimit` NEW habits pushed at once (one-habit-at-a-time).
 */

import type {
  DayRecord,
  Goal,
  InterventionEffect,
  PersonalTargets,
  RecommendedAction,
  UserProfile,
} from './types';
import { deriveTargets, fmtHour } from './personalize';
import { oddsDelta } from './montecarlo';

interface Candidate extends RecommendedAction {
  /** New-habit asks are capped; state-response actions are not */
  isNewHabit?: boolean;
  /** Measurable effect if adopted, for goal-odds simulation */
  intervention?: InterventionEffect;
  /** Which goal metrics this action plausibly moves */
  affects?: Goal['metric'][];
}

function situationActions(profile: UserProfile, t: PersonalTargets, today: DayRecord): Candidate[] {
  switch (profile.situation) {
    case 'sick':
      return [
        {
          id: 'sick-rest',
          title: 'Rest is the workout today',
          detail: `Resting HR is ${today.restingHR} (elevated) and recovery is ${today.recoveryScore}. The "neck check" rule: with fever or below-the-neck symptoms, training makes illness longer, not shorter.`,
          impactPoints: 3.5,
          pillar: 'health',
          prediction: 'Resting now typically shortens illness by days versus pushing through.',
          because: 'ACSM sick-day guidance (the "neck check") + your elevated resting HR.',
        },
        {
          id: 'sick-hydrate',
          title: 'Hydrate and keep meals simple',
          detail: 'Fluids, easy protein, early night. Skip alcohol entirely — it suppresses immune response and recovery.',
          impactPoints: 2.0,
          pillar: 'health',
          prediction: 'Tomorrow-you gets a measurably better recovery score.',
          because: 'Illness recovery basics; alcohol measurably degrades overnight HRV.',
        },
      ];
    case 'new-baby':
      return [
        {
          id: 'baby-sleep-op',
          title: 'Sleep when the baby sleeps — even 40 minutes counts',
          detail: `You got ${today.sleepHours}h in fragments. Perfection isn't available right now; harm reduction is. A nap repays sleep debt better than pushing through.`,
          impactPoints: 3.4,
          pillar: 'health',
          prediction: "One recovered nap-hour today lifts tomorrow's patience and mood more than any other lever available to you.",
          because: 'New-parent sleep research: duration recovers over months — naps are the bridge (new-parent-sleep).',
          intervention: { sleepFloorLift: 0.6 },
          affects: ['sleepAvg'],
        },
        {
          id: 'baby-tagteam',
          title: 'Tag-team tonight: one protected 3–4h sleep block each',
          detail: 'Alternating one protected block each gives you both at least some consolidated sleep — better than both being half-awake all night.',
          impactPoints: 2.6,
          pillar: 'health',
          prediction: 'Protected blocks are the single best-evidenced sleep strategy for new parents.',
          because: 'The anchor-sleep principle from shift-work research, applied to newborn care.',
          intervention: { sleepFloorLift: 0.8 },
          affects: ['sleepAvg'],
        },
        {
          id: 'baby-walk',
          title: 'Stroller walk — sunlight plus steps, zero childcare needed',
          detail: `${today.steps.toLocaleString()} steps so far. Morning light also helps reset a baby-scrambled circadian rhythm.`,
          impactPoints: 1.8,
          pillar: 'health',
          prediction: "Daylight exposure today nudges tonight's (interrupted) sleep to be deeper.",
          because: 'Movement floor + circadian light anchoring, adapted to your season of life.',
          intervention: { stepsBoost: 2500 },
          affects: ['stepsAvg'],
        },
      ];
    case 'crunch':
      return [
        {
          id: 'crunch-sleep-floor',
          title: `Protect a hard sleep floor: lights out by ${fmtHour(t.bedtimeIdeal + 0.75)}`,
          detail: `Crunch mode taxes sleep first — you're at ${today.sleepHours}h. Two weeks of 6h nights produces the error rate of 1–2 all-nighters, and you stop noticing the deficit while it grows.`,
          impactPoints: 3.6,
          pillar: 'health',
          prediction: "Holding the floor tonight preserves tomorrow's peak hours — the ones that actually produce output.",
          because: 'Van Dongen dose-response RCT: chronic restriction accumulates without plateau — and without felt sleepiness.',
          intervention: { sleepFloorLift: 0.7 },
          affects: ['sleepAvg', 'deepWorkWeekly'],
        },
        {
          id: 'crunch-deepwork',
          title: `Put your hardest task at ${fmtHour(t.deepWorkWindow[0])}–${fmtHour(t.deepWorkWindow[1])}`,
          detail: `That's your chronotype's peak window (synchrony effect). An if-then plan — "when I sit down at ${fmtHour(t.deepWorkWindow[0])}, I open the hardest thing first" — roughly doubles follow-through.`,
          impactPoints: 3.0,
          pillar: 'productivity',
          prediction: 'Peak-window hours are worth ~1.5× your off-peak hours for hard cognitive work.',
          because: 'Chronotype synchrony effect + implementation intentions (d = 0.65 across 94 studies).',
          intervention: { deepWorkBoost: 0.8 },
          affects: ['deepWorkWeekly'],
        },
        {
          id: 'crunch-caffeine',
          title: `Last coffee by ${fmtHour(((t.bedtimeIdeal % 24) - 9 + 24) % 24)}`,
          detail: 'Caffeine has a ~5h half-life (varying 3–4× between people); a 2023 meta-analysis puts the safe cutoff for a full dose at ~9h before bed — a big dose at 6h out still cuts real sleep by over an hour.',
          impactPoints: 1.6,
          pillar: 'health',
          prediction: 'Same focus today, meaningfully better sleep tonight.',
          because: 'Gardiner 2023 meta-analysis (Sleep Med Reviews) + Drake caffeine-timing RCT.',
          intervention: { sleepFloorLift: 0.3 },
          affects: ['sleepAvg'],
        },
      ];
    case 'travel':
      return [
        {
          id: 'travel-anchor',
          title: 'Anchor your routine: same wake time, morning light, first meal on local time',
          detail: 'Adjustment runs ~1h/day eastward and ~1.5h/day westward; well-timed light can compress that substantially. Morning light and meal timing are the strongest levers you control.',
          impactPoints: 2.8,
          pillar: 'health',
          prediction: 'Anchoring today shaves a day off adjustment.',
          because: 'Jet-lag adaptation guidance; light is the dominant zeitgeber.',
        },
        {
          id: 'travel-walk',
          title: 'Explore on foot — steps and daylight do double duty',
          detail: `Travel days average far below your ${t.stepsTarget.toLocaleString()}-step target. Walking the destination fixes steps, light exposure, and sightseeing at once.`,
          impactPoints: 1.8,
          pillar: 'health',
          prediction: 'Keeps your movement streak alive without a gym.',
          because: 'Your age-banded step target (Paluch 2022, Lancet Public Health), travel-adapted.',
          intervention: { stepsBoost: 3000 },
          affects: ['stepsAvg'],
        },
      ];
    case 'injury':
      return [
        {
          id: 'injury-move',
          title: "Move what isn't injured",
          detail: 'Pain-free movement speeds recovery versus total rest — swap running for upper-body work, lifting for walking, whatever the injury allows.',
          impactPoints: 2.6,
          pillar: 'health',
          prediction: "Active recovery preserves your habit loop so there's no cold restart later.",
          because: 'Modern rehab consensus: load management beats immobilization for most soft-tissue injuries.',
        },
      ];
    default:
      return [];
  }
}

export function recommendActions(
  records: DayRecord[],
  profile: UserProfile,
  limit = 5,
): RecommendedAction[] {
  const t = deriveTargets(profile);
  const today = records[records.length - 1];
  const last7 = records.slice(-7);
  const candidates: Candidate[] = [];

  // ── Situation first: it reframes the whole day ───────────────────────
  candidates.push(...situationActions(profile, t, today));
  const situationBlocksTraining =
    profile.situation === 'sick' || profile.situation === 'injury' || profile.situation === 'new-baby';

  // ── Training: match intensity to recovery AND fitness level ─────────
  if (!situationBlocksTraining) {
    if (today.recoveryScore >= 85 && !today.didWorkout) {
      const byLevel = {
        beginner: {
          title: 'Great day for your full-body session',
          detail: `Recovery is at ${today.recoveryScore} (HRV ${today.hrv}ms, resting HR ${today.restingHR}). As a newer lifter, 2–3 full-body sessions a week with small weekly load bumps is the evidence-backed path.`,
          prediction: "Consistency now compounds: novice gains are the fastest you'll ever get.",
        },
        intermediate: {
          title: 'Make today your heavy training day',
          detail: `Recovery is at ${today.recoveryScore} (HRV ${today.hrv}ms, resting HR ${today.restingHR}) — your body is primed for high intensity.`,
          prediction: 'Training on peak-recovery days builds strength more efficiently and avoids junk-fatigue days.',
        },
        advanced: {
          title: 'Green light: schedule your top-set / PR attempt today',
          detail: `Recovery ${today.recoveryScore} with HRV ${today.hrv}ms is your top decile — exactly the day periodization saves peak efforts for.`,
          prediction: 'HRV-guided training beats fixed programming for strength and endurance gains in trained athletes.',
        },
      }[profile.fitnessLevel];
      candidates.push({
        id: 'train-hard',
        ...byLevel,
        impactPoints: 3.2,
        pillar: 'health',
        because: `Recovery ${today.recoveryScore} is in your top decile (ACSM progression + HRV-guided training).`,
        intervention: { workoutsBoost: 1, weightDriftShift: -0.1 },
        affects: ['workoutsWeekly', 'weightLbs'],
      });
    } else if (today.recoveryScore < 45) {
      candidates.push({
        id: 'active-recovery',
        title: 'Swap the workout for a 30-minute walk',
        detail: `Recovery is only ${today.recoveryScore} today. A hard session now digs the hole deeper — walk, stretch, sleep.`,
        impactPoints: 2.1,
        pillar: 'health',
        prediction: 'Respecting low-recovery days cuts your odds of a multi-day energy crash this week.',
        because: `Recovery ${today.recoveryScore} is well below your baseline.`,
      });
    }
    const strength7 = last7.filter((r) => r.didWorkout).length;
    if (profile.age >= 65 && strength7 < t.strengthSessionsWeekly && today.recoveryScore >= 55) {
      candidates.push({
        id: 'strength-balance',
        title: 'A strength + balance session today',
        detail: `${strength7} of your ${t.strengthSessionsWeekly} weekly sessions done. At ${profile.age}, strength work plus balance training is the highest-value exercise there is — WHO recommends 3+ balance days weekly specifically to prevent falls.`,
        impactPoints: 2.9,
        pillar: 'health',
        prediction: 'Maintained leg strength is the best single predictor of independent living in your 80s.',
        because: 'WHO 2020 guidelines for adults 65+ and PROT-AGE protein recommendations.',
        intervention: { workoutsBoost: 1 },
        affects: ['workoutsWeekly'],
      });
    }
  }

  // ── Sleep: personalized window, chronotype-aware ─────────────────────
  const avgSleep7 = last7.reduce((a, r) => a + r.sleepHours, 0) / 7;
  if (profile.situation === 'normal' && (avgSleep7 < t.sleepRange[0] || today.sleepHours < t.sleepRange[0] - 0.3)) {
    if (profile.workPattern === 'shift') {
      candidates.push({
        id: 'anchor-sleep',
        title: 'Hold your anchor-sleep window today',
        detail: `You're averaging ${avgSleep7.toFixed(1)}h across rotations (your range: ${t.sleepRange[0]}–${t.sleepRange[1]}h). Keeping the same 3–4h core window on both shift and off days is what actually protects shift-worker health — not chasing a "normal" bedtime.`,
        impactPoints: 3.6,
        pillar: 'health',
        prediction: 'A stable anchor window cuts the metabolic cost of rotation more than extra total sleep does.',
        because: 'Anchor-sleep strategy for shift workers; sleep regularity predicts outcomes beyond duration.',
        intervention: { sleepFloorLift: 0.6 },
        affects: ['sleepAvg'],
      });
    } else {
      candidates.push({
        id: 'early-bedtime',
        title: `Be in bed by ${fmtHour(t.bedtimeIdeal)} tonight`,
        detail: `You're averaging ${avgSleep7.toFixed(1)}h this week against your ${t.sleepRange[0]}–${t.sleepRange[1]}h range (${profile.age >= 65 ? 'NSF guidance for 65+' : 'NSF guidance for your age'}). ${fmtHour(t.bedtimeIdeal)} fits your ${profile.chronotype} chronotype rather than fighting it.`,
        impactPoints: 3.6,
        pillar: 'health',
        prediction: "Tonight's bedtime will likely improve tomorrow's energy and focus more than any workout would.",
        because: `7-day average ${avgSleep7.toFixed(1)}h is under your personal range floor (NSF age-band guidance).`,
        intervention: { sleepFloorLift: 0.6 },
        affects: ['sleepAvg', 'deepWorkWeekly'],
      });
    }
  }

  // ── Finances: pace vs the income-derived budget ──────────────────────
  const spend7 = last7.reduce((a, r) => a + r.discretionarySpend, 0);
  const savingsGoal = profile.goals.find((g) => g.metric === 'savingsBalance');
  if (spend7 > t.weeklyDiscretionary * 0.92) {
    candidates.push({
      id: 'skip-takeout',
      title: 'Cook tonight — skip the takeout',
      detail: `You've spent $${Math.round(spend7)} of your $${t.weeklyDiscretionary} weekly discretionary budget (30% of income, 50/30/20). Tonight is the swing decision.`,
      impactPoints: 2.4,
      pillar: 'wealth',
      prediction: savingsGoal
        ? `Holding budget this week keeps "${savingsGoal.label}" on pace.`
        : 'Holding budget this week keeps your savings plan on pace.',
      because: `Weekly spend at ${Math.round((spend7 / t.weeklyDiscretionary) * 100)}% of your personalized 50/30/20 budget.`,
      intervention: { spendMult: 0.93 },
      affects: ['savingsBalance'],
    });
  }
  if (profile.lifeStage === 'student' && profile.savingsBalance < 1000) {
    candidates.push({
      id: 'starter-fund',
      title: 'Auto-transfer $20 to your starter emergency fund',
      detail: `You're at $${profile.savingsBalance} of a $1,000 starter fund. Even $250–750 of buffer cuts the odds of missing a housing payment by ~28% — small automatic transfers beat sporadic large ones.`,
      impactPoints: 1.8,
      pillar: 'wealth',
      isNewHabit: true,
      prediction: 'A starter fund is the single best predictor of avoiding high-interest debt spirals.',
      because: 'CFPB starter-fund guidance + Urban Institute hardship data, scaled to student income.',
      intervention: { extraWeeklySavings: 20 },
      affects: ['savingsBalance'],
    });
  }

  // ── Deep work: chronotype-aligned block ──────────────────────────────
  if (
    profile.situation === 'normal' &&
    profile.lifeStage !== 'retired' &&
    today.recoveryScore >= 70 &&
    today.sleepHours >= t.sleepRange[0]
  ) {
    candidates.push({
      id: 'deep-work-block',
      title: `Block ${fmtHour(t.deepWorkWindow[0])}–${fmtHour(t.deepWorkWindow[1])} for your hardest work`,
      detail: `You slept ${today.sleepHours}h with quality ${today.sleepQuality}, and ${fmtHour(t.deepWorkWindow[0])}–${fmtHour(t.deepWorkWindow[1])} is your ${profile.chronotype}-chronotype peak window.`,
      impactPoints: 2.6,
      pillar: 'productivity',
      prediction: 'Chronotype-aligned hours outperform misaligned ones, especially for executive tasks.',
      because: 'Chronotype synchrony effect + a well-rested morning.',
      intervention: { deepWorkBoost: 0.7 },
      affects: ['deepWorkWeekly'],
    });
  }

  // ── Meal prep window (Sundays) ───────────────────────────────────────
  if (today.dayOfWeek === 0 && profile.situation === 'normal') {
    candidates.push({
      id: 'meal-prep',
      title: 'Meal prep this afternoon (90 minutes)',
      detail: 'Your meal-prepped weeks show better nutrition and less takeout spending Monday–Thursday. Frequent home cooking tracks with higher diet quality and lower food spend in national data.',
      impactPoints: 3.0,
      pillar: 'health',
      isNewHabit: true,
      prediction: 'One 90-minute session upgrades roughly 12 meals this week.',
      because: 'Your own meal-prep pattern + national home-cooking cohort evidence.',
      intervention: { spendMult: 0.94, weightDriftShift: -0.15 },
      affects: ['savingsBalance', 'weightLbs'],
    });
  }

  // ── Green exercise for flexible/retired schedules ────────────────────
  if (profile.lifeStage === 'retired' || profile.workPattern === 'flexible') {
    const activeOutside7 = last7.reduce((a, r) => a + (r.steps > t.stepsTarget * 0.8 ? 30 : 10), 0);
    if (activeOutside7 < 120) {
      candidates.push({
        id: 'nature-dose',
        title: "Take today's walk somewhere green",
        detail: '120+ minutes/week in nature is the threshold associated with significantly better self-reported health and wellbeing — and it stacks with your step goal.',
        impactPoints: 1.6,
        pillar: 'health',
        isNewHabit: true,
        prediction: 'Same walk, measurably better mood — nature exposure adds benefit beyond exercise alone.',
        because: 'White et al. 2019 nature-dose threshold (Scientific Reports).',
        intervention: { stepsBoost: 2000 },
        affects: ['stepsAvg'],
      });
    }
  }

  // ── Movement floor (age-adjusted) ────────────────────────────────────
  if (
    today.steps < t.stepsTarget * 0.55 &&
    !candidates.some((c) => c.id === 'active-recovery' || c.id === 'baby-walk' || c.id === 'travel-walk')
  ) {
    candidates.push({
      id: 'walk',
      title: 'Take a 25-minute walk after lunch',
      detail: `${today.steps.toLocaleString()} steps so far against your ${t.stepsTarget.toLocaleString()}/day target (the mortality-benefit plateau for your age band — not a generic 10,000).`,
      impactPoints: 1.4,
      pillar: 'health',
      prediction: 'Keeps your movement streak alive and reliably bumps afternoon energy.',
      because: 'Step target personalized by age (Paluch 2022, Lancet Public Health).',
      intervention: { stepsBoost: 2500 },
      affects: ['stepsAvg'],
    });
  }

  // ── Alcohol: sex-specific weekly ceiling ─────────────────────────────
  const drinks7 = last7.reduce((a, r) => a + r.alcoholDrinks, 0);
  if (drinks7 > t.maxDrinksWeekly) {
    candidates.push({
      id: 'alcohol-reset',
      title: 'Make tonight alcohol-free',
      detail: `${drinks7} drinks this week vs your ${t.maxDrinksWeekly}-drink guideline ceiling. Your own data shows each drinking night costs measurable next-day recovery.`,
      impactPoints: 2.2,
      pillar: 'health',
      prediction: 'Tonight alcohol-free likely returns +8–12 recovery points tomorrow.',
      because: `Weekly total exceeds the ${profile.sex === 'female' ? 'female' : 'male'} low-risk ceiling (Canada 2023 guidance; alcohol–sleep field studies).`,
      intervention: { sleepFloorLift: 0.3, spendMult: 0.97 },
      affects: ['sleepAvg', 'savingsBalance'],
    });
  }

  // ── Rank: goal-odds delta first, generic impact second ───────────────
  // Each candidate with a measurable intervention is simulated against the
  // user's own goals; the displayed odds are the real ranking signal.
  for (const c of candidates) {
    if (!c.intervention || !c.affects) continue;
    let best: { goal: Goal; from: number; to: number } | null = null;
    for (const goal of profile.goals) {
      if (!c.affects.includes(goal.metric)) continue;
      const d = oddsDelta(goal, records, profile, c.intervention);
      if (!best || d.to - d.from > best.to - best.from) best = { goal, ...d };
    }
    if (best && best.to - best.from > 0.005) {
      c.goalOdds = { goalLabel: best.goal.label, from: best.from, to: best.to };
      // Bonus capped so a binary odds flip can't drown every other signal.
      c.impactPoints = Math.round((c.impactPoints + Math.min(best.to - best.from, 0.35) * 8) * 10) / 10;
    }
  }

  const sorted = candidates.sort((a, b) => b.impactPoints - a.impactPoints);
  const out: Candidate[] = [];
  let newHabits = 0;
  for (const c of sorted) {
    if (c.isNewHabit) {
      if (newHabits >= t.simultaneousHabitLimit) continue;
      newHabits++;
    }
    out.push(c);
    if (out.length >= limit) break;
  }
  return out;
}
