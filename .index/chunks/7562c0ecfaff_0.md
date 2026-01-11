# Chunk: 7562c0ecfaff_0

- source: `webui/src/app/monitoring/page.tsx`
- lines: 1-90
- chunk: 1/4

```
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
```
