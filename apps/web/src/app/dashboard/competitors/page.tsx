"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthProfile } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MOCK_COMPETITORS } from "@/lib/mock-data";
import {
  Plus, Search, Globe, ExternalLink, Linkedin, Instagram, Youtube,
  TrendingUp, Twitter, Filter,
} from "lucide-react";
import type { CompetitorTier } from "@/types";
import api from "@/lib/api";

const tierConfig: Record<CompetitorTier, { label: string; color: string; dot: string }> = {
  direct:       { label: "Direct",       color: "border-red-200 bg-red-50 text-red-700",         dot: "bg-red-500" },
  indirect:     { label: "Indirect",     color: "border-amber-200 bg-amber-50 text-amber-700",   dot: "bg-amber-500" },
  aspirational: { label: "Aspirational", color: "border-purple-200 bg-purple-50 text-purple-700", dot: "bg-purple-500" },
  regional:     { label: "Regional",     color: "border-blue-200 bg-blue-50 text-blue-700",       dot: "bg-blue-500" },
};

const TIER_ORDER: CompetitorTier[] = ["direct", "indirect", "aspirational", "regional"];

export default function CompetitorsPage() {
  const [search, setSearch] = useState("");
  const [activeTier, setActiveTier] = useState<CompetitorTier | "all">("all");
  const { brandProfile } = useAuthProfile();
  const brandId = brandProfile?.id;

  const { data, isError } = useQuery({
    queryKey: ["competitors", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/competitors`);
      return res.data;
    },
    enabled: !!brandId,
    retry: 1,
  });

  const competitors = (isError || !data?.length ? MOCK_COMPETITORS : data) as typeof MOCK_COMPETITORS;

  const filtered = competitors.filter((c) => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.website?.toLowerCase().includes(search.toLowerCase());
    const matchTier = activeTier === "all" || c.tier === activeTier;
    return matchSearch && matchTier;
  });

  const grouped = TIER_ORDER.reduce<Record<string, typeof filtered>>((acc, tier) => {
    const items = filtered.filter((c) => c.tier === tier);
    if (items.length) acc[tier] = items;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Competitors</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            {competitors.length} tracked · {competitors.filter((c) => c.active).length} active
          </p>
        </div>
        <Button size="sm">
          <Plus className="mr-1.5 h-4 w-4" />
          Add Competitor
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search competitors..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="flex items-center gap-1.5">
          <Filter className="h-4 w-4 text-gray-400" />
          {(["all", ...TIER_ORDER] as const).map((tier) => (
            <button
              key={tier}
              onClick={() => setActiveTier(tier as typeof activeTier)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                activeTier === tier
                  ? "bg-teal-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {tier === "all" ? "All" : tierConfig[tier].label}
            </button>
          ))}
        </div>
      </div>

      {/* Grouped competitor cards */}
      {Object.entries(grouped).map(([tier, items]) => {
        const cfg = tierConfig[tier as CompetitorTier];
        return (
          <div key={tier}>
            <div className="mb-3 flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${cfg.dot}`} />
              <h2 className="text-sm font-semibold text-gray-700">{cfg.label} Competitors</h2>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{items.length}</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {items.map((comp) => (
                <CompetitorCard key={comp.id} competitor={comp} />
              ))}
            </div>
          </div>
        );
      })}

      {filtered.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-gray-400">
          <Search className="h-8 w-8" />
          <p className="text-sm">No competitors match your filters.</p>
        </div>
      )}
    </div>
  );
}

function CompetitorCard({ competitor }: { competitor: typeof MOCK_COMPETITORS[0] }) {
  const cfg = tierConfig[competitor.tier];
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 truncate">{competitor.name}</h3>
              {competitor.ai_discovered && (
                <span className="rounded-full bg-teal-50 px-1.5 py-0.5 text-[10px] font-medium text-teal-600">
                  AI
                </span>
              )}
            </div>
            {competitor.website && (
              <a
                href={competitor.website}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-0.5 flex items-center gap-1 text-xs text-gray-400 hover:text-teal-600 truncate"
              >
                <Globe className="h-3 w-3 shrink-0" />
                {competitor.website.replace(/^https?:\/\//, "")}
              </a>
            )}
          </div>
          <Badge variant="outline" className={cfg.color}>{cfg.label}</Badge>
        </div>

        {/* Social links */}
        <div className="mt-3 flex items-center gap-2">
          {competitor.social_profiles?.linkedin_url && (
            <a href={competitor.social_profiles.linkedin_url} target="_blank" rel="noopener noreferrer"
               className="rounded p-1 text-gray-400 hover:bg-sky-50 hover:text-sky-600 transition-colors">
              <Linkedin className="h-4 w-4" />
            </a>
          )}
          {competitor.social_profiles?.instagram_handle && (
            <a href={`https://instagram.com/${competitor.social_profiles.instagram_handle}`} target="_blank" rel="noopener noreferrer"
               className="rounded p-1 text-gray-400 hover:bg-pink-50 hover:text-pink-600 transition-colors">
              <Instagram className="h-4 w-4" />
            </a>
          )}
          {(competitor.social_profiles as any)?.twitter_handle && (
            <a href={`https://twitter.com/${((competitor.social_profiles as any).twitter_handle as string).replace("@", "")}`} target="_blank" rel="noopener noreferrer"
               className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-800 transition-colors">
              <Twitter className="h-4 w-4" />
            </a>
          )}
          {competitor.ad_library_url && (
            <a href={competitor.ad_library_url} target="_blank" rel="noopener noreferrer"
               className="ml-auto flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700 hover:bg-amber-100 transition-colors">
              <ExternalLink className="h-3 w-3" />
              Ad Library
            </a>
          )}
        </div>

        {/* Action */}
        <div className="mt-3 border-t pt-3">
          <a
            href={`/dashboard/competitor/${competitor.id}`}
            className="flex items-center gap-1.5 text-xs font-medium text-teal-600 hover:text-teal-700"
          >
            <TrendingUp className="h-3.5 w-3.5" />
            View intelligence report
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
