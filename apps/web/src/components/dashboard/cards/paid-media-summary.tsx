"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Megaphone, Circle } from "lucide-react";

interface Campaign {
  competitor: string;
  name: string;
  platforms: string[];
  theme: string;
  status: string;
  ad_count: number;
  first_seen: string;
}

interface PaidSummary {
  total_active_ads?: number;
  new_campaigns_this_week?: number;
  top_platforms?: string[];
  top_ctas?: string[];
  recent_campaigns?: Campaign[];
  // legacy shape
  new_creatives?: number;
  by_competitor?: Array<{ name: string; active_ads: number; new_ads: number }>;
}

interface Props {
  data: PaidSummary | null;
}

const platformColors: Record<string, string> = {
  Facebook: "bg-blue-100 text-blue-700",
  Instagram: "bg-pink-100 text-pink-700",
  LinkedIn: "bg-sky-100 text-sky-700",
  YouTube: "bg-red-100 text-red-700",
};

export function PaidMediaSummaryCard({ data }: Props) {
  const hasData = data && (data.total_active_ads || 0) > 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Megaphone className="h-4 w-4 text-amber-500" />
          Paid Media Intelligence
        </CardTitle>
      </CardHeader>
      <CardContent>
        {hasData ? (
          <div className="space-y-4">
            {/* Stats row */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-amber-50 p-3 text-center">
                <p className="text-2xl font-bold text-amber-700">{data!.total_active_ads}</p>
                <p className="text-xs text-amber-600">Active Ads</p>
              </div>
              <div className="rounded-lg bg-blue-50 p-3 text-center">
                <p className="text-2xl font-bold text-blue-700">{data!.new_campaigns_this_week ?? data!.new_creatives ?? 0}</p>
                <p className="text-xs text-blue-600">New Campaigns</p>
              </div>
            </div>

            {/* Top CTAs */}
            {data!.top_ctas && data!.top_ctas.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium text-gray-500">Top CTAs across competitors</p>
                <div className="flex flex-wrap gap-1.5">
                  {data!.top_ctas.map((cta) => (
                    <span key={cta} className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-800">
                      {cta}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recent campaigns */}
            {data!.recent_campaigns && data!.recent_campaigns.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500">Active campaigns</p>
                {data!.recent_campaigns.slice(0, 3).map((c, i) => (
                  <div key={i} className="rounded-lg border bg-gray-50 p-2.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-gray-800">{c.competitor}</span>
                      <div className="flex gap-1">
                        {c.platforms.slice(0, 2).map((p) => (
                          <span key={p} className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${platformColors[p] || "bg-gray-100 text-gray-600"}`}>
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="mt-1 text-[11px] text-gray-600">{c.theme}</p>
                    <p className="mt-0.5 text-[10px] text-gray-400">{c.ad_count} creatives · since {c.first_seen}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="py-4 text-center text-sm text-muted-foreground">
            No active ads detected. Competitors may focus on organic channels.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
