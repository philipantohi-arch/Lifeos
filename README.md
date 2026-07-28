# ◉ LifeOS — The AI Operating System for Your Life

**One score. One coach. One intelligent system helping you become the best version of yourself every single day.**

LifeOS unifies your health, your finances, and your schedule into one intelligent platform that answers a single question every morning:

> **"What should I do next to improve my life the most?"**

And it answers that question *for you specifically*: your Life Score is anchored to **your own goals, your starting baseline, and your real capacity** — income, time, chronotype, age, situation — not to universal standards or other people. Every number traces to an auditable research base of official guidelines, meta-analyses, and landmark studies, gathered by a multi-agent web research sweep and adversarially fact-checked (90/91 claims confirmed).

## What's in this MVP

A fully working web app (React + TypeScript + Vite, zero runtime dependencies beyond React) with real engines behind every feature — not mocked screens. It ships with deterministic per-persona demo datasets that flow through the exact pipelines a production deployment would run against live wearable and financial data.

### 🏁 The individualized Life Score (the core algorithm)
Three pillars — **Health · Wealth · Productivity** — each blending:

- **Process (55%)**: did you do the controllable daily behaviors, measured against *your* personalized targets (sleep range for your age, chronotype-consistent bedtime, income-derived 50/30/20 budget, age-banded steps)? Process dominates because it's what you control today — and visible progress on controllables is the strongest known daily motivator (Amabile's progress principle).
- **Outcome (45%)**: are you on pace toward *your* goals from *your* baseline? Each goal (reach $40k · hit 175 lbs · sustain 15h/week deep work) is scored by pace along your own baseline→deadline line — never against anyone else (mastery-feedback research).

Pillar weights come from your stated priorities. Change a goal, a deadline, or a priority and the entire score recalibrates.

**Capacity & feasibility**: every reach goal is checked against what you can actually output — safe weight-loss bands (CDC, age-adjusted), sustainable savings rates (income − essentials, with slack), deep-work ceilings by work pattern and situation. When the math doesn't work, LifeOS says so and proposes the honest alternative (move the deadline or right-size the target) instead of letting you silently fail — because goals only motivate while they stay accepted and attainable (Locke & Latham).

### 🎲 Probability engine (Monte Carlo on YOUR data)
The most realistic simulation approach available without lying:

- **Bootstrap resampling of your own history** — your real week-to-week variability, not smooth average lines. This is an outside-view forecast by construction (the planning-fallacy antidote).
- **Reach goals**: hundreds of simulated futures → probability of hitting the goal by deadline, median completion date, and a 10th–90th percentile **fan chart**. Savings runs include realistic market volatility (~13%/yr around a 6% nominal drift).
- **Sustain goals**: block bootstrap (contiguous weeks, preserving autocorrelation) → odds your next 4-week average holds the target.
- **Cause and effect**: every recommendation and scenario maps to an intervention (bedtime discipline lifts short nights; meal prep cuts spend and shifts weight drift) that re-shapes the sampled distributions — so the app shows *"this action moves your odds on this goal from 46% → 68%."*

### ☀️ Morning Briefing (`Today`)
Life Score + delta and why it moved · a forecast banner ("today's #1 action moves your odds on 'College fund' from 46% to 68%") · goals-at-a-glance with pace bars · momentum chip · the day's actions ranked by simulated goal-odds impact, each with its reason and prediction.

### 🧭 Journey (built for years, not weeks)
The retention layer, built on what actually keeps people engaged long-term:

- **Auto-detected accomplishments** — streaks, personal records, milestones, and **comebacks** (a rough week followed by a strong one gets celebrated, never shamed — rewarding the return beat 53 other interventions in the largest exercise study ever run, Milkman et al., *Nature* 2021)
- **Streak repair tokens** — miss a day, spend a token, streak lives
- **Momentum** — execution trend vs two weeks ago, because direction beats level
- **Your proven potential** — your own best weeks on record vs now ("your best week averaged 7.9h — that wasn't luck")
- **Weekly review** — what happened, best day, and next week's 2–3 focuses
- **Adaptive micro-targets** — weekly bars auto-tune to your recent hit rate so they stay hard enough to matter, close enough to win

### 🧠 Pattern discovery (`Your Patterns`)
Correlation probes — including time-lagged ones — run across your unified history and rediscover *your* cause-and-effect statistically (each with Pearson r + sample size): you perform better after 7.5h+ sleep · you overspend after short sleep · meal prep transforms your week · alcohol taxes tomorrow's recovery · your weight follows your plate by about a week.

### 🔮 Future Simulator
Personalized what-if scenarios (commit to the cut · invest more · quit alcohol · sleep your range · hit your step target · meal prep) — each showing the Life Score trajectory *and* the Monte Carlo odds shift on your actual goals, with a fan chart for the primary affected goal.

### 👤 Personalization (`Profile`)
Age, sex, chronotype, life stage, work pattern, fitness level, income, situation (sick / travel / crunch / new baby / injury — each reshapes the whole day's coaching), pillar priorities — plus five demo personas (tech worker, ICU night nurse, new dad, retired teacher, student in finals) that exercise every adaptation live.

### 🔬 The Science
~50 citations rendered in-app: claim, exact figures, population, source, year, evidence strength, and how LifeOS uses each — plus an honest-limits statement. No invented numbers.

## Run it

```bash
npm install
npm run dev        # http://localhost:3000
npm run build      # typecheck + production bundle
```

## Architecture

```
src/
├── engine/              # Pure TypeScript, UI-independent — the product core
│   ├── types.ts         # DayRecord, UserProfile, Goal, PersonalTargets, forecasts
│   ├── researchBase.ts  # Citation registry: every number's source + usage
│   ├── personalize.ts   # Profile + research → personal targets & weights
│   ├── goals.ts         # Pace vs baseline→deadline, capacity, feasibility
│   ├── montecarlo.ts    # Bootstrap futures, fan charts, intervention odds
│   ├── lifeScore.ts     # Process (55%) + goal-pace outcome (45%) per pillar
│   ├── insights.ts      # Correlation probes → personal pattern discovery
│   ├── recommendations.ts # State + situation + goal-odds → ranked actions
│   ├── journey.ts       # Accomplishments, momentum, adaptive micro-targets
│   ├── briefing.ts      # Morning narrative (situation-aware)
│   └── simulator.ts     # Scenarios → trajectories + goal-odds + fan charts
├── data/
│   ├── generator.ts     # Profile-parameterized demo data w/ causal structure
│   ├── personas.ts      # Five demo lives with typed goals
│   └── connectors.ts    # Integration registry
├── components/          # ScoreRing, TrendChart, FanChart (hand-rolled SVG)
└── views/               # Today, Goals, Journey, Dashboard, Simulator,
                         # Patterns, Profile, Science, Integrations
```

The engine layer is pure and UI-free: swap `generateHistory()` for a real sync pipeline and everything downstream works unchanged.

```
UserProfile + Goals ──► personalize/goals ──► targets, capacity, pace
        │                                        │
        │              montecarlo ◄── your history (bootstrap)
        │                   │
        └──► every screen shows: score · odds · next best action
```

## Roadmap

- [ ] Live OAuth connectors (Oura, Plaid, Google Calendar) replacing the demo generator
- [ ] LLM-composed briefings and conversational coaching on top of the deterministic engines
- [ ] Causal inference upgrade (lagged regression, propensity matching) feeding better intervention effect sizes
- [ ] Goal templates + onboarding wizard (baseline capture from first 14 days)
- [ ] Push/email morning briefing delivery
- [ ] Mobile app shell

*Projections and insights are decision-support tools, not medical or financial advice.*
