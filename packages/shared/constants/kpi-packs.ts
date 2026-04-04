import type { KpiDefinition } from "../types";

export const DAILY_PACK: KpiDefinition[] = [
  { key: "posts_today", name: "New Posts Today", description: "Posts published in last 24h", category: "content" },
  { key: "engagement_latest", name: "Engagement on Latest Posts", description: "Likes, comments, shares within 24h", category: "engagement" },
  { key: "active_ads_change", name: "Active Ad Changes", description: "New campaigns launched or paused", category: "paid" },
  { key: "website_headline_change", name: "Website Changes", description: "Homepage headline or offer changes detected", category: "website" },
  { key: "new_content_published", name: "New Content Published", description: "Blog posts, landing pages, new URLs", category: "content" },
  { key: "pricing_change", name: "Price/Offer Changes", description: "Pricing or promotion page updates", category: "website" },
];

export const WEEKLY_PACK: KpiDefinition[] = [
  { key: "posting_frequency", name: "Posting Frequency", description: "Total posts per week across channels", category: "content" },
  { key: "engagement_rate", name: "Engagement Rate", description: "Average engagement per post", category: "engagement" },
  { key: "top_content_format", name: "Content Format Mix", description: "% video vs image vs carousel", category: "content" },
  { key: "active_ads_count", name: "Active Paid Campaigns", description: "Number and themes of running ads", category: "paid" },
  { key: "messaging_themes", name: "Key Messaging Themes", description: "Top 3-5 recurring value propositions", category: "messaging" },
  { key: "follower_growth_delta", name: "Follower Growth", description: "Week-over-week growth per channel", category: "audience" },
  { key: "new_offer_activity", name: "Promotion Activity", description: "Discounts, seasonal campaigns, giveaways", category: "paid" },
  { key: "share_of_voice", name: "Share of Voice", description: "Estimated category activity share", category: "benchmark" },
];

export const MONTHLY_PACK: KpiDefinition[] = [
  { key: "share_of_voice_monthly", name: "Share of Voice", description: "Monthly category position", category: "benchmark" },
  { key: "positioning_shift", name: "Positioning Shift", description: "Changes in core messaging or audience targeting", category: "messaging" },
  { key: "channel_investment_mix", name: "Channel Investment Mix", description: "Activity split across paid, organic, web", category: "benchmark" },
  { key: "content_pillars", name: "Content Pillar Analysis", description: "Recurring themes, topic clusters", category: "content" },
  { key: "audience_sentiment", name: "Audience Sentiment", description: "Comment tone and top reactions", category: "audience" },
  { key: "campaign_lifecycle", name: "Campaign Lifecycle", description: "Duration, format evolution", category: "paid" },
  { key: "seo_signals", name: "SEO & Web Signals", description: "Keyword movements, new pages", category: "website" },
  { key: "competitive_whitespace", name: "Competitive Whitespace", description: "Underserved topics, channels, segments", category: "benchmark" },
];

export const KPI_PACKS = {
  daily: DAILY_PACK,
  weekly: WEEKLY_PACK,
  monthly: MONTHLY_PACK,
} as const;
