"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface FormatData {
  competitor: string;
  reel: number;
  image: number;
  carousel: number;
  video: number;
  text: number;
}

interface Props {
  data: FormatData[];
}

const FORMAT_COLORS: Record<string, string> = {
  reel: "#7c3aed",
  image: "#2563eb",
  carousel: "#0d9488",
  video: "#dc2626",
  text: "#d97706",
};

export function ContentFormatMixCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Content Format Mix</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="competitor" type="category" tick={{ fontSize: 11 }} width={80} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
              {Object.entries(FORMAT_COLORS).map(([key, color]) => (
                <Bar key={key} dataKey={key} stackId="a" fill={color} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
            Content format data will appear after collection completes.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
