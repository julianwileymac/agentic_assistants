"use client";

import * as React from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import {
  CheckCircle2,
  XCircle,
  MinusCircle,
  Clock,
  Activity,
  TrendingUp,
  BarChart3,
} from "lucide-react";

import { apiFetch } from "@/lib/api";
import type { TestRun, TestResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const PIE_COLORS = {
  pass: "#22c55e",
  fail: "#ef4444",
  skip: "#eab308",
};

interface RunSummary {
  id: string;
  name: string;
  status: string;
  date: string;
  duration: number;
  passed: number;
  failed: number;
  skipped: number;
  total: number;
}

interface AggregateStats {
  totalRuns: number;
  totalPassed: number;
  totalFailed: number;
  totalSkipped: number;
  avgDuration: number;
  passRate: number;
}

export function TestResultsDashboard() {
  const [runs, setRuns] = React.useState<RunSummary[]>([]);
  const [stats, setStats] = React.useState<AggregateStats | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function fetchRuns() {
      setLoading(true);
      try {
        const res = await apiFetch<{ items: TestRun[] }>(
          "/api/v1/testing/runs?limit=50",
        );

        const allRuns = res.items ?? [];
        const summaries: RunSummary[] = [];

        for (const run of allRuns.slice(0, 20)) {
          let results: TestResult[] = [];
          try {
            const detail = await apiFetch<{
              run: TestRun;
              results: TestResult[];
            }>(`/api/v1/testing/runs/${run.id}`);
            results = detail.results ?? [];
          } catch {
            /* individual run detail may 404 */
          }

          const passed = results.filter((r) => r.passed).length;
          const failed = results.filter(
            (r) => !r.passed && r.status !== "skipped",
          ).length;
          const skipped = results.filter(
            (r) => r.status === "skipped",
          ).length;

          summaries.push({
            id: run.id,
            name: run.run_name || `Run ${run.id.slice(0, 8)}`,
            status: run.status,
            date: run.created_at,
            duration: run.duration_seconds ?? 0,
            passed,
            failed,
            skipped,
            total: results.length || 1,
          });
        }

        setRuns(summaries);

        const totalRuns = summaries.length;
        const totalPassed = summaries.reduce((a, r) => a + r.passed, 0);
        const totalFailed = summaries.reduce((a, r) => a + r.failed, 0);
        const totalSkipped = summaries.reduce((a, r) => a + r.skipped, 0);
        const totalTests = totalPassed + totalFailed + totalSkipped || 1;
        const avgDuration =
          totalRuns > 0
            ? summaries.reduce((a, r) => a + r.duration, 0) / totalRuns
            : 0;

        setStats({
          totalRuns,
          totalPassed,
          totalFailed,
          totalSkipped,
          avgDuration,
          passRate: (totalPassed / totalTests) * 100,
        });
      } catch {
        setRuns([]);
        setStats(null);
      } finally {
        setLoading(false);
      }
    }

    fetchRuns();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (!stats || runs.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-sm text-muted-foreground">
          No test run data available. Run some tests to see results here.
        </CardContent>
      </Card>
    );
  }

  const pieData = [
    { name: "Passed", value: stats.totalPassed, color: PIE_COLORS.pass },
    { name: "Failed", value: stats.totalFailed, color: PIE_COLORS.fail },
    { name: "Skipped", value: stats.totalSkipped, color: PIE_COLORS.skip },
  ].filter((d) => d.value > 0);

  const barData = runs
    .slice(0, 10)
    .map((r) => ({
      name: r.name.length > 12 ? r.name.slice(0, 12) + "..." : r.name,
      duration: Number(r.duration.toFixed(2)),
    }))
    .reverse();

  const trendData = runs
    .slice(0, 15)
    .map((r) => ({
      date: new Date(r.date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      passRate:
        r.total > 0 ? Number(((r.passed / r.total) * 100).toFixed(1)) : 0,
      total: r.total,
    }))
    .reverse();

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Runs"
          value={stats.totalRuns}
          icon={<Activity className="size-4 text-blue-500" />}
        />
        <StatCard
          title="Pass Rate"
          value={`${stats.passRate.toFixed(1)}%`}
          icon={<TrendingUp className="size-4 text-emerald-500" />}
          variant={stats.passRate >= 80 ? "success" : stats.passRate >= 50 ? "warning" : "danger"}
        />
        <StatCard
          title="Avg Duration"
          value={`${stats.avgDuration.toFixed(2)}s`}
          icon={<Clock className="size-4 text-amber-500" />}
        />
        <StatCard
          title="Tests Run"
          value={stats.totalPassed + stats.totalFailed + stats.totalSkipped}
          icon={<BarChart3 className="size-4 text-violet-500" />}
          subtitle={
            <span className="flex items-center gap-2 text-xs">
              <span className="flex items-center gap-0.5 text-emerald-500">
                <CheckCircle2 className="size-3" />
                {stats.totalPassed}
              </span>
              <span className="flex items-center gap-0.5 text-red-500">
                <XCircle className="size-3" />
                {stats.totalFailed}
              </span>
              <span className="flex items-center gap-0.5 text-yellow-500">
                <MinusCircle className="size-3" />
                {stats.totalSkipped}
              </span>
            </span>
          }
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Pass / Fail Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#18181b",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4">
              {pieData.map((d) => (
                <div key={d.name} className="flex items-center gap-1.5 text-xs">
                  <span
                    className="inline-block size-2.5 rounded-full"
                    style={{ backgroundColor: d.color }}
                  />
                  {d.name}: {d.value}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Test Durations (s)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={barData}>
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={35}
                />
                <Tooltip
                  contentStyle={{
                    background: "#18181b",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar
                  dataKey="duration"
                  fill="#8b5cf6"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={32}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Pass Rate Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={trendData}>
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={30}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "#18181b",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  formatter={(v: number) => [`${v}%`, "Pass Rate"]}
                />
                <Line
                  type="monotone"
                  dataKey="passRate"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={{ r: 3, fill: "#22c55e" }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Recent Runs</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {runs.slice(0, 10).map((run) => (
              <div
                key={run.id}
                className="flex items-center gap-3 px-6 py-2.5 text-sm hover:bg-muted/30 transition-colors"
              >
                <StatusDot status={run.status} />
                <span className="flex-1 truncate font-medium">{run.name}</span>
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground shrink-0">
                  <span className="text-emerald-500">{run.passed}P</span>
                  <span className="text-red-500">{run.failed}F</span>
                  <span className="text-yellow-500">{run.skipped}S</span>
                </span>
                {run.duration > 0 && (
                  <Badge variant="outline" className="text-xs shrink-0">
                    {run.duration.toFixed(2)}s
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground shrink-0">
                  {new Date(run.date).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  subtitle,
  variant,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: React.ReactNode;
  variant?: "success" | "warning" | "danger";
}) {
  const borderClass =
    variant === "success"
      ? "border-emerald-500/30"
      : variant === "warning"
        ? "border-yellow-500/30"
        : variant === "danger"
          ? "border-red-500/30"
          : "";

  return (
    <Card className={borderClass}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-muted-foreground">{title}</p>
          {icon}
        </div>
        <p className="mt-1 text-2xl font-bold">{value}</p>
        {subtitle && <div className="mt-1">{subtitle}</div>}
      </CardContent>
    </Card>
  );
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === "success"
      ? "bg-emerald-500"
      : status === "failed" || status === "error"
        ? "bg-red-500"
        : "bg-yellow-500";

  return <span className={`inline-block size-2 rounded-full ${color}`} />;
}
