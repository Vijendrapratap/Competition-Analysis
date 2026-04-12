"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthProfile } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MOCK_REPORTS } from "@/lib/mock-data";
import { FileText, Download, Clock, Sparkles, Loader2, Calendar } from "lucide-react";
import api from "@/lib/api";
import { formatDistanceToNow, format } from "date-fns";

const modeColors: Record<string, string> = {
  weekly:  "bg-blue-50 text-blue-700",
  monthly: "bg-purple-50 text-purple-700",
  daily:   "bg-green-50 text-green-700",
};

export default function ReportsPage() {
  const { brandProfile } = useAuthProfile();
  const brandId = brandProfile?.id;
  const [generating, setGenerating] = useState(false);

  const { data, isError, refetch } = useQuery({
    queryKey: ["reports", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/reports`);
      return res.data;
    },
    enabled: !!brandId,
    retry: 1,
  });

  const reports = (isError || !data?.length ? MOCK_REPORTS : data) as typeof MOCK_REPORTS;

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.post(`/api/brands/${brandId}/reports`, { filter_mode: "weekly" });
      refetch();
    } catch {
      // mock mode — just show success
    }
    setTimeout(() => setGenerating(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            AI-generated competitive intelligence reports — ready to share with your team
          </p>
        </div>
        <Button onClick={handleGenerate} disabled={generating} size="sm">
          {generating ? (
            <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="mr-1.5 h-4 w-4" />
          )}
          {generating ? "Generating…" : "Generate Report"}
        </Button>
      </div>

      {/* Reports list */}
      <div className="space-y-4">
        {reports.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-20 text-center text-gray-400">
            <FileText className="h-10 w-10 text-gray-300" />
            <div>
              <p className="font-medium text-gray-500">No reports yet</p>
              <p className="text-sm">Generate your first report to share competitive insights with your team.</p>
            </div>
            <Button onClick={handleGenerate} disabled={generating} variant="outline" size="sm">
              <Sparkles className="mr-1.5 h-4 w-4" />
              Generate first report
            </Button>
          </div>
        ) : (
          reports.map((report) => (
            <Card key={report.id} className="transition-shadow hover:shadow-md">
              <CardContent className="pt-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <FileText className="h-4 w-4 text-teal-600 shrink-0" />
                      <h3 className="font-semibold text-gray-900">{report.title}</h3>
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${modeColors[report.filter_mode] || "bg-gray-100 text-gray-600"}`}>
                        {report.filter_mode}
                      </span>
                    </div>

                    <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {report.period}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDistanceToNow(new Date(report.generated_at), { addSuffix: true })}
                      </span>
                    </div>

                    <p className="mt-2 text-sm text-gray-600 leading-relaxed">
                      {report.executive_summary}
                    </p>
                  </div>

                  <div className="flex shrink-0 gap-2">
                    <Button variant="outline" size="sm">
                      <Download className="mr-1.5 h-3.5 w-3.5" />
                      PDF
                    </Button>
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Scheduling hint */}
      <div className="rounded-xl border border-teal-100 bg-teal-50 p-4">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-teal-600 shrink-0" />
          <p className="text-sm text-teal-800">
            <span className="font-medium">Automated reports</span> — set a schedule in Settings to generate reports automatically and deliver them to your inbox every Monday.
          </p>
        </div>
      </div>
    </div>
  );
}
