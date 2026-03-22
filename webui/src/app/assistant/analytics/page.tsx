"use client";

import * as React from "react";
import { 
  BarChart3, 
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Bot,
  Database,
  RefreshCw,
  Loader2,
  Lightbulb,
  ArrowRight,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";

interface FrameworkStats {
  framework: string;
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  avgDurationSeconds: number;
  errorRate: number;
}

interface Analytics {
  periodStart: string;
  periodEnd: string;
  totalEvents: number;
  totalAgentRuns: number;
  totalApiCalls: number;
  totalRagQueries: number;
  totalErrors: number;
  frameworkStats: FrameworkStats[];
  avgResponseTimeMs: number;
  ragEffectivenessScore: number;
}

interface Suggestion {
  id: string;
  category: string;
  priority: string;
  title: string;
  description: string;
  recommendedAction: string;
  estimatedImpact: string;
}

interface HealthSummary {
  healthScore: number;
  status: string;
  trends: Record<string, string>;
  totalEvents: number;
  totalErrors: number;
  errorRate: number;
  topIssues: string[];
}

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = React.useState(true);
  const [timeframe, setTimeframe] = React.useState("7");
  const [analytics, setAnalytics] = React.useState<Analytics | null>(null);
  const [health, setHealth] = React.useState<HealthSummary | null>(null);
  const [suggestions, setSuggestions] = React.useState<Suggestion[]>([]);

  const setMockData = React.useCallback(() => {
    setAnalytics({
      periodStart: new Date(Date.now() - parseInt(timeframe) * 24 * 60 * 60 * 1000).toISOString(),
      periodEnd: new Date().toISOString(),
      totalEvents: 1247,
      totalAgentRuns: 342,
      totalApiCalls: 856,
      totalRagQueries: 234,
      totalErrors: 23,
      frameworkStats: [
        { framework: "crewai", totalRuns: 156, successfulRuns: 148, failedRuns: 8, avgDurationSeconds: 12.4, errorRate: 0.051 },
        { framework: "langgraph", totalRuns: 98, successfulRuns: 94, failedRuns: 4, avgDurationSeconds: 8.2, errorRate: 0.041 },
        { framework: "autogen", totalRuns: 45, successfulRuns: 42, failedRuns: 3, avgDurationSeconds: 15.6, errorRate: 0.067 },
        { framework: "agno", totalRuns: 43, successfulRuns: 41, failedRuns: 2, avgDurationSeconds: 9.1, errorRate: 0.047 },
      ],
      avgResponseTimeMs: 234,
      ragEffectivenessScore: 0.72,
    });

    setHealth({
      healthScore: 85,
      status: "good",
      trends: { activity: "active", errors: "moderate", rag_usage: "high" },
      totalEvents: 1247,
      totalErrors: 23,
      errorRate: 0.067,
      topIssues: ["High latency in AutoGen adapter", "RAG effectiveness below target"],
    });

    setSuggestions([
      {
        id: "1",
        category: "performance",
        priority: "medium",
        title: "Optimize AutoGen conversation flows",
        description: "AutoGen adapter has higher average latency than other frameworks.",
        recommendedAction: "Consider caching conversation context or reducing max turns.",
        estimatedImpact: "Could reduce latency by 20-30%",
      },
      {
        id: "2",
        category: "reliability",
        priority: "high",
        title: "Improve RAG retrieval quality",
        description: "RAG effectiveness score is below 0.8 threshold.",
        recommendedAction: "Review and update knowledge base content, consider re-indexing.",
        estimatedImpact: "Could improve answer accuracy by 15-25%",
      },
      {
        id: "3",
        category: "feature_adoption",
        priority: "low",
        title: "Consider using LangGraph for complex workflows",
        description: "LangGraph shows lowest error rate and good performance.",
        recommendedAction: "Migrate suitable workloads from CrewAI to LangGraph.",
        estimatedImpact: "Could reduce errors by 10%",
      },
    ]);
  }, [timeframe]);

  const fetchData = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const [analyticsData, healthData, suggestionsData] = await Promise.all([
        apiFetch<Analytics>(`/api/v1/assistant/analytics?days=${timeframe}`),
        apiFetch<HealthSummary>("/api/v1/assistant/health"),
        apiFetch<{ suggestions?: Suggestion[] }>("/api/v1/assistant/suggestions"),
      ]);

      setAnalytics(analyticsData);
      setHealth(healthData);
      setSuggestions(suggestionsData.suggestions || []);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
      // Set mock data for demo
      setMockData();
    } finally {
      setIsLoading(false);
    }
  }, [setMockData, timeframe]);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const runAnalysis = async () => {
    try {
      toast.info("Running meta-analysis...");
      await apiFetch("/api/v1/assistant/analyze", {
        method: "POST",
      });
      toast.success("Meta-analysis complete");
      fetchData();
    } catch {
      toast.error("Analysis failed");
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return "text-green-500";
    if (score >= 70) return "text-yellow-500";
    if (score >= 50) return "text-orange-500";
    return "text-red-500";
  };

  const getHealthBg = (score: number) => {
    if (score >= 90) return "bg-green-500/10";
    if (score >= 70) return "bg-yellow-500/10";
    if (score >= 50) return "bg-orange-500/10";
    return "bg-red-500/10";
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical": return "bg-red-500";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      default: return "bg-blue-500";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 text-white">
            <BarChart3 className="size-6" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Usage Analytics</h1>
            <p className="text-muted-foreground">
              Monitor framework usage and get improvement suggestions
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Last 24 hours</SelectItem>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={runAnalysis}>
            <Zap className="size-4 mr-2" />
            Run Analysis
          </Button>
        </div>
      </div>

      {/* Health Score Card */}
      {health && (
        <Card className={getHealthBg(health.healthScore)}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className={`text-6xl font-bold ${getHealthColor(health.healthScore)}`}>
                  {health.healthScore}
                </div>
                <div>
                  <p className="text-xl font-semibold">Framework Health Score</p>
                  <p className="text-muted-foreground capitalize">
                    Status: {health.status.replace("_", " ")}
                  </p>
                </div>
              </div>
              <div className="flex gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold">{health.totalEvents}</p>
                  <p className="text-xs text-muted-foreground">Total Events</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{health.totalErrors}</p>
                  <p className="text-xs text-muted-foreground">Errors</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{(health.errorRate * 100).toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground">Error Rate</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      {analytics && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10">
                  <Bot className="size-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.totalAgentRuns}</p>
                  <p className="text-xs text-muted-foreground">Agent Runs</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-500/10">
                  <Activity className="size-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.totalApiCalls}</p>
                  <p className="text-xs text-muted-foreground">API Calls</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/10">
                  <Database className="size-5 text-purple-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.totalRagQueries}</p>
                  <p className="text-xs text-muted-foreground">RAG Queries</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-500/10">
                  <Clock className="size-5 text-orange-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.avgResponseTimeMs}ms</p>
                  <p className="text-xs text-muted-foreground">Avg Response</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="frameworks">
        <TabsList>
          <TabsTrigger value="frameworks">Framework Performance</TabsTrigger>
          <TabsTrigger value="suggestions">Improvement Suggestions</TabsTrigger>
        </TabsList>

        <TabsContent value="frameworks">
          <Card>
            <CardHeader>
              <CardTitle>Framework Performance Comparison</CardTitle>
              <CardDescription>
                Compare success rates and performance across frameworks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {analytics?.frameworkStats.map((stats) => (
                  <div key={stats.framework} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="capitalize">
                          {stats.framework}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {stats.totalRuns} runs
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-green-500">
                          <CheckCircle className="size-3 inline mr-1" />
                          {stats.successfulRuns}
                        </span>
                        <span className="text-red-500">
                          <AlertCircle className="size-3 inline mr-1" />
                          {stats.failedRuns}
                        </span>
                        <span className="text-muted-foreground">
                          {stats.avgDurationSeconds.toFixed(1)}s avg
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(1 - stats.errorRate) * 100} 
                        className="flex-1"
                      />
                      <span className="text-sm font-medium w-16 text-right">
                        {((1 - stats.errorRate) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="suggestions">
          <Card>
            <CardHeader>
              <CardTitle>Improvement Suggestions</CardTitle>
              <CardDescription>
                AI-generated recommendations based on usage analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {suggestions.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No suggestions available. Run an analysis to generate recommendations.
                  </p>
                ) : (
                  suggestions.map((suggestion) => (
                    <Card key={suggestion.id}>
                      <CardContent className="pt-4">
                        <div className="flex items-start gap-4">
                          <div className={`p-2 rounded-lg ${getPriorityColor(suggestion.priority)} bg-opacity-10`}>
                            <Lightbulb className={`size-5 ${getPriorityColor(suggestion.priority).replace("bg-", "text-")}`} />
                          </div>
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center gap-2">
                              <h4 className="font-semibold">{suggestion.title}</h4>
                              <Badge variant="outline" className="capitalize text-xs">
                                {suggestion.priority}
                              </Badge>
                              <Badge variant="secondary" className="capitalize text-xs">
                                {suggestion.category.replace("_", " ")}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {suggestion.description}
                            </p>
                            <div className="flex items-center gap-2 text-sm">
                              <ArrowRight className="size-4 text-primary" />
                              <span className="font-medium">{suggestion.recommendedAction}</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Impact: {suggestion.estimatedImpact}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
