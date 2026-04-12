"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthProfile } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MOCK_ALERTS } from "@/lib/mock-data";
import { AlertTriangle, Info, CheckCircle, Bell, BellOff, Filter, Check } from "lucide-react";
import api from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

type Severity = "high" | "medium" | "low";
type AlertType = "posting_spike" | "new_campaign" | "message_shift" | "pricing_change" | "sov_move" | "engagement_spike" | "paid_pause";

const severityConfig = {
  high:   { icon: AlertTriangle, bg: "bg-red-50",    border: "border-red-200",   text: "text-red-700",    dot: "bg-red-500",    label: "High" },
  medium: { icon: Info,          bg: "bg-amber-50",  border: "border-amber-200", text: "text-amber-700",  dot: "bg-amber-500",  label: "Medium" },
  low:    { icon: CheckCircle,   bg: "bg-green-50",  border: "border-green-200", text: "text-green-700",  dot: "bg-green-500",  label: "Low" },
};

const alertTypeLabels: Record<AlertType, string> = {
  posting_spike:    "Posting Spike",
  new_campaign:     "New Campaign",
  message_shift:    "Message Shift",
  pricing_change:   "Pricing Change",
  sov_move:         "SOV Move",
  engagement_spike: "Engagement Spike",
  paid_pause:       "Paid Pause",
};

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [showDismissed, setShowDismissed] = useState(false);
  const { brandProfile } = useAuthProfile();
  const brandId = brandProfile?.id;
  const qc = useQueryClient();

  const { data, isError } = useQuery({
    queryKey: ["alerts", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/alerts`);
      return res.data;
    },
    enabled: !!brandId,
    retry: 1,
  });

  const alerts = (isError || !data?.length ? MOCK_ALERTS : data) as typeof MOCK_ALERTS;

  const markRead = useMutation({
    mutationFn: async (alertId: string) => {
      await api.patch(`/api/alerts/${alertId}/read`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const filtered = alerts.filter((a) => {
    if (!showDismissed && a.dismissed) return false;
    if (severityFilter !== "all" && a.severity !== severityFilter) return false;
    return true;
  });

  const unreadCount = alerts.filter((a) => !a.read && !a.dismissed).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            {unreadCount > 0 ? (
              <span className="font-medium text-amber-700">{unreadCount} unread</span>
            ) : (
              "All caught up"
            )}{" "}
            · {alerts.length} total this period
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowDismissed((v) => !v)}>
            {showDismissed ? <Bell className="mr-1.5 h-4 w-4" /> : <BellOff className="mr-1.5 h-4 w-4" />}
            {showDismissed ? "Hide dismissed" : "Show dismissed"}
          </Button>
        </div>
      </div>

      {/* Severity filter */}
      <div className="flex items-center gap-1.5">
        <Filter className="h-4 w-4 text-gray-400" />
        {(["all", "high", "medium", "low"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setSeverityFilter(s)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              severityFilter === s
                ? "bg-teal-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {s === "all" ? "All" : severityConfig[s].label}
          </button>
        ))}
      </div>

      {/* Alert list */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-20 text-center text-gray-400">
            <Bell className="h-10 w-10 text-gray-300" />
            <div>
              <p className="font-medium text-gray-500">No alerts</p>
              <p className="text-sm">All clear — no competitive movement detected in this period.</p>
            </div>
          </div>
        ) : (
          filtered.map((alert) => {
            const cfg = severityConfig[alert.severity];
            const Icon = cfg.icon;
            return (
              <div
                key={alert.id}
                className={`rounded-xl border ${cfg.border} ${alert.read ? "opacity-60" : ""} ${alert.dismissed ? "opacity-40" : ""} transition-opacity`}
              >
                <div className={`rounded-xl ${cfg.bg} px-4 py-4`}>
                  <div className="flex items-start gap-3">
                    <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${cfg.text}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div>
                          <p className={`font-semibold text-sm ${cfg.text}`}>{alert.title}</p>
                          {(alert as any).competitor_name && (
                            <span className="text-xs text-gray-500">{(alert as any).competitor_name}</span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-xs text-gray-400">
                            {formatDistanceToNow(new Date(alert.triggered_at), { addSuffix: true })}
                          </span>
                          {!alert.read && (
                            <button
                              onClick={() => markRead.mutate(alert.id)}
                              className="flex items-center gap-1 rounded-full bg-white/70 px-2 py-0.5 text-[10px] font-medium text-gray-600 hover:bg-white transition-colors"
                            >
                              <Check className="h-3 w-3" />
                              Mark read
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="mt-1.5 text-sm text-gray-700">{alert.description}</p>
                      <div className="mt-2 flex gap-1.5">
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${cfg.bg} ${cfg.text} border ${cfg.border}`}>
                          {cfg.label} severity
                        </span>
                        <span className="rounded-full bg-white/60 px-2 py-0.5 text-[10px] font-medium text-gray-500">
                          {alertTypeLabels[alert.alert_type as AlertType] || alert.alert_type}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
