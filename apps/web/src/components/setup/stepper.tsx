"use client";

import { cn } from "@/lib/utils";
import { Check, Building2, Users, BarChart3 } from "lucide-react";

interface StepDef {
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STEPS: StepDef[] = [
  {
    label: "Your Brand",
    description: "Tell us about your brand so we can benchmark it accurately",
    icon: Building2,
  },
  {
    label: "Competitors",
    description: "Add the brands you want to track and analyze",
    icon: Users,
  },
  {
    label: "KPI Setup",
    description: "Choose what metrics matter most to your team",
    icon: BarChart3,
  },
];

export function Stepper({ currentStep }: { currentStep: number }) {
  return (
    <div className="mb-8">
      {/* Step bar */}
      <div className="flex items-start gap-0">
        {STEPS.map((step, i) => {
          const isComplete = i < currentStep;
          const isCurrent = i === currentStep;
          const Icon = step.icon;

          return (
            <div key={step.label} className="flex flex-1 items-start">
              {/* Connector line before */}
              {i > 0 && (
                <div className="mt-5 flex-shrink-0 w-full max-w-[60px]">
                  <div
                    className={cn(
                      "h-0.5 w-full transition-colors",
                      isComplete || isCurrent ? "bg-teal-500" : "bg-gray-200"
                    )}
                  />
                </div>
              )}

              {/* Step */}
              <div className="flex flex-col items-center text-center min-w-[100px]">
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors",
                    isCurrent && "border-teal-600 bg-teal-600 text-white shadow-md shadow-teal-200",
                    isComplete && "border-teal-500 bg-teal-500 text-white",
                    !isCurrent && !isComplete && "border-gray-200 bg-white text-gray-400"
                  )}
                >
                  {isComplete ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <p
                  className={cn(
                    "mt-2 text-xs font-semibold leading-tight",
                    isCurrent && "text-teal-700",
                    isComplete && "text-teal-600",
                    !isCurrent && !isComplete && "text-gray-400"
                  )}
                >
                  {step.label}
                </p>
                <p
                  className={cn(
                    "mt-0.5 hidden text-[10px] leading-tight sm:block",
                    isCurrent ? "text-slate-500" : "text-gray-300"
                  )}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Current step description for mobile */}
      <p className="mt-4 text-center text-sm text-slate-500 sm:hidden">
        {STEPS[currentStep]?.description}
      </p>
    </div>
  );
}
