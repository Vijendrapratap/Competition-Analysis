"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface Step {
  label: string;
  href: string;
}

const STEPS: Step[] = [
  { label: "Brand", href: "/onboarding/brand" },
  { label: "Competitors", href: "/onboarding/competitors" },
  { label: "KPIs", href: "/onboarding/kpis" },
];

export function Stepper({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center justify-center gap-3 text-sm">
      {STEPS.map((step, i) => {
        const isComplete = i < currentStep;
        const isCurrent = i === currentStep;
        return (
          <div key={step.label} className="flex items-center gap-3">
            {i > 0 && <span className="h-px w-8 bg-gray-300" />}
            <span
              className={cn(
                "flex items-center gap-2",
                isCurrent && "font-medium text-teal-600",
                isComplete && "font-medium text-teal-600",
                !isCurrent && !isComplete && "text-gray-400"
              )}
            >
              <span
                className={cn(
                  "flex h-6 w-6 items-center justify-center rounded-full text-xs",
                  isCurrent && "bg-teal-600 text-white",
                  isComplete && "bg-teal-600 text-white",
                  !isCurrent && !isComplete && "bg-gray-200 text-gray-500"
                )}
              >
                {isComplete ? <Check className="h-3.5 w-3.5" /> : i + 1}
              </span>
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
