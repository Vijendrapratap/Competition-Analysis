"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Plus,
  Loader2,
  Trash2,
  Search,
  Facebook,
  Instagram,
  Linkedin,
  Youtube,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import api from "@/lib/api";

const TIERS = [
  { value: "direct", label: "Direct", tip: "Head-to-head competitors in your market" },
  { value: "indirect", label: "Indirect", tip: "Different product, same customer" },
  { value: "aspirational", label: "Aspirational", tip: "Brands you admire and want to benchmark against" },
  { value: "regional", label: "Regional", tip: "Competitors specific to your geographic market" },
];

interface Competitor {
  id: string;
  name: string;
  website: string | null;
  tier: string;
  social_profiles: Record<string, string | null> | null;
  ad_library_url: string | null;
  ai_discovered: boolean;
  active: boolean;
}

interface DiscoveryResult {
  name: string;
  website: string | null;
  suggested_tier: string;
  reason: string;
  relevance_score: number;
}

export default function CompetitorSetupPage() {
  const router = useRouter();
  const params = useSearchParams();
  const brandId = params.get("brand_id");
  const queryClient = useQueryClient();

  const [showManual, setShowManual] = useState(false);
  const [showDiscovery, setShowDiscovery] = useState(false);
  const [selectedDiscovered, setSelectedDiscovered] = useState<Set<number>>(new Set());

  const [form, setForm] = useState({
    name: "",
    website: "",
    tier: "direct",
    facebook_url: "",
    instagram_handle: "",
    linkedin_url: "",
    youtube_url: "",
    ad_library_url: "",
  });

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
        name: data.name,
        website: data.website || null,
        tier: data.tier,
        social_profiles: {
          facebook_url: data.facebook_url || null,
          instagram_handle: data.instagram_handle || null,
          linkedin_url: data.linkedin_url || null,
          youtube_url: data.youtube_url || null,
        },
        ad_library_url: data.ad_library_url || null,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors", brandId] });
      setForm({ name: "", website: "", tier: "direct", facebook_url: "", instagram_handle: "", linkedin_url: "", youtube_url: "", ad_library_url: "" });
      setShowManual(false);
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

  const [discoveryResults, setDiscoveryResults] = useState<DiscoveryResult[]>([]);

  const handleDiscover = async () => {
    setShowDiscovery(true);
    try {
      const result = await discover.mutateAsync();
      setDiscoveryResults(result.suggestions || []);
    } catch {
      setDiscoveryResults([]);
    }
  };

  const addDiscovered = async () => {
    for (const idx of selectedDiscovered) {
      const r = discoveryResults[idx];
      if (r) {
        await addCompetitor.mutateAsync({
          name: r.name,
          website: r.website || "",
          tier: r.suggested_tier,
          facebook_url: "",
          instagram_handle: "",
          linkedin_url: "",
          youtube_url: "",
          ad_library_url: "",
        });
      }
    }
    setSelectedDiscovered(new Set());
    setShowDiscovery(false);
  };

  const handleCollectAndContinue = async () => {
    try {
      await api.post(`/api/brands/${brandId}/collect`);
      router.push(`/onboarding/kpis?brand_id=${brandId}`);
    } catch {
      // proceed anyway
      router.push(`/onboarding/kpis?brand_id=${brandId}`);
    }
  };

  const channelIcons = (c: Competitor) => {
    const sp = c.social_profiles || {};
    const icons = [];
    if (sp.facebook_url) icons.push(<Facebook key="fb" className="h-4 w-4 text-blue-600" />);
    if (sp.instagram_handle) icons.push(<Instagram key="ig" className="h-4 w-4 text-pink-500" />);
    if (sp.linkedin_url) icons.push(<Linkedin key="li" className="h-4 w-4 text-blue-700" />);
    if (sp.youtube_url) icons.push(<Youtube key="yt" className="h-4 w-4 text-red-600" />);
    return icons;
  };

  const tierColor = (tier: string) => {
    switch (tier) {
      case "direct": return "bg-red-50 text-red-700 border-red-200";
      case "indirect": return "bg-amber-50 text-amber-700 border-amber-200";
      case "aspirational": return "bg-purple-50 text-purple-700 border-purple-200";
      case "regional": return "bg-blue-50 text-blue-700 border-blue-200";
      default: return "";
    }
  };

  if (!brandId) {
    router.push("/onboarding/brand");
    return null;
  }

  return (
    <div className="space-y-6">
      <Stepper currentStep={1} />

      <div className="flex items-center gap-3">
        <Button variant="outline" onClick={() => setShowManual(!showManual)}>
          <Plus className="mr-2 h-4 w-4" /> Add Manually
        </Button>
        <Button variant="outline" onClick={handleDiscover} disabled={discover.isPending}>
          {discover.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Search className="mr-2 h-4 w-4" />
          )}
          Find My Competitors
        </Button>
      </div>

      {/* Manual Entry */}
      {showManual && (
        <Card>
          <CardHeader><CardTitle className="text-base">Add Competitor</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Brand Name *</Label>
                <Input placeholder="Competitor name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Website URL</Label>
                <Input placeholder="https://competitor.com" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Competitor Tier</Label>
                <Select value={form.tier} onValueChange={(v) => setForm({ ...form, tier: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {TIERS.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Ad Library URL</Label>
                <Input placeholder="Facebook Ad Library URL" value={form.ad_library_url} onChange={(e) => setForm({ ...form, ad_library_url: e.target.value })} />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Facebook Page URL</Label>
                <Input placeholder="https://facebook.com/page" value={form.facebook_url} onChange={(e) => setForm({ ...form, facebook_url: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Instagram Handle</Label>
                <Input placeholder="@handle" value={form.instagram_handle} onChange={(e) => setForm({ ...form, instagram_handle: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>LinkedIn Page URL</Label>
                <Input placeholder="https://linkedin.com/company/..." value={form.linkedin_url} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>YouTube Channel URL</Label>
                <Input placeholder="https://youtube.com/@channel" value={form.youtube_url} onChange={(e) => setForm({ ...form, youtube_url: e.target.value })} />
              </div>
            </div>
            <Button onClick={() => addCompetitor.mutate(form)} disabled={!form.name || addCompetitor.isPending}>
              {addCompetitor.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add Competitor
            </Button>
          </CardContent>
        </Card>
      )}

      {/* AI Discovery */}
      {showDiscovery && (
        <Card>
          <CardHeader><CardTitle className="text-base">AI Discovered Competitors</CardTitle></CardHeader>
          <CardContent>
            {discover.isPending ? (
              <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground justify-center">
                <Loader2 className="h-4 w-4 animate-spin" />
                Searching your competitive landscape...
              </div>
            ) : discoveryResults.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">
                No suggestions found yet. Discovery will improve as more data is collected.
              </p>
            ) : (
              <div className="space-y-3">
                {discoveryResults.map((r, i) => (
                  <label key={i} className="flex items-start gap-3 rounded-lg border p-3 cursor-pointer hover:bg-gray-50">
                    <input
                      type="checkbox"
                      checked={selectedDiscovered.has(i)}
                      onChange={(e) => {
                        const next = new Set(selectedDiscovered);
                        e.target.checked ? next.add(i) : next.delete(i);
                        setSelectedDiscovered(next);
                      }}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{r.name}</span>
                        <Badge className={tierColor(r.suggested_tier)} variant="outline">{r.suggested_tier}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{r.reason}</p>
                    </div>
                  </label>
                ))}
                <Button onClick={addDiscovered} disabled={selectedDiscovered.size === 0}>
                  Add Selected ({selectedDiscovered.size})
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Competitor List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Competitors ({competitors.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {competitors.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No competitors added yet. Add at least one to continue.
            </p>
          ) : (
            <div className="space-y-2">
              {competitors.map((c) => (
                <div key={c.id} className="flex items-center justify-between rounded-lg border px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-sm">{c.name}</span>
                    <Badge className={tierColor(c.tier)} variant="outline">{c.tier}</Badge>
                    <div className="flex items-center gap-1">{channelIcons(c)}</div>
                  </div>
                  <button
                    onClick={() => removeCompetitor.mutate(c.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={handleCollectAndContinue}
          disabled={competitors.length === 0}
        >
          Collect Data & Continue
        </Button>
      </div>

      {competitors.length > 0 && (
        <p className="text-xs text-center text-muted-foreground">
          We'll begin collecting data for {competitors.length} competitor{competitors.length > 1 ? "s" : ""}.
          This takes 5-15 minutes. You can configure your KPIs while we work.
        </p>
      )}
    </div>
  );
}
