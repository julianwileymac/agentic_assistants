"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  Plus,
  BookOpen,
  Clock,
  CheckCircle2,
  Pause,
  Play,
  MoreHorizontal,
  Loader2,
  Trash2,
  Edit,
  Sparkles,
  Target,
  FileText,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  useLearningTopics,
  useCreateLearningTopic,
  useUpdateLearningTopic,
  useDeleteLearningTopic,
  useLearningGoals,
  useGenerateLessonPlan,
} from "@/lib/api";
import { toast } from "sonner";

const statusConfig: Record<string, { color: string; bgColor: string; label: string }> = {
  not_started: { color: "text-gray-500", bgColor: "bg-gray-100", label: "Not Started" },
  in_progress: { color: "text-blue-500", bgColor: "bg-blue-100", label: "In Progress" },
  completed: { color: "text-green-500", bgColor: "bg-green-100", label: "Completed" },
  paused: { color: "text-yellow-500", bgColor: "bg-yellow-100", label: "Paused" },
};

const difficultyConfig: Record<string, { color: string; label: string }> = {
  beginner: { color: "bg-green-100 text-green-700", label: "Beginner" },
  intermediate: { color: "bg-blue-100 text-blue-700", label: "Intermediate" },
  advanced: { color: "bg-orange-100 text-orange-700", label: "Advanced" },
  expert: { color: "bg-red-100 text-red-700", label: "Expert" },
};

interface TopicFormData {
  name: string;
  description: string;
  goal_id: string;
  difficulty_level: string;
  estimated_hours: string;
}

function TopicFormDialog({
  open,
  onOpenChange,
  topic,
  onSave,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  topic?: any;
  onSave: (data: TopicFormData) => Promise<void>;
}) {
  const { data: goals } = useLearningGoals({ status: "active" });
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [formData, setFormData] = React.useState<TopicFormData>({
    name: "",
    description: "",
    goal_id: "",
    difficulty_level: "intermediate",
    estimated_hours: "",
  });

  React.useEffect(() => {
    if (topic) {
      setFormData({
        name: topic.name || "",
        description: topic.description || "",
        goal_id: topic.goal_id || "",
        difficulty_level: topic.difficulty_level || "intermediate",
        estimated_hours: topic.estimated_hours?.toString() || "",
      });
    } else {
      setFormData({
        name: "",
        description: "",
        goal_id: "",
        difficulty_level: "intermediate",
        estimated_hours: "",
      });
    }
  }, [topic, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Topic name is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSave(formData);
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
            <DialogTitle>{topic ? "Edit Topic" : "Create Learning Topic"}</DialogTitle>
            <DialogDescription>
              {topic
                ? "Update your learning topic details"
                : "Add a new topic to learn and track your progress"}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Topic Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Neural Network Architectures"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="What does this topic cover?"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Difficulty</Label>
                <Select
                  value={formData.difficulty_level}
                  onValueChange={(v) => setFormData({ ...formData, difficulty_level: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                    <SelectItem value="expert">Expert</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="estimated_hours">Est. Hours</Label>
                <Input
                  id="estimated_hours"
                  type="number"
                  min="0"
                  step="0.5"
                  placeholder="e.g., 5"
                  value={formData.estimated_hours}
                  onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                />
              </div>
            </div>

            {goals?.items?.length > 0 && (
              <div className="space-y-2">
                <Label>Link to Goal (Optional)</Label>
                <Select
                  value={formData.goal_id}
                  onValueChange={(v) => setFormData({ ...formData, goal_id: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a goal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No goal</SelectItem>
                    {goals.items.map((goal: any) => (
                      <SelectItem key={goal.id} value={goal.id}>
                        {goal.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  {topic ? "Saving..." : "Creating..."}
                </>
              ) : topic ? (
                "Save Changes"
              ) : (
                "Create Topic"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function TopicCard({
  topic,
  onEdit,
  onDelete,
  onStatusChange,
  onGeneratePlan,
  isGenerating,
}: {
  topic: any;
  onEdit: () => void;
  onDelete: () => void;
  onStatusChange: (status: string) => void;
  onGeneratePlan: () => void;
  isGenerating: boolean;
}) {
  const status = statusConfig[topic.status] || statusConfig.not_started;
  const difficulty = difficultyConfig[topic.difficulty_level] || difficultyConfig.intermediate;

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between mb-3">
          <Link href={`/learning/topics/${topic.id}`} className="flex-1 min-w-0">
            <h3 className="font-medium hover:text-primary transition-colors">
              {topic.name}
            </h3>
            {topic.description && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                {topic.description}
              </p>
            )}
          </Link>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="size-8 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onEdit}>
                <Edit className="size-4 mr-2" />
                Edit
              </DropdownMenuItem>
              {!topic.lesson_plan_id && (
                <DropdownMenuItem onClick={onGeneratePlan} disabled={isGenerating}>
                  <Sparkles className="size-4 mr-2" />
                  Generate Lesson Plan
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              {topic.status === "not_started" && (
                <DropdownMenuItem onClick={() => onStatusChange("in_progress")}>
                  <Play className="size-4 mr-2" />
                  Start Learning
                </DropdownMenuItem>
              )}
              {topic.status === "in_progress" && (
                <>
                  <DropdownMenuItem onClick={() => onStatusChange("completed")}>
                    <CheckCircle2 className="size-4 mr-2" />
                    Mark Complete
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onStatusChange("paused")}>
                    <Pause className="size-4 mr-2" />
                    Pause
                  </DropdownMenuItem>
                </>
              )}
              {topic.status === "paused" && (
                <DropdownMenuItem onClick={() => onStatusChange("in_progress")}>
                  <Play className="size-4 mr-2" />
                  Resume
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onDelete} className="text-destructive">
                <Trash2 className="size-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className={difficulty.color}>{difficulty.label}</Badge>
            <Badge variant="outline" className={status.color}>
              {status.label}
            </Badge>
            {topic.lesson_plan_id && (
              <Badge variant="secondary">
                <FileText className="size-3 mr-1" />
                Has Plan
              </Badge>
            )}
            {topic.estimated_hours && (
              <Badge variant="secondary">
                <Clock className="size-3 mr-1" />
                {topic.estimated_hours}h
              </Badge>
            )}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{Math.round(topic.progress_percent || 0)}%</span>
            </div>
            <Progress value={topic.progress_percent || 0} className="h-2" />
          </div>

          {topic.goal_id && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Target className="size-3" />
              <span>Linked to goal</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function LearningTopicsPage() {
  const searchParams = useSearchParams();
  const showNewDialog = searchParams.get("new") === "true";

  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [difficultyFilter, setDifficultyFilter] = React.useState<string>("all");
  const [dialogOpen, setDialogOpen] = React.useState(showNewDialog);
  const [editingTopic, setEditingTopic] = React.useState<any>(null);
  const [generatingPlanFor, setGeneratingPlanFor] = React.useState<string | null>(null);

  const { data, isLoading, mutate } = useLearningTopics({
    status: statusFilter !== "all" ? statusFilter : undefined,
  });
  const { trigger: createTopic } = useCreateLearningTopic();
  const { trigger: updateTopic } = useUpdateLearningTopic();
  const { trigger: deleteTopic } = useDeleteLearningTopic();
  const { trigger: generatePlan } = useGenerateLessonPlan();

  const handleSave = async (formData: TopicFormData) => {
    try {
      const payload = {
        ...formData,
        goal_id: formData.goal_id || null,
        estimated_hours: formData.estimated_hours ? parseFloat(formData.estimated_hours) : null,
      };

      if (editingTopic) {
        await updateTopic({ id: editingTopic.id, ...payload });
        toast.success("Topic updated");
      } else {
        await createTopic(payload);
        toast.success("Topic created");
      }
      mutate();
      setEditingTopic(null);
    } catch (error) {
      toast.error("Failed to save topic");
    }
  };

  const handleDelete = async (topic: any) => {
    if (!confirm(`Delete "${topic.name}"?`)) return;
    try {
      await deleteTopic({ id: topic.id });
      toast.success("Topic deleted");
      mutate();
    } catch (error) {
      toast.error("Failed to delete topic");
    }
  };

  const handleStatusChange = async (topic: any, status: string) => {
    try {
      await updateTopic({ id: topic.id, status });
      toast.success("Topic updated");
      mutate();
    } catch (error) {
      toast.error("Failed to update topic");
    }
  };

  const handleGeneratePlan = async (topic: any) => {
    setGeneratingPlanFor(topic.id);
    try {
      await generatePlan({ topicId: topic.id });
      toast.success("Lesson plan generated!");
      mutate();
    } catch (error) {
      toast.error("Failed to generate lesson plan");
    } finally {
      setGeneratingPlanFor(null);
    }
  };

  let topics = data?.items || [];

  // Client-side difficulty filter
  if (difficultyFilter !== "all") {
    topics = topics.filter((t: any) => t.difficulty_level === difficultyFilter);
  }

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
            <h1 className="text-3xl font-bold tracking-tight">Learning Topics</h1>
            <p className="text-muted-foreground">
              Manage your learning topics and track progress
            </p>
          </div>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="size-4 mr-2" />
          New Topic
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="not_started">Not Started</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
          </SelectContent>
        </Select>

        <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            <SelectItem value="beginner">Beginner</SelectItem>
            <SelectItem value="intermediate">Intermediate</SelectItem>
            <SelectItem value="advanced">Advanced</SelectItem>
            <SelectItem value="expert">Expert</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Topics Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="pt-4">
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : topics.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topics.map((topic: any) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              onEdit={() => {
                setEditingTopic(topic);
                setDialogOpen(true);
              }}
              onDelete={() => handleDelete(topic)}
              onStatusChange={(status) => handleStatusChange(topic, status)}
              onGeneratePlan={() => handleGeneratePlan(topic)}
              isGenerating={generatingPlanFor === topic.id}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <BookOpen className="size-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No topics yet</h3>
              <p className="text-sm mb-4">Create your first learning topic to get started</p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="size-4 mr-2" />
                Create Topic
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Topic Form Dialog */}
      <TopicFormDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditingTopic(null);
        }}
        topic={editingTopic}
        onSave={handleSave}
      />
    </div>
  );
}
