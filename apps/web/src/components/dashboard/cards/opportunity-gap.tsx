"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Lightbulb } from "lucide-react";

interface Opportunity {
  title: string;
  description: string;
}

interface Props {
  opportunities: Opportunity[];
}

export function OpportunityGapCard({ opportunities }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Lightbulb className="h-4 w-4 text-teal-500" />
          Competitive Opportunities
        </CardTitle>
      </CardHeader>
      <CardContent>
        {opportunities.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {opportunities.map((opp, i) => (
              <div key={i} className="rounded-lg border border-teal-100 bg-teal-50/50 p-3">
                <p className="text-sm font-medium text-teal-800">{opp.title}</p>
                <p className="mt-1 text-xs text-teal-600">{opp.description}</p>
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
