import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { Inter } from "next/font/google";
import { QueryProvider } from "@/components/layout/query-provider";
import { AuthTokenProvider } from "@/components/layout/auth-provider";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CompeteIQ — Competitive Intelligence Platform",
  description: "AI-powered competitive intelligence for marketing teams",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>
          <QueryProvider>
            <AuthTokenProvider>{children}</AuthTokenProvider>
          </QueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
