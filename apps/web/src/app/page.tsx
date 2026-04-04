import Link from "next/link";
import { auth } from "@clerk/nextjs";
import { redirect } from "next/navigation";

export default async function LandingPage() {
  const { userId } = auth();

  if (userId) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-teal-50 to-white">
      <div className="mx-auto max-w-3xl px-4 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">
          Compete<span className="text-teal-600">IQ</span>
        </h1>
        <p className="mt-4 text-xl text-gray-600">
          AI-powered competitive intelligence for marketing teams.
          Track competitors, decode their strategy, and find your edge.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            href="/sign-in"
            className="rounded-lg bg-teal-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-teal-500 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/sign-up"
            className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </div>
    </div>
  );
}
