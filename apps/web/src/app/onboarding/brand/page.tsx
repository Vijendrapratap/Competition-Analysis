"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Stepper } from "@/components/setup/stepper";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronDown, ChevronUp, Loader2, Pencil, Check } from "lucide-react";
import api from "@/lib/api";

const INDUSTRIES = [
  "Hospitality", "F&B", "Retail", "Tech", "Healthcare",
  "Finance", "Real Estate", "Beauty & Wellness", "Education", "Automotive", "Other",
];
const REGIONS = ["Thailand", "Southeast Asia", "India", "Global", "Custom"];

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

  const [brandId, setBrandId] = useState<string | null>(null);
  const [persona, setPersona] = useState<PersonaData | null>(null);
  const [personaStatus, setPersonaStatus] = useState<string>("idle");

  const isValid = form.name && form.website && form.industry && form.target_region;

  const createBrand = useMutation({
    mutationFn: async () => {
      const res = await api.post("/api/brands", {
        name: form.name,
        website: form.website,
        industry: form.industry,
        target_region: form.target_region,
        target_audience: form.target_audience || null,
        social_profiles: {
          facebook_url: form.facebook_url || null,
          instagram_handle: form.instagram_handle || null,
          linkedin_url: form.linkedin_url || null,
          youtube_url: form.youtube_url || null,
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
      // Poll for completion
      pollPersona(id!);
    } catch {
      setPersonaStatus("failed");
    }
  };

  const pollPersona = async (id: string) => {
    const maxAttempts = 30;
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      try {
        const res = await api.get(`/api/brands/${id}/persona-status`);
        if (res.data.status === "complete" && res.data.persona) {
          setPersona(res.data.persona);
          setPersonaStatus("complete");
          return;
        }
        if (res.data.status === "failed") {
          setPersonaStatus("failed");
          return;
        }
      } catch {
        // Continue polling
      }
    }
    setPersonaStatus("failed");
  };

  const handleSaveAndContinue = async () => {
    if (!brandId) return;
    try {
      await api.patch(`/api/brands/${brandId}`, { persona });
      router.push(`/onboarding/competitors?brand_id=${brandId}`);
    } catch {
      // handle error
    }
  };

  const updatePersonaField = (key: keyof PersonaData, value: string | string[]) => {
    if (!persona) return;
    setPersona({ ...persona, [key]: value });
  };

  const set = (key: string, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="space-y-6">
      <Stepper currentStep={0} />

      <Card>
        <CardHeader>
          <CardTitle>Set up your brand</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">Brand Name *</Label>
              <Input
                id="name"
                placeholder="Acme Corp"
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="website">Website URL *</Label>
              <Input
                id="website"
                type="url"
                placeholder="https://example.com"
                value={form.website}
                onChange={(e) => set("website", e.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Industry / Category *</Label>
              <Select value={form.industry} onValueChange={(v) => set("industry", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  {INDUSTRIES.map((ind) => (
                    <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Target Region *</Label>
              <Select value={form.target_region} onValueChange={(v) => set("target_region", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select region" />
                </SelectTrigger>
                <SelectContent>
                  {REGIONS.map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="audience">Target Audience</Label>
            <Textarea
              id="audience"
              placeholder="Describe your ideal customer — age, interests, lifestyle"
              value={form.target_audience}
              onChange={(e) => set("target_audience", e.target.value)}
            />
          </div>

          {/* Social profiles collapsible */}
          <button
            type="button"
            onClick={() => setShowSocials(!showSocials)}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            {showSocials ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            Social Profiles (optional)
          </button>

          {showSocials && (
            <div className="grid gap-4 sm:grid-cols-2 rounded-lg border p-4">
              <div className="space-y-2">
                <Label htmlFor="fb">Facebook Page URL</Label>
                <Input id="fb" placeholder="https://facebook.com/yourpage" value={form.facebook_url} onChange={(e) => set("facebook_url", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ig">Instagram Handle</Label>
                <Input id="ig" placeholder="@yourhandle" value={form.instagram_handle} onChange={(e) => set("instagram_handle", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="li">LinkedIn Page URL</Label>
                <Input id="li" placeholder="https://linkedin.com/company/yours" value={form.linkedin_url} onChange={(e) => set("linkedin_url", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="yt">YouTube Channel URL</Label>
                <Input id="yt" placeholder="https://youtube.com/@yourchannel" value={form.youtube_url} onChange={(e) => set("youtube_url", e.target.value)} />
              </div>
            </div>
          )}

          <div className="pt-4">
            <Button
              onClick={handleGenerate}
              disabled={!isValid || personaStatus === "creating" || personaStatus === "generating"}
              className="w-full sm:w-auto"
            >
              {(personaStatus === "creating" || personaStatus === "generating") && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              {personaStatus === "generating" ? "Analyzing your brand..." : "Generate Brand Persona"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading skeleton */}
      {personaStatus === "generating" && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing your brand...
              </div>
              {["Brand Voice", "Core Audience", "Value Propositions", "Market Positioning", "Key Channels", "Content Style"].map((label) => (
                <div key={label} className="space-y-2">
                  <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
                  <div className="h-4 w-full animate-pulse rounded bg-gray-100" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Persona result */}
      {personaStatus === "complete" && persona && (
        <Card>
          <CardHeader>
            <CardTitle>Brand Persona</CardTitle>
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
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-500">Value Propositions</p>
              <ul className="list-inside list-disc text-sm">
                {persona.value_propositions.map((vp, i) => (
                  <li key={i}>{vp}</li>
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
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-500">Key Channels</p>
              <div className="flex flex-wrap gap-2">
                {persona.key_channels.map((ch, i) => (
                  <span key={i} className="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">{ch}</span>
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

            <div className="pt-4">
              <Button onClick={handleSaveAndContinue}>Save & Continue</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {personaStatus === "failed" && (
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-sm text-destructive">Persona generation failed. Please try again.</p>
            <Button variant="outline" className="mt-4" onClick={handleGenerate}>
              Retry
            </Button>
          </CardContent>
        </Card>
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
      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <div className="flex items-center gap-2">
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSave(draft)}
            autoFocus
          />
          <Button size="icon" variant="ghost" onClick={() => onSave(draft)}>
            <Check className="h-4 w-4" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="group space-y-1">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <div className="flex items-start justify-between">
        <p className="text-sm">{value}</p>
        <button onClick={onEdit} className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Pencil className="h-3.5 w-3.5 text-gray-400 hover:text-gray-600" />
        </button>
      </div>
    </div>
  );
}
