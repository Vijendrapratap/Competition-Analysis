"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user has completed onboarding
    const onboardingDone = localStorage.getItem("onboarding_complete");
    if (onboardingDone === "true") {
      router.replace("/dashboard");
    } else {
      // In dev mock mode, go straight to dashboard (no onboarding required)
      // Change this to "/onboarding/brand" to force onboarding flow
      router.replace("/dashboard");
    }
  }, [router]);

  return null;
}
