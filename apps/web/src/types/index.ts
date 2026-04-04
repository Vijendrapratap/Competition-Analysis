export type FilterMode = "daily" | "weekly" | "monthly";
export type CompetitorTier = "direct" | "indirect" | "aspirational" | "regional";
export type UserRole = "owner" | "editor" | "viewer";
export type AccountPlan = "starter" | "growth" | "enterprise";

export interface Competitor {
  id: string;
  name: string;
  website: string;
  tier: CompetitorTier;
  social_profiles: SocialProfiles;
  ad_library_url: string | null;
  ai_discovered: boolean;
  active: boolean;
}

export interface SocialProfiles {
  facebook_url?: string;
  instagram_handle?: string;
  linkedin_url?: string;
  youtube_url?: string;
}

export interface BrandProfile {
  id: string;
  name: string;
  website: string;
  industry: string;
  target_region: string;
  target_audience: string;
  persona: BrandPersona | null;
  social_profiles: SocialProfiles;
  setup_complete: boolean;
}

export interface BrandPersona {
  brand_voice: string;
  core_audience: string;
  value_propositions: string[];
  market_positioning: string;
  key_channels: string[];
  content_style: string;
}

export interface KpiConfig {
  id: string;
  filter_mode: FilterMode;
  kpi_pack: "default" | "custom";
  kpis: string[];
}

export interface Alert {
  id: string;
  competitor_id: string;
  alert_type: string;
  severity: "high" | "medium" | "low";
  title: string;
  description: string;
  triggered_at: string;
  read: boolean;
  dismissed: boolean;
}
