"use client";

import * as React from "react";
import Link from "next/link";
import {
  FolderKanban,
  Bot,
  GitBranch,
  Puzzle,
  FlaskConical,
  Activity,
  Plus,
  ExternalLink,
  RefreshCw,
  Zap,
  Database,
  Server,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useSystemHealth, useSystemStats } from "@/lib/api";
import { openJupyterLab, getMlflowUrl } from "@/lib/api";

// Quick action cards
const quickActions = [
  {
    title: "New Project",
    description: "Create a new agentic project",
    icon: FolderKanban,
    href: "/projects/new",
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "Create Agent",
    description: "Define a new AI agent",
    icon: Bot,
    href: "/agents/new",
    color: "from-violet-500 to-purple-500",
  },
  {
    title: "Design Flow",
    description: "Build a multi-agent workflow",
    icon: GitBranch,
    href: "/flows/new",
    color: "from-emerald-500 to-teal-500",
  },
  {
    title: "Add Component",
    description: "Create reusable code component",
    icon: Puzzle,
    href: "/library/new",
    color: "from-orange-500 to-amber-500",
  },
];

// Stats cards configuration
const statsConfig = [
  { key: "projects", label: "Projects", icon: FolderKanban, href: "/projects" },
  { key: "agents", label: "Agents", icon: Bot, href: "/agents" },
  { key: "flows", label: "Flows", icon: GitBranch, href: "/flows" },
  { key: "components", label: "Components", icon: Puzzle, href: "/library" },
];

function ServiceStatusCard({ 
  name, 
  status, 
  url, 
  latency,
  icon: Icon 
}: { 
  name: string; 
  status: 'healthy' | 'unhealthy' | 'unknown'; 
  url: string;
  latency?: number;
  icon: React.ElementType;
}) {
  const statusColors = {
    healthy: "bg-green-500",
    unhealthy: "bg-red-500",
    unknown: "bg-yellow-500",
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <Icon className="size-5 text-muted-foreground" />
            </div>
            <div>
              <p className="font-medium">{name}</p>
              <p className="text-xs text-muted-foreground">{url}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {latency && (
              <span className="text-xs text-muted-foreground">{latency}ms</span>
            )}
            <div className={`size-3 rounded-full ${statusColors[status]}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatsCard({ 
  label, 
  value, 
  icon: Icon, 
  href 
}: { 
  label: string; 
  value: number | string; 
  icon: React.ElementType;
  href: string;
}) {
  return (
    <Link href={href}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="text-3xl font-bold">{value}</p>
            </div>
            <div className="p-3 rounded-xl bg-muted">
              <Icon className="size-6 text-muted-foreground" />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default function DashboardPage() {
  const { data: health, isLoading: healthLoading, mutate: refreshHealth } = useSystemHealth();

  const { data: realStats } = useSystemStats();
  const stats = {
    projects: realStats?.projects ?? 0,
    agents: realStats?.agents ?? 0,
    flows: realStats?.flows ?? 0,
    components: realStats?.components ?? 0,
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to the Agentic Control Panel
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refreshHealth()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm" asChild>
            <Link href="/projects/new">
              <Plus className="size-4 mr-2" />
              New Project
            </Link>
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden">
                <CardContent className="pt-6 relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`} />
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${action.color} text-white`}>
                      <action.icon className="size-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold group-hover:text-primary transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Stats Overview */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsConfig.map((stat) => (
            <StatsCard
              key={stat.key}
              label={stat.label}
              value={stats[stat.key as keyof typeof stats]}
              icon={stat.icon}
              href={stat.href}
            />
          ))}
        </div>
      </section>

      {/* System Status */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">System Status</h2>
          <div className="flex items-center gap-2">
            {health && (
              <Badge variant={
                Object.values(health).every(s => s.status === 'healthy') 
                  ? 'default' 
                  : 'destructive'
              }>
                {Object.values(health).filter(s => s.status === 'healthy').length} / {Object.values(health).length} Services Healthy
              </Badge>
            )}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {healthLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <Skeleton className="h-12 w-full" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : health ? (
            <>
              <ServiceStatusCard
                name="Backend API"
                status={health.backend.status}
                url="localhost:8080"
                latency={health.backend.latency_ms}
                icon={Server}
              />
              <ServiceStatusCard
                name="Ollama"
                status={health.ollama.status}
                url="localhost:11434"
                latency={health.ollama.latency_ms}
                icon={Zap}
              />
              <ServiceStatusCard
                name="MLFlow"
                status={health.mlflow.status}
                url="localhost:5000"
                latency={health.mlflow.latency_ms}
                icon={FlaskConical}
              />
              <ServiceStatusCard
                name="JupyterLab"
                status={health.jupyter.status}
                url="localhost:8888"
                latency={health.jupyter.latency_ms}
                icon={Database}
              />
            </>
          ) : (
            <Card className="col-span-full">
              <CardContent className="pt-6 text-center text-muted-foreground">
                Unable to fetch system status
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* External Tools */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Development Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="size-5" />
                JupyterLab
              </CardTitle>
              <CardDescription>
                Interactive notebooks for experimentation and development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => openJupyterLab()} className="w-full">
                <ExternalLink className="size-4 mr-2" />
                Open JupyterLab
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FlaskConical className="size-5" />
                MLFlow
              </CardTitle>
              <CardDescription>
                Experiment tracking, model registry, and deployment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => window.open(getMlflowUrl(), '_blank')} 
                className="w-full"
              >
                <ExternalLink className="size-4 mr-2" />
                Open MLFlow UI
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Recent Activity Placeholder */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="size-12 mx-auto mb-4 opacity-50" />
              <p>No recent activity</p>
              <p className="text-sm">Create a project or run an agent to see activity here</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
