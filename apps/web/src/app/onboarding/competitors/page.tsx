"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Plus, Loader2, Trash2, Search,
  Facebook, Instagram, Linkedin, Youtube,
  ChevronDown, ChevronUp, Sparkles, AlertCircle, Globe
} from "lucide-react";
import api from "@/lib/api";

const TIERS = [
  {
    value: "direct",
    label: "Direct",
    description: "Head-to-head in your market",
    color: "border-red-200 bg-red-50 text-red-700",
    dot: "bg-red-400",
  },
  {
    value: "indirect",
    label: "Indirect",
    description: "Different product, same customer",
    color: "border-amber-200 bg-amber-50 text-amber-700",
    dot: "bg-amber-400",
  },
  {
    value: "aspirational",
    label: "Aspirational",
    description: "Brands you benchmark against",
    color: "border-purple-200 bg-purple-50 text-purple-700",
    dot: "bg-purple-400",
  },
  {
    value: "regional",
    label: "Regional",
    description: "Geography-specific rivals",
    color: "border-blue-200 bg-blue-50 text-blue-700",
    dot: "bg-blue-400",
  },
];

interface Competitor {
  id: string;
  name: string;
  website: string | null;
  tier: string;
  social_profiles: Record<string, string | null> | null;
  ad_library_url: string | null;
  ai_discovered: boolean;
}

interface DiscoveryResult {
  name: string;
  website: string | null;
  suggested_tier: string;
  reason: string;
  relevance_score: number;
}

const EMPTY_FORM = {
  name: "",
  website: "",
  tier: "direct",
  facebook_url: "",
  instagram_handle: "",
  linkedin_url: "",
  youtube_url: "",
  ad_library_url: "",
};

export default function CompetitorSetupPage() {
  const router = useRouter();
  const params = useSearchParams();
  const brandId = params.get("brand_id");
  const queryClient = useQueryClient();

  const [showManual, setShowManual] = useState(false);
  const [showSocials, setShowSocials] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [discoveryResults, setDiscoveryResults] = useState<DiscoveryResult[]>([]);
  const [selectedDiscovered, setSelectedDiscovered] = useState<Set<number>>(new Set());
  const [showDiscovery, setShowDiscovery] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: competitors = [], isLoading } = useQuery<Competitor[]>({
    queryKey: ["competitors", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/competitors`);
      return res.data;
    },
    enabled: !!brandId,
  });

  const addCompetitor = useMutation({
    mutationFn: async (data: typeof form) => {
      const res = await api.post(`/api/brands/${brandId}/competitors`, {
        name: data.name.trim(),
        website: data.website.trim() || null,
        tier: data.tier,
        social_profiles: {
          facebook_url: data.facebook_url.trim() || null,
          instagram_handle: data.instagram_handle.trim() || null,
          linkedin_url: data.linkedin_url.trim() || null,
          youtube_url: data.youtube_url.trim() || null,
        },
        ad_library_url: data.ad_library_url.trim() || null,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors", brandId] });
      setForm(EMPTY_FORM);
      setShowManual(false);
      setShowSocials(false);
    },
    onError: (e: any) => {
      setErrorMsg(e?.response?.data?.detail || "Failed to add competitor.");
    },
  });

  const removeCompetitor = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/competitors/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors", brandId] }),
  });

  const discover = useMutation({
    mutationFn: async () => {
      const res = await api.post(`/api/brands/${brandId}/competitors/discover`);
      return res.data;
    },
  });

  const handleDiscover = async () => {
    setErrorMsg(null);
    setShowDiscovery(true);
    setDiscoveryResults([]);
    try {
      const result = await discover.mutateAsync();
      setDiscoveryResults(result.suggestions || []);
    } catch (e: any) {
      setErrorMsg(e?.response?.data?.detail || "AI discovery failed. Check your OpenRouter and Apify keys.");
      setShowDiscovery(false);
    }
  };

  const addDiscovered = async () => {
    for (const idx of selectedDiscovered) {
      const r = discoveryResults[idx];
      if (r) {
        await addCompetitor.mutateAsync({
          ...EMPTY_FORM,
          name: r.name,
          website: r.website || "",
          tier: r.suggested_tier,
        });
      }
    }
    setSelectedDiscovered(new Set());
    setShowDiscovery(false);
    setDiscoveryResults([]);
  };

  const handleContinue = () => {
    router.push(`/onboarding/kpis?brand_id=${brandId}`);
  };

  const tierDef = (tier: string) => TIERS.find((t) => t.value === tier) || TIERS[0];

  const socialIcons = (c: Competitor) => {
    const sp = c.social_profiles || {};
    return [
      sp.facebook_url && <Facebook key="fb" className="h-3.5 w-3.5 text-blue-600" />,
      sp.instagram_handle && <Instagram key="ig" className="h-3.5 w-3.5 text-pink-500" />,
      sp.linkedin_url && <Linkedin key="li" className="h-3.5 w-3.5 text-blue-700" />,
      sp.youtube_url && <Youtube key="yt" className="h-3.5 w-3.5 text-red-600" />,
    ].filter(Boolean);
  };

  if (!brandId) {
    router.push("/onboarding/brand");
    return null;
  }

  return (
    <div className="space-y-6">
      <Stepper currentStep={1} />

      {/* Header + actions */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Add your competitors</CardTitle>
          <CardDescription>
            Add at least one competitor to start tracking. You can always add more from Settings later.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              onClick={() => { setShowManual(!showManual); setShowDiscovery(false); }}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Manually
            </Button>
            <Button
              variant="outline"
              onClick={handleDiscover}
              disabled={discover.isPending}
            >
              {discover.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="mr-2 h-4 w-4 text-teal-600" />
              )}
              {discover.isPending ? "Searching…" : "Discover with AI"}
            </Button>
          </div>

          {errorMsg && (
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
              {errorMsg}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Manual form */}
      {showManual && (
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">New Competitor</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label>Brand Name <span className="text-red-500">*</span></Label>
                <Input
                  placeholder="e.g. Competitor Co."
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="flex items-center gap-1.5">
                  <Globe className="h-3.5 w-3.5" /> Website URL
                </Label>
                <Input
                  placeholder="https://competitor.com"
                  value={form.website}
                  onChange={(e) => setForm({ ...form, website: e.target.value })}
                />
              </div>
            </div>

            {/* Tier selection */}
            <div className="space-y-1.5">
              <Label>Competitor Type</Label>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {TIERS.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setForm({ ...form, tier: t.value })}
                    className={`rounded-lg border-2 p-3 text-left transition-all ${
                      form.tier === t.value
                        ? `${t.color} border-current`
                        : "border-gray-200 bg-white hover:border-gray-300"
                    }`}
                  >
                    <p className="text-xs font-semibold">{t.label}</p>
                    <p className="mt-0.5 text-[10px] leading-tight text-inherit opacity-70">
                      {t.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Ad library */}
            <div className="space-y-1.5">
              <Label>Facebook Ad Library URL <span className="text-xs text-slate-400">(for paid media tracking)</span></Label>
              <Input
                placeholder="https://facebook.com/ads/library/?id=..."
                value={form.ad_library_url}
                onChange={(e) => setForm({ ...form, ad_library_url: e.target.value })}
              />
            </div>

            {/* Social profiles */}
            <div>
              <button
                type="button"
                onClick={() => setShowSocials(!showSocials)}
                className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800"
              >
                {showSocials ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                Add social profiles
              </button>
              {showSocials && (
                <div className="mt-3 grid gap-3 rounded-lg border bg-slate-50 p-3 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-1.5 text-slate-600 text-xs">
                      <Facebook className="h-3.5 w-3.5 text-blue-600" /> Facebook Page
                    </Label>
                    <Input size={1} placeholder="https://facebook.com/page" value={form.facebook_url} onChange={(e) => setForm({ ...form, facebook_url: e.target.value })} />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-1.5 text-slate-600 text-xs">
                      <Instagram className="h-3.5 w-3.5 text-pink-500" /> Instagram Handle
                    </Label>
                    <Input size={1} placeholder="@handle" value={form.instagram_handle} onChange={(e) => setForm({ ...form, instagram_handle: e.target.value })} />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-1.5 text-slate-600 text-xs">
                      <Linkedin className="h-3.5 w-3.5 text-blue-700" /> LinkedIn
                    </Label>
                    <Input size={1} placeholder="https://linkedin.com/company/..." value={form.linkedin_url} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="flex items-center gap-1.5 text-slate-600 text-xs">
                      <Youtube className="h-3.5 w-3.5 text-red-600" /> YouTube
                    </Label>
                    <Input size={1} placeholder="https://youtube.com/@channel" value={form.youtube_url} onChange={(e) => setForm({ ...form, youtube_url: e.target.value })} />
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => addCompetitor.mutate(form)}
                disabled={!form.name.trim() || addCompetitor.isPending}
                className="bg-teal-600 hover:bg-teal-700"
              >
                {addCompetitor.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Competitor
              </Button>
              <Button variant="ghost" onClick={() => { setShowManual(false); setForm(EMPTY_FORM); }}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Discovery results */}
      {showDiscovery && (
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-teal-600" />
              AI-Discovered Competitors
            </CardTitle>
            <CardDescription>
              Based on your brand profile and industry. Select any to add them instantly.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {discover.isPending ? (
              <div className="flex flex-col items-center gap-3 py-10">
                <Loader2 className="h-6 w-6 animate-spin text-teal-600" />
                <p className="text-sm text-slate-500">Searching your competitive landscape…</p>
                <p className="text-xs text-slate-400">This takes about 15–30 seconds</p>
              </div>
            ) : discoveryResults.length === 0 ? (
              <p className="py-6 text-center text-sm text-slate-400">
                No suggestions found. Try adding competitors manually.
              </p>
            ) : (
              <div className="space-y-2">
                {discoveryResults.map((r, i) => {
                  const td = tierDef(r.suggested_tier);
                  const isSelected = selectedDiscovered.has(i);
                  return (
                    <label
                      key={i}
                      className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors ${
                        isSelected ? "border-teal-300 bg-teal-50" : "bg-white hover:bg-slate-50"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          const next = new Set(selectedDiscovered);
                          e.target.checked ? next.add(i) : next.delete(i);
                          setSelectedDiscovered(next);
                        }}
                        className="mt-1"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-medium text-sm">{r.name}</span>
                          <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${td.color}`}>
                            {td.label}
                          </span>
                          <span className="text-xs text-slate-400">
                            {r.relevance_score}% match
                          </span>
                        </div>
                        {r.website && (
                          <p className="text-xs text-slate-400 truncate">{r.website}</p>
                        )}
                        <p className="text-xs text-slate-500 mt-0.5">{r.reason}</p>
                      </div>
                    </label>
                  );
                })}

                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={addDiscovered}
                    disabled={selectedDiscovered.size === 0 || addCompetitor.isPending}
                    className="bg-teal-600 hover:bg-teal-700"
                  >
                    {addCompetitor.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Add Selected ({selectedDiscovered.size})
                  </Button>
                  <Button variant="ghost" onClick={() => { setShowDiscovery(false); setDiscoveryResults([]); }}>
                    Close
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Competitors list */}
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              Tracked Competitors
              {competitors.length > 0 && (
                <span className="ml-2 rounded-full bg-teal-100 px-2 py-0.5 text-xs font-semibold text-teal-700">
                  {competitors.length}
                </span>
              )}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2].map((i) => (
                <div key={i} className="h-14 animate-pulse rounded-lg bg-slate-100" />
              ))}
            </div>
          ) : competitors.length === 0 ? (
            <div className="py-10 text-center">
              <p className="text-sm text-slate-400">No competitors added yet.</p>
              <p className="text-xs text-slate-300 mt-1">Add at least one to continue.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {competitors.map((c) => {
                const td = tierDef(c.tier);
                const icons = socialIcons(c);
                return (
                  <div
                    key={c.id}
                    className="flex items-center gap-3 rounded-lg border bg-white px-4 py-3"
                  >
                    <div className={`h-2 w-2 flex-shrink-0 rounded-full ${td.dot}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium text-sm">{c.name}</span>
                        {c.ai_discovered && (
                          <span className="rounded-full bg-teal-50 px-1.5 py-0.5 text-[9px] font-semibold text-teal-600">
                            AI
                          </span>
                        )}
                        <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${td.color}`}>
                          {td.label}
                        </span>
                      </div>
                      {c.website && (
                        <p className="text-xs text-slate-400 truncate">{c.website}</p>
                      )}
                    </div>
                    {icons.length > 0 && (
                      <div className="flex items-center gap-1">{icons}</div>
                    )}
                    <button
                      onClick={() => removeCompetitor.mutate(c.id)}
                      className="rounded p-1 text-slate-300 hover:bg-red-50 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Continue */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-400">
          {competitors.length > 0
            ? `Ready to configure KPIs for ${competitors.length} competitor${competitors.length > 1 ? "s" : ""}.`
            : "Add at least one competitor to continue."}
        </p>
        <Button
          onClick={handleContinue}
          disabled={competitors.length === 0}
          className="bg-teal-600 hover:bg-teal-700"
        >
          Configure KPIs →
        </Button>
      </div>
    </div>
  );
}
