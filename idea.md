# CompeteIQ — Product Idea & Development Reference

> AI-powered competitive intelligence platform for marketing teams.
> Track competitors, decode their strategy, and find your edge.

---

## 1. Problem

Marketing teams waste hours manually tracking competitors — checking websites, scrolling social feeds, screenshotting ads. By the time insights reach decision-makers they're stale. There's no single place to see what all your competitors are doing, how that's changing, and what it means for your positioning.

---

## 2. Solution

CompeteIQ automates competitive data collection across web, social, and paid media channels. It runs LLM analysis pipelines to extract KPIs, messaging themes, and strategic signals — then surfaces them in a clean dashboard with alerts when something important changes.

**Core value loop:**
1. User sets up their brand + competitors + KPIs (onboarding)
2. Automated jobs collect data on a schedule (daily / weekly / monthly)
3. Analysis pipeline computes KPIs, messaging themes, share of voice
4. Dashboard shows trends, alerts fire on significant changes
5. PDF reports for stakeholder sharing

---

## 3. Target Users

- **Primary:** Marketing managers at B2C / DTC brands (SMB to mid-market)
- **Secondary:** Growth/strategy leads, brand managers, agency strategists
- **Region focus:** Southeast Asia initially (configurable)

---

## 4. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (Python 3.12), async SQLAlchemy |
| Database | PostgreSQL 16 + pgvector (for future embedding search) |
| Job Queue | Temporal (durable workflows, retry logic) |
| LLM | OpenRouter API (default: `google/gemini-2.5-pro`) |
| Scraping | Apify (social) + Firecrawl (websites) |
| Auth | Clerk (JWT, org/user management) |
| Storage | AWS S3 (PDF exports, raw data) |
| Email | Resend |
| State management | Zustand (filter mode), TanStack Query (server state) |

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Next.js Frontend (apps/web)                            │
│  ├── /onboarding  → brand setup → competitors → KPIs   │
│  ├── /dashboard   → main view (daily/weekly/monthly)    │
│  ├── /competitor/[id] → deep dive per competitor        │
│  └── /settings    → alerts, schedule, notifications     │
└──────────────────────────┬──────────────────────────────┘
                           │ REST (axios, Bearer JWT)
┌──────────────────────────▼──────────────────────────────┐
│  FastAPI Backend (apps/api)                             │
│  ├── Auth: Clerk JWT → account_id scoping               │
│  ├── Routers: brands, competitors, dashboard, alerts,   │
│  │            kpi_config, collection_jobs, reports      │
│  └── Services: pdf_report, alert_delivery, email        │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
┌──────────────▼────────┐  ┌──────────▼──────────────────┐
│  PostgreSQL            │  │  Temporal Workers            │
│  ├── accounts/users    │  │  ├── FullCollectionWorkflow  │
│  ├── brand_profiles    │  │  ├── AnalysisWorkflow        │
│  ├── competitors       │  │  ├── SynthesisWorkflow       │
│  ├── kpi_configs       │  │  └── ScheduledWorkflow       │
│  ├── kpi_snapshots     │  │                              │
│  ├── page_snapshots    │  │  Activities:                 │
│  ├── social_posts      │  │  ├── collect_website         │
│  ├── ad_creatives      │  │  ├── collect_facebook        │
│  ├── message_themes    │  │  ├── collect_instagram       │
│  ├── website_changes   │  │  ├── collect_ad_library      │
│  ├── alerts            │  │  ├── data_hygiene            │
│  ├── alert_rules       │  │  ├── analysis_activities     │
│  ├── reports           │  │  └── synthesis_activities    │
│  └── collection_jobs   │  └──────────────────────────────┘
└───────────────────────-┘
```

---

## 6. Data Models

### Account & Users
- `Account` — org unit, has a plan (starter/growth/enterprise)
- `User` — linked to Clerk, has a role (owner/editor/viewer)

### Brand & Competitors
- `BrandProfile` — one per account, holds persona (JSONB: brand_voice, value_props, positioning)
- `Competitor` — many per brand, classified by tier: direct / indirect / aspirational / regional
  - Plan limits: starter=5, growth=10, enterprise=20

### Data Collection
- `PageSnapshot` — raw website scrapes (text + `extra_metadata` JSONB)
- `SocialPost` — FB/IG posts with engagement metrics
- `AdCreative` — active ads from Facebook Ad Library
- `MessageTheme` — LLM-extracted messaging patterns from all channels
- `WebsiteChange` — diffed website changes with significance classification

### Analytics
- `KpiSnapshot` — time-series KPI values per competitor (posting_frequency, engagement_rate, etc.)
- `ShareOfVoice` — brand vs competitor share per period
- `Alert` — triggered intelligence signals (posting_spike, new_campaign, message_shift, etc.)
- `AlertRule` — user-defined threshold rules
- `Report` — generated PDF reports with executive summary

### Config
- `KpiConfig` — per-brand: filter_mode (daily/weekly/monthly), which KPIs to track

---

## 7. Key Workflows

### Onboarding Flow (3 steps)
1. **Brand Setup** — name, website, industry, region, target audience → AI generates brand persona
2. **Competitor Setup** — manual add + AI discovery (Apify search + Gemini classification)
3. **KPI Config** — choose default pack or custom KPIs, set filter mode

### Data Collection Pipeline (Temporal)
```
FullCollectionWorkflow
  └── per competitor (max 5 concurrent):
      ├── collect_website_data   (Firecrawl → PageSnapshot)
      ├── collect_facebook_data  (Apify → SocialPost)
      ├── collect_instagram_data (Apify → SocialPost)
      ├── collect_ad_library     (Apify → AdCreative)
      └── run_data_hygiene       (deduplicate, quality flags)
```

### Analysis Pipeline (Temporal)
```
AnalysisWorkflow
  ├── run_social_analysis      (deterministic KPI computation)
  ├── run_paid_media_analysis  (LLM: campaign theme extraction)
  ├── run_website_change_analysis (diff + conditional LLM classification)
  └── run_messaging_analysis   (LLM: cross-channel messaging patterns)
```

### Synthesis Pipeline (Temporal)
```
SynthesisWorkflow
  ├── compute_share_of_voice   (deterministic)
  ├── generate_executive_summary (LLM: narrative summary)
  ├── detect_alerts            (rule-based + LLM anomaly detection)
  └── trigger_alert_delivery   (email via Resend)
```

---

## 8. Frontend Architecture

### Pages
| Route | Purpose |
|---|---|
| `/` | Landing / redirect |
| `/sign-in`, `/sign-up` | Clerk auth |
| `/onboarding/brand` | Step 1: brand setup |
| `/onboarding/competitors` | Step 2: competitor setup |
| `/onboarding/kpis` | Step 3: KPI config |
| `/dashboard` | Main dashboard (daily/weekly/monthly toggle) |
| `/dashboard/competitor/[id]` | Per-competitor deep dive |
| `/settings` | Alerts, schedule, notifications |

### Dashboard Card System
Dashboard is built on a card renderer (`card-renderer.tsx`) that maps card types to components:

| Card Type | Component | Data Source |
|---|---|---|
| `summary-strip` | `summary-strip.tsx` | `dashboard.summary` |
| `executive-summary` | `executive-summary.tsx` | `dashboard.executive_summary` |
| `kpi-trend-chart` | `kpi-trend-chart.tsx` | `dashboard.kpi_snapshots` |
| `competitor-card` | `competitor-card.tsx` | `dashboard.competitor_cards` |
| `messaging-themes` | `messaging-themes.tsx` | `dashboard.messaging_themes` |
| `share-of-voice-donut` | `share-of-voice-donut.tsx` | `dashboard.share_of_voice` |
| `content-format-mix` | `content-format-mix.tsx` | `dashboard.content_format_mix` |
| `paid-media-summary` | `paid-media-summary.tsx` | `dashboard.paid_media_summary` |
| `opportunity-gap` | `opportunity-gap.tsx` | `dashboard.opportunities` |
| `alert-feed` | `alert-feed.tsx` | `dashboard.alerts` |

Layout is computed in `dashboard-layout.ts` based on filter mode + available KPIs + competitors.

### State
- `filter-store.ts` (Zustand) — global filter mode (daily/weekly/monthly)
- `use-auth.ts` — Clerk auth + brand profile fetch
- TanStack Query — all API calls with stale time per filter mode

---

## 9. API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/users/me` | Upsert current user (post-Clerk login) |
| GET | `/api/users/me/brand` | Get user's brand profile |
| POST | `/api/brands` | Create brand profile |
| PATCH | `/api/brands/{id}` | Update brand profile |
| POST | `/api/brands/{id}/persona` | Generate AI brand persona |
| GET | `/api/brands/{id}/competitors` | List competitors |
| POST | `/api/brands/{id}/competitors` | Add competitor |
| PATCH | `/api/competitors/{id}` | Update competitor |
| DELETE | `/api/competitors/{id}` | Delete competitor |
| POST | `/api/brands/{id}/competitors/discover` | AI competitor discovery |
| GET | `/api/brands/{id}/kpi-config` | Get KPI config |
| POST | `/api/brands/{id}/kpi-config` | Save KPI config |
| GET | `/api/brands/{id}/dashboard` | Main dashboard data |
| GET | `/api/brands/{id}/dashboard/refresh` | Trigger data refresh |
| GET | `/api/brands/{id}/alerts` | List alerts |
| PATCH | `/api/alerts/{id}` | Mark read/dismissed |
| GET | `/api/brands/{id}/collection-jobs` | List collection jobs |
| POST | `/api/brands/{id}/collection-jobs` | Trigger manual collection |
| GET | `/api/brands/{id}/reports` | List reports |
| GET | `/api/brands/{id}/reports/{id}/pdf` | Download PDF |
| GET | `/api/brands/{id}/schedule` | Get collection schedule |
| PUT | `/api/brands/{id}/schedule` | Update schedule |
| GET | `/api/competitors/{id}/detail` | Full competitor detail view |

---

## 10. KPI Definitions

| KPI Key | Label | Source |
|---|---|---|
| `posting_frequency` | Posts this period | Social analysis |
| `engagement_rate` | Avg engagement rate | Social analysis |
| `top_content_format` | Top content format | Social analysis |
| `engagement_spike_count` | Posts with 3x avg engagement | Social analysis |
| `active_ads_count` | Active ad campaigns | Paid media analysis |
| `new_ad_creatives` | New ads this period | Paid media analysis |
| `share_of_voice` | Share of voice % | Synthesis |
| `message_shift_detected` | Messaging theme changes | Synthesis |

---

## 11. Alert Types

| Type | Trigger |
|---|---|
| `posting_spike` | Competitor posts 2x+ above their norm |
| `new_campaign` | New paid campaign detected |
| `message_shift` | Core messaging theme changed significantly |
| `pricing_change` | Website pricing page changed |
| `sov_move` | Share of voice shift > threshold |
| `engagement_spike` | Post goes viral (3x+ avg engagement) |
| `paid_pause` | Competitor stops running ads |

---

## 12. Current State (as of initial build)

### Done (scaffolded)
- [x] Monorepo structure (Turborepo)
- [x] FastAPI backend with all routers
- [x] All SQLAlchemy models
- [x] Clerk auth middleware
- [x] Temporal workflow scaffolding (collection + analysis + synthesis)
- [x] Scraping utilities (Apify + Firecrawl)
- [x] LLM utility (OpenRouter)
- [x] Dashboard page + card system
- [x] Onboarding flow (3 steps)
- [x] Competitor management UI
- [x] KPI config UI
- [x] Settings page
- [x] PDF report generation (WeasyPrint)
- [x] Alert delivery service (Resend)
- [x] Docker Compose (Postgres, Redis, Temporal)

### Not Done / Incomplete
- [ ] No `.env` file — API keys needed to actually run
- [ ] Dashboard API returns empty placeholder data (no real DB queries for cards)
- [ ] Collection jobs router — Temporal client not wired to actual trigger
- [ ] Competitor detail page — mostly placeholder
- [ ] No DB migrations run yet (alembic not executed)
- [ ] No tests written
- [ ] `packages/shared` is empty (shared types not extracted)
- [ ] No CI/CD pipeline
- [ ] Clerk webhook to auto-create user on signup not wired
- [ ] AI brand persona generation endpoint exists but not called from onboarding UI
- [ ] Alert rule management UI missing (rules table exists in DB)
- [ ] Report list / PDF download UI not connected to API

---

## 13. Development Priorities

### Phase A — Make it real (immediate)
1. Set up `.env` with actual API keys (Clerk, OpenRouter, Apify, Firecrawl)
2. Run `alembic upgrade head` to create DB schema
3. Wire dashboard API to return real data from DB
4. Wire collection job trigger to Temporal client
5. Connect onboarding UI to persona generation endpoint

### Phase B — Data flowing
1. Test full collection pipeline end-to-end (1 competitor, 1 channel)
2. Test analysis pipeline (social KPIs computed)
3. Test alert generation and email delivery

### Phase C — Polish & ship
1. Competitor detail page with real data
2. Alert rule management UI
3. Report history + PDF download UI
4. CI/CD (GitHub Actions → deploy)
5. Write integration tests for critical paths

---

## 14. Conventions

### API
- All routes are account-scoped via `AccountId` dependency (Clerk JWT → account_id)
- DB sessions use `get_db` dependency (async SQLAlchemy)
- All UUIDs, no integer PKs
- Pydantic schemas in `app/schemas/` separate from SQLAlchemy models in `app/models/`

### Frontend
- All API calls through `apps/web/src/lib/api.ts` (axios instance with auth interceptor)
- Server state: TanStack Query, client state: Zustand
- UI components: shadcn/ui in `components/ui/`, page-specific in `components/dashboard/`
- Types in `src/types/index.ts` mirror API schemas

### Naming
- Python: snake_case everywhere
- TypeScript: camelCase for variables, PascalCase for components/types
- DB columns: snake_case, mapped to snake_case in Pydantic schemas
- API paths: `/api/brands/{brand_id}/...` pattern throughout
