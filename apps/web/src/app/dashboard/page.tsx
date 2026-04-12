"use client";

import { useQuery } from "@tanstack/react-query";
import { useFilterStore } from "@/stores/filter-store";
import { useAuthProfile } from "@/hooks/use-auth";
import { getDashboardLayout } from "@/lib/dashboard-layout";
import { CardRenderer } from "@/components/dashboard/card-renderer";
import { Button } from "@/components/ui/button";
import { RefreshCw, Download, Loader2, Zap, Share2 } from "lucide-react";
import api from "@/lib/api";
import { MOCK_DASHBOARD_DATA } from "@/lib/mock-data";
import type { FilterMode } from "@/types";

const MODE_LABELS: Record<FilterMode, string> = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
};

export default function DashboardPage() {
  const { filterMode, setFilterMode } = useFilterStore();
  const { brandProfile } = useAuthProfile();
  const brandId = brandProfile?.id;

  const { data, isLoading, refetch, isFetching, isError } = useQuery({
    queryKey: ["dashboard", brandId, filterMode],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/dashboard`, {
        params: { filter_mode: filterMode },
      });
      return res.data;
    },
    enabled: !!brandId,
    staleTime: filterMode === "daily" ? 5 * 60 * 1000 : filterMode === "weekly" ? 30 * 60 * 1000 : 2 * 60 * 60 * 1000,
    retry: 1,
  });

  // Use mock data as fallback when API is unavailable (no DB in dev)
  const dashData = (data && !isError) ? data : MOCK_DASHBOARD_DATA;
  const isUsingMockData = !data || isError;

  // Build layout from KPI config
  const kpis = Object.keys(dashData.kpi_snapshots || {});
  // Default KPIs for weekly view when none configured
  const effectiveKpis = kpis.length > 0 ? kpis : [
    "posting_frequency", "engagement_rate", "follower_growth_delta",
    "share_of_voice", "messaging_themes", "active_ads_count", "top_content_format",
    "competitive_whitespace",
  ];
  const competitors = (dashData.competitor_cards || []).map((c: any) => ({
    id: c.competitor_id,
    name: c.name,
  }));
  const cards = getDashboardLayout(filterMode, effectiveKpis, competitors);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          {dashData.summary?.data_freshness && (
            <p className="mt-0.5 text-xs text-gray-400">Updated {dashData.summary.data_freshness}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {/* Filter Mode Toggle */}
          <div className="inline-flex rounded-lg border bg-white p-0.5 shadow-sm">
            {(["daily", "weekly", "monthly"] as FilterMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setFilterMode(mode)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  filterMode === mode
                    ? "bg-teal-600 text-white shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                {MODE_LABELS[mode]}
              </button>
            ))}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${isFetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Button variant="outline" size="sm" onClick={() => window.open(`/api/brands/${brandId}/report`, "_blank")}>
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Export PDF
          </Button>
          <Button variant="outline" size="sm" onClick={() => {
            navigator.clipboard?.writeText(window.location.href);
          }}>
            <Share2 className="mr-1.5 h-3.5 w-3.5" />
            Share
          </Button>
        </div>
      </div>

      {/* Mock data notice */}
      {isUsingMockData && !isLoading && (
        <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-4 py-2.5">
          <Zap className="h-4 w-4 text-blue-600 shrink-0" />
          <p className="text-sm text-blue-800">
            <span className="font-medium">Demo mode</span> — showing sample data. Connect a database to see live competitive intelligence.
          </p>
        </div>
      )}

      {/* Dashboard Content */}
      {isLoading ? (
        <DashboardSkeleton />
      ) : (
        <CardRenderer cards={cards} data={dashData} />
      )}
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg border bg-gray-100" />
        ))}
      </div>
      <div className="h-24 animate-pulse rounded-lg border bg-gray-100" />
      <div className="grid gap-4 md:grid-cols-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-64 animate-pulse rounded-lg border bg-gray-100" />
        ))}
      </div>
    </div>
  );
}
