"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";

interface Theme {
  theme: string;
  frequency: number;
  competitors: string[];
}

interface Props {
  themes: Theme[];
}

export function MessagingThemesCard({ themes }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <MessageSquare className="h-4 w-4 text-pink-500" />
          Key Messaging Themes
        </CardTitle>
      </CardHeader>
      <CardContent>
        {themes.length > 0 ? (
          <div className="space-y-3">
            {themes.slice(0, 5).map((t, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{t.theme}</span>
                  <span className="text-xs text-muted-foreground">{t.frequency}x</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {t.competitors.map((c) => (
                    <span key={c} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">{c}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="py-4 text-center text-sm text-muted-foreground">
            Collecting messaging data — themes will appear after the first analysis cycle.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
