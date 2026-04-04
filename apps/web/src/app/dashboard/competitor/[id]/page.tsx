"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useFilterStore } from "@/stores/filter-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Users,
  MessageSquare,
  Megaphone,
  Globe,
  BarChart3,
  Calendar,
  Shield,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar,
} from "recharts";
import api from "@/lib/api";

const CHART_COLORS = ["#0d9488", "#2563eb", "#dc2626", "#d97706", "#7c3aed"];

const tierColors: Record<string, string> = {
  direct: "bg-red-50 text-red-700 border-red-200",
  indirect: "bg-amber-50 text-amber-700 border-amber-200",
  aspirational: "bg-purple-50 text-purple-700 border-purple-200",
  regional: "bg-blue-50 text-blue-700 border-blue-200",
};

export default function CompetitorDeepDivePage() {
  const params = useParams();
  const router = useRouter();
  const competitorId = params.id as string;
  const { filterMode } = useFilterStore();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["competitor-profile", competitorId, filterMode],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/profile`, {
        params: { filter_mode: filterMode },
      });
      return res.data;
    },
    enabled: !!competitorId,
  });

  const { data: posts } = useQuery({
    queryKey: ["competitor-posts", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/posts`, { params: { limit: 20 } });
      return res.data;
    },
    enabled: !!competitorId,
  });

  const { data: ads } = useQuery({
    queryKey: ["competitor-ads", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/ads`);
      return res.data;
    },
    enabled: !!competitorId,
  });

  const { data: changes } = useQuery({
    queryKey: ["competitor-changes", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/changes`);
      return res.data;
    },
    enabled: !!competitorId,
  });

  const { data: themes } = useQuery({
    queryKey: ["competitor-themes", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/themes`);
      return res.data;
    },
    enabled: !!competitorId,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
        <div className="h-64 animate-pulse rounded-lg border bg-gray-100" />
      </div>
    );
  }

  const p = profile || {};
  const metrics = p.metrics || {};
  const formatMix = p.format_mix || [];
  const postingSchedule = p.posting_schedule || [];

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Dashboard
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">{p.name || "Competitor"}</h1>
        {p.tier && <Badge className={tierColors[p.tier] || ""} variant="outline">{p.tier}</Badge>}
        <span className="text-xs text-muted-foreground capitalize">{filterMode} view</span>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="social">Social</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="paid">Paid Media</TabsTrigger>
          <TabsTrigger value="website">Website</TabsTrigger>
          <TabsTrigger value="messaging">Messaging</TabsTrigger>
        </TabsList>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <MetricCard icon={Users} label="Followers" value={metrics.followers ?? "—"} delta={metrics.follower_delta} />
            <MetricCard icon={BarChart3} label="Posts This Period" value={metrics.posts_count ?? 0} delta={metrics.posts_delta} />
            <MetricCard icon={TrendingUp} label="Avg Engagement" value={metrics.avg_engagement ? `${(metrics.avg_engagement * 100).toFixed(1)}%` : "—"} />
            <MetricCard icon={Megaphone} label="Active Ads" value={metrics.active_ads ?? 0} />
          </div>

          {/* Best post */}
          {p.best_post && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Best Performing Post</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 line-clamp-3">{p.best_post.caption}</p>
                <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                  <span>{p.best_post.likes} likes</span>
                  <span>{p.best_post.comments} comments</span>
                  <span>{p.best_post.shares} shares</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Data confidence */}
          {p.data_confidence != null && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Shield className="h-3.5 w-3.5" />
              Data quality: <span className="font-medium">{p.data_confidence}%</span>
            </div>
          )}
        </TabsContent>

        {/* SOCIAL TAB */}
        <TabsContent value="social" className="space-y-4">
          {p.platform_breakdown && Object.keys(p.platform_breakdown).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(p.platform_breakdown).map(([platform, data]: [string, any]) => (
                <Card key={platform}>
                  <CardHeader className="pb-2"><CardTitle className="text-sm capitalize">{platform}</CardTitle></CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div><p className="text-lg font-bold">{data.followers ?? "—"}</p><p className="text-muted-foreground">Followers</p></div>
                      <div><p className="text-lg font-bold">{data.posts ?? 0}</p><p className="text-muted-foreground">Posts</p></div>
                      <div><p className="text-lg font-bold">{data.engagement ? `${(data.engagement * 100).toFixed(1)}%` : "—"}</p><p className="text-muted-foreground">Eng. Rate</p></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState message="Social data will appear after collection completes." />
          )}

          {/* Recent posts */}
          {(posts || []).length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Recent Posts</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {(posts || []).map((post: any, i: number) => (
                    <div key={i} className="flex items-start gap-3 border-b pb-3 last:border-0">
                      <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium uppercase">{post.post_type}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-gray-700 line-clamp-2">{post.caption || "No caption"}</p>
                        <div className="mt-1 flex gap-3 text-[10px] text-muted-foreground">
                          <span>{post.likes ?? 0} likes</span>
                          <span>{post.comments ?? 0} comments</span>
                          <span>{post.published_at ? new Date(post.published_at).toLocaleDateString() : ""}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* CONTENT TAB */}
        <TabsContent value="content" className="space-y-4">
          {formatMix.length > 0 ? (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Content Format Mix</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={formatMix} cx="50%" cy="50%" outerRadius={70} dataKey="value" nameKey="name" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {formatMix.map((_: any, i: number) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          ) : (
            <EmptyState message="Content analysis will appear after collection." />
          )}

          {p.top_hashtags && p.top_hashtags.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Top Hashtags</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {p.top_hashtags.map((h: string, i: number) => (
                    <span key={i} className="rounded-full bg-gray-100 px-2.5 py-1 text-xs text-gray-700">#{h}</span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* PAID MEDIA TAB */}
        <TabsContent value="paid" className="space-y-4">
          {(ads || []).length > 0 ? (
            <>
              <div className="flex items-center gap-2 text-sm">
                <Megaphone className="h-4 w-4 text-amber-500" />
                <span className="font-medium">{(ads || []).length} active campaigns</span>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {(ads || []).map((ad: any, i: number) => (
                  <Card key={i}>
                    <CardContent className="p-4">
                      <span className="rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700 uppercase">{ad.media_type}</span>
                      {ad.headline && <p className="mt-2 text-sm font-medium">{ad.headline}</p>}
                      {ad.body_text && <p className="mt-1 text-xs text-gray-600 line-clamp-3">{ad.body_text}</p>}
                      {ad.cta && <span className="mt-2 inline-block rounded bg-teal-50 px-2 py-0.5 text-[10px] font-medium text-teal-700">{ad.cta}</span>}
                      <div className="mt-2 text-[10px] text-muted-foreground">
                        {ad.first_seen && <span>Since {new Date(ad.first_seen).toLocaleDateString()}</span>}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          ) : (
            <EmptyState message="No active ads detected. This brand may focus on organic channels." />
          )}
        </TabsContent>

        {/* WEBSITE TAB */}
        <TabsContent value="website" className="space-y-4">
          {(changes || []).length > 0 ? (
            <div className="space-y-3">
              {(changes || []).map((c: any, i: number) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px]">{c.change_type}</Badge>
                      <Badge variant={c.significance === "high" ? "destructive" : "secondary"} className="text-[10px]">{c.significance}</Badge>
                      <span className="ml-auto text-[10px] text-muted-foreground">
                        {c.detected_at ? new Date(c.detected_at).toLocaleDateString() : ""}
                      </span>
                    </div>
                    {c.before_value && (
                      <div className="mt-2 rounded bg-red-50 p-2 text-xs">
                        <span className="font-medium text-red-600">Before:</span> {c.before_value}
                      </div>
                    )}
                    {c.after_value && (
                      <div className="mt-1 rounded bg-green-50 p-2 text-xs">
                        <span className="font-medium text-green-600">After:</span> {c.after_value}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState message="No website changes detected this period." />
          )}
        </TabsContent>

        {/* MESSAGING TAB */}
        <TabsContent value="messaging" className="space-y-4">
          {(themes || []).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {(themes || []).map((t: any, i: number) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{t.theme}</span>
                      <span className="text-xs text-muted-foreground">{t.frequency}x</span>
                    </div>
                    {t.evidence && t.evidence.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {t.evidence.slice(0, 3).map((e: string, j: number) => (
                          <p key={j} className="text-xs text-gray-500 italic line-clamp-1">"{e}"</p>
                        ))}
                      </div>
                    )}
                    <span className="mt-2 inline-block rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">{t.source}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState message="Messaging themes will appear after analysis completes." />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, delta }: { icon: any; label: string; value: string | number; delta?: number | null }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">{label}</span>
        </div>
        <p className="mt-1 text-2xl font-bold">{value}</p>
        {delta != null && (
          <span className={`flex items-center gap-1 text-xs ${delta >= 0 ? "text-green-600" : "text-red-600"}`}>
            {delta >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {delta >= 0 ? "+" : ""}{delta.toFixed(1)}%
          </span>
        )}
      </CardContent>
    </Card>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border bg-card p-8 text-center">
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
