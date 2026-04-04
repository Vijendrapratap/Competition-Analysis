"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const COLORS = ["#0d9488", "#2563eb", "#dc2626", "#d97706", "#7c3aed", "#059669", "#db2777", "#ea580c"];

interface SovEntry {
  brand_name: string;
  sov_pct: number;
}

interface Props {
  entries: SovEntry[];
}

export function ShareOfVoiceDonut({ entries }: Props) {
  const hasData = entries.length > 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Category Activity Share</CardTitle>
      </CardHeader>
      <CardContent>
        {hasData ? (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={entries}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="sov_pct"
                nameKey="brand_name"
              >
                {entries.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                iconSize={8}
                formatter={(value) => <span className="text-xs">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[220px] items-center justify-center text-sm text-muted-foreground">
            Share of voice data will appear after the first analysis cycle.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
