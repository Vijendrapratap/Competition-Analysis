export const INDUSTRIES = [
  "Hospitality",
  "F&B",
  "Retail",
  "Tech",
  "Healthcare",
  "Finance",
  "Real Estate",
  "Beauty & Wellness",
  "Education",
  "Automotive",
  "Other",
] as const;

export const REGIONS = [
  "Thailand",
  "Southeast Asia",
  "India",
  "Global",
  "Custom",
] as const;

export type Industry = (typeof INDUSTRIES)[number];
export type Region = (typeof REGIONS)[number];
