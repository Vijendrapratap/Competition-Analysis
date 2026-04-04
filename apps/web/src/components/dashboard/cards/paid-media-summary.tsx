"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Megaphone } from "lucide-react";

interface PaidSummary {
  total_active_ads: number;
  new_creatives: number;
  top_hooks: string[];
  by_competitor: Array<{ name: string; active_ads: number; new_ads: number }>;
}

interface Props {
  data: PaidSummary | null;
}

export function PaidMediaSummaryCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Megaphone className="h-4 w-4 text-amber-500" />
          Paid Media Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        {data && data.total_active_ads > 0 ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-amber-50 p-3 text-center">
                <p className="text-2xl font-bold text-amber-700">{data.total_active_ads}</p>
                <p className="text-xs text-amber-600">Active Ads</p>
              </div>
              <div className="rounded-lg bg-blue-50 p-3 text-center">
                <p className="text-2xl font-bold text-blue-700">{data.new_creatives}</p>
                <p className="text-xs text-blue-600">New This Period</p>
              </div>
            </div>
            {data.by_competitor.length > 0 && (
              <div className="space-y-1">
                {data.by_competitor.map((c) => (
                  <div key={c.name} className="flex items-center justify-between text-xs">
                    <span className="text-gray-700">{c.name}</span>
                    <span className="text-muted-foreground">{c.active_ads} active, {c.new_ads} new</span>
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
