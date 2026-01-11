# Chunk: dbc7b7cc22b1_0

- source: `webui/src/app/models/tuning/page.tsx`
- lines: 1-110
- chunk: 1/6

```
"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Sliders, 
  Plus, 
  Play,
  Pause,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  TrendingUp,
  Users,
} from "lucide-react";
import Link from "next/link";

interface RLExperiment {
  id: string;
  name: string;
  method: string;
  status: string;
  base_model: string;
  metrics: Record<string, number>;
  created_at: string;
}

interface PreferenceData {
  id: string;
  prompt: string;
  response_a: string;
  response_b: string;
  preference: number;
}

export default function TuningPage() {
  const [experiments, setExperiments] = useState<RLExperiment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch RL experiments
    setLoading(false);
    // Mock data for now
    setExperiments([]);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "bg-green-500/10 text-green-500";
      case "running":
        return "bg-blue-500/10 text-blue-500";
      case "failed":
        return "bg-red-500/10 text-red-500";
      default:
        return "bg-gray-500/10 text-gray-500";
    }
  };

  const getMethodBadgeColor = (method: string) => {
    switch (method.toLowerCase()) {
      case "dpo":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20";
      case "ppo":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "reward_model":
        return "bg-orange-500/10 text-orange-500 border-orange-500/20";
      default:
        return "bg-gray-500/10 text-gray-500";
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tuning & RLHF</h1>
          <p className="text-muted-foreground">
            Reinforcement Learning from Human Feedback and preference optimization
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setLoading(true)}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Link href="/models/tuning/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New RL Experiment
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
```
