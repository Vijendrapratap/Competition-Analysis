"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Clock, Calendar, BarChart3, Loader2 } from "lucide-react";
import api from "@/lib/api";

type FilterMode = "daily" | "weekly" | "monthly";

interface KpiDef {
  key: string;
  name: string;
  description: string;
  category: string;
}

const DAILY_PACK: KpiDef[] = [
  { key: "posts_today", name: "New Posts Today", description: "Posts published in last 24h", category: "content" },
  { key: "engagement_latest", name: "Engagement on Latest Posts", description: "Likes, comments, shares within 24h", category: "engagement" },
  { key: "active_ads_change", name: "Active Ad Changes", description: "New campaigns launched or paused", category: "paid" },
  { key: "website_headline_change", name: "Website Changes", description: "Homepage headline or offer changes detected", category: "website" },
  { key: "new_content_published", name: "New Content Published", description: "Blog posts, landing pages, new URLs", category: "content" },
  { key: "pricing_change", name: "Price/Offer Changes", description: "Pricing or promotion page updates", category: "website" },
];

const WEEKLY_PACK: KpiDef[] = [
  { key: "posting_frequency", name: "Posting Frequency", description: "Total posts per week across channels", category: "content" },
  { key: "engagement_rate", name: "Engagement Rate", description: "Average engagement per post", category: "engagement" },
  { key: "top_content_format", name: "Content Format Mix", description: "% video vs image vs carousel", category: "content" },
  { key: "active_ads_count", name: "Active Paid Campaigns", description: "Number and themes of running ads", category: "paid" },
  { key: "messaging_themes", name: "Key Messaging Themes", description: "Top 3-5 recurring value propositions", category: "messaging" },
  { key: "follower_growth_delta", name: "Follower Growth", description: "Week-over-week growth per channel", category: "audience" },
  { key: "new_offer_activity", name: "Promotion Activity", description: "Discounts, seasonal campaigns, giveaways", category: "paid" },
  { key: "share_of_voice", name: "Share of Voice", description: "Estimated category activity share", category: "benchmark" },
];

const MONTHLY_PACK: KpiDef[] = [
  { key: "share_of_voice_monthly", name: "Share of Voice", description: "Monthly category position", category: "benchmark" },
  { key: "positioning_shift", name: "Positioning Shift", description: "Changes in core messaging or audience targeting", category: "messaging" },
  { key: "channel_investment_mix", name: "Channel Investment Mix", description: "Activity split across paid, organic, web", category: "benchmark" },
  { key: "content_pillars", name: "Content Pillar Analysis", description: "Recurring themes, topic clusters", category: "content" },
  { key: "audience_sentiment", name: "Audience Sentiment", description: "Comment tone and top reactions", category: "audience" },
  { key: "campaign_lifecycle", name: "Campaign Lifecycle", description: "Duration, format evolution", category: "paid" },
  { key: "seo_signals", name: "SEO & Web Signals", description: "Keyword movements, new pages", category: "website" },
  { key: "competitive_whitespace", name: "Competitive Whitespace", description: "Underserved topics, channels, segments", category: "benchmark" },
];

const PACKS: Record<FilterMode, KpiDef[]> = {
  daily: DAILY_PACK,
  weekly: WEEKLY_PACK,
  monthly: MONTHLY_PACK,
};

const MODE_CONFIG = [
  { mode: "daily" as FilterMode, label: "Daily", subtitle: "Tactical signals", icon: Clock },
  { mode: "weekly" as FilterMode, label: "Weekly", subtitle: "Campaign review", icon: Calendar },
  { mode: "monthly" as FilterMode, label: "Monthly", subtitle: "Strategic overview", icon: BarChart3 },
];

const categoryColors: Record<string, string> = {
  content: "bg-blue-50 text-blue-700",
  engagement: "bg-green-50 text-green-700",
  paid: "bg-amber-50 text-amber-700",
  website: "bg-purple-50 text-purple-700",
  messaging: "bg-pink-50 text-pink-700",
  audience: "bg-cyan-50 text-cyan-700",
  benchmark: "bg-teal-50 text-teal-700",
};

export default function KpiSelectionPage() {
  const router = useRouter();
  const params = useSearchParams();
  const brandId = params.get("brand_id");

  const [filterMode, setFilterMode] = useState<FilterMode>("weekly");
  const [enabledKpis, setEnabledKpis] = useState<Set<string>>(new Set());

  // Initialize KPIs when filter mode changes
  useEffect(() => {
    const pack = PACKS[filterMode];
    setEnabledKpis(new Set(pack.map((k) => k.key)));
  }, [filterMode]);

  // Poll collection job status
  const { data: collectionStatus } = useQuery({
    queryKey: ["collection-status", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/collection-history`);
      const jobs = res.data;
      if (jobs.length > 0) return jobs[0];
      return null;
    },
    enabled: !!brandId,
    refetchInterval: 5000,
  });

  const saveConfig = useMutation({
    mutationFn: async () => {
      await api.post(`/api/brands/${brandId}/kpi-config`, {
        filter_mode: filterMode,
        kpi_pack: "default",
        kpis: Array.from(enabledKpis),
      });
    },
  });

  const handleGenerate = async () => {
    try {
      await saveConfig.mutateAsync();
      router.push("/dashboard");
    } catch {
      // Try PATCH if POST fails (config already exists)
      try {
        await api.patch(`/api/brands/${brandId}/kpi-config`, {
          filter_mode: filterMode,
          kpis: Array.from(enabledKpis),
        });
        router.push("/dashboard");
      } catch {
        // proceed anyway
        router.push("/dashboard");
      }
    }
  };

  const toggleKpi = (key: string) => {
    const next = new Set(enabledKpis);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    setEnabledKpis(next);
  };

  const currentPack = PACKS[filterMode];

  if (!brandId) {
    router.push("/onboarding/brand");
    return null;
  }

  return (
    <div className="space-y-6">
      <Stepper currentStep={2} />

      {/* Filter Mode Selection */}
      <div className="grid gap-4 sm:grid-cols-3">
        {MODE_CONFIG.map(({ mode, label, subtitle, icon: Icon }) => (
          <button
            key={mode}
            onClick={() => setFilterMode(mode)}
            className={`rounded-lg border-2 p-4 text-left transition-colors ${
              filterMode === mode
                ? "border-teal-500 bg-teal-50"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <Icon className={`h-6 w-6 ${filterMode === mode ? "text-teal-600" : "text-gray-400"}`} />
            <p className={`mt-2 font-semibold ${filterMode === mode ? "text-teal-900" : "text-gray-900"}`}>
              {label}
            </p>
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          </button>
        ))}
      </div>

      {/* KPI Pack */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Recommended KPIs for {filterMode.charAt(0).toUpperCase() + filterMode.slice(1)} mode
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {currentPack.map((kpi) => (
              <div
                key={kpi.key}
                className="flex items-center justify-between rounded-lg border px-4 py-3"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{kpi.name}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${categoryColors[kpi.category] || "bg-gray-100 text-gray-700"}`}>
                      {kpi.category}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">{kpi.description}</p>
                </div>
                <Switch
                  checked={enabledKpis.has(kpi.key)}
                  onCheckedChange={() => toggleKpi(kpi.key)}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Collection Status Bar */}
      {collectionStatus && collectionStatus.status !== "completed" && (
        <div className="rounded-lg border bg-blue-50 px-4 py-3">
          <div className="flex items-center gap-2 text-sm">
            <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
            <span className="text-blue-800">
              Collecting data: {collectionStatus.competitors_completed || 0} of{" "}
              {collectionStatus.competitors_total || "?"} competitors complete...
            </span>
          </div>
          {collectionStatus.competitors_total > 0 && (
            <div className="mt-2 h-1.5 rounded-full bg-blue-200">
              <div
                className="h-1.5 rounded-full bg-blue-600 transition-all"
                style={{
                  width: `${((collectionStatus.competitors_completed || 0) / collectionStatus.competitors_total) * 100}%`,
                }}
              />
            </div>
          )}
        </div>
      )}

      <div className="flex justify-end">
        <Button onClick={handleGenerate} disabled={enabledKpis.size === 0 || saveConfig.isPending}>
          {saveConfig.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Generate Dashboard
        </Button>
      </div>
    </div>
  );
}
