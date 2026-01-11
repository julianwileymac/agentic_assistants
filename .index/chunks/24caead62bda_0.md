# Chunk: 24caead62bda_0

- source: `webui/src/app/page.tsx`
- lines: 1-122
- chunk: 1/4

```
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
import { useSystemHealth } from "@/lib/api";
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
```
