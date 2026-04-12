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
  Clock,
  Shield,
  Search,
  ExternalLink,
  Hash,
  Zap,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar,
} from "recharts";
import api from "@/lib/api";
import { MOCK_COMPETITOR_PROFILES, MOCK_COMPETITORS } from "@/lib/mock-data";

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

  // Try to find mock profile first (demo fallback)
  const mockProfile = MOCK_COMPETITOR_PROFILES[competitorId] ?? null;
  // Also try by name match from MOCK_COMPETITORS
  const mockCompetitor = MOCK_COMPETITORS.find((c) => c.id === competitorId) ?? null;
  // If not found by exact ID, fall back to first mock profile (handles slug-based IDs)
  const fallbackProfile = mockProfile ?? Object.values(MOCK_COMPETITOR_PROFILES)[0];

  const { data: profile, isError: profileError } = useQuery({
    queryKey: ["competitor-profile", competitorId, filterMode],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/profile`, {
        params: { filter_mode: filterMode },
      });
      return res.data;
    },
    enabled: !!competitorId,
    retry: false,
  });

  const { data: ads, isError: adsError } = useQuery({
    queryKey: ["competitor-ads", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/ads`);
      return res.data;
    },
    enabled: !!competitorId,
    retry: false,
  });

  const { data: changes, isError: changesError } = useQuery({
    queryKey: ["competitor-changes", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/changes`);
      return res.data;
    },
    enabled: !!competitorId,
    retry: false,
  });

  const { data: themes, isError: themesError } = useQuery({
    queryKey: ["competitor-themes", competitorId],
    queryFn: async () => {
      const res = await api.get(`/api/competitors/${competitorId}/themes`);
      return res.data;
    },
    enabled: !!competitorId,
    retry: false,
  });

  // Use API data when available, fall back to mock
  const isUsingMock = !profile || profileError;
  const p = isUsingMock ? fallbackProfile : { ...fallbackProfile, ...profile };

  const effectiveAds = (ads && !adsError) ? ads : (p.ads ?? []);
  const effectiveChanges = (changes && !changesError) ? changes : (p.changes ?? []);
  const effectiveThemes = (themes && !themesError) ? themes : (p.themes ?? []);

  const metrics = p.metrics || {};
  const formatMix = p.format_mix || [];
  const postingSchedule = p.posting_schedule || [];
  const platformBreakdown = p.platform_breakdown || {};
  const seo = p.seo || null;
  const socialCompetitor = mockCompetitor ?? null;

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard/competitors")}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Competitors
        </Button>
        {isUsingMock && (
          <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700 border border-amber-200">
            Demo data
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-gray-100 to-gray-200 text-sm font-bold text-gray-600">
          {p.name?.[0] ?? "?"}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">{p.name || "Competitor"}</h1>
            {p.tier && (
              <Badge className={tierColors[p.tier] || ""} variant="outline">
                {p.tier}
              </Badge>
            )}
          </div>
          {p.website && (
            <a href={p.website} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs text-muted-foreground hover:underline">
              <Globe className="h-3 w-3" /> {p.website.replace(/^https?:\/\//, "")}
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
        <div className="ml-auto flex items-center gap-2">
          {socialCompetitor?.social_profiles?.linkedin_url && (
            <a href={socialCompetitor.social_profiles.linkedin_url} target="_blank" rel="noreferrer">
              <Button variant="outline" size="sm" className="text-xs">LinkedIn</Button>
            </a>
          )}
          {socialCompetitor?.ad_library_url && (
            <a href={socialCompetitor.ad_library_url} target="_blank" rel="noreferrer">
              <Button variant="outline" size="sm" className="text-xs">Ad Library</Button>
            </a>
          )}
          <span className="text-xs text-muted-foreground capitalize">{filterMode} view</span>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="social">Social</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="paid">Paid Media</TabsTrigger>
          <TabsTrigger value="website">Website</TabsTrigger>
          <TabsTrigger value="messaging">Messaging</TabsTrigger>
        </TabsList>

        {/* ── OVERVIEW TAB ── */}
        <TabsContent value="overview" className="space-y-4 pt-4">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <MetricCard icon={Users} label="Followers" value={metrics.followers ?? "—"} delta={metrics.follower_delta} />
            <MetricCard icon={BarChart3} label="Posts This Period" value={metrics.posts_count ?? 0} delta={metrics.posts_delta} />
            <MetricCard icon={TrendingUp} label="Avg Engagement" value={metrics.avg_engagement ? `${(metrics.avg_engagement * 100).toFixed(1)}%` : "—"} />
            <MetricCard icon={Megaphone} label="Active Ads" value={metrics.active_ads ?? 0} />
          </div>

          {/* Best post */}
          {p.best_post && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-500" />
                  Best Performing Post
                  <Badge variant="outline" className="text-[10px] ml-auto capitalize">{p.best_post.platform}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">{p.best_post.caption}</p>
                <div className="mt-3 flex gap-6 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1 font-medium text-gray-800">
                    <span>❤️</span> {(p.best_post.likes ?? 0).toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1 font-medium text-gray-800">
                    <span>💬</span> {(p.best_post.comments ?? 0).toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1 font-medium text-gray-800">
                    <span>🔄</span> {(p.best_post.shares ?? 0).toLocaleString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick stats grid */}
          <div className="grid gap-4 md:grid-cols-2">
            {p.audience_language && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><MessageSquare className="h-4 w-4 text-teal-500" />Audience Language</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{p.audience_language}</p>
                </CardContent>
              </Card>
            )}
            {p.posting_times && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Clock className="h-4 w-4 text-blue-500" />Peak Posting Times</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{p.posting_times}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* CTA Patterns */}
          {p.cta_patterns && p.cta_patterns.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Common CTAs</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {p.cta_patterns.map((cta: string, i: number) => (
                    <span key={i} className="rounded-full bg-teal-50 border border-teal-200 px-3 py-1 text-xs font-medium text-teal-700">
                      {cta}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Data confidence */}
          {p.data_confidence != null && (
            <div className="flex items-center gap-2 rounded-lg border bg-gray-50 px-3 py-2 text-xs text-muted-foreground">
              <Shield className="h-3.5 w-3.5 text-green-500" />
              Data confidence: <span className="font-semibold text-gray-700">{p.data_confidence}%</span>
              <div className="ml-2 h-1.5 w-32 rounded-full bg-gray-200">
                <div className="h-1.5 rounded-full bg-green-500" style={{ width: `${p.data_confidence}%` }} />
              </div>
            </div>
          )}
        </TabsContent>

        {/* ── SOCIAL TAB ── */}
        <TabsContent value="social" className="space-y-4 pt-4">
          {Object.keys(platformBreakdown).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(platformBreakdown).map(([platform, data]: [string, any]) => (
                <Card key={platform}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm capitalize flex items-center gap-2">
                      <span className="h-6 w-6 rounded bg-gray-100 flex items-center justify-center text-xs">{platform[0].toUpperCase()}</span>
                      {platform}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-lg font-bold text-gray-900">{data.followers ?? "—"}</p>
                        <p className="text-[10px] text-muted-foreground">Followers</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-gray-900">{data.posts ?? 0}</p>
                        <p className="text-[10px] text-muted-foreground">Posts</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-gray-900">{data.engagement ? `${(data.engagement * 100).toFixed(1)}%` : "—"}</p>
                        <p className="text-[10px] text-muted-foreground">Eng. Rate</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : null}

          {/* Posting frequency chart */}
          {postingSchedule.length > 0 && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Posting Frequency by Day</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={postingSchedule} barSize={20}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="day" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Bar dataKey="posts" fill="#0d9488" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ── CONTENT TAB ── */}
        <TabsContent value="content" className="space-y-4 pt-4">
          <div className="grid gap-4 md:grid-cols-2">
            {formatMix.length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Content Format Mix</CardTitle></CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={formatMix}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {formatMix.map((_: any, i: number) => (
                          <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v: any) => [`${v}%`, "Share"]} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {p.top_hashtags && p.top_hashtags.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Hash className="h-4 w-4 text-blue-500" />
                    Top Hashtags
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {p.top_hashtags.map((h: string, i: number) => (
                      <span key={i} className="rounded-full bg-blue-50 border border-blue-100 px-3 py-1 text-xs text-blue-700">
                        #{h}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Best post in content tab too */}
          {p.best_post && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Top Performing Content</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-lg bg-gray-50 border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline" className="text-[10px] capitalize">{p.best_post.platform}</Badge>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">{p.best_post.caption}</p>
                  <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
                    <span>❤️ {(p.best_post.likes ?? 0).toLocaleString()}</span>
                    <span>💬 {(p.best_post.comments ?? 0).toLocaleString()}</span>
                    <span>🔄 {(p.best_post.shares ?? 0).toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {formatMix.length === 0 && !p.top_hashtags?.length && !p.best_post && (
            <EmptyState message="Content analysis will appear after collection." />
          )}
        </TabsContent>

        {/* ── PAID MEDIA TAB ── */}
        <TabsContent value="paid" className="space-y-4 pt-4">
          {effectiveAds.length > 0 ? (
            <>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <Megaphone className="h-4 w-4 text-amber-500" />
                  <span className="font-medium">{effectiveAds.length} active ads detected</span>
                </div>
                {socialCompetitor?.ad_library_url && (
                  <a href={socialCompetitor.ad_library_url} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm" className="text-xs gap-1">
                      View Full Ad Library <ExternalLink className="h-3 w-3" />
                    </Button>
                  </a>
                )}
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {effectiveAds.map((ad: any, i: number) => (
                  <Card key={i} className="flex flex-col">
                    <CardContent className="p-4 flex flex-col gap-2 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="rounded bg-amber-50 border border-amber-200 px-1.5 py-0.5 text-[10px] font-medium text-amber-700 uppercase">{ad.media_type}</span>
                        {ad.platform && (
                          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 capitalize">{ad.platform}</span>
                        )}
                      </div>
                      {ad.headline && <p className="text-sm font-semibold text-gray-900">{ad.headline}</p>}
                      {ad.body_text && <p className="text-xs text-gray-600 line-clamp-4 flex-1">{ad.body_text}</p>}
                      {ad.cta && (
                        <span className="mt-auto inline-block rounded-full bg-teal-600 px-3 py-1 text-[10px] font-semibold text-white self-start">
                          {ad.cta}
                        </span>
                      )}
                      {ad.first_seen && (
                        <p className="text-[10px] text-muted-foreground">
                          Running since {new Date(ad.first_seen).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          ) : (
            <EmptyState message="No active ads detected. This brand may focus on organic channels." />
          )}
        </TabsContent>

        {/* ── WEBSITE TAB ── */}
        <TabsContent value="website" className="space-y-4 pt-4">
          {/* SEO snapshot */}
          {seo && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Search className="h-4 w-4 text-purple-500" />
                  SEO Snapshot
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4 mb-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{seo.domain_authority}</p>
                    <p className="text-[10px] text-muted-foreground">Domain Authority</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{seo.organic_traffic_est}</p>
                    <p className="text-[10px] text-muted-foreground">Est. Organic Traffic</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{seo.top_keywords?.length ?? 0}</p>
                    <p className="text-[10px] text-muted-foreground">Tracked Keywords</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{seo.new_pages_this_week}</p>
                    <p className="text-[10px] text-muted-foreground">New Pages (7d)</p>
                  </div>
                </div>
                {seo.top_keywords && seo.top_keywords.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-2">Top Keywords</p>
                    <div className="flex flex-wrap gap-1.5">
                      {seo.top_keywords.map((kw: string, i: number) => (
                        <span key={i} className="rounded bg-purple-50 border border-purple-100 px-2 py-0.5 text-xs text-purple-700">{kw}</span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Website changes */}
          {effectiveChanges.length > 0 ? (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-700">Recent Website Changes</h3>
              {effectiveChanges.map((c: any, i: number) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-[10px] capitalize">{c.change_type}</Badge>
                      <Badge
                        className={`text-[10px] ${c.significance === "high" ? "bg-red-50 text-red-700 border-red-200" : c.significance === "medium" ? "bg-amber-50 text-amber-700 border-amber-200" : "bg-gray-50 text-gray-600 border-gray-200"}`}
                        variant="outline"
                      >
                        {c.significance} significance
                      </Badge>
                      <span className="ml-auto text-[10px] text-muted-foreground">
                        {c.detected_at ? new Date(c.detected_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : ""}
                      </span>
                    </div>
                    {c.before_value && (
                      <div className="mt-2 rounded bg-red-50 border border-red-100 p-2 text-xs">
                        <span className="font-medium text-red-600">Before: </span>
                        <span className="text-gray-700">{c.before_value}</span>
                      </div>
                    )}
                    {c.after_value && (
                      <div className="mt-1 rounded bg-green-50 border border-green-100 p-2 text-xs">
                        <span className="font-medium text-green-600">After: </span>
                        <span className="text-gray-700">{c.after_value}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            !seo && <EmptyState message="No website changes detected this period." />
          )}
        </TabsContent>

        {/* ── MESSAGING TAB ── */}
        <TabsContent value="messaging" className="space-y-4 pt-4">
          {effectiveThemes.length > 0 ? (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                {effectiveThemes.map((t: any, i: number) => (
                  <Card key={i}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-900">{t.theme}</span>
                        <span className="text-xs bg-gray-100 rounded px-1.5 py-0.5 text-gray-600">{t.frequency}× mentions</span>
                      </div>
                      {t.source && (
                        <span className="inline-block rounded bg-blue-50 border border-blue-100 px-1.5 py-0.5 text-[10px] text-blue-700 mb-2 capitalize">{t.source}</span>
                      )}
                      {t.evidence && t.evidence.length > 0 && (
                        <div className="space-y-1.5 mt-2">
                          {t.evidence.slice(0, 3).map((e: string, j: number) => (
                            <p key={j} className="text-xs text-gray-600 italic bg-gray-50 rounded px-2 py-1.5 border-l-2 border-teal-300 line-clamp-2">{e}</p>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Audience language + CTAs summary */}
              <div className="grid gap-4 md:grid-cols-2">
                {p.audience_language && (
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Tone & Voice</CardTitle></CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 leading-relaxed">{p.audience_language}</p>
                    </CardContent>
                  </Card>
                )}
                {p.cta_patterns && p.cta_patterns.length > 0 && (
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Recurring CTAs</CardTitle></CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {p.cta_patterns.map((cta: string, i: number) => (
                          <span key={i} className="rounded-full bg-teal-50 border border-teal-200 px-3 py-1 text-xs font-medium text-teal-700">{cta}</span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </>
          ) : (
            <EmptyState message="Messaging themes will appear after analysis completes." />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  delta,
}: {
  icon: any;
  label: string;
  value: string | number;
  delta?: number | null;
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <Icon className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">{label}</span>
        </div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {delta != null && (
          <span className={`flex items-center gap-1 text-xs mt-0.5 ${delta >= 0 ? "text-green-600" : "text-red-600"}`}>
            {delta >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {delta >= 0 ? "+" : ""}{delta.toFixed(1)}% vs last period
          </span>
        )}
      </CardContent>
    </Card>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border bg-card p-10 text-center">
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
