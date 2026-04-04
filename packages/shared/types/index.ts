export type FilterMode = "daily" | "weekly" | "monthly";
export type CompetitorTier = "direct" | "indirect" | "aspirational" | "regional";
export type UserRole = "owner" | "editor" | "viewer";
export type AccountPlan = "starter" | "growth" | "enterprise";
export type AlertSeverity = "high" | "medium" | "low";
export type PostType = "reel" | "image" | "carousel" | "video" | "text" | "story";
export type MediaType = "image" | "video" | "carousel";

export interface KpiDefinition {
  key: string;
  name: string;
  description: string;
  category: string;
}

export interface SocialProfiles {
  facebook_url?: string;
  instagram_handle?: string;
  linkedin_url?: string;
  youtube_url?: string;
}
