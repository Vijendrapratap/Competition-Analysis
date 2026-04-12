"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  ChevronDown, ChevronUp, Loader2, Check, Pencil,
  Globe, Facebook, Instagram, Linkedin, Youtube,
  Sparkles, AlertCircle
} from "lucide-react";
import api from "@/lib/api";

const INDUSTRIES = [
  "F&B / Food & Beverage", "Hospitality & Travel", "Retail & E-commerce",
  "Beauty & Wellness", "Fashion & Apparel", "Technology & SaaS",
  "Healthcare & Pharma", "Finance & Fintech", "Real Estate & Property",
  "Education & EdTech", "Automotive", "Media & Entertainment",
  "Logistics & Supply Chain", "Consumer Goods / FMCG", "Other",
];

const REGIONS = [
  "Thailand", "Singapore", "Malaysia", "Indonesia", "Philippines",
  "Vietnam", "Southeast Asia (multi-country)", "India", "Global", "Custom",
];

const AUDIENCE_EXAMPLES = [
  "Urban professionals aged 25–40 who value convenience and quality",
  "Young parents looking for safe, healthy products for their children",
  "SME business owners seeking cost-effective digital solutions",
];

interface PersonaData {
  brand_voice: string;
  core_audience: string;
  value_propositions: string[];
  market_positioning: string;
  key_channels: string[];
  content_style: string;
}

export default function BrandSetupPage() {
  const router = useRouter();
  const [showSocials, setShowSocials] = useState(false);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [brandId, setBrandId] = useState<string | null>(null);
  const [persona, setPersona] = useState<PersonaData | null>(null);
  const [personaStatus, setPersonaStatus] = useState<"idle" | "creating" | "generating" | "complete" | "failed">("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: "",
    website: "",
    industry: "",
    target_region: "",
    target_audience: "",
    facebook_url: "",
    instagram_handle: "",
    linkedin_url: "",
    youtube_url: "",
  });

  const set = (key: string, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const isValid = form.name.trim() && form.website.trim() && form.industry && form.target_region;

  const DEMO_PERSONA: PersonaData = {
    brand_voice: "Confident, helpful, and data-driven. Speaks to growth-minded professionals without jargon.",
    core_audience: "Mid-market B2B teams (50–500 employees) who are frustrated by their current tools and ready to switch.",
    value_propositions: [
      "Save 5+ hours per week with automated competitive monitoring",
      "Never miss a pricing change or product launch from competitors",
      "Turn competitive data into board-ready insights in one click",
    ],
    market_positioning: "The intelligence layer for growth teams who can't afford to be caught off-guard by competitors.",
    key_channels: ["LinkedIn", "Email Newsletter", "Google Search (SEO)", "Product Hunt"],
    content_style: "Educational and proof-driven. Leads with data and customer case studies. Avoids buzzwords.",
  };

  const handleDemoPersona = () => {
    setPersona(DEMO_PERSONA);
    setPersonaStatus("complete");
    // Create a local-only brand ID so the flow can continue
    setBrandId("demo-brand-00000000-0000-0000-0000-000000000003");
  };

  const createBrand = useMutation({
    mutationFn: async () => {
      const res = await api.post("/api/brands", {
        name: form.name.trim(),
        website: form.website.trim(),
        industry: form.industry,
        target_region: form.target_region,
        target_audience: form.target_audience.trim() || null,
        social_profiles: {
          facebook_url: form.facebook_url.trim() || null,
          instagram_handle: form.instagram_handle.trim() || null,
          linkedin_url: form.linkedin_url.trim() || null,
          youtube_url: form.youtube_url.trim() || null,
        },
      });
      return res.data;
    },
  });

  const generatePersona = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/api/brands/${id}/generate-persona`);
      return res.data;
    },
  });

  const handleGenerate = async () => {
    setErrorMsg(null);
    setPersonaStatus("creating");
    try {
      let id = brandId;
      if (!id) {
        const brand = await createBrand.mutateAsync();
        id = brand.id;
        setBrandId(id);
      }
      setPersonaStatus("generating");
      await generatePersona.mutateAsync(id!);
      pollPersona(id!);
    } catch (e: any) {
      setErrorMsg(e?.response?.data?.detail || "Failed to start persona generation. Is the API running?");
      setPersonaStatus("failed");
    }
  };

  const pollPersona = async (id: string) => {
    for (let i = 0; i < 40; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      try {
        const res = await api.get(`/api/brands/${id}/persona-status`);
        if (res.data.status === "complete" && res.data.persona) {
          setPersona(res.data.persona);
          setPersonaStatus("complete");
          return;
        }
        if (res.data.status === "failed") {
          setErrorMsg("Persona generation failed. Check your OpenRouter API key.");
          setPersonaStatus("failed");
          return;
        }
      } catch {
        // keep polling
      }
    }
    setErrorMsg("Persona generation timed out. Please retry.");
    setPersonaStatus("failed");
  };

  const handleSaveAndContinue = async () => {
    if (!brandId) return;
    // Demo mode — skip API patch
    if (brandId.startsWith("demo-brand-")) {
      router.push(`/onboarding/competitors?brand_id=${brandId}`);
      return;
    }
    try {
      if (persona) {
        await api.patch(`/api/brands/${brandId}`, { persona });
      }
      router.push(`/onboarding/competitors?brand_id=${brandId}`);
    } catch {
      router.push(`/onboarding/competitors?brand_id=${brandId}`);
    }
  };

  const handleSkipPersona = async () => {
    if (!brandId) {
      try {
        const brand = await createBrand.mutateAsync();
        setBrandId(brand.id);
        router.push(`/onboarding/competitors?brand_id=${brand.id}`);
      } catch {
        setErrorMsg("Failed to create brand. Is the API and database running?");
      }
    } else {
      router.push(`/onboarding/competitors?brand_id=${brandId}`);
    }
  };

  const updatePersonaField = (key: keyof PersonaData, value: string | string[]) => {
    if (!persona) return;
    setPersona({ ...persona, [key]: value });
  };

  const isGenerating = personaStatus === "creating" || personaStatus === "generating";

  return (
    <div className="space-y-6">
      <Stepper currentStep={0} />

      {/* Brand Details Card */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Tell us about your brand</CardTitle>
          <CardDescription>
            This information helps our AI understand your market position and generate accurate competitive insights.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Name + Website */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="name">Brand Name <span className="text-red-500">*</span></Label>
              <Input
                id="name"
                placeholder="e.g. Oishi, Grab, Central"
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="website">
                <Globe className="mr-1 inline h-3.5 w-3.5" />
                Website URL <span className="text-red-500">*</span>
              </Label>
              <Input
                id="website"
                type="url"
                placeholder="https://yourbrand.com"
                value={form.website}
                onChange={(e) => set("website", e.target.value)}
              />
            </div>
          </div>

          {/* Industry + Region */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Industry / Category <span className="text-red-500">*</span></Label>
              <Select value={form.industry} onValueChange={(v) => set("industry", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your industry" />
                </SelectTrigger>
                <SelectContent>
                  {INDUSTRIES.map((ind) => (
                    <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Primary Market / Region <span className="text-red-500">*</span></Label>
              <Select value={form.target_region} onValueChange={(v) => set("target_region", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your region" />
                </SelectTrigger>
                <SelectContent>
                  {REGIONS.map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Target Audience */}
          <div className="space-y-1.5">
            <Label htmlFor="audience">Target Audience</Label>
            <Textarea
              id="audience"
              placeholder={AUDIENCE_EXAMPLES[0]}
              value={form.target_audience}
              onChange={(e) => set("target_audience", e.target.value)}
              rows={2}
              className="resize-none"
            />
            <p className="text-xs text-slate-400">
              Describe your ideal customer — the more detail, the better the AI persona.
            </p>
          </div>

          {/* Social Profiles */}
          <div>
            <button
              type="button"
              onClick={() => setShowSocials(!showSocials)}
              className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              {showSocials ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              Social Media Profiles
              <span className="text-xs font-normal text-slate-400">(optional — improves data collection)</span>
            </button>

            {showSocials && (
              <div className="mt-3 grid gap-3 rounded-lg border bg-slate-50 p-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label htmlFor="fb" className="flex items-center gap-1.5 text-slate-600">
                    <Facebook className="h-3.5 w-3.5 text-blue-600" /> Facebook Page URL
                  </Label>
                  <Input id="fb" placeholder="https://facebook.com/yourpage" value={form.facebook_url} onChange={(e) => set("facebook_url", e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="ig" className="flex items-center gap-1.5 text-slate-600">
                    <Instagram className="h-3.5 w-3.5 text-pink-500" /> Instagram Handle
                  </Label>
                  <Input id="ig" placeholder="@yourhandle" value={form.instagram_handle} onChange={(e) => set("instagram_handle", e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="li" className="flex items-center gap-1.5 text-slate-600">
                    <Linkedin className="h-3.5 w-3.5 text-blue-700" /> LinkedIn Page URL
                  </Label>
                  <Input id="li" placeholder="https://linkedin.com/company/yours" value={form.linkedin_url} onChange={(e) => set("linkedin_url", e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="yt" className="flex items-center gap-1.5 text-slate-600">
                    <Youtube className="h-3.5 w-3.5 text-red-600" /> YouTube Channel URL
                  </Label>
                  <Input id="yt" placeholder="https://youtube.com/@yourchannel" value={form.youtube_url} onChange={(e) => set("youtube_url", e.target.value)} />
                </div>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              onClick={handleGenerate}
              disabled={!isValid || isGenerating}
              className="bg-teal-600 hover:bg-teal-700"
            >
              {isGenerating ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="mr-2 h-4 w-4" />
              )}
              {isGenerating ? "Analyzing your brand…" : "Generate AI Brand Persona"}
            </Button>
            {personaStatus === "idle" && (
              <button
                onClick={handleDemoPersona}
                className="text-sm text-teal-600 font-medium underline-offset-2 hover:underline"
              >
                Preview with sample persona
              </button>
            )}
            {isValid && personaStatus === "idle" && (
              <button
                onClick={handleSkipPersona}
                className="text-sm text-slate-400 underline-offset-2 hover:underline"
              >
                Skip for now
              </button>
            )}
          </div>

          {/* Error */}
          {errorMsg && (
            <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
              {errorMsg}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Generating skeleton */}
      {personaStatus === "generating" && (
        <Card className="shadow-sm">
          <CardContent className="p-6">
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-teal-700">
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing your brand against market data…
            </div>
            <div className="space-y-4">
              {["Brand Voice", "Core Audience", "Value Propositions", "Market Positioning", "Key Channels"].map((label) => (
                <div key={label}>
                  <div className="mb-1.5 h-3 w-28 animate-pulse rounded bg-slate-200" />
                  <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Persona result */}
      {personaStatus === "complete" && persona && (
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-teal-100">
                <Sparkles className="h-4 w-4 text-teal-600" />
              </div>
              <CardTitle className="text-base">AI Brand Persona</CardTitle>
            </div>
            <CardDescription>Review and edit any field before continuing.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <PersonaField
              label="Brand Voice"
              value={persona.brand_voice}
              editing={editingField === "brand_voice"}
              onEdit={() => setEditingField("brand_voice")}
              onSave={(v) => { updatePersonaField("brand_voice", v); setEditingField(null); }}
            />
            <PersonaField
              label="Core Audience"
              value={persona.core_audience}
              editing={editingField === "core_audience"}
              onEdit={() => setEditingField("core_audience")}
              onSave={(v) => { updatePersonaField("core_audience", v); setEditingField(null); }}
            />
            <div className="space-y-1.5">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Value Propositions</p>
              <ul className="space-y-1">
                {persona.value_propositions.map((vp, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-teal-500" />
                    {vp}
                  </li>
                ))}
              </ul>
            </div>
            <PersonaField
              label="Market Positioning"
              value={persona.market_positioning}
              editing={editingField === "market_positioning"}
              onEdit={() => setEditingField("market_positioning")}
              onSave={(v) => { updatePersonaField("market_positioning", v); setEditingField(null); }}
            />
            <div className="space-y-1.5">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Key Channels</p>
              <div className="flex flex-wrap gap-2">
                {persona.key_channels.map((ch, i) => (
                  <span key={i} className="rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
                    {ch}
                  </span>
                ))}
              </div>
            </div>
            <PersonaField
              label="Content Style"
              value={persona.content_style}
              editing={editingField === "content_style"}
              onEdit={() => setEditingField("content_style")}
              onSave={(v) => { updatePersonaField("content_style", v); setEditingField(null); }}
            />

            <div className="pt-2">
              <Button onClick={handleSaveAndContinue} className="bg-teal-600 hover:bg-teal-700">
                Save Persona & Continue
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Retry on failure */}
      {personaStatus === "failed" && (
        <div className="flex items-center justify-between rounded-lg border bg-white px-4 py-3">
          <p className="text-sm text-slate-600">Want to skip the persona and continue anyway?</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleGenerate}>Retry</Button>
            <Button size="sm" onClick={handleSkipPersona} className="bg-teal-600 hover:bg-teal-700">
              Skip & Continue
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function PersonaField({
  label,
  value,
  editing,
  onEdit,
  onSave,
}: {
  label: string;
  value: string;
  editing: boolean;
  onEdit: () => void;
  onSave: (value: string) => void;
}) {
  const [draft, setDraft] = useState(value);

  if (editing) {
    return (
      <div className="space-y-1.5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
        <div className="flex items-center gap-2">
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSave(draft)}
            autoFocus
          />
          <Button size="icon" variant="ghost" onClick={() => onSave(draft)}>
            <Check className="h-4 w-4 text-teal-600" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="group space-y-1.5">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-slate-700">{value}</p>
        <button
          onClick={onEdit}
          className="flex-shrink-0 rounded p-1 opacity-0 transition-opacity hover:bg-slate-100 group-hover:opacity-100"
        >
          <Pencil className="h-3.5 w-3.5 text-slate-400" />
        </button>
      </div>
    </div>
  );
}
