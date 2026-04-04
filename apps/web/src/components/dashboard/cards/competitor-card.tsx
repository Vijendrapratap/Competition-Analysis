"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, TrendingUp, TrendingDown } from "lucide-react";

interface CompetitorMetrics {
  posts_this_period: number;
  engagement_rate: number;
  active_ads: number;
  follower_growth_pct: number | null;
  top_format: string | null;
  top_message: string | null;
}

interface Props {
  id: string;
  name: string;
  tier: string;
  metrics: CompetitorMetrics | null;
}

const tierColors: Record<string, string> = {
  direct: "bg-red-50 text-red-700 border-red-200",
  indirect: "bg-amber-50 text-amber-700 border-amber-200",
  aspirational: "bg-purple-50 text-purple-700 border-purple-200",
  regional: "bg-blue-50 text-blue-700 border-blue-200",
};

export function CompetitorCard({ id, name, tier, metrics }: Props) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <span>{name}</span>
            <Badge className={tierColors[tier] || ""} variant="outline">{tier}</Badge>
          </div>
          <Link
            href={`/dashboard/competitor/${id}`}
            className="flex items-center gap-1 text-xs font-normal text-teal-600 hover:text-teal-700"
          >
            View <ArrowRight className="h-3 w-3" />
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {metrics ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3 text-center">
              <Metric label="Posts" value={metrics.posts_this_period} />
              <Metric label="Eng. Rate" value={`${(metrics.engagement_rate * 100).toFixed(1)}%`} />
              <Metric label="Active Ads" value={metrics.active_ads} />
              <div>
                <p className="text-lg font-bold">
                  {metrics.follower_growth_pct != null ? (
                    <span className={`flex items-center justify-center gap-1 ${metrics.follower_growth_pct >= 0 ? "text-green-600" : "text-red-600"}`}>
                      {metrics.follower_growth_pct >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {metrics.follower_growth_pct >= 0 ? "+" : ""}{metrics.follower_growth_pct.toFixed(1)}%
                    </span>
                  ) : "—"}
                </p>
                <p className="text-[10px] text-muted-foreground">Growth</p>
              </div>
            </div>
            {metrics.top_format && (
              <p className="text-xs text-muted-foreground">
                Top format: <span className="font-medium text-gray-700">{metrics.top_format}</span>
              </p>
            )}
            {metrics.top_message && (
              <p className="text-xs text-muted-foreground">
                Key message: <span className="font-medium text-gray-700">{metrics.top_message}</span>
              </p>
            )}
          </div>
        ) : (
          <p className="py-4 text-center text-sm text-muted-foreground">
            Data collection in progress...
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <p className="text-lg font-bold">{value}</p>
      <p className="text-[10px] text-muted-foreground">{label}</p>
    </div>
  );
}
