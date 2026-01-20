"use client";

import * as React from "react";
import Link from "next/link";
import {
  GraduationCap,
  Target,
  BookOpen,
  ClipboardCheck,
  Plus,
  Upload,
  TrendingUp,
  Clock,
  CheckCircle2,
  ArrowRight,
  Sparkles,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useLearningGoals,
  useLearningTopics,
  useEvaluations,
} from "@/lib/api";

// Quick action cards for learning
const quickActions = [
  {
    title: "New Goal",
    description: "Set a learning objective",
    icon: Target,
    href: "/learning/goals?new=true",
    color: "from-emerald-500 to-teal-500",
  },
  {
    title: "Start Topic",
    description: "Begin learning something new",
    icon: BookOpen,
    href: "/learning/topics?new=true",
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "Import Paper",
    description: "Learn from research",
    icon: Upload,
    href: "/learning?import=true",
    color: "from-violet-500 to-purple-500",
  },
  {
    title: "Take Evaluation",
    description: "Test your knowledge",
    icon: ClipboardCheck,
    href: "/learning/evaluations?new=true",
    color: "from-orange-500 to-amber-500",
  },
];

function StatsCard({
  label,
  value,
  icon: Icon,
  href,
  trend,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  href: string;
  trend?: string;
}) {
  return (
    <Link href={href}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              <div className="flex items-center gap-2">
                <p className="text-3xl font-bold">{value}</p>
                {trend && (
                  <Badge variant="secondary" className="text-xs">
                    <TrendingUp className="size-3 mr-1" />
                    {trend}
                  </Badge>
                )}
              </div>
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

function TopicCard({
  topic,
}: {
  topic: {
    id: string;
    name: string;
    description?: string;
    progress_percent: number;
    status: string;
    difficulty_level: string;
  };
}) {
  const statusColors: Record<string, string> = {
    not_started: "bg-gray-500",
    in_progress: "bg-blue-500",
    completed: "bg-green-500",
    paused: "bg-yellow-500",
  };

  return (
    <Link href={`/learning/topics/${topic.id}`}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardContent className="pt-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h4 className="font-medium">{topic.name}</h4>
              {topic.description && (
                <p className="text-sm text-muted-foreground line-clamp-1">
                  {topic.description}
                </p>
              )}
            </div>
            <Badge variant="outline" className="capitalize">
              {topic.difficulty_level}
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{Math.round(topic.progress_percent)}%</span>
            </div>
            <Progress value={topic.progress_percent} className="h-2" />
          </div>
          <div className="flex items-center gap-2 mt-3">
            <div className={`size-2 rounded-full ${statusColors[topic.status] || 'bg-gray-500'}`} />
            <span className="text-xs text-muted-foreground capitalize">
              {topic.status.replace(/_/g, " ")}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function EvaluationItem({
  evaluation,
}: {
  evaluation: {
    id: string;
    question: string;
    score?: number;
    grade?: string;
    status: string;
    created_at: string;
  };
}) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{evaluation.question}</p>
        <p className="text-xs text-muted-foreground">
          {new Date(evaluation.created_at).toLocaleDateString()}
        </p>
      </div>
      <div className="flex items-center gap-2 ml-4">
        {evaluation.status === "completed" ? (
          <>
            <Badge variant={evaluation.score && evaluation.score >= 70 ? "default" : "secondary"}>
              {evaluation.grade || `${evaluation.score}%`}
            </Badge>
            <CheckCircle2 className="size-4 text-green-500" />
          </>
        ) : (
          <Badge variant="outline">{evaluation.status}</Badge>
        )}
      </div>
    </div>
  );
}

export default function LearningDashboardPage() {
  const { data: goalsData, isLoading: goalsLoading } = useLearningGoals({ status: "active" });
  const { data: topicsData, isLoading: topicsLoading } = useLearningTopics({ status: "in_progress" });
  const { data: evaluationsData, isLoading: evalsLoading } = useEvaluations({ limit: 5 });

  const activeGoals = goalsData?.items?.length || 0;
  const activeTopics = topicsData?.items?.length || 0;
  const completedEvals = evaluationsData?.items?.filter((e: any) => e.status === "completed").length || 0;

  // Calculate average progress
  const avgProgress = topicsData?.items?.length
    ? Math.round(
        topicsData.items.reduce((sum: number, t: any) => sum + (t.progress_percent || 0), 0) /
          topicsData.items.length
      )
    : 0;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
              <GraduationCap className="size-6" />
            </div>
            Learning Hub
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your learning goals, topics, and progress
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" asChild>
            <Link href="/learning/goals">
              <Target className="size-4 mr-2" />
              Goals
            </Link>
          </Button>
          <Button asChild>
            <Link href="/learning/topics?new=true">
              <Plus className="size-4 mr-2" />
              New Topic
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
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`}
                  />
                  <div className="flex items-start gap-4">
                    <div
                      className={`p-3 rounded-xl bg-gradient-to-br ${action.color} text-white`}
                    >
                      <action.icon className="size-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold group-hover:text-primary transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
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
          <StatsCard
            label="Active Goals"
            value={goalsLoading ? "..." : activeGoals}
            icon={Target}
            href="/learning/goals"
          />
          <StatsCard
            label="Topics in Progress"
            value={topicsLoading ? "..." : activeTopics}
            icon={BookOpen}
            href="/learning/topics"
          />
          <StatsCard
            label="Completed Evaluations"
            value={evalsLoading ? "..." : completedEvals}
            icon={ClipboardCheck}
            href="/learning/evaluations"
          />
          <StatsCard
            label="Average Progress"
            value={topicsLoading ? "..." : `${avgProgress}%`}
            icon={TrendingUp}
            href="/learning/topics"
          />
        </div>
      </section>

      {/* Active Topics */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Topics in Progress</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/learning/topics">
              View All
              <ArrowRight className="size-4 ml-1" />
            </Link>
          </Button>
        </div>
        {topicsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="pt-4">
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : topicsData?.items?.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topicsData.items.slice(0, 6).map((topic: any) => (
              <TopicCard key={topic.id} topic={topic} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="size-12 mx-auto mb-4 opacity-50" />
                <p>No topics in progress</p>
                <p className="text-sm mt-1">Start learning something new!</p>
                <Button className="mt-4" asChild>
                  <Link href="/learning/topics?new=true">
                    <Plus className="size-4 mr-2" />
                    Start a Topic
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </section>

      {/* Recent Evaluations */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Evaluations</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/learning/evaluations">
              View All
              <ArrowRight className="size-4 ml-1" />
            </Link>
          </Button>
        </div>
        <Card>
          <CardContent className="pt-4">
            {evalsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : evaluationsData?.items?.length ? (
              <div className="space-y-2">
                {evaluationsData.items.slice(0, 5).map((evaluation: any) => (
                  <EvaluationItem key={evaluation.id} evaluation={evaluation} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <ClipboardCheck className="size-12 mx-auto mb-4 opacity-50" />
                <p>No evaluations yet</p>
                <p className="text-sm mt-1">Complete topics and test your knowledge</p>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {/* AI Learning Assistant Teaser */}
      <section>
        <Card className="bg-gradient-to-br from-violet-500/10 to-purple-500/10 border-violet-500/20">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 text-white">
                <Sparkles className="size-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">AI-Powered Learning</h3>
                <p className="text-sm text-muted-foreground">
                  Generate lesson plans, get instant feedback on evaluations, and chat with an AI
                  tutor about any topic.
                </p>
              </div>
              <Button variant="secondary">
                Learn More
                <ArrowRight className="size-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
