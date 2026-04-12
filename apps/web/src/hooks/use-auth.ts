"use client";

// Mock auth — no Clerk keys in dev
// UUIDs must be valid format for API path validation
const MOCK_PROFILE = {
  id: "00000000-0000-0000-0000-000000000001",
  account_id: "00000000-0000-0000-0000-000000000002",
  clerk_user_id: "dev_user",
  name: "Demo User",
  email: "demo@competeiq.app",
  role: "owner" as const,
  account: {
    id: "00000000-0000-0000-0000-000000000002",
    name: "Demo Account",
    plan: "growth" as const,
    created_at: new Date().toISOString(),
  },
  brand_profile: {
    id: "00000000-0000-0000-0000-000000000003",
    name: "Demo Brand",
    setup_complete: true,
  },
};

export function useAuthProfile() {
  return {
    user: { fullName: "Demo User", primaryEmailAddress: { emailAddress: "demo@competeiq.app" } },
    profile: MOCK_PROFILE,
    isLoading: false,
    isSignedIn: true,
    account: MOCK_PROFILE.account,
    brandProfile: MOCK_PROFILE.brand_profile,
  };
}
