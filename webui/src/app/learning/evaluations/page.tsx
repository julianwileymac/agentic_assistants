"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  ClipboardCheck,
  Plus,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Send,
  BookOpen,
  TrendingUp,
  Award,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useEvaluations,
  useEvaluationStats,
  useCreateEvaluation,
  useSubmitEvaluation,
  useLearningTopics,
} from "@/lib/api";
import { toast } from "sonner";
import { TestingSection } from "@/components/testing/testing-section";

const gradeColors: Record<string, string> = {
  A: "bg-green-100 text-green-700",
  "A-": "bg-green-100 text-green-700",
  "B+": "bg-blue-100 text-blue-700",
  B: "bg-blue-100 text-blue-700",
  "B-": "bg-blue-100 text-blue-700",
  "C+": "bg-yellow-100 text-yellow-700",
  C: "bg-yellow-100 text-yellow-700",
  "C-": "bg-yellow-100 text-yellow-700",
  D: "bg-orange-100 text-orange-700",
  F: "bg-red-100 text-red-700",
};

function EvaluationDialog({
  open,
  onOpenChange,
  evaluation,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evaluation: any;
  onSubmit: (response: string) => Promise<void>;
}) {
  const [response, setResponse] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (open) {
      setResponse("");
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!response.trim()) {
      toast.error("Please provide a response");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(response);
      onOpenChange(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Answer Evaluation</DialogTitle>
            <DialogDescription>
              Provide your response to the question below. Your answer will be evaluated by AI.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4 space-y-4">
            <div className="p-4 rounded-lg bg-muted">
              <p className="font-medium mb-2">Question:</p>
              <p className="text-sm">{evaluation?.question}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="response">Your Response</Label>
              <Textarea
                id="response"
                placeholder="Type your answer here..."
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                rows={6}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Evaluating...
                </>
              ) : (
                <>
                  <Send className="size-4 mr-2" />
                  Submit for Grading
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function NewEvaluationDialog({
  open,
  onOpenChange,
  defaultTopicId,
  onCreate,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultTopicId?: string;
  onCreate: (data: { topic_id: string; question: string; evaluation_type: string }) => Promise<void>;
}) {
  const { data: topics } = useLearningTopics();
  const [topicId, setTopicId] = React.useState(defaultTopicId || "");
  const [question, setQuestion] = React.useState("");
  const [evaluationType, setEvaluationType] = React.useState("comprehension");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (open) {
      setTopicId(defaultTopicId || "");
      setQuestion("");
      setEvaluationType("comprehension");
    }
  }, [open, defaultTopicId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error("Question is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await onCreate({ topic_id: topicId, question, evaluation_type: evaluationType });
      onOpenChange(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Evaluation</DialogTitle>
            <DialogDescription>
              Create a new evaluation question to test your knowledge
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Topic (Optional)</Label>
              <Select value={topicId} onValueChange={setTopicId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a topic" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">No specific topic</SelectItem>
                  {topics?.items?.map((topic: any) => (
                    <SelectItem key={topic.id} value={topic.id}>
                      {topic.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Evaluation Type</Label>
              <Select value={evaluationType} onValueChange={setEvaluationType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="comprehension">Comprehension</SelectItem>
                  <SelectItem value="application">Application</SelectItem>
                  <SelectItem value="synthesis">Synthesis</SelectItem>
                  <SelectItem value="analysis">Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="question">Question *</Label>
              <Textarea
                id="question"
                placeholder="Enter your evaluation question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={4}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Evaluation"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EvaluationCard({
  evaluation,
  onAnswer,
}: {
  evaluation: any;
  onAnswer: () => void;
}) {
  const gradeColor = gradeColors[evaluation.grade] || "bg-gray-100 text-gray-700";

  return (
    <Card className="hover:bg-muted/50 transition-colors">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <p className="font-medium line-clamp-2">{evaluation.question}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(evaluation.created_at).toLocaleDateString()} ·{" "}
              <span className="capitalize">{evaluation.evaluation_type}</span>
            </p>
          </div>
          <div className="flex items-center gap-2 ml-4">
            {evaluation.status === "completed" ? (
              <>
                {evaluation.score !== null && (
                  <Badge className={gradeColor}>
                    {evaluation.grade || `${Math.round(evaluation.score)}%`}
                  </Badge>
                )}
                <CheckCircle2 className="size-5 text-green-500" />
              </>
            ) : evaluation.status === "failed" ? (
              <>
                <Badge variant="destructive">Failed</Badge>
                <XCircle className="size-5 text-red-500" />
              </>
            ) : (
              <>
                <Badge variant="outline">Pending</Badge>
                <Button size="sm" onClick={onAnswer}>
                  Answer
                </Button>
              </>
            )}
          </div>
        </div>

        {evaluation.status === "completed" && evaluation.feedback && (
          <div className="mt-3 p-3 rounded-lg bg-muted text-sm">
            <p className="font-medium text-xs mb-1">Feedback:</p>
            <p className="text-muted-foreground line-clamp-3">{evaluation.feedback}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function StatsOverview({ stats }: { stats: any }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100">
              <ClipboardCheck className="size-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_evaluations}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-100">
              <CheckCircle2 className="size-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completed_evaluations}</p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-100">
              <TrendingUp className="size-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {stats.average_score ? `${Math.round(stats.average_score)}%` : "—"}
              </p>
              <p className="text-xs text-muted-foreground">Average</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-100">
              <Award className="size-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {stats.highest_score ? `${Math.round(stats.highest_score)}%` : "—"}
              </p>
              <p className="text-xs text-muted-foreground">Best Score</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function EvaluationsPage() {
  const searchParams = useSearchParams();
  const topicIdParam = searchParams.get("topic_id");
  const showNew = searchParams.get("new") === "true";

  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [newDialogOpen, setNewDialogOpen] = React.useState(showNew);
  const [answerDialogOpen, setAnswerDialogOpen] = React.useState(false);
  const [selectedEvaluation, setSelectedEvaluation] = React.useState<any>(null);

  const { data, isLoading, mutate } = useEvaluations({
    status: statusFilter !== "all" ? statusFilter : undefined,
    topic_id: topicIdParam || undefined,
  });
  const { data: stats, isLoading: statsLoading } = useEvaluationStats({
    topic_id: topicIdParam || undefined,
  });
  const { trigger: createEvaluation } = useCreateEvaluation();
  const { trigger: submitEvaluation } = useSubmitEvaluation();

  const handleCreate = async (data: {
    topic_id: string;
    question: string;
    evaluation_type: string;
  }) => {
    try {
      await createEvaluation(data);
      toast.success("Evaluation created");
      mutate();
    } catch (error) {
      toast.error("Failed to create evaluation");
    }
  };

  const handleSubmit = async (response: string) => {
    if (!selectedEvaluation) return;

    try {
      await submitEvaluation({
        evaluation_id: selectedEvaluation.id,
        user_response: response,
      });
      toast.success("Response submitted and graded!");
      mutate();
    } catch (error) {
      toast.error("Failed to submit evaluation");
    }
  };

  const evaluations = data?.items || [];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/learning">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Evaluations</h1>
            <p className="text-muted-foreground">
              Test your knowledge with AI-graded assessments
            </p>
          </div>
        </div>
        <Button onClick={() => setNewDialogOpen(true)}>
          <Plus className="size-4 mr-2" />
          New Evaluation
        </Button>
      </div>

      {/* Stats */}
      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="pt-4">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : stats ? (
        <StatsOverview stats={stats} />
      ) : null}

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Evaluations List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-4">
                <Skeleton className="h-24 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : evaluations.length > 0 ? (
        <div className="space-y-4">
          {evaluations.map((evaluation: any) => (
            <EvaluationCard
              key={evaluation.id}
              evaluation={evaluation}
              onAnswer={() => {
                setSelectedEvaluation(evaluation);
                setAnswerDialogOpen(true);
              }}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <ClipboardCheck className="size-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No evaluations yet</h3>
              <p className="text-sm mb-4">Create your first evaluation to test your knowledge</p>
              <Button onClick={() => setNewDialogOpen(true)}>
                <Plus className="size-4 mr-2" />
                Create Evaluation
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* New Evaluation Dialog */}
      <NewEvaluationDialog
        open={newDialogOpen}
        onOpenChange={setNewDialogOpen}
        defaultTopicId={topicIdParam || undefined}
        onCreate={handleCreate}
      />

      {/* Answer Dialog */}
      <EvaluationDialog
        open={answerDialogOpen}
        onOpenChange={setAnswerDialogOpen}
        evaluation={selectedEvaluation}
        onSubmit={handleSubmit}
      />

      <TestingSection
        resourceType="evaluation"
        resourceName="Evaluation"
        defaultCode={`# Evaluation test\nresult = {\n    \"status\": \"ok\",\n    \"notes\": \"Validate evaluation workflows\",\n}\n`}
      />
    </div>
  );
}
