"use client";

import { Bell, User } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuthProfile } from "@/hooks/use-auth";
import api from "@/lib/api";

export function Header() {
  const { brandProfile, profile } = useAuthProfile();

  const { data: alerts } = useQuery({
    queryKey: ["unread-alerts", brandProfile?.id],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfile!.id}/alerts`, {
        params: { unread: true },
      });
      return res.data;
    },
    enabled: !!brandProfile?.id,
    refetchInterval: 60 * 1000,
  });

  const unreadCount = alerts?.length ?? 0;

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div className="text-sm text-muted-foreground">
        {brandProfile?.name && (
          <span>
            Monitoring for{" "}
            <span className="font-medium text-gray-900">{brandProfile.name}</span>
          </span>
        )}
      </div>
      <div className="flex items-center gap-4">
        <button className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>
        <div className="flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm text-gray-700">
          <User className="h-4 w-4" />
          <span>{profile?.name ?? "Demo User"}</span>
        </div>
      </div>
    </header>
  );
}
