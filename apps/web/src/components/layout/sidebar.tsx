"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard,
  Users,
  FileText,
  Bell,
  Settings,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthProfile } from "@/hooks/use-auth";
import api from "@/lib/api";
import { MOCK_ALERTS } from "@/lib/mock-data";

export function Sidebar() {
  const pathname = usePathname();
  const { brandProfile } = useAuthProfile();
  const brandId = brandProfile?.id;

  const { data: alertData } = useQuery({
    queryKey: ["alerts-count", brandId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandId}/alerts`, { params: { unread: true } });
      return res.data;
    },
    enabled: !!brandId,
    retry: 1,
    staleTime: 60_000,
  });

  const unreadAlerts = (alertData && Array.isArray(alertData))
    ? alertData.filter((a: any) => !a.read).length
    : MOCK_ALERTS.filter((a) => !a.read).length;

  const navItems = [
    { href: "/dashboard",              label: "Dashboard",   icon: LayoutDashboard, badge: null },
    { href: "/dashboard/competitors",  label: "Competitors", icon: Users,           badge: null },
    { href: "/dashboard/reports",      label: "Reports",     icon: FileText,        badge: null },
    { href: "/dashboard/alerts",       label: "Alerts",      icon: Bell,            badge: unreadAlerts || null },
    { href: "/settings",               label: "Settings",    icon: Settings,        badge: null },
  ];

  return (
    <aside className="hidden w-64 border-r bg-white lg:flex lg:flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-teal-600">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">
            Compete<span className="text-teal-600">IQ</span>
          </span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href + "/")) ||
            (item.href === "/dashboard" && pathname === "/dashboard");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-teal-50 text-teal-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon className={cn("h-5 w-5", isActive ? "text-teal-600" : "text-gray-400")} />
              <span className="flex-1">{item.label}</span>
              {item.badge && item.badge > 0 && (
                <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">
                  {item.badge > 9 ? "9+" : item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom: brand pill */}
      <div className="border-t p-4">
        <div className="flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">
            {brandProfile?.name?.slice(0, 2).toUpperCase() || "DB"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-xs font-semibold text-gray-800">{brandProfile?.name || "Demo Brand"}</p>
            <p className="text-[10px] text-gray-400">Growth plan</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
