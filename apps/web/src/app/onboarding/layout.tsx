export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-teal-50">
      <div className="mx-auto max-w-4xl px-4 py-10">
        {/* Logo */}
        <div className="mb-10 text-center">
          <a href="/" className="inline-block">
            <h1 className="text-3xl font-bold tracking-tight">
              Compete<span className="text-teal-600">IQ</span>
            </h1>
          </a>
          <p className="mt-1 text-sm text-slate-500">
            Set up your competitive intelligence workspace
          </p>
        </div>

        {children}
      </div>
    </div>
  );
}
