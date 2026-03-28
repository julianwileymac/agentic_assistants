"use client";

import * as React from "react";
import useSWR from "swr";
import {
  Activity,
  RefreshCw,
  Radio,
  Server,
  Cpu,
  HardDrive,
  Gauge,
  Waves,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { TimeSeriesChart, type TimeSeriesDataPoint } from "@/components/visualizations";
import { MetricsGauge } from "@/components/visualizations";
import { apiFetch, useSystemHealth } from "@/lib/api";
import { getWsUrl } from "@/lib/api-client";
import { isInitialized } from "@/lib/telemetry";
import type { SystemHealth, SystemStats } from "@/lib/types";
import { cn } from "@/lib/utils";

const STATS_KEY = "/api/v1/stats";
const MAX_SERIES_POINTS = 72;

type LiveMetricsState = {
  cpu_percent: number | null;
  memory_percent: number | null;
  requests_per_minute: number | null;
};

function formatNowLabel(): string {
  return new Date().toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function appendSeriesPoint(
  prev: TimeSeriesDataPoint[],
  value: number,
  series: string
): TimeSeriesDataPoint[] {
  const time = formatNowLabel();
  const next = [...prev, { time, value, series }];
  if (next.length > MAX_SERIES_POINTS) return next.slice(-MAX_SERIES_POINTS);
  return next;
}

function pickNumber(obj: Record<string, unknown>, keys: string[]): number | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "number" && Number.isFinite(v)) return v;
  }
  return undefined;
}

function mergeLiveFromPayload(
  data: Record<string, unknown>,
  prev: LiveMetricsState
): LiveMetricsState {
  const nested =
    data.metrics && typeof data.metrics === "object"
      ? (data.metrics as Record<string, unknown>)
      : {};

  const cpu =
    pickNumber(data, ["cpu_percent", "cpu", "cpu_usage"]) ??
    pickNumber(nested, ["cpu_percent", "cpu", "cpu_usage"]);
  const memory =
    pickNumber(data, ["memory_percent", "memory", "mem_percent"]) ??
    pickNumber(nested, ["memory_percent", "memory", "mem_percent"]);
  const rpm =
    pickNumber(data, ["requests_per_minute", "rpm", "req_per_min"]) ??
    pickNumber(nested, ["requests_per_minute", "rpm", "req_per_min"]);

  return {
    cpu_percent: cpu ?? prev.cpu_percent,
    memory_percent: memory ?? prev.memory_percent,
    requests_per_minute: rpm ?? prev.requests_per_minute,
  };
}

function extractLatencyMs(data: Record<string, unknown>): number | undefined {
  const nested =
    data.metrics && typeof data.metrics === "object"
      ? (data.metrics as Record<string, unknown>)
      : {};
  return (
    pickNumber(data, ["latency_ms", "latency", "avg_latency_ms", "request_latency_ms"]) ??
    pickNumber(nested, ["latency_ms", "latency", "avg_latency_ms"])
  );
}

function useJsHeapMemoryPercent(): number | null {
  const [pct, setPct] = React.useState<number | null>(null);

  React.useEffect(() => {
    const tick = () => {
      const perf = performance as Performance & {
        memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number };
      };
      const m = perf.memory;
      if (m && m.jsHeapSizeLimit > 0) {
        setPct((m.usedJSHeapSize / m.jsHeapSizeLimit) * 100);
      }
    };
    tick();
    const id = window.setInterval(tick, 3000);
    return () => window.clearInterval(id);
  }, []);

  return pct;
}

function ServiceHealthCard({
  label,
  row,
}: {
  label: string;
  row: SystemHealth["backend"] | undefined;
}) {
  if (!row) return null;
  const ok = row.status === "healthy";
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="font-semibold truncate text-sm sm:text-base" title={row.url}>
              {row.url.replace(/^https?:\/\//, "")}
            </p>
          </div>
          <div
            className={cn(
              "size-3 shrink-0 rounded-full",
              ok ? "bg-green-500" : row.status === "unknown" ? "bg-amber-500" : "bg-red-500"
            )}
          />
        </div>
        {row.latency_ms != null && (
          <p className="mt-2 text-xs text-muted-foreground">{row.latency_ms}ms latency</p>
        )}
        {row.message && (
          <p className="mt-1 text-xs text-destructive line-clamp-2">{row.message}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function MonitoringPage() {
  const { data: health, isLoading: healthLoading, mutate: mutateHealth } = useSystemHealth();
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    mutate: mutateStats,
  } = useSWR<SystemStats>(STATS_KEY, (url) => apiFetch<SystemStats>(url), {
    revalidateOnFocus: false,
    dedupingInterval: 5000,
  });

  const [live, setLive] = React.useState<LiveMetricsState>({
    cpu_percent: null,
    memory_percent: null,
    requests_per_minute: null,
  });
  const [latencySeries, setLatencySeries] = React.useState<TimeSeriesDataPoint[]>([]);
  const [rpmSeries, setRpmSeries] = React.useState<TimeSeriesDataPoint[]>([]);
  const [wsState, setWsState] = React.useState<"idle" | "connecting" | "open" | "error" | "closed">(
    "idle"
  );

  const [otelOptIn, setOtelOptIn] = React.useState(true);
  const [collectorUrl, setCollectorUrl] = React.useState<string | null>(null);
  const [otelReady, setOtelReady] = React.useState(false);

  const jsHeapPct = useJsHeapMemoryPercent();

  React.useEffect(() => {
    setOtelOptIn(typeof window !== "undefined" && localStorage.getItem("otel_disabled") !== "true");
    setCollectorUrl(
      typeof window !== "undefined" ? localStorage.getItem("otel_collector_url") : null
    );
  }, []);

  React.useEffect(() => {
    const sync = () => setOtelReady(isInitialized());
    sync();
    const t = window.setInterval(sync, 400);
    const max = window.setTimeout(() => window.clearInterval(t), 8000);
    return () => {
      window.clearInterval(t);
      window.clearTimeout(max);
    };
  }, []);

  React.useEffect(() => {
    if (!health?.backend?.latency_ms) return;
    const ms = health.backend.latency_ms;
    setLatencySeries((prev) => appendSeriesPoint(prev, ms, "Latency (ms)"));
  }, [health?.backend?.latency_ms]);

  React.useEffect(() => {
    const url = getWsUrl("/ws");
    setWsState("connecting");
    let ws: WebSocket;
    try {
      ws = new WebSocket(url);
    } catch {
      setWsState("error");
      return;
    }

    ws.onopen = () => {
      setWsState("open");
      ws.send(JSON.stringify({ command: "subscribe", params: { topic: "metrics" } }));
    };

    ws.onerror = () => setWsState("error");
    ws.onclose = () => setWsState((s) => (s === "connecting" ? "error" : "closed"));

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string) as {
          type?: string;
          data?: Record<string, unknown>;
        };
        if (msg.type === "ping") {
          ws.send(JSON.stringify({ command: "pong", params: {} }));
          return;
        }
        const data = msg.data ?? {};
        if (typeof data.subscribed === "string") return;

        const applyMetricsPayload = () => {
          setLive((prev) => mergeLiveFromPayload(data, prev));
          const lat = extractLatencyMs(data);
          if (lat != null) {
            setLatencySeries((p) => appendSeriesPoint(p, lat, "Latency (ms)"));
          }
          const rpm =
            pickNumber(data, ["requests_per_minute", "rpm", "req_per_min"]) ??
            (data.metrics && typeof data.metrics === "object"
              ? pickNumber(data.metrics as Record<string, unknown>, [
                  "requests_per_minute",
                  "rpm",
                  "req_per_min",
                ])
              : undefined);
          if (rpm != null) {
            setRpmSeries((p) => appendSeriesPoint(p, rpm, "Requests/min"));
          }
        };

        if (msg.type === "metrics.logged") {
          applyMetricsPayload();
          return;
        }

        if (msg.type === "notification") {
          const looksLikeMetrics =
            extractLatencyMs(data) != null ||
            pickNumber(data, ["cpu_percent", "cpu", "cpu_usage"]) != null ||
            pickNumber(data, ["memory_percent", "memory", "mem_percent"]) != null ||
            pickNumber(data, ["requests_per_minute", "rpm", "req_per_min"]) != null ||
            (data.metrics && typeof data.metrics === "object");
          if (looksLikeMetrics) applyMetricsPayload();
        }
      } catch {
        /* ignore malformed frames */
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const refreshAll = () => {
    void mutateHealth();
    void mutateStats();
  };

  const memoryGauge =
    live.memory_percent ?? (jsHeapPct != null ? Math.round(jsHeapPct * 10) / 10 : null);
  const memoryFromLive = live.memory_percent != null;
  const hasMemorySample = memoryGauge != null;
  const cpuGauge = live.cpu_percent ?? 0;
  const rpmGauge = live.requests_per_minute ?? 0;
  const rpmMax = Math.max(120, Math.ceil((rpmGauge || 1) * 1.25 / 10) * 10);

  const onOtelToggle = (enabled: boolean) => {
    setOtelOptIn(enabled);
    if (typeof window === "undefined") return;
    if (enabled) localStorage.removeItem("otel_disabled");
    else localStorage.setItem("otel_disabled", "true");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Monitoring & Observability</h1>
          <p className="text-muted-foreground">
            Live service health, API statistics, and telemetry status
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="font-normal">
            <Radio className="mr-1 size-3" />
            WS:{" "}
            {wsState === "open"
              ? "live"
              : wsState === "connecting"
                ? "connecting"
                : wsState === "error"
                  ? "error"
                  : wsState}
          </Badge>
          <Button variant="outline" onClick={refreshAll}>
            <RefreshCw className="mr-2 size-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Row 1 — service health */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">System health</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {healthLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <Skeleton className="h-16 w-full" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : health ? (
            <>
              <ServiceHealthCard label="Backend API" row={health.backend} />
              <ServiceHealthCard label="Ollama" row={health.ollama} />
              <ServiceHealthCard label="MLFlow" row={health.mlflow} />
              <ServiceHealthCard label="JupyterLab" row={health.jupyter} />
            </>
          ) : (
            <Card className="col-span-full">
              <CardContent className="pt-6 text-center text-muted-foreground">
                Unable to fetch system health
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* Row 2 — gauges */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">Live metrics</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="size-4" />
                CPU
              </CardTitle>
              <CardDescription>
                From WebSocket <code className="text-xs">metrics</code> topic when the server emits
                CPU usage
              </CardDescription>
            </CardHeader>
            <CardContent>
              {live.cpu_percent == null ? (
                <div className="flex flex-col items-center justify-center py-8 text-center text-sm text-muted-foreground">
                  <Gauge className="mb-2 size-8 opacity-40" />
                  No live CPU samples yet
                </div>
              ) : (
                <MetricsGauge value={cpuGauge} max={100} title="CPU" unit="%" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="flex items-center gap-2 text-base">
                <HardDrive className="size-4" />
                Memory
              </CardTitle>
              <CardDescription>
                {memoryFromLive
                  ? "From WebSocket metrics stream"
                  : "Browser JS heap usage (approx.) when OTel stream has no memory %"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!hasMemorySample ? (
                <div className="flex flex-col items-center justify-center py-8 text-center text-sm text-muted-foreground">
                  <HardDrive className="mb-2 size-8 opacity-40" />
                  No memory samples yet
                </div>
              ) : (
                <MetricsGauge
                  value={Math.min(100, memoryGauge)}
                  max={100}
                  title="Memory"
                  unit="%"
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="flex items-center gap-2 text-base">
                <Waves className="size-4" />
                Requests / min
              </CardTitle>
              <CardDescription>
                Live stream when available; gauge scale grows with observed traffic
              </CardDescription>
            </CardHeader>
            <CardContent>
              {live.requests_per_minute == null && rpmGauge === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center text-sm text-muted-foreground">
                  <Activity className="mb-2 size-8 opacity-40" />
                  No RPM samples yet
                </div>
              ) : (
                <MetricsGauge value={rpmGauge} max={rpmMax} title="Req/min" unit="" />
              )}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Row 3 — time series (stats from /api/v1/stats in header) */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">Request latency over time</h2>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Server className="size-4" />
              Time series
            </CardTitle>
            <CardDescription>
              Request latency from backend health checks and optional WebSocket{" "}
              <code className="text-xs">metrics</code> payloads. Counts below are from{" "}
              <code className="text-xs">{STATS_KEY}</code>.
            </CardDescription>
            {statsLoading ? (
              <Skeleton className="mt-3 h-10 w-full max-w-2xl" />
            ) : statsError ? (
              <p className="mt-3 text-sm text-destructive">Could not load control panel statistics.</p>
            ) : stats ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {(
                  [
                    ["Projects", stats.projects_count],
                    ["Agents", stats.agents_count],
                    ["Flows", stats.flows_count],
                    ["Components", stats.components_count],
                    ["Data sources", stats.datasources_count],
                    ["Sessions", stats.active_sessions],
                  ] as const
                ).map(([k, v]) => (
                  <Badge key={k} variant="secondary" className="font-normal tabular-nums">
                    {k}: {v}
                  </Badge>
                ))}
              </div>
            ) : null}
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="latency">
              <TabsList>
                <TabsTrigger value="latency">Request latency</TabsTrigger>
                <TabsTrigger value="rpm">Requests / min</TabsTrigger>
              </TabsList>
              <TabsContent value="latency" className="mt-4">
                {latencySeries.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16 text-center text-muted-foreground">
                    <Activity className="mb-2 size-10 opacity-30" />
                    <p className="text-sm">No latency points yet</p>
                    <p className="mt-1 max-w-md text-xs">
                      Points appear as health checks run and when the server publishes latency on the
                      metrics topic.
                    </p>
                  </div>
                ) : (
                  <TimeSeriesChart
                    data={latencySeries}
                    title="Latency (ms)"
                    height={320}
                    theme="dark"
                    showLegend
                  />
                )}
              </TabsContent>
              <TabsContent value="rpm" className="mt-4">
                {rpmSeries.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16 text-center text-muted-foreground">
                    <Waves className="mb-2 size-10 opacity-30" />
                    <p className="text-sm">No throughput samples yet</p>
                    <p className="mt-1 max-w-md text-xs">
                      Subscribe to the same WebSocket stream; when the backend emits RPM, it will
                      chart here.
                    </p>
                  </div>
                ) : (
                  <TimeSeriesChart
                    data={rpmSeries}
                    title="Requests per minute"
                    height={320}
                    theme="dark"
                    showLegend
                  />
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </section>

      {/* Row 4 — OTel + traces */}
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">OpenTelemetry (browser)</CardTitle>
            <CardDescription>
              Frontend SDK status and collector URL from local settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="space-y-1">
                <p className="text-sm font-medium">Initialized</p>
                <p className="text-xs text-muted-foreground">
                  Reflects whether the web UI telemetry module has finished startup
                </p>
              </div>
              <Badge variant={otelReady ? "default" : "secondary"}>
                {otelReady ? "Yes" : "No"}
              </Badge>
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium">Collector endpoint</p>
              <p className="break-all rounded-md bg-muted px-3 py-2 font-mono text-xs">
                {collectorUrl?.trim() || "Not set (localStorage key otel_collector_url)"}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Enable OpenTelemetry</p>
                <p className="text-xs text-muted-foreground">
                  Stored as <code className="text-xs">otel_disabled</code>. Reload the app after
                  changing.
                </p>
              </div>
              <Switch checked={otelOptIn} onCheckedChange={onOtelToggle} aria-label="Toggle OTel" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent traces</CardTitle>
            <CardDescription>
              Trace IDs and spans will appear here once a collector and trace backend (Jaeger,
              Zipkin, Grafana Tempo, etc.) are configured
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-12 text-center text-muted-foreground">
              <Activity className="mb-3 size-12 opacity-40" />
              <p className="text-sm font-medium">No traces to display</p>
              <p className="mt-2 max-w-sm text-xs">
                Point <code className="text-xs">otel_collector_url</code> at your OTLP HTTP endpoint
                and open your trace UI to inspect spans exported from the browser and API.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
