# ◉ LifeOS — The AI Operating System for Your Life

**One score. One coach. One intelligent system helping you become the best version of yourself every single day.**

LifeOS unifies every major aspect of your life — health, wealth, productivity, relationships, and habits — into one intelligent platform that answers a single question every morning:

> **"What should I do next to improve my life the most?"**

And it answers that question *for you specifically*: every target, recommendation, and simulation adapts to your age, sex, chronotype, life stage, work pattern, fitness level, income, priorities, and what's happening in your life right now — grounded in an auditable research base of official guidelines, meta-analyses, and landmark studies.

## What's in this MVP

A fully working web app (React + TypeScript + Vite, zero runtime dependencies beyond React) with real engines behind every feature — not mocked screens. It ships with a deterministic 120-day demo dataset that flows through the exact pipelines a production deployment would run against live wearable and financial data.

### ☀️ Morning Briefing (`Today`)
- Current **Life Score** (0–100) with today's delta
- A plain-language narrative of **why the score moved**, decomposed by pillar
- The **highest-impact actions** for today, ranked by predicted Life Score points, each with a forward-looking prediction and the data-grounded reason it was chosen ("Recovery score 91 is in your top decile")

### 🧮 Life Score engine
- Five weighted pillars: Health (30%), Wealth (20%), Productivity (20%), Relationships (15%), Habits & Goals (15%)
- Recency-weighted rolling windows, weekday-aware productivity scoring, budget-pace and goal-progress wealth scoring

### 🧠 Pattern discovery (`Your Patterns`)
The "learns your personal cause-and-effect" layer. Correlation probes — including **time-lagged** ones (last night's alcohol → today's recovery) — run across the unified history. Nothing is hard-coded advice: every insight shows its Pearson *r* and sample size, with confidence tiers (emerging → moderate → strong). The demo data embeds realistic causal structure, and the engine **rediscovers it statistically**:
- You perform better after 7.5+ hours of sleep
- You overspend after poor sleep
- Morning workouts lead to your most productive days
- Sunday meal prep transforms your week
- Alcohol quietly taxes your next day

### 🔮 Future Simulator
Ask "what if" and get a projected trajectory vs. your current path over 6 months to 5 years:
- *What happens if I lose 20 pounds?*
- *What if I invest an extra $500 every month?* (real compound-growth math, goal-arrival acceleration)
- *What if I stop drinking alcohol?*
- *What if I sleep eight hours every night?*
- *What if I walk 10,000 steps every day?*

Models include habit ramp-up curves, diminishing returns near pillar ceilings, and compounding dollar trajectories.

### 👤 Personalization engine (`Profile`)
The core answer to "different people, different situations":

- **Who you are** — age, sex, chronotype (lark/owl), life stage (student → retired), work pattern (9–5 / flexible / shift / not working), fitness level, income stability, and per-pillar priorities that reweight the Life Score itself.
- **Personal targets, not universal ones** — sleep range by NSF age band; step targets at the age-dependent mortality-benefit plateau (Paluch 2022 — 10,000 is *not* universal); bedtime and deep-work windows from chronotype synchrony research; strength + balance emphasis for 65+ (WHO); budgets from 50/30/20 on actual income; savings rates by life stage; sex-specific alcohol ceilings; emergency-fund sizing for variable income.
- **Situations** — sick, traveling, crunch week, new baby, injured. Each mode reshapes the day's coaching: the "neck check" rule replaces training targets when sick; anchor-sleep harm reduction replaces optimization for new parents; sleep floors and if-then peak-window plans for crunch weeks.
- **Shift-work aware** — regularity is scored against personal anchor-sleep clusters, not clock bedtimes; recommendations follow AASM shift-work strategies.
- **Behavior-change guardrails** — max 1–2 *new* habits pushed at once (multiple-behavior-change research), if-then phrasing (implementation intentions, d=0.65), autonomy-supportive tone (self-determination theory).
- **Five demo personas** — a 34-year-old tech worker, a 29-year-old ICU nurse on rotating nights, a 38-year-old new dad, a 67-year-old retired teacher, and a 21-year-old student in finals crunch — switch live and watch every screen recalibrate.

### 🔬 The Science
Every number in the engine traces to a citation registry (`src/engine/researchBase.ts`) rendered in-app: claim, exact figures, population, source, year, evidence strength (guideline / meta-analysis / RCT / cohort / expert), and *how LifeOS uses it* — plus an honest-limits statement. No invented numbers.

### 📊 Dashboard
30-day Life Score trend, sleep-vs-focus overlay, spending trend, and the key stats across all connected sources — each annotated with *your* target, not a generic one.

### 🔌 Integrations
Connector registry covering the production integration surface: Oura, Apple Health, Whoop, Garmin, Fitbit, Plaid (banks/cards), brokerages, Google Calendar, Todoist, Screen Time, MyFitnessPal — all normalized into one `DayRecord` schema so sleep, money, tasks, and relationships can finally talk to each other.

## Run it

```bash
npm install
npm run dev        # http://localhost:3000
npm run build      # typecheck + production bundle
```

## Architecture

```
src/
├── engine/            # Pure TypeScript, UI-independent — the product core
│   ├── types.ts       # Unified DayRecord schema, UserProfile, PersonalTargets
│   ├── researchBase.ts# Citation registry: every number's source + how it's used
│   ├── personalize.ts # Profile + research → personal targets & pillar weights
│   ├── lifeScore.ts   # Target-driven pillar scorers → weighted composite
│   ├── insights.ts    # Correlation probes → personal pattern discovery
│   ├── recommendations.ts  # State + targets + situation → ranked actions
│   ├── briefing.ts    # Composes the morning narrative (situation-aware)
│   └── simulator.ts   # Personalized what-if projections (ramps, compounding)
├── data/
│   ├── generator.ts   # Profile-parameterized demo data w/ causal structure
│   ├── personas.ts    # Five demo lives exercising different adaptations
│   └── connectors.ts  # Integration registry
├── components/        # ScoreRing, TrendChart (hand-rolled SVG, no chart deps)
└── views/             # Today, Dashboard, Simulator, Patterns, Profile,
                       # Science, Integrations
```

The engine layer is deliberately pure and UI-free: swap `generateHistory()` for a real sync pipeline and everything downstream — scoring, insights, recommendations, simulations — works unchanged. The flow is one-directional:

```
UserProfile ──► personalize.ts ──► PersonalTargets ──► every engine
     ▲                │
     │                └── every rule cites researchBase.ts
     └── edited live in the Profile view (or a future onboarding flow)
```

## Roadmap

- [ ] Live OAuth connectors (Oura, Plaid, Google Calendar) replacing the demo generator
- [ ] LLM-composed briefings and conversational coaching on top of the deterministic engines
- [ ] Per-user learned weights (personalized pillar importance)
- [ ] Causal inference upgrade (beyond correlation: lagged regression, propensity matching)
- [ ] Push/email delivery of the morning briefing
- [ ] Mobile app shell

*Projections and insights are decision-support tools, not medical or financial advice.*
