/**
 * Rich mock data used as fallback when the API is unavailable (no DB in dev).
 * Simulates what a populated CompeteIQ workspace looks like for the SaaS category.
 */

export const MOCK_COMPETITORS = [
  {
    id: "c1000000-0000-0000-0000-000000000001",
    name: "Salesforce",
    website: "https://salesforce.com",
    tier: "direct" as const,
    ai_discovered: false,
    active: true,
    social_profiles: {
      linkedin_url: "https://linkedin.com/company/salesforce",
      twitter_handle: "@salesforce",
      instagram_handle: "salesforce",
    },
    ad_library_url: "https://www.facebook.com/ads/library/?q=salesforce",
  },
  {
    id: "c2000000-0000-0000-0000-000000000002",
    name: "HubSpot",
    website: "https://hubspot.com",
    tier: "direct" as const,
    ai_discovered: false,
    active: true,
    social_profiles: {
      linkedin_url: "https://linkedin.com/company/hubspot",
      twitter_handle: "@hubspot",
      instagram_handle: "hubspot",
    },
    ad_library_url: "https://www.facebook.com/ads/library/?q=hubspot",
  },
  {
    id: "c3000000-0000-0000-0000-000000000003",
    name: "Pipedrive",
    website: "https://pipedrive.com",
    tier: "indirect" as const,
    ai_discovered: true,
    active: true,
    social_profiles: {
      linkedin_url: "https://linkedin.com/company/pipedrive",
      twitter_handle: "@pipedrive",
    },
    ad_library_url: null,
  },
  {
    id: "c4000000-0000-0000-0000-000000000004",
    name: "Monday.com",
    website: "https://monday.com",
    tier: "aspirational" as const,
    ai_discovered: true,
    active: true,
    social_profiles: {
      linkedin_url: "https://linkedin.com/company/mondaydotcom",
      instagram_handle: "mondaydotcom",
    },
    ad_library_url: "https://www.facebook.com/ads/library/?q=monday.com",
  },
];

function weekLabels(n: number) {
  const labels: string[] = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i * 7);
    labels.push(`W${d.toISOString().slice(5, 7)}/${d.toISOString().slice(8, 10)}`);
  }
  return labels;
}

const weeks = weekLabels(8);

export const MOCK_DASHBOARD_DATA = {
  summary: {
    competitors_tracked: 4,
    channels_monitored: 12,
    active_alerts: 3,
    rising_threat: "HubSpot",
    data_freshness: "2 hours ago",
  },

  executive_summary:
    "This week HubSpot increased posting frequency by 43% with a heavy push on short-form video, targeting SMB decision-makers. Salesforce launched a new 'Einstein AI' campaign across LinkedIn and YouTube. Pipedrive shifted messaging from 'ease of use' to 'sales velocity', suggesting a repositioning toward mid-market. Monday.com continued its viral LinkedIn strategy — 3 posts exceeded 1,000 shares. Your biggest opportunity: the 'team collaboration' narrative is underserved across all four competitors.",

  kpi_snapshots: {
    posting_frequency: weeks.map((period, i) => ({
      period,
      Salesforce: 12 + Math.round(Math.sin(i) * 3),
      HubSpot: 8 + i * 2 + Math.round(Math.random() * 2),
      Pipedrive: 5 + Math.round(Math.cos(i) * 2),
      "Monday.com": 15 + Math.round(Math.sin(i + 1) * 4),
    })),
    engagement_rate: weeks.map((period, i) => ({
      period,
      Salesforce: +(2.1 + Math.sin(i) * 0.4).toFixed(2),
      HubSpot: +(3.4 + Math.sin(i + 1) * 0.6).toFixed(2),
      Pipedrive: +(1.8 + Math.cos(i) * 0.3).toFixed(2),
      "Monday.com": +(4.2 + Math.sin(i + 2) * 0.8).toFixed(2),
    })),
    follower_growth_delta: weeks.map((period, i) => ({
      period,
      Salesforce: 1200 + Math.round(Math.sin(i) * 300),
      HubSpot: 2800 + Math.round(i * 150 + Math.random() * 200),
      Pipedrive: 450 + Math.round(Math.cos(i) * 100),
      "Monday.com": 3500 + Math.round(Math.sin(i + 1) * 500),
    })),
    share_of_voice: weeks.map((period, i) => ({
      period,
      "Your Brand": 18 + Math.round(Math.sin(i) * 2),
      Salesforce: 30 - Math.round(Math.sin(i) * 1),
      HubSpot: 25 + Math.round(Math.cos(i) * 2),
      Pipedrive: 12 + Math.round(Math.sin(i + 1) * 1),
      "Monday.com": 15 - Math.round(Math.cos(i + 1) * 1),
    })),
  },

  competitor_cards: [
    {
      competitor_id: "c1000000-0000-0000-0000-000000000001",
      name: "Salesforce",
      tier: "direct",
      metrics: {
        posts_this_period: 14,
        engagement_rate: 2.3,
        active_ads: 28,
        follower_growth_pct: 1.2,
        top_format: "Video",
        top_message: "AI-powered CRM for enterprise teams",
        channels: ["linkedin", "youtube", "facebook"],
        sentiment: "neutral",
      },
    },
    {
      competitor_id: "c2000000-0000-0000-0000-000000000002",
      name: "HubSpot",
      tier: "direct",
      metrics: {
        posts_this_period: 31,
        engagement_rate: 4.1,
        active_ads: 45,
        follower_growth_pct: 3.8,
        top_format: "Reel",
        top_message: "The free CRM that grows with you",
        channels: ["instagram", "linkedin", "facebook"],
        sentiment: "positive",
      },
    },
    {
      competitor_id: "c3000000-0000-0000-0000-000000000003",
      name: "Pipedrive",
      tier: "indirect",
      metrics: {
        posts_this_period: 6,
        engagement_rate: 1.7,
        active_ads: 12,
        follower_growth_pct: 0.4,
        top_format: "Image",
        top_message: "Close more deals, faster",
        channels: ["linkedin", "facebook"],
        sentiment: "neutral",
      },
    },
    {
      competitor_id: "c4000000-0000-0000-0000-000000000004",
      name: "Monday.com",
      tier: "aspirational",
      metrics: {
        posts_this_period: 22,
        engagement_rate: 5.2,
        active_ads: 67,
        follower_growth_pct: 5.1,
        top_format: "Carousel",
        top_message: "Work the way that works for you",
        channels: ["instagram", "linkedin", "youtube"],
        sentiment: "positive",
      },
    },
  ],

  messaging_themes: [
    { theme: "AI-powered automation", frequency: 38, competitors: ["Salesforce", "HubSpot"] },
    { theme: "Ease of use / No learning curve", frequency: 27, competitors: ["HubSpot", "Monday.com", "Pipedrive"] },
    { theme: "Team collaboration", frequency: 21, competitors: ["Monday.com"] },
    { theme: "Sales velocity / Close more deals", frequency: 18, competitors: ["Pipedrive", "Salesforce"] },
    { theme: "Free tier / Try before you buy", frequency: 15, competitors: ["HubSpot", "Pipedrive"] },
    { theme: "Enterprise security & compliance", frequency: 12, competitors: ["Salesforce"] },
  ],

  paid_media_summary: {
    total_active_ads: 152,
    new_campaigns_this_week: 4,
    top_platforms: ["Facebook", "LinkedIn", "YouTube"],
    top_ctas: ["Start Free Trial", "Book a Demo", "Get Started"],
    recent_campaigns: [
      {
        competitor: "HubSpot",
        name: "Free CRM Spring 2025",
        platforms: ["Facebook", "Instagram"],
        theme: "Free tier + onboarding simplicity",
        status: "active",
        ad_count: 12,
        first_seen: "2025-03-15",
      },
      {
        competitor: "Salesforce",
        name: "Einstein AI Launch",
        platforms: ["LinkedIn", "YouTube"],
        theme: "AI-first CRM, enterprise trust",
        status: "active",
        ad_count: 8,
        first_seen: "2025-04-01",
      },
      {
        competitor: "Monday.com",
        name: "Work Better Together",
        platforms: ["Facebook", "Instagram", "YouTube"],
        theme: "Team productivity, visual workflows",
        status: "active",
        ad_count: 22,
        first_seen: "2025-03-28",
      },
    ],
  },

  opportunities: [
    {
      title: "Team collaboration narrative is unclaimed",
      description:
        "None of the top 4 competitors are consistently messaging around cross-functional team collaboration. You could own this whitespace with a content series targeting RevOps and marketing ops roles.",
      effort: "low" as const,
      impact: "high" as const,
    },
    {
      title: "YouTube is underleveraged across the category",
      description:
        "Salesforce and Monday.com have YouTube presence but post fewer than 2 videos/week. Consistent educational content (demos, tutorials) could capture high-intent search traffic.",
      effort: "medium" as const,
      impact: "high" as const,
    },
    {
      title: "Pipedrive repositioning to mid-market",
      description:
        "Pipedrive's messaging shift from 'ease of use' to 'sales velocity' signals a move upmarket. Their SMB audience may be underserved — a short-term acquisition opportunity.",
      effort: "low" as const,
      impact: "medium" as const,
    },
    {
      title: "Free trial CTAs dominate — consider a ROI calculator",
      description:
        "All competitors lead with free trials. A ROI/savings calculator CTA could differentiate and attract higher-intent enterprise buyers who want to justify budget.",
      effort: "medium" as const,
      impact: "medium" as const,
    },
  ],

  alerts: [
    {
      id: "a1",
      competitor_id: "c2000000-0000-0000-0000-000000000002",
      competitor_name: "HubSpot",
      alert_type: "posting_spike",
      severity: "high" as const,
      title: "HubSpot posting frequency +43% this week",
      description: "HubSpot published 31 posts vs their 7-day average of 22. Heavy short-form video push targeting SMB decision-makers.",
      triggered_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      read: false,
      dismissed: false,
    },
    {
      id: "a2",
      competitor_id: "c1000000-0000-0000-0000-000000000001",
      competitor_name: "Salesforce",
      alert_type: "new_campaign",
      severity: "medium" as const,
      title: "Salesforce launched 'Einstein AI' campaign",
      description: "New multi-channel campaign detected across LinkedIn and YouTube. 8 new ad creatives with AI-first messaging. Landing page updated.",
      triggered_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      read: false,
      dismissed: false,
    },
    {
      id: "a3",
      competitor_id: "c3000000-0000-0000-0000-000000000003",
      competitor_name: "Pipedrive",
      alert_type: "message_shift",
      severity: "medium" as const,
      title: "Pipedrive messaging shift detected",
      description: "'Ease of use' dropped from top messaging. 'Sales velocity' and 'close more deals faster' now dominate. Possible mid-market repositioning.",
      triggered_at: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(),
      read: false,
      dismissed: false,
    },
  ],

  share_of_voice: [
    { brand_name: "Your Brand", sov_pct: 18 },
    { brand_name: "Salesforce", sov_pct: 30 },
    { brand_name: "HubSpot", sov_pct: 25 },
    { brand_name: "Pipedrive", sov_pct: 12 },
    { brand_name: "Monday.com", sov_pct: 15 },
  ],

  content_format_mix: [
    { competitor: "Salesforce", reel: 20, image: 35, carousel: 25, video: 15, text: 5 },
    { competitor: "HubSpot", reel: 45, image: 20, carousel: 20, video: 10, text: 5 },
    { competitor: "Pipedrive", reel: 10, image: 50, carousel: 15, video: 10, text: 15 },
    { competitor: "Monday.com", reel: 30, image: 25, carousel: 35, video: 8, text: 2 },
  ],
};

export const MOCK_ALERTS = MOCK_DASHBOARD_DATA.alerts;

// ── Competitor deep-dive profiles (one per competitor ID) ──────────────────

export const MOCK_COMPETITOR_PROFILES: Record<string, any> = {
  "c1000000-0000-0000-0000-000000000001": {
    id: "c1000000-0000-0000-0000-000000000001",
    name: "Salesforce",
    website: "https://salesforce.com",
    tier: "direct",
    data_confidence: 87,
    metrics: {
      followers: "4.2M",
      follower_delta: 1.2,
      posts_count: 14,
      posts_delta: 16.7,
      avg_engagement: 0.023,
      active_ads: 28,
    },
    platform_breakdown: {
      linkedin: { followers: "2.1M", posts: 6, engagement: 0.031 },
      instagram: { followers: "890K", posts: 5, engagement: 0.018 },
      youtube: { followers: "1.2M", posts: 3, engagement: 0.012 },
    },
    format_mix: [
      { name: "Video", value: 40 },
      { name: "Image", value: 30 },
      { name: "Carousel", value: 20 },
      { name: "Text", value: 10 },
    ],
    posting_schedule: [
      { day: "Mon", posts: 3 }, { day: "Tue", posts: 2 }, { day: "Wed", posts: 3 },
      { day: "Thu", posts: 2 }, { day: "Fri", posts: 2 }, { day: "Sat", posts: 1 }, { day: "Sun", posts: 1 },
    ],
    top_hashtags: ["CRM", "AI", "SalesCloud", "EinsteinAI", "CustomerSuccess", "Trailhead"],
    best_post: {
      caption: "The future of sales is AI. Einstein GPT is now available for all Sales Cloud customers — automate repetitive tasks, surface the right leads at the right time, and close deals faster. Try it free for 30 days.",
      likes: 4821,
      comments: 312,
      shares: 891,
      platform: "linkedin",
    },
    themes: [
      {
        theme: "AI-powered CRM",
        frequency: 18,
        source: "social",
        evidence: [
          "\"Let AI handle the busywork so your team can focus on selling\"",
          "\"Einstein AI surfaces your best leads before your competition does\"",
          "\"Automate follow-ups, forecast revenue, close faster\"",
        ],
      },
      {
        theme: "Enterprise trust & security",
        frequency: 11,
        source: "website",
        evidence: [
          "\"Trusted by 150,000+ companies worldwide\"",
          "\"SOC 2, ISO 27001, GDPR compliant\"",
          "\"Your data stays yours — always\"",
        ],
      },
      {
        theme: "Customer success stories",
        frequency: 9,
        source: "social",
        evidence: [
          "\"How Coca-Cola increased sales velocity by 34% with Salesforce\"",
          "\"AWS scaled to $1B in pipeline with Sales Cloud — here's how\"",
        ],
      },
    ],
    ads: [
      {
        headline: "Close More Deals with Einstein AI",
        body_text: "Automate data entry, get AI-powered lead scores, and never miss a follow-up. Try Salesforce free for 30 days.",
        cta: "Start Free Trial",
        media_type: "video",
        platform: "linkedin",
        first_seen: "2025-04-01",
      },
      {
        headline: "The #1 CRM for Enterprise Teams",
        body_text: "150,000+ companies trust Salesforce to power their growth. See why in our free demo.",
        cta: "Book a Demo",
        media_type: "image",
        platform: "facebook",
        first_seen: "2025-03-20",
      },
      {
        headline: "Salesforce Spring '25 Release — What's New",
        body_text: "100+ new features across Sales, Service, and Marketing Cloud. Watch the release highlights.",
        cta: "Watch Now",
        media_type: "video",
        platform: "youtube",
        first_seen: "2025-04-05",
      },
    ],
    changes: [
      {
        change_type: "headline",
        before_value: "The World's #1 CRM",
        after_value: "The World's #1 AI CRM",
        significance: "high",
        detected_at: "2025-04-03T10:00:00Z",
      },
      {
        change_type: "pricing",
        before_value: "Starter: $25/user/month",
        after_value: "Starter: $25/user/month (+ Einstein AI included)",
        significance: "medium",
        detected_at: "2025-04-01T00:00:00Z",
      },
    ],
    seo: {
      domain_authority: 91,
      organic_traffic_est: "14.2M/mo",
      top_keywords: ["CRM software", "sales CRM", "customer relationship management", "salesforce pricing", "best CRM"],
      new_pages_this_week: 3,
    },
    cta_patterns: ["Start Free Trial", "Book a Demo", "Watch Now", "Get the Guide"],
    audience_language: "Professional, aspirational, ROI-focused. Heavy use of statistics and case study proof points.",
    posting_times: "Mon–Fri, 9am–11am and 4pm–6pm UTC",
  },

  "c2000000-0000-0000-0000-000000000002": {
    id: "c2000000-0000-0000-0000-000000000002",
    name: "HubSpot",
    website: "https://hubspot.com",
    tier: "direct",
    data_confidence: 94,
    metrics: {
      followers: "1.8M",
      follower_delta: 3.8,
      posts_count: 31,
      posts_delta: 43.0,
      avg_engagement: 0.041,
      active_ads: 45,
    },
    platform_breakdown: {
      instagram: { followers: "640K", posts: 14, engagement: 0.055 },
      linkedin: { followers: "850K", posts: 10, engagement: 0.038 },
      facebook: { followers: "310K", posts: 7, engagement: 0.029 },
    },
    format_mix: [
      { name: "Reel", value: 45 },
      { name: "Carousel", value: 25 },
      { name: "Image", value: 20 },
      { name: "Text", value: 10 },
    ],
    posting_schedule: [
      { day: "Mon", posts: 5 }, { day: "Tue", posts: 6 }, { day: "Wed", posts: 5 },
      { day: "Thu", posts: 6 }, { day: "Fri", posts: 5 }, { day: "Sat", posts: 2 }, { day: "Sun", posts: 2 },
    ],
    top_hashtags: ["HubSpot", "MarketingTips", "Inbound", "CRM", "GrowBetter", "SmallBusiness"],
    best_post: {
      caption: "Your CRM shouldn't cost more than your first customer. HubSpot's free CRM is free forever — not a trial, not a gimmick. Real tools, zero cost. Start today 👇",
      likes: 9240,
      comments: 678,
      shares: 2103,
      platform: "instagram",
    },
    themes: [
      {
        theme: "Free tier / Try before you buy",
        frequency: 22,
        source: "social",
        evidence: [
          "\"Free forever. No credit card required.\"",
          "\"Start with free tools and upgrade when you're ready\"",
          "\"Your competitors are already using free CRM — are you?\"",
        ],
      },
      {
        theme: "Ease of use / No learning curve",
        frequency: 17,
        source: "social",
        evidence: [
          "\"Up and running in minutes, not months\"",
          "\"Your team will actually use this CRM (we promise)\"",
          "\"Built for humans, not IT teams\"",
        ],
      },
      {
        theme: "Inbound marketing thought leadership",
        frequency: 14,
        source: "website",
        evidence: [
          "\"The HubSpot Blog — 1M monthly readers\"",
          "\"Download the 2025 State of Marketing Report\"",
          "\"Inbound methodology: attract, engage, delight\"",
        ],
      },
    ],
    ads: [
      {
        headline: "Free CRM — Really Free. Forever.",
        body_text: "HubSpot's CRM is 100% free. No trial, no time limit. Get your whole team set up today and start closing more deals.",
        cta: "Get Started Free",
        media_type: "reel",
        platform: "instagram",
        first_seen: "2025-03-15",
      },
      {
        headline: "The Marketing Platform Your Team Will Love",
        body_text: "Email, social, ads, SEO — all in one place. Connect HubSpot to your CRM and see ROI from day one.",
        cta: "Get a Free Demo",
        media_type: "carousel",
        platform: "facebook",
        first_seen: "2025-03-28",
      },
    ],
    changes: [
      {
        change_type: "offer",
        before_value: "14-day free trial of Marketing Hub",
        after_value: "Free forever plan + 90-day starter deal at 50% off",
        significance: "high",
        detected_at: "2025-04-07T00:00:00Z",
      },
    ],
    seo: {
      domain_authority: 93,
      organic_traffic_est: "18.7M/mo",
      top_keywords: ["free CRM", "hubspot pricing", "email marketing software", "inbound marketing", "marketing automation"],
      new_pages_this_week: 8,
    },
    cta_patterns: ["Get Started Free", "Get a Free Demo", "Download Now", "See It in Action"],
    audience_language: "Conversational, friendly, empowering. SMB-focused. Occasional humour. Heavy use of social proof via stats.",
    posting_times: "Mon–Fri, 8am–10am and 6pm–8pm UTC. High Tue/Thu volume.",
  },

  "c3000000-0000-0000-0000-000000000003": {
    id: "c3000000-0000-0000-0000-000000000003",
    name: "Pipedrive",
    website: "https://pipedrive.com",
    tier: "indirect",
    data_confidence: 76,
    metrics: {
      followers: "280K",
      follower_delta: 0.4,
      posts_count: 6,
      posts_delta: -25.0,
      avg_engagement: 0.017,
      active_ads: 12,
    },
    platform_breakdown: {
      linkedin: { followers: "180K", posts: 4, engagement: 0.021 },
      facebook: { followers: "100K", posts: 2, engagement: 0.012 },
    },
    format_mix: [
      { name: "Image", value: 50 },
      { name: "Text", value: 25 },
      { name: "Carousel", value: 15 },
      { name: "Video", value: 10 },
    ],
    posting_schedule: [
      { day: "Mon", posts: 1 }, { day: "Tue", posts: 2 }, { day: "Wed", posts: 0 },
      { day: "Thu", posts: 2 }, { day: "Fri", posts: 1 }, { day: "Sat", posts: 0 }, { day: "Sun", posts: 0 },
    ],
    top_hashtags: ["SalesVelocity", "Pipedrive", "CRM", "SalesTips", "PipelineManagement"],
    best_post: {
      caption: "Sales teams that use a visual pipeline close 28% more deals. Pipedrive keeps your focus on the actions that matter. See how in 2 minutes →",
      likes: 1820,
      comments: 94,
      shares: 312,
      platform: "linkedin",
    },
    themes: [
      {
        theme: "Sales velocity & deal closing",
        frequency: 14,
        source: "social",
        evidence: [
          "\"Close more deals, faster — that's the Pipedrive promise\"",
          "\"Every rep closes 28% more with a visual pipeline\"",
          "\"Speed wins deals. Pipedrive helps your team move faster\"",
        ],
      },
      {
        theme: "Simple, visual pipeline",
        frequency: 10,
        source: "social",
        evidence: [
          "\"If you can see it, you can manage it\"",
          "\"Your whole pipeline, one screen\"",
          "\"Drag-and-drop simplicity, enterprise-level insight\"",
        ],
      },
    ],
    ads: [
      {
        headline: "Close Deals Faster — Free 14-Day Trial",
        body_text: "Pipedrive's visual pipeline gives your sales team the clarity they need to close more deals. No setup fee, no long-term contract.",
        cta: "Try Free",
        media_type: "image",
        platform: "linkedin",
        first_seen: "2025-03-10",
      },
    ],
    changes: [
      {
        change_type: "headline",
        before_value: "The easy-to-use CRM for salespeople",
        after_value: "Drive revenue. Close deals faster.",
        significance: "high",
        detected_at: "2025-04-02T00:00:00Z",
      },
    ],
    seo: {
      domain_authority: 78,
      organic_traffic_est: "3.1M/mo",
      top_keywords: ["sales CRM", "pipedrive pricing", "pipeline management", "CRM for sales teams"],
      new_pages_this_week: 1,
    },
    cta_patterns: ["Try Free", "Start Free Trial", "Watch Demo"],
    audience_language: "Direct, outcome-focused, B2B professional. Messaging is shifting from 'easy to use' toward 'revenue growth'.",
    posting_times: "Tue and Thu, 9am–11am UTC.",
  },

  "c4000000-0000-0000-0000-000000000004": {
    id: "c4000000-0000-0000-0000-000000000004",
    name: "Monday.com",
    website: "https://monday.com",
    tier: "aspirational",
    data_confidence: 91,
    metrics: {
      followers: "2.1M",
      follower_delta: 5.1,
      posts_count: 22,
      posts_delta: 10.0,
      avg_engagement: 0.052,
      active_ads: 67,
    },
    platform_breakdown: {
      instagram: { followers: "890K", posts: 10, engagement: 0.068 },
      linkedin: { followers: "760K", posts: 8, engagement: 0.045 },
      youtube: { followers: "450K", posts: 4, engagement: 0.031 },
    },
    format_mix: [
      { name: "Reel", value: 35 },
      { name: "Carousel", value: 30 },
      { name: "Image", value: 25 },
      { name: "Video", value: 10 },
    ],
    posting_schedule: [
      { day: "Mon", posts: 3 }, { day: "Tue", posts: 4 }, { day: "Wed", posts: 3 },
      { day: "Thu", posts: 4 }, { day: "Fri", posts: 4 }, { day: "Sat", posts: 2 }, { day: "Sun", posts: 2 },
    ],
    top_hashtags: ["mondaydotcom", "WorkManagement", "Productivity", "TeamWork", "NoCode", "Remote"],
    best_post: {
      caption: "When your team finally has a single source of truth 🙌 No more 47 Slack messages to find the right doc. No more 'which spreadsheet is the latest one?' Just clarity, all the time. Tag someone who needs this in their life 👇",
      likes: 18400,
      comments: 2103,
      shares: 4821,
      platform: "instagram",
    },
    themes: [
      {
        theme: "Work your way / Flexibility",
        frequency: 24,
        source: "social",
        evidence: [
          "\"Work the way that works for you\"",
          "\"One platform, infinite possibilities\"",
          "\"Build it your way — no code required\"",
        ],
      },
      {
        theme: "Team collaboration & visibility",
        frequency: 19,
        source: "social",
        evidence: [
          "\"Everyone knows what's happening — all the time\"",
          "\"Single source of truth for your entire team\"",
          "\"No more status update meetings — monday.com shows you everything\"",
        ],
      },
      {
        theme: "Viral / shareable content",
        frequency: 15,
        source: "social",
        evidence: [
          "Relatable team frustration memes",
          "\"Tag someone who needs this\" call to action",
          "Before/after workflow transformations",
        ],
      },
    ],
    ads: [
      {
        headline: "Work Better Together — Free Forever Plan",
        body_text: "monday.com helps teams plan, track, and deliver work with confidence. Start free and see why 225,000+ teams choose monday.",
        cta: "Get Started Free",
        media_type: "carousel",
        platform: "facebook",
        first_seen: "2025-03-28",
      },
      {
        headline: "Your Team Deserves Better Than Spreadsheets",
        body_text: "See everything happening across your projects in real-time. monday.com — the visual platform your team will actually love.",
        cta: "Try It Free",
        media_type: "reel",
        platform: "instagram",
        first_seen: "2025-04-05",
      },
    ],
    changes: [],
    seo: {
      domain_authority: 88,
      organic_traffic_est: "9.4M/mo",
      top_keywords: ["project management software", "monday.com pricing", "team collaboration tools", "work management", "no code platform"],
      new_pages_this_week: 5,
    },
    cta_patterns: ["Get Started Free", "Try It Free", "Book a Demo", "See How It Works"],
    audience_language: "Casual, relatable, occasionally humorous. Strong social-first content. Heavily shareable and community-oriented.",
    posting_times: "Mon–Fri, 6am–9am UTC. Also Sat/Sun 10am UTC.",
  },
};

export const MOCK_REPORTS = [
  {
    id: "r1",
    title: "Weekly Competitive Intelligence Report",
    period: "Apr 7 – Apr 13, 2025",
    filter_mode: "weekly",
    generated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    executive_summary: "HubSpot accelerated content output significantly. Salesforce launched AI campaign.",
    status: "ready",
  },
  {
    id: "r2",
    title: "Weekly Competitive Intelligence Report",
    period: "Mar 31 – Apr 6, 2025",
    filter_mode: "weekly",
    generated_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
    executive_summary: "Monday.com viral carousel campaign drove 3x normal engagement. Pipedrive reduced ad spend.",
    status: "ready",
  },
  {
    id: "r3",
    title: "Monthly Strategic Overview — March 2025",
    period: "March 2025",
    filter_mode: "monthly",
    generated_at: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
    executive_summary: "Q1 competitive landscape summary with positioning shifts and channel investment analysis.",
    status: "ready",
  },
];
