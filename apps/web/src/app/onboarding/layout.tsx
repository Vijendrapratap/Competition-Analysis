export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold">
            Compete<span className="text-teal-600">IQ</span>
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Set up your competitive intelligence
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
