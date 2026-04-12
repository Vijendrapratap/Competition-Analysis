"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthProfile } from "@/hooks/use-auth";
import api from "@/lib/api";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

// ── Profile Tab ──

function ProfileTab({ brandProfile, account }: { brandProfile: any; account: any }) {
  const { data: brand } = useQuery({
    queryKey: ["brand", brandProfile?.id],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfile.id}`);
      return res.data;
    },
    enabled: !!brandProfile?.id,
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Your organization details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Organization Name</Label>
            <Input value={account?.name || ""} disabled className="mt-1" />
          </div>
          <div>
            <Label>Plan</Label>
            <Badge variant="secondary" className="ml-2 capitalize">
              {account?.plan || "starter"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Brand Profile</CardTitle>
          <CardDescription>Your brand information used for competitive analysis</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Brand Name</Label>
            <Input value={brand?.name || ""} disabled className="mt-1" />
          </div>
          <div>
            <Label>Website</Label>
            <Input value={brand?.website || ""} disabled className="mt-1" />
          </div>
          <div>
            <Label>Industry</Label>
            <Input value={brand?.industry || ""} disabled className="mt-1" />
          </div>
          {brand?.persona && (
            <div>
              <Label>Brand Persona</Label>
              <p className="text-sm text-muted-foreground mt-1">
                <strong>Tone:</strong> {brand.persona.tone} | <strong>Audience:</strong>{" "}
                {brand.persona.target_audience} | <strong>USP:</strong> {brand.persona.usp}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Competitors Tab ──

function CompetitorsTab({ brandProfileId }: { brandProfileId: string }) {
  const queryClient = useQueryClient();

  const { data: competitors = [], isLoading } = useQuery({
    queryKey: ["competitors", brandProfileId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfileId}/competitors`);
      return res.data;
    },
  });

  const toggleActive = useMutation({
    mutationFn: async ({ id, active }: { id: string; active: boolean }) => {
      await api.patch(`/api/competitors/${id}`, { active });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
  });

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading competitors...</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Competitors</CardTitle>
        <CardDescription>Manage tracked competitors</CardDescription>
      </CardHeader>
      <CardContent>
        {competitors.length === 0 ? (
          <p className="text-sm text-muted-foreground">No competitors configured.</p>
        ) : (
          <div className="space-y-3">
            {competitors.map((c: any) => (
              <div key={c.id} className="flex items-center justify-between border rounded-lg p-3">
                <div>
                  <p className="font-medium">{c.name}</p>
                  <p className="text-sm text-muted-foreground">{c.website}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={c.tier === "primary" ? "default" : "secondary"}>
                    {c.tier}
                  </Badge>
                  <Switch
                    checked={c.active}
                    onCheckedChange={(checked) =>
                      toggleActive.mutate({ id: c.id, active: checked })
                    }
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── KPI Configuration Tab ──

function KpiConfigTab({ brandProfileId }: { brandProfileId: string }) {
  const queryClient = useQueryClient();

  const { data: config } = useQuery({
    queryKey: ["kpi-config", brandProfileId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfileId}/kpi-config`);
      return res.data;
    },
  });

  const updateConfig = useMutation({
    mutationFn: async (payload: any) => {
      await api.put(`/api/brands/${brandProfileId}/kpi-config`, payload);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["kpi-config"] }),
  });

  const filterModes = [
    { value: "daily", label: "Daily", desc: "Real-time monitoring for fast-moving markets" },
    { value: "weekly", label: "Weekly", desc: "Balanced view of competitive activity" },
    { value: "monthly", label: "Monthly", desc: "Strategic trends and long-term patterns" },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Collection Frequency</CardTitle>
          <CardDescription>How often data is collected and analyzed</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {filterModes.map((mode) => (
              <button
                key={mode.value}
                onClick={() => updateConfig.mutate({ filter_mode: mode.value, kpis: config?.kpis || {} })}
                className={`border rounded-lg p-4 text-left transition-colors ${
                  config?.filter_mode === mode.value
                    ? "border-teal-500 bg-teal-50 dark:bg-teal-950"
                    : "hover:border-gray-400"
                }`}
              >
                <p className="font-medium">{mode.label}</p>
                <p className="text-sm text-muted-foreground mt-1">{mode.desc}</p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {config?.kpis && (
        <Card>
          <CardHeader>
            <CardTitle>Active KPIs</CardTitle>
            <CardDescription>KPIs being tracked for this filter mode</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Object.entries(config.kpis)
                .filter(([, v]) => v)
                .map(([key]) => (
                  <Badge key={key} variant="secondary">
                    {key.replace(/_/g, " ")}
                  </Badge>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ── Alerts Tab ──

const BLUEPRINT_DEFAULTS = [
  { kpi_key: "posting_frequency", label: "Posting Spike", condition: "changes_by_pct", threshold: 40, severity: "medium", description: "Competitor posts >40% more than their baseline — indicates a campaign launch" },
  { kpi_key: "engagement_rate", label: "Engagement Surge", condition: "changes_by_pct", threshold: 200, severity: "high", description: "Engagement 3× higher than baseline — viral content or paid boost detected" },
  { kpi_key: "follower_growth", label: "Follower Growth Spike", condition: "changes_by_pct", threshold: 50, severity: "medium", description: "Unusually fast follower acquisition — possible paid campaign or influencer collab" },
  { kpi_key: "active_ads", label: "New Ad Campaign", condition: "new_detected", threshold: 1, severity: "high", description: "New paid ad creative detected in competitor's ad library" },
  { kpi_key: "website_change", label: "Pricing Page Change", condition: "new_detected", threshold: 1, severity: "high", description: "Competitor's pricing or homepage headline was updated" },
  { kpi_key: "keyword_ranking", label: "Keyword Rank Drop", condition: "drops_below", threshold: 10, severity: "medium", description: "Competitor gains top-10 ranking on a keyword you're targeting" },
];

function AlertsTab({ brandProfileId }: { brandProfileId: string }) {
  const queryClient = useQueryClient();
  const [newRule, setNewRule] = useState({ kpi_key: "", condition: "exceeds", threshold: "" });
  const [activeRules, setActiveRules] = useState<Record<string, boolean>>({
    posting_frequency: true,
    engagement_rate: true,
    active_ads: true,
    website_change: true,
  });

  const { data: rules = [] } = useQuery({
    queryKey: ["alert-rules", brandProfileId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfileId}/alert-rules`);
      return res.data;
    },
    retry: false,
  });

  const createRule = useMutation({
    mutationFn: async (payload: any) => {
      await api.post(`/api/brands/${brandProfileId}/alert-rules`, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
      setNewRule({ kpi_key: "", condition: "exceeds", threshold: "" });
    },
  });

  const deleteRule = useMutation({
    mutationFn: async (ruleId: string) => {
      await api.delete(`/api/alert-rules/${ruleId}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alert-rules"] }),
  });

  const severityColors: Record<string, string> = {
    high: "bg-red-50 text-red-700 border-red-200",
    medium: "bg-amber-50 text-amber-700 border-amber-200",
    low: "bg-gray-50 text-gray-600 border-gray-200",
  };

  return (
    <div className="space-y-6">
      {/* Recommended Defaults */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Alert Thresholds</CardTitle>
          <CardDescription>
            Industry-standard triggers based on competitive intelligence best practices. Toggle to enable or disable each.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {BLUEPRINT_DEFAULTS.map((rule) => (
            <div key={rule.kpi_key} className="flex items-start justify-between gap-4 rounded-lg border p-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-sm font-medium">{rule.label}</span>
                  <Badge variant="outline" className={`text-[10px] ${severityColors[rule.severity]}`}>
                    {rule.severity}
                  </Badge>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {rule.condition === "new_detected" ? "on detection" :
                     rule.condition === "drops_below" ? `< ${rule.threshold}` :
                     `> ${rule.threshold}%`}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{rule.description}</p>
              </div>
              <Switch
                checked={activeRules[rule.kpi_key] ?? false}
                onCheckedChange={(v) => setActiveRules((prev) => ({ ...prev, [rule.kpi_key]: v }))}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Custom Rules */}
      <Card>
        <CardHeader>
          <CardTitle>Custom Alert Rules</CardTitle>
          <CardDescription>
            Add your own rules for any metric
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {rules.length > 0 && (
            <div className="space-y-2">
              {rules.map((rule: any) => (
                <div key={rule.id} className="flex items-center justify-between border rounded-lg p-3">
                  <div>
                    <p className="text-sm font-medium">
                      {rule.kpi_key.replace(/_/g, " ")} {rule.condition} {rule.threshold}
                    </p>
                    {rule.competitor_id && (
                      <p className="text-xs text-muted-foreground">
                        Competitor: {rule.competitor_id}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteRule.mutate(rule.id)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="border rounded-lg p-4 space-y-3 bg-gray-50">
            <p className="text-sm font-medium">Add Custom Rule</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <Label>Metric</Label>
                <Input
                  placeholder="e.g. engagement_rate"
                  value={newRule.kpi_key}
                  onChange={(e) => setNewRule({ ...newRule, kpi_key: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Condition</Label>
                <select
                  className="mt-1 w-full rounded-md border px-3 py-2 text-sm bg-white"
                  value={newRule.condition}
                  onChange={(e) => setNewRule({ ...newRule, condition: e.target.value })}
                >
                  <option value="exceeds">Exceeds</option>
                  <option value="drops_below">Drops Below</option>
                  <option value="changes_by_pct">Changes by %</option>
                  <option value="new_detected">New Detected</option>
                </select>
              </div>
              <div>
                <Label>Threshold</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={newRule.threshold}
                  onChange={(e) => setNewRule({ ...newRule, threshold: e.target.value })}
                  className="mt-1"
                />
              </div>
            </div>
            <Button
              size="sm"
              onClick={() =>
                createRule.mutate({
                  kpi_key: newRule.kpi_key,
                  condition: newRule.condition,
                  threshold: parseFloat(newRule.threshold) || 0,
                })
              }
              disabled={!newRule.kpi_key}
            >
              Add Rule
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Channels</CardTitle>
          <CardDescription>How and when you receive alert notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email — High Severity</p>
              <p className="text-xs text-muted-foreground">
                Immediate email for pricing changes, major campaigns, and viral content
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email — Weekly Digest</p>
              <p className="text-xs text-muted-foreground">
                Medium/low alerts bundled into a Monday morning summary
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">In-App Feed</p>
              <p className="text-xs text-muted-foreground">
                All alerts visible in the dashboard Alerts page
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Slack Integration</p>
              <p className="text-xs text-muted-foreground">
                Push high-severity alerts to a Slack channel
              </p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Team Tab ──

function TeamTab({ account }: { account: any }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("viewer");

  const invite = useMutation({
    mutationFn: async () => {
      await api.post(`/api/accounts/${account.id}/invite`, { email, role });
    },
    onSuccess: () => setEmail(""),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Members</CardTitle>
        <CardDescription>Invite team members to your workspace</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium">Invite New Member</p>
          <div className="flex gap-3">
            <Input
              placeholder="email@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
            />
            <select
              className="rounded-md border px-3 py-2 text-sm"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
              <option value="owner">Owner</option>
            </select>
            <Button onClick={() => invite.mutate()} disabled={!email}>
              Invite
            </Button>
          </div>
          {invite.isSuccess && (
            <p className="text-sm text-green-600">Invitation sent!</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Data Tab ──

function DataTab({ brandProfileId }: { brandProfileId: string }) {
  const { data: history = [], isLoading } = useQuery({
    queryKey: ["collection-history", brandProfileId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfileId}/collection-history`);
      return res.data;
    },
  });

  const { data: schedule } = useQuery({
    queryKey: ["schedule", brandProfileId],
    queryFn: async () => {
      const res = await api.get(`/api/brands/${brandProfileId}/schedule`);
      return res.data;
    },
  });

  const triggerCollection = useMutation({
    mutationFn: async () => {
      await api.post(`/api/brands/${brandProfileId}/schedule/trigger`);
    },
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Collection Schedule</CardTitle>
          <CardDescription>Automated data collection status</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm">
                Status: <Badge variant={schedule?.active ? "default" : "secondary"}>
                  {schedule?.active ? "Active" : "Inactive"}
                </Badge>
              </p>
              {schedule?.cron && (
                <p className="text-xs text-muted-foreground mt-1">
                  Schedule: {schedule.filter_mode} ({schedule.cron})
                </p>
              )}
            </div>
            <Button
              size="sm"
              onClick={() => triggerCollection.mutate()}
              disabled={triggerCollection.isPending}
            >
              {triggerCollection.isPending ? "Triggering..." : "Run Now"}
            </Button>
          </div>
          {triggerCollection.isSuccess && (
            <p className="text-sm text-green-600">Collection triggered successfully.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Collection History</CardTitle>
          <CardDescription>Recent data collection runs</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : history.length === 0 ? (
            <p className="text-sm text-muted-foreground">No collection runs yet.</p>
          ) : (
            <div className="space-y-2">
              {history.map((job: any) => (
                <div key={job.id} className="flex items-center justify-between border rounded-lg p-3">
                  <div>
                    <p className="text-sm font-medium">
                      {new Date(job.created_at).toLocaleString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {job.total_competitors} competitors
                    </p>
                  </div>
                  <Badge
                    variant={
                      job.status === "completed"
                        ? "default"
                        : job.status === "failed"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {job.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main Settings Page ──

export default function SettingsPage() {
  const { profile, account, brandProfile, isLoading } = useAuthProfile();

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-48" />
          <div className="h-64 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (!brandProfile) {
    return (
      <div className="container mx-auto py-8 px-4">
        <p className="text-muted-foreground">No brand profile found. Complete onboarding first.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <Tabs defaultValue="profile">
        <TabsList className="mb-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="competitors">Competitors</TabsTrigger>
          <TabsTrigger value="kpis">KPI Configuration</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <ProfileTab brandProfile={brandProfile} account={account} />
        </TabsContent>

        <TabsContent value="competitors">
          <CompetitorsTab brandProfileId={brandProfile.id} />
        </TabsContent>

        <TabsContent value="kpis">
          <KpiConfigTab brandProfileId={brandProfile.id} />
        </TabsContent>

        <TabsContent value="alerts">
          <AlertsTab brandProfileId={brandProfile.id} />
        </TabsContent>

        <TabsContent value="team">
          <TeamTab account={account} />
        </TabsContent>

        <TabsContent value="data">
          <DataTab brandProfileId={brandProfile.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
