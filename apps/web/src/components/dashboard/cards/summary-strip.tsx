"use client";

import { Users, Radio, Bell, TrendingUp } from "lucide-react";

interface Props {
  data: {
    competitors_tracked: number;
    channels_monitored: number;
    active_alerts: number;
    rising_threat: string | null;
  } | null;
}

export function SummaryStripCard({ data }: Props) {
  const items = [
    { label: "Competitors Tracked", value: data?.competitors_tracked ?? 0, icon: Users, color: "text-blue-600" },
    { label: "Channels Monitored", value: data?.channels_monitored ?? 0, icon: Radio, color: "text-green-600" },
    { label: "Active Alerts", value: data?.active_alerts ?? 0, icon: Bell, color: "text-amber-600" },
    { label: "Rising Threat", value: data?.rising_threat ?? "—", icon: TrendingUp, color: "text-red-600" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2">
            <item.icon className={`h-4 w-4 ${item.color}`} />
            <span className="text-xs text-muted-foreground">{item.label}</span>
          </div>
          <p className="mt-1 text-2xl font-bold">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
