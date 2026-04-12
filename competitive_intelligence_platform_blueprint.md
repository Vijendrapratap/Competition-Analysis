# Competitive Intelligence Platform — Full Product Blueprint

\---

## Executive Summary

This document is the complete product blueprint for a multi-agent competitive intelligence platform. It covers the end-to-end user flow, page-by-page wireframes, database schema, agent architecture, and the filter-driven KPI system (Daily / Weekly / Monthly) that makes output actionable for marketing managers and executives alike. The platform is designed around one core principle: reduce the distance between raw competitive signals and a decision a team can act on today.

\---

## 1\. Product Philosophy

Most competitive intelligence tools fail at the last mile. They collect data but do not contextualise it. They show charts but do not answer "what changed and why does it matter?" This platform solves that by anchoring every insight to the user's own brand persona, the competitor tier structure they defined, and the time window they care about right now.

The filter system (Daily / Weekly / Monthly) is not just a date range — it drives which KPI pack surfaces, what signal thresholds trigger alerts, and how the report language is framed. A daily user is a social media manager looking for tactical shifts. A weekly user is a marketing lead reviewing campaign performance. A monthly user is a CMO or brand strategist reviewing positioning and share of voice. Each mode is a different product experience built on the same data layer.

\---

## 2\. Full User Flow

```
\[Landing / Sign-up]
        ↓
\[Step 1: Brand Setup]
  → Enter brand name, website, socials, region, category
  → Brand Persona Agent generates draft persona + ICP
  → User reviews and edits persona
  → Save Brand Profile
        ↓
\[Step 2: Competitor Setup]
  → Manual entry: website, Facebook, Instagram, LinkedIn, YouTube, Ad Library
  → AI Discovery: platform suggests competitors by industry + region + audience
  → User reviews, approves, and tiers competitors (Direct / Indirect / Aspirational / Regional)
  → Collect button → agents begin async data collection
        ↓
\[Step 3: KPI \& Filter Selection]
  → User selects time filter: Daily / Weekly / Monthly
  → Platform recommends KPI pack based on filter + industry
  → User can customise: add, remove, reorder KPIs
  → Save KPI Config
        ↓
\[Step 4: Dashboard]
  → Executive summary cards
  → Trend charts by KPI
  → Competitor cards with breakdown
  → Messaging and content panels
  → Paid media panel
  → Opportunity and gap panel
  → Alert feed (meaningful movement only)
  → Export: PDF report / slides
        ↓
\[Ongoing: Alerts \& Refresh]
  → Agents re-run on schedule (daily / weekly / monthly)
  → Alert triggers on threshold breaches
  → Dashboard refreshes automatically
```

\---

## 3\. Page-by-Page Wireframe

\---

### Page 1 — Brand Setup

**Purpose:** Establish the user's brand identity and generate a brand persona that will be used as context for all agents, comparisons, and report language.

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Progress: \[1 Brand ● 2 Competitors ○ 3 KPIs ○] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Tell us about your brand                                       │
│  ─────────────────────────────────────────────────────────────  │
│  Brand Name         \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Website URL        \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Industry / Category \[Dropdown: FMCG / Tech / Retail / etc.]   │
│  Target Region      \[Dropdown: India / SEA / Global / etc.]    │
│  Target Audience    \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│                                                                 │
│  Your social profiles (optional but recommended)               │
│  Facebook Page URL  \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Instagram Handle   \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  LinkedIn Page      \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  YouTube Channel    \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│                                                                 │
│  \[→ Generate Brand Persona]                                     │
│                                                                 │
├─ AGENT OUTPUT (shown after generation) ─────────────────────── │
│                                                                 │
│  ✦ Brand Persona Draft                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Brand Voice:     Bold, conversational, aspirational       │ │
│  │ Core Audience:   Urban millennials, 25–35, tier 1 cities  │ │
│  │ Value Props:     Affordable quality, fast delivery        │ │
│  │ Positioning:     Mass premium, challenger to X and Y      │ │
│  │ Key Channels:    Instagram, YouTube, Search               │ │
│  │ Content Style:   Short-form video, UGC, seasonal offers   │ │
│  └───────────────────────────────────────────────────────────┘ │
│  \[Edit Persona ✏]          \[Save \& Continue →]                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**States:**

* Initial empty form
* Generating (spinner, progress label "Analysing your brand...")
* Persona ready (editable fields, save CTA)
* Saved (confirmation toast, progress step marked complete)

\---

### Page 2 — Competitor Setup

**Purpose:** Build a tracked competitor list through manual input and AI-assisted discovery. Tier them for report segmentation.

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Progress: \[1 Brand ✓ 2 Competitors ● 3 KPIs ○] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Add your competitors                                           │
│                                                                 │
│  \[+ Add manually]    \[🔍 Find my competitors]                   │
│                                                                 │
│  ── Manual Entry Panel ──────────────────────────────────────  │
│  Brand Name         \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Website URL        \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Facebook Page      \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Instagram Handle   \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  LinkedIn Page      \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  YouTube Channel    \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Ad Library URL     \[\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_]                  │
│  Competitor Tier    \[Direct ▾ / Indirect / Aspirational /      │
│                      Regional]                                  │
│  \[Add Competitor]                                               │
│                                                                 │
│  ── AI Discovery Panel (triggered by "Find my competitors") ── │
│  ✦ Based on your brand profile, here are suggested competitors: │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │ Brand A      │ Brand B      │ Brand C      │ Brand D     │  │
│  │ Direct       │ Direct       │ Indirect     │ Regional    │  │
│  │ \[✓ Add]      │ \[✓ Add]      │ \[✓ Add]      │ \[✓ Add]     │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
│  \[Load more suggestions]                                        │
│                                                                 │
│  ── Your Competitor List ─────────────────────────────────────  │
│  ┌────────────┬────────────┬──────────────────┬────────────┐   │
│  │ Name       │ Tier       │ Channels Linked  │ Actions    │   │
│  ├────────────┼────────────┼──────────────────┼────────────┤   │
│  │ Brand A    │ Direct     │ Web IG FB YT      │ Edit | ✕  │   │
│  │ Brand B    │ Direct     │ Web IG            │ Edit | ✕  │   │
│  └────────────┴────────────┴──────────────────┴────────────┘   │
│                                                                 │
│  \[← Back]                   \[Collect Data \& Continue →]        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Background:** When "Collect Data \& Continue" is pressed, all source collection agents are dispatched asynchronously. The user moves to the KPI page immediately while collection runs in the background.

\---

### Page 3 — KPI \& Filter Selection

**Purpose:** Let users choose their time window and the KPIs they want to track. The filter is the primary driver of what gets shown in the dashboard.

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Progress: \[1 Brand ✓ 2 Competitors ✓ 3 KPIs ●] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  How often do you want to monitor competitors?                  │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                   │
│  │  Daily   │   │ Weekly   │   │ Monthly  │                   │
│  │ Tactical │   │ Campaign │   │Strategic │                   │
│  │ signals  │   │ review   │   │ overview │                   │
│  └──────────┘   └──────────┘   └──────────┘                   │
│  (selected = teal highlight)                                    │
│                                                                 │
│  ── Recommended KPI Pack for \[Weekly] + \[FMCG] ──────────────  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │  ✓ Posting frequency (posts/week)           │               │
│  │  ✓ Engagement rate (avg per post)           │               │
│  │  ✓ Top content format mix (video/image/text)│               │
│  │  ✓ Active paid campaigns (count + themes)   │               │
│  │  ✓ Key messaging themes (top 3)             │               │
│  │  ✓ Follower growth delta (%)                │               │
│  │  + New offer / promotion activity           │               │
│  │  + Share of voice (estimated)               │               │
│  └─────────────────────────────────────────────┘               │
│  \[Customise KPIs ✏]                                            │
│                                                                 │
│  ── Customise (expanded panel) ──────────────────────────────  │
│  Drag to reorder. Toggle on/off.                                │
│  \[Posting freq ✓] \[Eng rate ✓] \[Reach proxy ○] \[Ad count ✓]  │
│  \[SOV ✓] \[Messaging ✓] \[Content format ✓] \[CTA type ○] ...   │
│                                                                 │
│  \[← Back]                  \[Generate Dashboard →]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

\---

### KPI Packs by Filter

The filter selection is not cosmetic — it drives which KPI pack defaults, what alert thresholds trigger, and how report language is framed.

**Daily KPI Pack — Tactical signals**

|KPI|What it tracks|
|-|-|
|New posts published today|Volume and format (video, image, reel, story)|
|Engagement on latest posts|Likes, comments, shares within 24h|
|Active ad creatives (new/paused)|New campaign launches or paused campaigns|
|Mention spikes|Sudden increase in brand mentions or hashtag use|
|Price change detection|Website/landing page pricing or offer changes|
|New blog or content published|SEO and editorial activity|

**Weekly KPI Pack — Campaign review**

|KPI|What it tracks|
|-|-|
|Posting frequency (posts/week)|Total posts across channels|
|Engagement rate (avg per post)|Engagement / reach or followers ratio|
|Top content formats this week|% video vs image vs carousel vs text|
|Active paid campaigns (themes)|Number and headline themes of running ads|
|Key messaging themes (top 3)|Most repeated value props or CTAs|
|Follower growth delta (%)|Week-over-week growth per channel|
|New offer or promotion activity|Discounts, seasonal campaigns, giveaways|
|Share of voice (estimated)|Brand mentions vs competitor mentions in category|

**Monthly KPI Pack — Strategic overview**

|KPI|What it tracks|
|-|-|
|Share of voice (monthly)|Position in category conversation|
|Positioning shift|Changes in core messaging or audience language|
|Channel investment mix|Relative activity across paid, organic, web, email|
|Content pillar analysis|Recurring themes, topic clusters, narrative arcs|
|Audience sentiment proxy|Comment tone analysis, top reactions|
|Campaign lifecycle|Start/end dates, longevity, format evolution|
|SEO and web traffic proxies|Keyword moves, new pages, domain authority signals|
|Competitive whitespace|Underserved topics, channels, or audience segments|

\---

### Page 4 — Main Dashboard

**Purpose:** Single-screen competitive intelligence view for executives and marketing teams. Uses the saved filter and KPI config to present findings in plain language with supporting charts.

**Layout:**

```
┌──────────────────────────────────────────────────────────────────────┐
│ HEADER: \[Brand Logo] CompeteIQ  |  \[Daily] \[Weekly●] \[Monthly]  |  🔔│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ── Summary Strip ────────────────────────────────────────────────── │
│  \[5 Competitors tracked] \[3 Channels monitored] \[2 New alerts] \[↑1  │
│   Rising threat: Brand C]                                            │
│                                                                      │
│ ── Executive Summary (AI-generated, plain language) ──────────────  │
│  "This week Brand A increased posting frequency by 40% on Instagram  │
│   and launched a new UGC campaign. Brand B appears to have paused    │
│   paid ads. Brand C is gaining traction in the 18–25 segment with   │
│   reels. Your share of voice in the category is estimated at 22%."  │
│                                                                      │
│ ── KPI Trend Charts (inline, 2-column grid) ──────────────────────  │
│  \[Posting Frequency — Line chart, last 4 weeks per competitor]      │
│  \[Engagement Rate — Bar chart, this week vs last week]              │
│  \[Active Ads — Timeline chart, per competitor]                       │
│  \[Share of Voice — Donut chart, category conversation share]         │
│                                                                      │
│ ── Competitor Cards ───────────────────────────────────────────────  │
│  ┌────────────────────────────────────┐  ┌────────────────────────┐ │
│  │ Brand A (Direct)                   │  │ Brand B (Direct)       │ │
│  │ Posts/wk: 14 ↑ | Eng rate: 3.2%   │  │ Posts/wk: 6 ↓         │ │
│  │ Top format: Reels (70%)            │  │ Paid: Paused           │ │
│  │ Top message: "Fastest delivery"    │  │ Top message: "Trust"   │ │
│  │ \[View full profile →]              │  │ \[View full profile →]  │ │
│  └────────────────────────────────────┘  └────────────────────────┘ │
│                                                                      │
│ ── Messaging \& Content Panel ─────────────────────────────────────  │
│  Top 5 messaging themes this week (across all competitors):         │
│  1. Speed / Fast delivery (3 brands)                                │
│  2. Price leadership (2 brands)                                      │
│  3. Sustainability / Green (1 brand, new this week ⚡)               │
│  4. Celebrity association (2 brands)                                 │
│  5. User reviews / Social proof (4 brands)                           │
│                                                                      │
│ ── Paid Media Panel ──────────────────────────────────────────────  │
│  Active campaigns this week: 8 across 4 competitors                 │
│  Common hooks: Discount + urgency | Lifestyle aspirational           │
│  New creatives: Brand A (3 new), Brand C (5 new)                    │
│  \[View ad gallery →]                                                 │
│                                                                      │
│ ── Opportunity \& Gap Panel ───────────────────────────────────────  │
│  ⚡ No competitor is consistently posting on LinkedIn in your space  │
│  ⚡ Long-form content (blogs) is underused — only 1 competitor active │
│  ⚡ Sustainability messaging is emerging — Brand C moved first        │
│                                                                      │
│ ── Alert Feed ─────────────────────────────────────────────────────  │
│  🔴 Brand C: +180% reel views this week (unusual spike)             │
│  🟡 Brand A: Changed homepage headline — new offer language          │
│  🟢 Brand B: Paused all paid ads — potential budget reallocation     │
│                                                                      │
│ \[Export PDF Report]  \[Export to Slides]  \[Share Dashboard link]     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

\---

### Page 5 — Competitor Deep Dive (Drill-through)

Accessed from any competitor card. Shows full profile for one competitor.

```
┌──────────────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard   |   Brand A — Full Profile   |  \[Weekly ●]    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Overview: Website | Facebook | Instagram | LinkedIn | YouTube | Ads  │
│ (tabs for channel drill-down)                                        │
│                                                                      │
│ ── Social Performance ─────────────────────────────────────────────  │
│  Followers: 420K (+2.1% this week)                                   │
│  Posts this week: 14 (↑ from 10 last week)                           │
│  Avg engagement rate: 3.2% (category avg: 1.8%)                      │
│  Best performing post: \[thumbnail + caption + stats]                 │
│                                                                      │
│ ── Content Breakdown ──────────────────────────────────────────────  │
│  Format mix: Reels 70% | Carousels 20% | Static 10%                 │
│  Posting times: Tue/Thu/Sat 6–8pm                                    │
│  Content pillars: Product demos | Offers | Lifestyle | UGC           │
│                                                                      │
│ ── Messaging Breakdown ────────────────────────────────────────────  │
│  Repeated claims: "Fastest delivery in India" | "Quality guaranteed" │
│  CTA patterns: "Order now" 60% | "Shop the look" 30%                 │
│  Audience language: casual, emoji-heavy, question hooks              │
│                                                                      │
│ ── Paid Activity ──────────────────────────────────────────────────  │
│  Active campaigns: 3  |  New creatives this week: 3                  │
│  Campaign themes: Festive sale | New product launch                  │
│  \[View all ads →]                                                    │
│                                                                      │
│ ── Website \& SEO Signals ──────────────────────────────────────────  │
│  New pages published: 2 (blog + landing page)                        │
│  Pricing page changes: None detected                                 │
│  Top organic keywords (estimated): \[list]                            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

\---

### Page 6 — Alerts \& Settings

* Alert rules: set thresholds per KPI per competitor (e.g., "alert me if any competitor increases posting by >30% in a week")
* Notification channels: email digest, in-app, Slack webhook
* Data refresh schedule: aligned to chosen filter (daily → daily crawl, weekly → weekly crawl, monthly → monthly crawl)
* User management (multi-seat): owner, editor, viewer roles
* Brand profile and competitor list management

\---

## 4\. Database Schema

### Core Tables

```sql
-- Accounts and users
accounts (
  id UUID PRIMARY KEY,
  name TEXT,
  plan TEXT,  -- 'starter' | 'growth' | 'enterprise'
  created\_at TIMESTAMP
)

users (
  id UUID PRIMARY KEY,
  account\_id UUID REFERENCES accounts(id),
  name TEXT,
  email TEXT UNIQUE,
  role TEXT,  -- 'owner' | 'editor' | 'viewer'
  created\_at TIMESTAMP
)

-- Brand profiles
brand\_profiles (
  id UUID PRIMARY KEY,
  account\_id UUID REFERENCES accounts(id),
  name TEXT,
  website TEXT,
  industry TEXT,
  target\_region TEXT,
  target\_audience TEXT,
  persona JSONB,  -- AI-generated + user-edited persona blob
  social\_profiles JSONB,  -- {facebook, instagram, linkedin, youtube}
  created\_at TIMESTAMP,
  updated\_at TIMESTAMP
)

-- Competitors
competitors (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  name TEXT,
  website TEXT,
  tier TEXT,  -- 'direct' | 'indirect' | 'aspirational' | 'regional'
  social\_profiles JSONB,
  ad\_library\_url TEXT,
  ai\_discovered BOOLEAN DEFAULT false,
  active BOOLEAN DEFAULT true,
  created\_at TIMESTAMP
)

-- KPI configurations
kpi\_configs (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  filter\_mode TEXT,  -- 'daily' | 'weekly' | 'monthly'
  kpi\_pack TEXT,     -- 'default' | 'custom'
  kpis JSONB,        -- ordered list of active KPI keys
  created\_at TIMESTAMP,
  updated\_at TIMESTAMP
)
```

### Data Collection Tables

```sql
-- Raw page snapshots
page\_snapshots (
  id UUID PRIMARY KEY,
  competitor\_id UUID REFERENCES competitors(id),
  source\_type TEXT,  -- 'website' | 'facebook' | 'instagram' | 'linkedin' | 'youtube' | 'ad\_library'
  url TEXT,
  raw\_html TEXT,
  extracted\_text TEXT,
  metadata JSONB,
  scraped\_at TIMESTAMP
)

-- Normalised social posts
social\_posts (
  id UUID PRIMARY KEY,
  competitor\_id UUID REFERENCES competitors(id),
  platform TEXT,
  post\_id TEXT,  -- platform native ID
  post\_type TEXT,  -- 'reel' | 'image' | 'carousel' | 'video' | 'text' | 'story'
  caption TEXT,
  hashtags TEXT\[],
  published\_at TIMESTAMP,
  likes INT,
  comments INT,
  shares INT,
  views INT,
  engagement\_rate NUMERIC,
  collected\_at TIMESTAMP
)

-- Paid ads
ad\_creatives (
  id UUID PRIMARY KEY,
  competitor\_id UUID REFERENCES competitors(id),
  platform TEXT,
  ad\_id TEXT,
  headline TEXT,
  body\_text TEXT,
  cta TEXT,
  media\_type TEXT,  -- 'image' | 'video' | 'carousel'
  media\_url TEXT,
  landing\_page\_url TEXT,
  first\_seen TIMESTAMP,
  last\_seen TIMESTAMP,
  active BOOLEAN
)

-- Extracted messaging themes
message\_themes (
  id UUID PRIMARY KEY,
  competitor\_id UUID REFERENCES competitors(id),
  source TEXT,  -- 'social' | 'website' | 'ads'
  theme TEXT,   -- AI-extracted label e.g. "Price leadership"
  evidence TEXT\[],  -- raw quotes supporting this theme
  frequency INT,  -- occurrences in collection window
  period\_start TIMESTAMP,
  period\_end TIMESTAMP
)

-- Website change log
website\_changes (
  id UUID PRIMARY KEY,
  competitor\_id UUID REFERENCES competitors(id),
  change\_type TEXT,  -- 'headline' | 'pricing' | 'new\_page' | 'nav\_change' | 'offer'
  before\_value TEXT,
  after\_value TEXT,
  detected\_at TIMESTAMP
)
```

### Analytics and Reporting Tables

```sql
-- KPI snapshots (computed metrics per competitor per period)
kpi\_snapshots (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  competitor\_id UUID REFERENCES competitors(id),  -- NULL for own brand
  filter\_mode TEXT,  -- 'daily' | 'weekly' | 'monthly'
  period\_start TIMESTAMP,
  period\_end TIMESTAMP,
  kpi\_key TEXT,    -- e.g. 'posting\_frequency' | 'engagement\_rate' | 'active\_ads'
  kpi\_value NUMERIC,
  kpi\_label TEXT,  -- human-readable value
  delta\_pct NUMERIC,  -- change vs previous period
  computed\_at TIMESTAMP
)

-- Share of voice snapshots
share\_of\_voice (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  period\_start TIMESTAMP,
  period\_end TIMESTAMP,
  filter\_mode TEXT,
  entries JSONB  -- \[{competitor\_id, brand\_name, mention\_count, sov\_pct}]
)

-- Alert records
alerts (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  competitor\_id UUID REFERENCES competitors(id),
  alert\_type TEXT,  -- 'posting\_spike' | 'new\_campaign' | 'message\_shift' | 'pricing\_change' | 'sov\_move'
  severity TEXT,   -- 'high' | 'medium' | 'low'
  title TEXT,
  description TEXT,
  evidence JSONB,
  triggered\_at TIMESTAMP,
  read BOOLEAN DEFAULT false
)

-- Reports
reports (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  filter\_mode TEXT,
  period\_start TIMESTAMP,
  period\_end TIMESTAMP,
  executive\_summary TEXT,
  full\_json JSONB,  -- complete structured report data
  generated\_at TIMESTAMP
)

-- Alert rules (user-defined)
alert\_rules (
  id UUID PRIMARY KEY,
  brand\_profile\_id UUID REFERENCES brand\_profiles(id),
  competitor\_id UUID REFERENCES competitors(id),  -- NULL = all competitors
  kpi\_key TEXT,
  condition TEXT,   -- 'increase\_pct\_gt' | 'decrease\_pct\_gt' | 'new\_value'
  threshold NUMERIC,
  active BOOLEAN DEFAULT true,
  created\_at TIMESTAMP
)
```

\---

## 5\. Agent Architecture

### Overview

The platform uses a multi-agent system where each agent has a single responsibility. Agents communicate via a job queue. The orchestration layer dispatches agents based on trigger type (user action, schedule, alert threshold). Each agent writes to a defined set of database tables and emits completion events for downstream agents.

```
User Action / Schedule Trigger
          ↓
  Orchestration Layer (job queue)
          ↓
  ┌──────────────────────────────────────────────────────────┐
  │                    Agent Pool                            │
  │                                                          │
  │  Brand Persona Agent       Competitor Discovery Agent    │
  │  Source Collection Agent   Social Analysis Agent         │
  │  Messaging Analysis Agent  Paid Media Agent              │
  │  Website Change Agent      Benchmark \& SOV Agent         │
  │  Alert Evaluation Agent    Report Generation Agent       │
  └──────────────────────────────────────────────────────────┘
          ↓
      Database (Postgres)
          ↓
  Dashboard / Alert Feed / Export
```

\---

### Agent Definitions

**Agent 1: Brand Persona Agent**

* Trigger: User submits brand setup form
* Input: Brand name, website URL, social links, industry, region, audience
* Process: Crawl website and social profiles with Firecrawl / Apify; extract value props, messaging tone, audience signals, category; call LLM to generate structured persona
* Output: Writes to `brand\_profiles.persona`
* Model: GPT-4o or Claude 3.5 for reasoning quality
* Estimated runtime: 30–90 seconds

**Agent 2: Competitor Discovery Agent**

* Trigger: User clicks "Find my competitors"
* Input: Brand profile (industry, region, audience, category, website)
* Process: Query Google via SerpAPI or Apify for category + region; cross-reference ad libraries and social directories; score by audience overlap, keyword proximity, and geographic match; deduplicate and rank
* Output: Returns ranked competitor suggestions with name, website, category, and suggested tier
* Model: Embedding similarity + LLM ranking
* Estimated runtime: 60–180 seconds

**Agent 3: Source Collection Agent**

* Trigger: User completes competitor list and clicks "Collect Data"
* Input: Competitor list with all channel URLs
* Process: Dispatch parallel sub-tasks — website crawl (Firecrawl), social profile scrape (Apify actors per platform), ad library scrape, review platform scrape; store raw results
* Output: Writes to `page\_snapshots`
* Tools: Firecrawl (website), Apify (social), custom scrapers (ad library)
* Estimated runtime: 5–20 minutes (runs async, user moves to KPI page)

**Agent 4: Social Analysis Agent**

* Trigger: Source Collection Agent completes per platform
* Input: Raw social post data from `page\_snapshots`
* Process: Parse posts, extract metrics, normalise engagement rates, classify post type and format, identify posting frequency, detect content pillars, flag anomalous spikes
* Output: Writes to `social\_posts`, updates `kpi\_snapshots` for social KPIs
* Model: Rule-based extraction + lightweight classifier
* Estimated runtime: 2–5 minutes per competitor

**Agent 5: Messaging Analysis Agent**

* Trigger: Social Analysis Agent completes + website snapshots available
* Input: Post captions, website copy, ad body text
* Process: Extract recurring claims, identify CTA patterns, classify value propositions, detect sentiment and audience language style, cluster into message themes
* Output: Writes to `message\_themes`
* Model: GPT-4o for theme extraction and clustering
* Estimated runtime: 1–3 minutes per competitor

**Agent 6: Paid Media Agent**

* Trigger: Source Collection Agent completes (ad library data)
* Input: Raw ad library data from `page\_snapshots`
* Process: Parse active creatives, extract headline, body, CTA, landing page; detect new/paused ads by comparing to last snapshot; classify campaign themes; identify hooks and offer types
* Output: Writes to `ad\_creatives`
* Model: LLM extraction + rule-based change detection
* Estimated runtime: 2–4 minutes per competitor

**Agent 7: Website Change Agent**

* Trigger: Source Collection Agent completes (website snapshot)
* Input: Current website snapshot vs last snapshot in `page\_snapshots`
* Process: Diff homepage headline, pricing page, nav items, key CTAs, new page URLs; flag meaningful changes only (ignores minor text edits); write to change log
* Output: Writes to `website\_changes`
* Model: Diff algorithm + LLM to classify change significance
* Estimated runtime: 30–90 seconds per competitor

**Agent 8: Benchmark \& SOV Agent**

* Trigger: All per-competitor analysis agents complete for a given collection run
* Input: `kpi\_snapshots`, `social\_posts`, `message\_themes` for all competitors in a brand profile
* Process: Compute category averages per KPI; rank competitors per KPI; compute estimated share of voice from mention data; compute delta vs previous period; flag leaders and laggards per KPI
* Output: Updates `kpi\_snapshots` with benchmarks; writes to `share\_of\_voice`
* Model: Statistical aggregation — no LLM needed here
* Estimated runtime: 30–60 seconds

**Agent 9: Alert Evaluation Agent**

* Trigger: Benchmark \& SOV Agent completes each run
* Input: `kpi\_snapshots`, `website\_changes`, `ad\_creatives`, `alert\_rules`
* Process: Evaluate each alert rule against fresh data; compare to threshold; check for system-default alert patterns (spike detection, new campaign, message shift, pricing change); create alert records for triggered conditions only
* Output: Writes to `alerts`; sends notification if rule has email/Slack delivery
* Model: Rule-based threshold matching — no LLM for core evaluation; LLM used only to write the alert description in plain English
* Estimated runtime: 15–30 seconds

**Agent 10: Report Generation Agent**

* Trigger: Scheduled (daily/weekly/monthly per user filter config), or on-demand from dashboard Export button
* Input: All `kpi\_snapshots`, `message\_themes`, `ad\_creatives`, `website\_changes`, `share\_of\_voice`, `alerts` for the reporting period
* Process: Aggregate all signals; generate executive summary paragraph; build structured report JSON (KPIs, narratives, charts config, recommendations); write plain-English insight per section
* Output: Writes to `reports`; available for PDF and slide export
* Model: GPT-4o with structured output for report JSON; narrative generation for summary
* Estimated runtime: 60–120 seconds

\---

### Orchestration and Scheduling

```
Orchestration Layer manages:

1. Job Queue (BullMQ / Temporal)
   - Job types: one per agent
   - Priority levels: user-triggered (high) > scheduled (normal) > background re-crawl (low)
   - Retry policy: 3 retries with exponential backoff
   - Dead letter queue for failed jobs with alerting

2. Scheduling
   - Daily mode: Source collection + analysis runs every 24h at midnight UTC
   - Weekly mode: Runs every Monday at 2am local time
   - Monthly mode: Runs on the 1st of each month

3. Agent Dependencies (DAG)
   Source Collection
       ↓
   \[Social Analysis] \[Paid Media] \[Website Change] (parallel)
       ↓ (all complete)
   \[Messaging Analysis]
       ↓
   \[Benchmark \& SOV]
       ↓
   \[Alert Evaluation]
       ↓
   \[Report Generation] (on schedule or on-demand)

4. Concurrency
   - Max 5 Source Collection jobs per account simultaneously
   - Max 3 LLM-heavy agent jobs per account simultaneously
   - Rate limit Firecrawl / Apify calls per account plan
```

\---

## 6\. Filter-to-KPI Mapping — Full Reference

|KPI Key|Daily|Weekly|Monthly|Notes|
|-|-|-|-|-|
|`posts\_today`|✓|—|—|Count of posts in last 24h|
|`posting\_frequency`|—|✓|✓|Posts per week or month|
|`engagement\_rate`|✓|✓|✓|Threshold: >2x category avg triggers alert|
|`engagement\_spike`|✓|—|—|Single post spike in 24h|
|`top\_content\_format`|—|✓|✓|% breakdown by format type|
|`active\_ads\_count`|✓|✓|—|New / paused ads detected|
|`ad\_themes`|—|✓|✓|Campaign messaging clusters|
|`new\_ad\_creatives`|✓|✓|—|Creatives added since last run|
|`messaging\_themes`|—|✓|✓|Top 3–5 recurring claims|
|`messaging\_shift`|—|—|✓|Change in dominant theme vs prior month|
|`follower\_growth\_delta`|—|✓|✓|% WoW or MoM|
|`share\_of\_voice`|—|✓|✓|Category mention share|
|`website\_headline\_change`|✓|✓|—|Detect copy changes on homepage|
|`pricing\_change`|✓|✓|—|Detect price or offer page changes|
|`new\_content\_published`|✓|✓|—|Blog posts, landing pages, new URLs|
|`content\_pillars`|—|—|✓|Monthly topic cluster analysis|
|`audience\_sentiment\_proxy`|—|—|✓|Comment tone analysis|
|`campaign\_lifecycle`|—|—|✓|Campaign duration and evolution|
|`seo\_keyword\_movement`|—|—|✓|Estimated keyword rank changes|
|`competitive\_whitespace`|—|—|✓|Underserved channels or topics|

\---

## 7\. Alert Threshold Defaults

|Alert Type|Default Trigger|Severity|
|-|-|-|
|Posting spike|>40% increase in posts vs same period last run|High|
|Engagement spike|Any post exceeds 3x competitor's average engagement|High|
|New paid campaign|New ad creative detected for a Direct tier competitor|Medium|
|Paid pause|All active ads disappear for a competitor|Medium|
|Messaging shift|Primary messaging theme changes vs prior period|High|
|Pricing change|Any text change on pricing or offer page|High|
|New page published|New URL detected on competitor website|Low|
|Follower growth spike|>5% follower growth in one week|Medium|
|SOV movement|Brand's estimated SOV drops by >5 percentage points|High|

All thresholds are editable in the Alerts \& Settings page.

\---

## 8\. Technology Stack Recommendation

|Layer|Recommended Option|Rationale|
|-|-|-|
|Frontend|Next.js (App Router) + Tailwind|Fast builds, SSR for dashboard, component reuse|
|Backend API|FastAPI (Python)|Native async, LangChain integration, agent orchestration|
|Job Queue|BullMQ (Redis-backed) or Temporal|Durable workflows, retry logic, scheduling|
|Database|PostgreSQL + pgvector|Relational + vector search for message clustering|
|Scraping — websites|Firecrawl|Managed crawling with markdown extraction|
|Scraping — social/ads|Apify actors|Maintained actor library per platform|
|LLM|OpenAI GPT-4o + Claude 3.5 Sonnet|GPT-4o for extraction, Claude for long report writing|
|Embeddings|OpenAI text-embedding-3-small|Message theme clustering, competitor similarity|
|Auth|Clerk or Auth0|Multi-tenant, team invites, SSO-ready|
|Storage|AWS S3|Ad creatives, screenshots, exports|
|Email / Alerts|Resend + Slack webhooks|Digest emails, instant alerts|
|Export|Puppeteer (PDF) + PPTX.js (slides)|Dashboard-to-PDF, report-to-slides|

\---



