"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bell, AlertTriangle, Info, CheckCircle } from "lucide-react";
import type { Alert } from "@/types";

interface Props {
  alerts: Alert[];
}

const severityConfig = {
  high: { icon: AlertTriangle, bg: "bg-red-50", border: "border-red-200", text: "text-red-700", dot: "bg-red-500" },
  medium: { icon: Info, bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", dot: "bg-amber-500" },
  low: { icon: CheckCircle, bg: "bg-green-50", border: "border-green-200", text: "text-green-700", dot: "bg-green-500" },
};

export function AlertFeedCard({ alerts }: Props) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Bell className="h-4 w-4 text-slate-500" />
          Alerts
          {alerts.length > 0 && (
            <span className="ml-auto rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
              {alerts.length}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            All clear! No competitive alerts this period.
          </p>
        ) : (
          <div className="space-y-2">
            {alerts.slice(0, 5).map((alert) => {
              const config = severityConfig[alert.severity];
              return (
                <div
                  key={alert.id}
                  className={`rounded-lg border ${config.border} ${config.bg} px-4 py-3`}
                >
                  <div className="flex items-start gap-3">
                    <span className={`mt-0.5 h-2 w-2 rounded-full ${config.dot} shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${config.text}`}>{alert.title}</p>
                      <p className="mt-0.5 text-xs text-gray-600">{alert.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
