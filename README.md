# ◉ LifeOS — The AI Operating System for Your Life

**One score. One coach. One intelligent system helping you become the best version of yourself every single day.**

LifeOS unifies every major aspect of your life — health, wealth, productivity, relationships, and habits — into one intelligent platform that answers a single question every morning:

> **"What should I do next to improve my life the most?"**

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

### 📊 Dashboard
30-day Life Score trend, sleep-vs-focus overlay, spending trend, and the key stats across all connected sources.

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
│   ├── types.ts       # Unified DayRecord schema + all domain types
│   ├── lifeScore.ts   # Pillar scorers → weighted composite + history
│   ├── insights.ts    # Correlation probes → personal pattern discovery
│   ├── recommendations.ts  # Today's state → ranked high-leverage actions
│   ├── briefing.ts    # Composes the morning narrative
│   └── simulator.ts   # What-if projection models (ramps, compounding)
├── data/
│   ├── generator.ts   # Deterministic demo data with embedded causal structure
│   └── connectors.ts  # Integration registry
├── components/        # ScoreRing, TrendChart (hand-rolled SVG, no chart deps)
└── views/             # Today, Dashboard, Simulator, Patterns, Integrations
```

The engine layer is deliberately pure and UI-free: swap `generateHistory()` for a real sync pipeline and everything downstream — scoring, insights, recommendations, simulations — works unchanged.

## Roadmap

- [ ] Live OAuth connectors (Oura, Plaid, Google Calendar) replacing the demo generator
- [ ] LLM-composed briefings and conversational coaching on top of the deterministic engines
- [ ] Per-user learned weights (personalized pillar importance)
- [ ] Causal inference upgrade (beyond correlation: lagged regression, propensity matching)
- [ ] Push/email delivery of the morning briefing
- [ ] Mobile app shell

*Projections and insights are decision-support tools, not medical or financial advice.*
