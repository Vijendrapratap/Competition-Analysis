"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";

interface Theme {
  theme: string;
  frequency: number;
  competitors: string[];
  evidence?: string[];
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
          <div className="space-y-4">
            {themes.slice(0, 5).map((t, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-gray-900">{t.theme}</span>
                  <span className="text-xs bg-gray-100 rounded px-1.5 py-0.5 text-gray-600">{t.frequency}× mentions</span>
                </div>
                {t.competitors && t.competitors.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {t.competitors.map((c) => (
                      <span key={c} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">{c}</span>
                    ))}
                  </div>
                )}
                {t.evidence && t.evidence.length > 0 && (
                  <p className="text-xs text-gray-500 italic border-l-2 border-pink-200 pl-2 line-clamp-1">
                    "{t.evidence[0]}"
                  </p>
                )}
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
