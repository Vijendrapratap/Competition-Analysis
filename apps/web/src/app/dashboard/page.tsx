"use client";

import { useQuery } from "@tanstack/react-query";
import { useFilterStore } from "@/stores/filter-store";
import { useAuthProfile } from "@/hooks/use-auth";
import { getDashboardLayout } from "@/lib/dashboard-layout";
import { CardRenderer } from "@/components/dashboard/card-renderer";
import { Button } from "@/components/ui/button";
import { RefreshCw, Download, Loader2 } from "lucide-react";
import api from "@/lib/api";
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

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["dashboard", brandId, filterMode],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/dashboard`, {
        params: { filter_mode: filterMode },
      });
      return res.data;
    },
    enabled: !!brandId,
    staleTime: filterMode === "daily" ? 5 * 60 * 1000 : filterMode === "weekly" ? 30 * 60 * 1000 : 2 * 60 * 60 * 1000,
  });

  const dashData = data || {
    summary: { competitors_tracked: 0, channels_monitored: 0, active_alerts: 0, rising_threat: null },
    executive_summary: null,
    kpi_snapshots: {},
    competitor_cards: [],
    messaging_themes: [],
    paid_media_summary: null,
    opportunities: [],
    alerts: [],
    share_of_voice: [],
    content_format_mix: [],
  };

  // Build layout from KPI config
  const kpis = dashData.kpi_snapshots ? Object.keys(dashData.kpi_snapshots) : [];
  const competitors = (dashData.competitor_cards || []).map((c: any) => ({
    id: c.competitor_id,
    name: c.name,
  }));
  const cards = getDashboardLayout(filterMode, kpis, competitors);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center gap-3">
          {/* Filter Mode Toggle */}
          <div className="inline-flex rounded-lg border bg-white p-0.5">
            {(["daily", "weekly", "monthly"] as FilterMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setFilterMode(mode)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  filterMode === mode
                    ? "bg-teal-600 text-white"
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

          <Button variant="outline" size="sm">
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Export PDF
          </Button>
        </div>
      </div>

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
      {/* Summary strip skeleton */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg border bg-gray-100" />
        ))}
      </div>
      {/* Executive summary skeleton */}
      <div className="h-24 animate-pulse rounded-lg border bg-gray-100" />
      {/* Chart skeletons */}
      <div className="grid gap-4 md:grid-cols-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-64 animate-pulse rounded-lg border bg-gray-100" />
        ))}
      </div>
    </div>
  );
}
