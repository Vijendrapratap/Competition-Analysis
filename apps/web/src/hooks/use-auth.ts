"use client";

import { useUser } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import api from "@/lib/api";

interface UserProfile {
  id: string;
  account_id: string;
  clerk_user_id: string;
  name: string;
  email: string;
  role: "owner" | "editor" | "viewer";
  account: {
    id: string;
    name: string;
    plan: "starter" | "growth" | "enterprise";
    created_at: string;
  };
  brand_profile: {
    id: string;
    name: string;
    setup_complete: boolean;
  } | null;
}

export function useAuthProfile() {
  const { user, isLoaded, isSignedIn } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  const {
    data: profile,
    isLoading: isProfileLoading,
    error,
  } = useQuery<UserProfile>({
    queryKey: ["user-profile"],
    queryFn: async () => {
      const res = await api.get("/api/users/me");
      return res.data;
    },
    enabled: !!isSignedIn,
    retry: false,
  });

  useEffect(() => {
    if (!isLoaded || isProfileLoading || !isSignedIn) return;
    if (pathname.startsWith("/onboarding")) return;

    if (profile && !profile.brand_profile?.setup_complete) {
      router.push("/onboarding/brand");
    }
  }, [isLoaded, isSignedIn, isProfileLoading, profile, pathname, router]);

  return {
    user,
    profile,
    isLoading: !isLoaded || (isSignedIn && isProfileLoading),
    isSignedIn,
    account: profile?.account ?? null,
    brandProfile: profile?.brand_profile ?? null,
  };
}
