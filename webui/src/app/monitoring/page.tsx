"use client";

import * as React from "react";
import { Activity, RefreshCw, Clock, Cpu, Database, Zap, TrendingUp, AlertCircle } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useSystemHealth } from "@/lib/api";

// Mock metrics data - in a real app this would come from OpenTelemetry
const mockMetrics = {
  totalRequests: 1234,
  avgLatency: 245,
  errorRate: 0.02,
  activeAgents: 3,
  activeSessions: 5,
  queuedTasks: 12,
};

function MetricCard({ 
  title, 
  value, 
  unit, 
  trend, 
  icon: Icon 
}: { 
  title: string; 
  value: string | number; 
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">
              {value}
              {unit && <span className="text-sm font-normal text-muted-foreground ml-1">{unit}</span>}
            </p>
          </div>
          <div className="p-3 rounded-xl bg-muted">
            <Icon className="size-6 text-muted-foreground" />
          </div>
        </div>
        {trend && (
          <div className="mt-2 flex items-center gap-1 text-xs">
            <TrendingUp className={`size-3 ${trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500 rotate-180' : 'text-gray-500'}`} />
            <span className={trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-500'}>
              {trend === 'up' ? '+12%' : trend === 'down' ? '-5%' : '0%'} from last hour
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function MonitoringPage() {
  const { data: health, isLoading, mutate } = useSystemHealth();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Monitoring</h1>
          <p className="text-muted-foreground">
            System telemetry and performance metrics
          </p>
        </div>
        <Button variant="outline" onClick={() => mutate()}>
          <RefreshCw className="size-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* System Health */}
      <section>
        <h2 className="text-lg font-semibold mb-4">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
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
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Backend API</p>
                      <p className="font-semibold">localhost:8080</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.backend.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.backend.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.backend.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Ollama</p>
                      <p className="font-semibold">localhost:11434</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.ollama.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.ollama.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.ollama.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">MLFlow</p>
                      <p className="font-semibold">localhost:5000</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.mlflow.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.mlflow.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.mlflow.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">JupyterLab</p>
                      <p className="font-semibold">localhost:8888</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.jupyter.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.jupyter.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.jupyter.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
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

      {/* Performance Metrics */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard
            title="Total Requests"
            value={mockMetrics.totalRequests.toLocaleString()}
            icon={Activity}
            trend="up"
          />
          <MetricCard
            title="Avg Response Time"
            value={mockMetrics.avgLatency}
            unit="ms"
            icon={Clock}
            trend="down"
          />
          <MetricCard
            title="Error Rate"
            value={(mockMetrics.errorRate * 100).toFixed(1)}
            unit="%"
            icon={AlertCircle}
            trend="neutral"
          />
          <MetricCard
            title="Active Agents"
            value={mockMetrics.activeAgents}
            icon={Cpu}
          />
          <MetricCard
            title="Active Sessions"
            value={mockMetrics.activeSessions}
            icon={Database}
          />
          <MetricCard
            title="Queued Tasks"
            value={mockMetrics.queuedTasks}
            icon={Zap}
          />
        </div>
      </section>

      {/* OpenTelemetry Info */}
      <section>
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <Activity className="size-8 text-muted-foreground" />
              <div>
                <h3 className="font-semibold">OpenTelemetry Integration</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  This page shows basic system health and mock metrics. For detailed distributed tracing 
                  and metrics, configure an OpenTelemetry collector and connect to a backend like Jaeger, 
                  Zipkin, or Grafana. The framework automatically instruments agent runs, API calls, 
                  and database operations.
                </p>
                <div className="flex items-center gap-2 mt-4">
                  <Badge variant="outline">Traces: Enabled</Badge>
                  <Badge variant="outline">Metrics: Enabled</Badge>
                  <Badge variant="secondary">Collector: Not Configured</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Recent Traces Placeholder */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recent Traces</h2>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <Activity className="size-12 mx-auto mb-4 opacity-50" />
              <p>No recent traces</p>
              <p className="text-sm">Configure an OpenTelemetry collector to view traces</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

