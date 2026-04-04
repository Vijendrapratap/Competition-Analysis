"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText } from "lucide-react";

interface Props {
  summary: string | null;
}

export function ExecutiveSummaryCard({ summary }: Props) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <FileText className="h-4 w-4 text-slate-500" />
          Executive Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        {summary ? (
          <p className="text-sm leading-relaxed text-gray-700">{summary}</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Your executive summary will appear here after the first analysis cycle completes.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
