import type { FilterMode } from "@/types";

export interface CardConfig {
  type: string;
  layer: 1 | 2 | 3;
  position: "full_width" | "half_width" | "third_width";
  dataKey: string;
  visible: boolean;
  competitorId?: string;
  competitorName?: string;
}

export function getDashboardLayout(
  filterMode: FilterMode,
  kpis: string[],
  competitors: Array<{ id: string; name: string }>,
): CardConfig[] {
  const cards: CardConfig[] = [];

  // Layer 1 — Executive (always shown)
  cards.push({ type: "summary_strip", layer: 1, position: "full_width", dataKey: "summary", visible: true });
  cards.push({ type: "executive_summary", layer: 1, position: "full_width", dataKey: "executive_summary", visible: true });
  cards.push({ type: "alert_feed", layer: 1, position: "full_width", dataKey: "alerts", visible: true });

  // Layer 2 — Strategic (shown per KPI config)
  const kpiSet = new Set(kpis);

  const kpiCharts: Array<{ key: string; label: string }> = [
    { key: "posting_frequency", label: "Posting Frequency" },
    { key: "engagement_rate", label: "Engagement Rate" },
    { key: "follower_growth_delta", label: "Follower Growth" },
    { key: "posts_today", label: "New Posts Today" },
    { key: "engagement_latest", label: "Latest Engagement" },
    { key: "share_of_voice", label: "Share of Voice Trend" },
  ];

  for (const kpi of kpiCharts) {
    if (kpiSet.has(kpi.key)) {
      cards.push({
        type: "kpi_trend_chart",
        layer: 2,
        position: "half_width",
        dataKey: kpi.key,
        visible: true,
      });
    }
  }

  if (kpiSet.has("top_content_format") || kpiSet.has("content_pillars")) {
    cards.push({ type: "content_format_mix", layer: 2, position: "half_width", dataKey: "content_format_mix", visible: true });
  }

  if (kpiSet.has("share_of_voice") || kpiSet.has("share_of_voice_monthly")) {
    cards.push({ type: "share_of_voice_donut", layer: 2, position: "half_width", dataKey: "share_of_voice", visible: true });
  }

  if (kpiSet.has("messaging_themes") || kpiSet.has("positioning_shift")) {
    cards.push({ type: "messaging_themes", layer: 2, position: "half_width", dataKey: "messaging_themes", visible: true });
  }

  if (kpiSet.has("active_ads_count") || kpiSet.has("active_ads_change")) {
    cards.push({ type: "paid_media_summary", layer: 2, position: "half_width", dataKey: "paid_media_summary", visible: true });
  }

  if (kpiSet.has("competitive_whitespace")) {
    cards.push({ type: "opportunity_gap", layer: 2, position: "full_width", dataKey: "opportunities", visible: true });
  }

  // Layer 3 — Tactical (per competitor)
  for (const comp of competitors) {
    cards.push({
      type: "competitor_card",
      layer: 3,
      position: "half_width",
      dataKey: `competitor_${comp.id}`,
      visible: true,
      competitorId: comp.id,
      competitorName: comp.name,
    });
  }

  return cards;
}
