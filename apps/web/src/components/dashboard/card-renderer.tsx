"use client";

import type { CardConfig } from "@/lib/dashboard-layout";
import { SummaryStripCard } from "./cards/summary-strip";
import { ExecutiveSummaryCard } from "./cards/executive-summary";
import { AlertFeedCard } from "./cards/alert-feed";
import { KpiTrendChart } from "./cards/kpi-trend-chart";
import { ShareOfVoiceDonut } from "./cards/share-of-voice-donut";
import { MessagingThemesCard } from "./cards/messaging-themes";
import { ContentFormatMixCard } from "./cards/content-format-mix";
import { PaidMediaSummaryCard } from "./cards/paid-media-summary";
import { OpportunityGapCard } from "./cards/opportunity-gap";
import { CompetitorCard } from "./cards/competitor-card";

const KPI_LABELS: Record<string, string> = {
  posting_frequency: "Posting Frequency",
  engagement_rate: "Engagement Rate",
  follower_growth_delta: "Follower Growth",
  posts_today: "New Posts Today",
  engagement_latest: "Latest Engagement",
};

interface DashboardData {
  summary: { competitors_tracked: number; channels_monitored: number; active_alerts: number; rising_threat: string | null };
  executive_summary: string | null;
  kpi_snapshots: Record<string, Array<{ period: string; [key: string]: string | number }>>;
  competitor_cards: Array<{ competitor_id: string; name: string; tier: string; metrics: any }>;
  messaging_themes: Array<{ theme: string; frequency: number; competitors: string[] }>;
  paid_media_summary: any;
  opportunities: Array<{ title: string; description: string }>;
  alerts: any[];
  share_of_voice: Array<{ brand_name: string; sov_pct: number }>;
  content_format_mix: Array<{ competitor: string; reel: number; image: number; carousel: number; video: number; text: number }>;
}

interface Props {
  cards: CardConfig[];
  data: DashboardData;
}

export function CardRenderer({ cards, data }: Props) {
  const competitorNames = data.competitor_cards.map((c) => c.name);

  const renderCard = (card: CardConfig) => {
    switch (card.type) {
      case "summary_strip":
        return <SummaryStripCard data={data.summary} />;
      case "executive_summary":
        return <ExecutiveSummaryCard summary={data.executive_summary} />;
      case "alert_feed":
        return <AlertFeedCard alerts={data.alerts} />;
      case "kpi_trend_chart": {
        const chartData = data.kpi_snapshots[card.dataKey] || [];
        // Derive competitor keys from data rather than relying on explicit list
        const chartKeys = chartData.length > 0
          ? Object.keys(chartData[0]).filter((k) => k !== "period")
          : competitorNames;
        return (
          <KpiTrendChart
            title={KPI_LABELS[card.dataKey] || card.dataKey}
            data={chartData}
            competitors={chartKeys}
          />
        );
      }
      case "share_of_voice_donut":
        return <ShareOfVoiceDonut entries={data.share_of_voice || []} />;
      case "messaging_themes":
        return <MessagingThemesCard themes={data.messaging_themes} />;
      case "content_format_mix":
        return <ContentFormatMixCard data={data.content_format_mix || []} />;
      case "paid_media_summary":
        return <PaidMediaSummaryCard data={data.paid_media_summary} />;
      case "opportunity_gap":
        return <OpportunityGapCard opportunities={data.opportunities} />;
      case "competitor_card": {
        const comp = data.competitor_cards.find((c) => c.competitor_id === card.competitorId);
        if (!comp) return null;
        return (
          <CompetitorCard
            id={comp.competitor_id}
            name={comp.name}
            tier={comp.tier}
            metrics={comp.metrics}
          />
        );
      }
      default:
        return null;
    }
  };

  // Group cards by layer
  const layer1 = cards.filter((c) => c.layer === 1 && c.visible);
  const layer2 = cards.filter((c) => c.layer === 2 && c.visible);
  const layer3 = cards.filter((c) => c.layer === 3 && c.visible);

  return (
    <div className="space-y-6">
      {/* Layer 1 — Executive */}
      {layer1.map((card, i) => (
        <div key={`l1-${i}`}>{renderCard(card)}</div>
      ))}

      {/* Layer 2 — Strategic */}
      {layer2.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {layer2.map((card, i) => (
            <div key={`l2-${i}`} className={card.position === "full_width" ? "md:col-span-2" : ""}>
              {renderCard(card)}
            </div>
          ))}
        </div>
      )}

      {/* Layer 3 — Tactical (per competitor) */}
      {layer3.length > 0 && (
        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Competitors</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {layer3.map((card, i) => (
              <div key={`l3-${i}`}>{renderCard(card)}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
