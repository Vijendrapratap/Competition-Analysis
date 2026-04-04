"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const CHART_COLORS = [
  "#0d9488", "#2563eb", "#dc2626", "#d97706", "#7c3aed",
  "#059669", "#db2777", "#ea580c", "#4f46e5", "#0891b2",
];

interface KpiDataPoint {
  period: string;
  [competitorName: string]: string | number;
}

interface Props {
  title: string;
  data: KpiDataPoint[];
  competitors: string[];
  deltaPct?: number | null;
}

export function KpiTrendChart({ title, data, competitors, deltaPct }: Props) {
  const hasData = data.length > 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between text-sm">
          <span>{title}</span>
          {deltaPct != null && (
            <span className={`flex items-center gap-1 text-xs font-medium ${deltaPct >= 0 ? "text-green-600" : "text-red-600"}`}>
              {deltaPct >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {deltaPct >= 0 ? "+" : ""}{deltaPct.toFixed(1)}%
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {hasData ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              {competitors.map((name, i) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={CHART_COLORS[i % CHART_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
            Trend data will appear after the first collection cycle.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
