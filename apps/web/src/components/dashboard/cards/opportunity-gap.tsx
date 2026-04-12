"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Lightbulb, ArrowUpRight } from "lucide-react";

interface Opportunity {
  title: string;
  description: string;
  effort?: "low" | "medium" | "high";
  impact?: "low" | "medium" | "high";
}

interface Props {
  opportunities: Opportunity[];
}

const effortColors = {
  low: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

const impactColors = {
  low: "bg-gray-100 text-gray-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-purple-100 text-purple-700",
};

export function OpportunityGapCard({ opportunities }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Lightbulb className="h-4 w-4 text-teal-500" />
          Competitive Whitespace & Opportunities
        </CardTitle>
      </CardHeader>
      <CardContent>
        {opportunities.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {opportunities.map((opp, i) => (
              <div key={i} className="group rounded-lg border border-teal-100 bg-teal-50/50 p-3 hover:border-teal-200 hover:bg-teal-50 transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-teal-800">{opp.title}</p>
                  <ArrowUpRight className="h-3.5 w-3.5 shrink-0 text-teal-400 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <p className="mt-1.5 text-xs text-teal-700 leading-relaxed">{opp.description}</p>
                {(opp.effort || opp.impact) && (
                  <div className="mt-2 flex gap-1.5">
                    {opp.impact && (
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${impactColors[opp.impact]}`}>
                        {opp.impact} impact
                      </span>
                    )}
                    {opp.effort && (
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${effortColors[opp.effort]}`}>
                        {opp.effort} effort
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="py-4 text-center text-sm text-muted-foreground">
            Opportunity analysis will appear after enough competitive data is collected.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
