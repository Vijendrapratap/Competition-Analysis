"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Clock, Calendar, BarChart3, Loader2, Target, Check } from "lucide-react";
import api from "@/lib/api";

type FilterMode = "daily" | "weekly" | "monthly";

interface KpiDef {
  key: string;
  name: string;
  description: string;
  category: string;
}

interface GoalDef {
  id: string;
  label: string;
  description: string;
  emoji: string;
  kpis: string[];
}

const ALL_KPIS: Record<string, KpiDef> = {
  posts_today:              { key: "posts_today",              name: "New Posts Today",          description: "Posts published in last 24h",                     category: "content" },
  engagement_latest:        { key: "engagement_latest",        name: "Engagement on Latest Posts", description: "Likes, comments, shares within 24h",             category: "engagement" },
  active_ads_change:        { key: "active_ads_change",        name: "Active Ad Changes",         description: "New campaigns launched or paused",               category: "paid" },
  website_headline_change:  { key: "website_headline_change",  name: "Website Changes",           description: "Homepage headline or offer changes detected",     category: "website" },
  new_content_published:    { key: "new_content_published",    name: "New Content Published",     description: "Blog posts, landing pages, new URLs",             category: "content" },
  pricing_change:           { key: "pricing_change",           name: "Price/Offer Changes",       description: "Pricing or promotion page updates",               category: "website" },
  posting_frequency:        { key: "posting_frequency",        name: "Posting Frequency",         description: "Total posts per week across channels",            category: "content" },
  engagement_rate:          { key: "engagement_rate",          name: "Engagement Rate",           description: "Average engagement per post",                     category: "engagement" },
  top_content_format:       { key: "top_content_format",       name: "Content Format Mix",        description: "% video vs image vs carousel",                   category: "content" },
  active_ads_count:         { key: "active_ads_count",         name: "Active Paid Campaigns",     description: "Number and themes of running ads",                category: "paid" },
  messaging_themes:         { key: "messaging_themes",         name: "Key Messaging Themes",      description: "Top 3-5 recurring value propositions",            category: "messaging" },
  follower_growth_delta:    { key: "follower_growth_delta",    name: "Follower Growth",           description: "Week-over-week growth per channel",               category: "audience" },
  new_offer_activity:       { key: "new_offer_activity",       name: "Promotion Activity",        description: "Discounts, seasonal campaigns, giveaways",        category: "paid" },
  share_of_voice:           { key: "share_of_voice",           name: "Share of Voice",            description: "Estimated category activity share",               category: "benchmark" },
  share_of_voice_monthly:   { key: "share_of_voice_monthly",   name: "Share of Voice",            description: "Monthly category position",                      category: "benchmark" },
  positioning_shift:        { key: "positioning_shift",        name: "Positioning Shift",         description: "Changes in core messaging or audience targeting",  category: "messaging" },
  channel_investment_mix:   { key: "channel_investment_mix",   name: "Channel Investment Mix",    description: "Activity split across paid, organic, web",         category: "benchmark" },
  content_pillars:          { key: "content_pillars",          name: "Content Pillar Analysis",   description: "Recurring themes, topic clusters",                 category: "content" },
  audience_sentiment:       { key: "audience_sentiment",       name: "Audience Sentiment",        description: "Comment tone and top reactions",                  category: "audience" },
  campaign_lifecycle:       { key: "campaign_lifecycle",       name: "Campaign Lifecycle",        description: "Duration, format evolution",                      category: "paid" },
  seo_signals:              { key: "seo_signals",              name: "SEO & Web Signals",         description: "Keyword movements, new pages",                    category: "website" },
  competitive_whitespace:   { key: "competitive_whitespace",   name: "Competitive Whitespace",    description: "Underserved topics, channels, segments",          category: "benchmark" },
};

const GOALS: GoalDef[] = [
  {
    id: "awareness",
    emoji: "📢",
    label: "Brand Awareness",
    description: "Track share of voice, reach, and category presence",
    kpis: ["share_of_voice", "posting_frequency", "follower_growth_delta", "top_content_format", "competitive_whitespace"],
  },
  {
    id: "engagement",
    emoji: "💬",
    label: "Social Engagement",
    description: "Benchmark content performance and audience resonance",
    kpis: ["engagement_rate", "top_content_format", "posting_frequency", "content_pillars", "audience_sentiment"],
  },
  {
    id: "paid",
    emoji: "💰",
    label: "Paid Acquisition",
    description: "Monitor competitor ad campaigns and landing page strategies",
    kpis: ["active_ads_count", "active_ads_change", "new_offer_activity", "campaign_lifecycle", "messaging_themes"],
  },
  {
    id: "messaging",
    emoji: "✍️",
    label: "Positioning & Messaging",
    description: "Track how competitors talk about their product and audience",
    kpis: ["messaging_themes", "positioning_shift", "content_pillars", "audience_sentiment", "share_of_voice"],
  },
  {
    id: "web",
    emoji: "🌐",
    label: "Website & SEO",
    description: "Detect landing page changes, new content, and keyword moves",
    kpis: ["seo_signals", "website_headline_change", "new_content_published", "pricing_change", "competitive_whitespace"],
  },
  {
    id: "benchmark",
    emoji: "📊",
    label: "Full Benchmarking",
    description: "The complete picture across all channels and dimensions",
    kpis: ["share_of_voice", "posting_frequency", "engagement_rate", "messaging_themes", "active_ads_count", "competitive_whitespace", "follower_growth_delta"],
  },
];

const PACKS_BY_MODE: Record<FilterMode, string[]> = {
  daily:   ["posts_today", "engagement_latest", "active_ads_change", "website_headline_change", "new_content_published", "pricing_change"],
  weekly:  ["posting_frequency", "engagement_rate", "top_content_format", "active_ads_count", "messaging_themes", "follower_growth_delta", "new_offer_activity", "share_of_voice"],
  monthly: ["share_of_voice_monthly", "positioning_shift", "channel_investment_mix", "content_pillars", "audience_sentiment", "campaign_lifecycle", "seo_signals", "competitive_whitespace"],
};

const MODE_CONFIG = [
  { mode: "daily" as FilterMode,   label: "Daily",   subtitle: "Tactical signals — react fast",   icon: Clock },
  { mode: "weekly" as FilterMode,  label: "Weekly",  subtitle: "Campaign review — stay ahead",     icon: Calendar },
  { mode: "monthly" as FilterMode, label: "Monthly", subtitle: "Strategic view — spot shifts",     icon: BarChart3 },
];

const categoryColors: Record<string, string> = {
  content:    "bg-blue-50 text-blue-700",
  engagement: "bg-green-50 text-green-700",
  paid:       "bg-amber-50 text-amber-700",
  website:    "bg-purple-50 text-purple-700",
  messaging:  "bg-pink-50 text-pink-700",
  audience:   "bg-cyan-50 text-cyan-700",
  benchmark:  "bg-teal-50 text-teal-700",
};

export default function KpiSelectionPage() {
  const router = useRouter();
  const params = useSearchParams();
  const brandId = params.get("brand_id");

  const [filterMode, setFilterMode] = useState<FilterMode>("weekly");
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [enabledKpis, setEnabledKpis] = useState<Set<string>>(new Set(PACKS_BY_MODE.weekly));
  const [showCustom, setShowCustom] = useState(false);

  // When goal changes, update enabled KPIs
  const handleGoalSelect = (goal: GoalDef) => {
    if (selectedGoal === goal.id) {
      setSelectedGoal(null);
      setEnabledKpis(new Set(PACKS_BY_MODE[filterMode]));
    } else {
      setSelectedGoal(goal.id);
      setEnabledKpis(new Set(goal.kpis));
    }
  };

  // When filter mode changes, reset to pack default if no goal selected
  useEffect(() => {
    if (!selectedGoal) {
      setEnabledKpis(new Set(PACKS_BY_MODE[filterMode]));
    }
  }, [filterMode, selectedGoal]);

  const saveConfig = useMutation({
    mutationFn: async () => {
      await api.post(`/api/brands/${brandId}/kpi-config`, {
        filter_mode: filterMode,
        kpi_pack: selectedGoal ? "custom" : "default",
        kpis: Array.from(enabledKpis),
      });
    },
  });

  const handleGenerate = async () => {
    // Save to localStorage so dashboard can use it even without API
    localStorage.setItem("kpi_config", JSON.stringify({
      filter_mode: filterMode,
      kpis: Array.from(enabledKpis),
    }));

    try {
      await saveConfig.mutateAsync();
    } catch {
      try {
        await api.patch(`/api/brands/${brandId}/kpi-config`, {
          filter_mode: filterMode,
          kpis: Array.from(enabledKpis),
        });
      } catch { /* proceed anyway */ }
    }
    router.push("/dashboard");
  };

  const toggleKpi = (key: string) => {
    const next = new Set(enabledKpis);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    setEnabledKpis(next);
  };

  // KPIs relevant to current filter mode
  const modePack = PACKS_BY_MODE[filterMode];
  const displayKpis = showCustom
    ? Object.values(ALL_KPIS).filter((k) => modePack.includes(k.key))
    : modePack.map((key) => ALL_KPIS[key]).filter(Boolean);

  if (!brandId) {
    router.push("/onboarding/brand");
    return null;
  }

  return (
    <div className="space-y-6">
      <Stepper currentStep={2} />

      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">What's your primary goal?</h2>
        <p className="mt-1.5 text-sm text-gray-500">
          Pick the goal that matters most — we'll recommend the right KPIs. You can customise afterwards.
        </p>
      </div>

      {/* Goal cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {GOALS.map((goal) => {
          const isSelected = selectedGoal === goal.id;
          return (
            <button
              key={goal.id}
              onClick={() => handleGoalSelect(goal)}
              className={`group relative rounded-xl border-2 p-4 text-left transition-all ${
                isSelected
                  ? "border-teal-500 bg-teal-50 shadow-sm"
                  : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm"
              }`}
            >
              {isSelected && (
                <span className="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-teal-600">
                  <Check className="h-3 w-3 text-white" />
                </span>
              )}
              <span className="text-2xl">{goal.emoji}</span>
              <p className={`mt-2 font-semibold ${isSelected ? "text-teal-900" : "text-gray-900"}`}>{goal.label}</p>
              <p className="mt-0.5 text-xs text-gray-500">{goal.description}</p>
            </button>
          );
        })}
      </div>

      {/* Time frame */}
      <div>
        <p className="mb-2 text-sm font-medium text-gray-700">How often do you review competitive data?</p>
        <div className="grid gap-3 sm:grid-cols-3">
          {MODE_CONFIG.map(({ mode, label, subtitle, icon: Icon }) => (
            <button
              key={mode}
              onClick={() => setFilterMode(mode)}
              className={`rounded-xl border-2 p-4 text-left transition-colors ${
                filterMode === mode
                  ? "border-teal-500 bg-teal-50"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <Icon className={`h-5 w-5 ${filterMode === mode ? "text-teal-600" : "text-gray-400"}`} />
              <p className={`mt-2 font-semibold text-sm ${filterMode === mode ? "text-teal-900" : "text-gray-900"}`}>{label}</p>
              <p className="text-xs text-gray-500">{subtitle}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Selected KPIs preview */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">
              {enabledKpis.size} KPIs selected
              {selectedGoal && (
                <span className="ml-2 text-xs font-normal text-teal-600">
                  · optimised for {GOALS.find((g) => g.id === selectedGoal)?.label}
                </span>
              )}
            </CardTitle>
            <button
              onClick={() => setShowCustom((v) => !v)}
              className="text-xs font-medium text-teal-600 hover:text-teal-700"
            >
              {showCustom ? "Hide details" : "Customise KPIs"}
            </button>
          </div>
        </CardHeader>
        {showCustom && (
          <CardContent>
            <div className="space-y-2">
              {displayKpis.map((kpi) => (
                <div
                  key={kpi.key}
                  className="flex items-center justify-between rounded-lg border px-3 py-2.5"
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
        )}
        {!showCustom && (
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {Array.from(enabledKpis).map((key) => {
                const kpi = ALL_KPIS[key];
                if (!kpi) return null;
                return (
                  <span key={key} className={`rounded-full px-2.5 py-1 text-xs font-medium ${categoryColors[kpi.category] || "bg-gray-100 text-gray-700"}`}>
                    {kpi.name}
                  </span>
                );
              })}
            </div>
          </CardContent>
        )}
      </Card>

      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push("/dashboard")}
          className="text-sm text-gray-400 hover:text-gray-600"
        >
          Skip for now
        </button>
        <Button onClick={handleGenerate} disabled={enabledKpis.size === 0 || saveConfig.isPending} size="lg">
          {saveConfig.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          <Target className="mr-2 h-4 w-4" />
          Generate Dashboard
        </Button>
      </div>
    </div>
  );
}
