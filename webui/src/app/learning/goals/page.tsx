"use client";

import * as React from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Plus,
  Target,
  Calendar,
  CheckCircle2,
  Clock,
  Pause,
  Archive,
  MoreHorizontal,
  Loader2,
  Trash2,
  Edit,
  FolderKanban,
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
  useLearningGoals,
  useCreateLearningGoal,
  useUpdateLearningGoal,
  useDeleteLearningGoal,
  useProjects,
} from "@/lib/api";
import { toast } from "sonner";

const statusConfig: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  active: { icon: Target, color: "text-blue-500", label: "Active" },
  completed: { icon: CheckCircle2, color: "text-green-500", label: "Completed" },
  paused: { icon: Pause, color: "text-yellow-500", label: "Paused" },
  archived: { icon: Archive, color: "text-gray-500", label: "Archived" },
};

const priorityConfig: Record<string, { color: string; label: string }> = {
  low: { color: "bg-gray-100 text-gray-700", label: "Low" },
  medium: { color: "bg-blue-100 text-blue-700", label: "Medium" },
  high: { color: "bg-orange-100 text-orange-700", label: "High" },
  critical: { color: "bg-red-100 text-red-700", label: "Critical" },
};

interface GoalFormData {
  title: string;
  description: string;
  level: string;
  project_id: string;
  priority: string;
  target_date: string;
}

function GoalFormDialog({
  open,
  onOpenChange,
  goal,
  onSave,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  goal?: any;
  onSave: (data: GoalFormData) => Promise<void>;
}) {
  const { data: projects } = useProjects();
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [formData, setFormData] = React.useState<GoalFormData>({
    title: "",
    description: "",
    level: "user",
    project_id: "",
    priority: "medium",
    target_date: "",
  });

  React.useEffect(() => {
    if (goal) {
      setFormData({
        title: goal.title || "",
        description: goal.description || "",
        level: goal.level || "user",
        project_id: goal.project_id || "",
        priority: goal.priority || "medium",
        target_date: goal.target_date?.split("T")[0] || "",
      });
    } else {
      setFormData({
        title: "",
        description: "",
        level: "user",
        project_id: "",
        priority: "medium",
        target_date: "",
      });
    }
  }, [goal, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error("Title is required");
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
            <DialogTitle>{goal ? "Edit Goal" : "Create Learning Goal"}</DialogTitle>
            <DialogDescription>
              {goal
                ? "Update your learning goal details"
                : "Set a new learning objective to track your progress"}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                placeholder="e.g., Master Machine Learning Fundamentals"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe what you want to achieve..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Level</Label>
                <Select
                  value={formData.level}
                  onValueChange={(v) => setFormData({ ...formData, level: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">Personal</SelectItem>
                    <SelectItem value="project">Project-specific</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Priority</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(v) => setFormData({ ...formData, priority: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {formData.level === "project" && (
              <div className="space-y-2">
                <Label>Project</Label>
                <Select
                  value={formData.project_id}
                  onValueChange={(v) => setFormData({ ...formData, project_id: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects?.items?.map((project: any) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="target_date">Target Date</Label>
              <Input
                id="target_date"
                type="date"
                value={formData.target_date}
                onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
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
                  {goal ? "Saving..." : "Creating..."}
                </>
              ) : goal ? (
                "Save Changes"
              ) : (
                "Create Goal"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function GoalCard({
  goal,
  onEdit,
  onDelete,
  onStatusChange,
}: {
  goal: any;
  onEdit: () => void;
  onDelete: () => void;
  onStatusChange: (status: string) => void;
}) {
  const status = statusConfig[goal.status] || statusConfig.active;
  const priority = priorityConfig[goal.priority] || priorityConfig.medium;
  const StatusIcon = status.icon;

  return (
    <Card className="group">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`p-2 rounded-lg bg-muted ${status.color}`}>
              <StatusIcon className="size-4" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-medium truncate">{goal.title}</h3>
              {goal.description && (
                <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                  {goal.description}
                </p>
              )}
            </div>
          </div>
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
              <DropdownMenuSeparator />
              {goal.status !== "completed" && (
                <DropdownMenuItem onClick={() => onStatusChange("completed")}>
                  <CheckCircle2 className="size-4 mr-2" />
                  Mark Complete
                </DropdownMenuItem>
              )}
              {goal.status !== "paused" && goal.status !== "completed" && (
                <DropdownMenuItem onClick={() => onStatusChange("paused")}>
                  <Pause className="size-4 mr-2" />
                  Pause
                </DropdownMenuItem>
              )}
              {goal.status === "paused" && (
                <DropdownMenuItem onClick={() => onStatusChange("active")}>
                  <Target className="size-4 mr-2" />
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
            <Badge className={priority.color}>{priority.label}</Badge>
            <Badge variant="outline" className="capitalize">
              {goal.level === "project" ? (
                <>
                  <FolderKanban className="size-3 mr-1" />
                  Project
                </>
              ) : (
                "Personal"
              )}
            </Badge>
            {goal.target_date && (
              <Badge variant="secondary">
                <Calendar className="size-3 mr-1" />
                {new Date(goal.target_date).toLocaleDateString()}
              </Badge>
            )}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{Math.round(goal.progress_percent || 0)}%</span>
            </div>
            <Progress value={goal.progress_percent || 0} className="h-2" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function LearningGoalsPage() {
  const [statusFilter, setStatusFilter] = React.useState<string>("all");
  const [levelFilter, setLevelFilter] = React.useState<string>("all");
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [editingGoal, setEditingGoal] = React.useState<any>(null);

  const { data, isLoading, mutate } = useLearningGoals({
    status: statusFilter !== "all" ? statusFilter : undefined,
    level: levelFilter !== "all" ? levelFilter : undefined,
  });
  const { trigger: createGoal } = useCreateLearningGoal();
  const { trigger: updateGoal } = useUpdateLearningGoal();
  const { trigger: deleteGoal } = useDeleteLearningGoal();

  const handleSave = async (formData: GoalFormData) => {
    try {
      if (editingGoal) {
        await updateGoal({
          id: editingGoal.id,
          ...formData,
          project_id: formData.level === "project" ? formData.project_id : null,
        });
        toast.success("Goal updated");
      } else {
        await createGoal({
          ...formData,
          project_id: formData.level === "project" ? formData.project_id : null,
        });
        toast.success("Goal created");
      }
      mutate();
      setEditingGoal(null);
    } catch (error) {
      toast.error("Failed to save goal");
    }
  };

  const handleDelete = async (goal: any) => {
    if (!confirm(`Delete "${goal.title}"?`)) return;
    try {
      await deleteGoal({ id: goal.id });
      toast.success("Goal deleted");
      mutate();
    } catch (error) {
      toast.error("Failed to delete goal");
    }
  };

  const handleStatusChange = async (goal: any, status: string) => {
    try {
      await updateGoal({ id: goal.id, status });
      toast.success(`Goal ${status === "completed" ? "completed" : "updated"}`);
      mutate();
    } catch (error) {
      toast.error("Failed to update goal");
    }
  };

  const goals = data?.items || [];

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
            <h1 className="text-3xl font-bold tracking-tight">Learning Goals</h1>
            <p className="text-muted-foreground">
              Set and track your learning objectives
            </p>
          </div>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="size-4 mr-2" />
          New Goal
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
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>

        <Select value={levelFilter} onValueChange={setLevelFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            <SelectItem value="user">Personal</SelectItem>
            <SelectItem value="project">Project</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Goals Grid */}
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
      ) : goals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {goals.map((goal: any) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onEdit={() => {
                setEditingGoal(goal);
                setDialogOpen(true);
              }}
              onDelete={() => handleDelete(goal)}
              onStatusChange={(status) => handleStatusChange(goal, status)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <Target className="size-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No goals yet</h3>
              <p className="text-sm mb-4">Create your first learning goal to get started</p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="size-4 mr-2" />
                Create Goal
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Goal Form Dialog */}
      <GoalFormDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditingGoal(null);
        }}
        goal={editingGoal}
        onSave={handleSave}
      />
    </div>
  );
}
