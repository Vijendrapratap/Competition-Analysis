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
    {
      label: "Competitors Tracked",
      value: data?.competitors_tracked ?? 0,
      icon: Users,
      color: "text-blue-600",
      bg: "bg-blue-50",
      borderColor: "border-blue-100",
    },
    {
      label: "Channels Monitored",
      value: data?.channels_monitored ?? 0,
      icon: Radio,
      color: "text-green-600",
      bg: "bg-green-50",
      borderColor: "border-green-100",
    },
    {
      label: "Active Alerts",
      value: data?.active_alerts ?? 0,
      icon: Bell,
      color: "text-amber-600",
      bg: "bg-amber-50",
      borderColor: "border-amber-100",
    },
    {
      label: "Rising Threat",
      value: data?.rising_threat ?? "—",
      icon: TrendingUp,
      color: "text-red-600",
      bg: "bg-red-50",
      borderColor: "border-red-100",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className={`rounded-xl border ${item.borderColor} ${item.bg} p-4 transition-shadow hover:shadow-sm`}
        >
          <div className="flex items-center gap-2">
            <div className={`rounded-md bg-white p-1.5 shadow-sm`}>
              <item.icon className={`h-4 w-4 ${item.color}`} />
            </div>
            <span className="text-xs font-medium text-gray-500">{item.label}</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-gray-900">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
