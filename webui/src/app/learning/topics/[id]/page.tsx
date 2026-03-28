"use client";

import * as React from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  Clock,
  CheckCircle2,
  Circle,
  Sparkles,
  MessageSquare,
  FileText,
  ChevronDown,
  ChevronRight,
  Loader2,
  Play,
  MoreHorizontal,
  ClipboardCheck,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  useLearningTopic,
  useLessonPlan,
  useUpdateLearningTopic,
  useGenerateLessonPlan,
  useUpdateLessonSection,
} from "@/lib/api";
import { toast } from "sonner";
import { TopicChat } from "@/components/learning/topic-chat";

const difficultyConfig: Record<string, { color: string; label: string }> = {
  beginner: { color: "bg-green-100 text-green-700", label: "Beginner" },
  intermediate: { color: "bg-blue-100 text-blue-700", label: "Intermediate" },
  advanced: { color: "bg-orange-100 text-orange-700", label: "Advanced" },
  expert: { color: "bg-red-100 text-red-700", label: "Expert" },
};

function LessonPlanViewer({
  plan,
  onSectionComplete,
}: {
  plan: any;
  onSectionComplete: (sectionId: string, completed: boolean) => void;
}) {
  const [expandedSections, setExpandedSections] = React.useState<string[]>([]);

  const toggleSection = (sectionId: string) => {
    setExpandedSections((prev) =>
      prev.includes(sectionId)
        ? prev.filter((id) => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  return (
    <div className="space-y-4">
      {/* Plan Overview */}
      <Card>
        <CardHeader>
          <CardTitle>{plan.title}</CardTitle>
          {plan.overview && (
            <CardDescription className="whitespace-pre-wrap">{plan.overview}</CardDescription>
          )}
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="p-3 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground">Sections</p>
              <p className="text-xl font-semibold">
                {plan.completed_sections} / {plan.total_sections}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground">Est. Duration</p>
              <p className="text-xl font-semibold">
                {plan.estimated_duration_minutes
                  ? `${Math.round(plan.estimated_duration_minutes / 60)}h`
                  : "—"}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground">Progress</p>
              <p className="text-xl font-semibold">
                {plan.total_sections > 0
                  ? Math.round((plan.completed_sections / plan.total_sections) * 100)
                  : 0}%
              </p>
            </div>
            <div className="p-3 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground">Status</p>
              <p className="text-xl font-semibold capitalize">{plan.status}</p>
            </div>
          </div>

          {plan.objectives?.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium">Learning Objectives</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                {plan.objectives.map((obj: string, i: number) => (
                  <li key={i}>{obj}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sections */}
      <div className="space-y-2">
        <h3 className="font-semibold">Lesson Sections</h3>
        {plan.sections?.map((section: any, index: number) => (
          <Card key={section.id} className="overflow-hidden">
            <Collapsible
              open={expandedSections.includes(section.id)}
              onOpenChange={() => toggleSection(section.id)}
            >
              <CollapsibleTrigger className="w-full">
                <div className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSectionComplete(section.id, !section.is_completed);
                    }}
                  >
                    {section.is_completed ? (
                      <CheckCircle2 className="size-5 text-green-500" />
                    ) : (
                      <Circle className="size-5 text-muted-foreground" />
                    )}
                  </Button>
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {index + 1}. {section.title}
                      </span>
                      <Badge variant="outline" className="text-xs capitalize">
                        {section.section_type}
                      </Badge>
                      {section.estimated_minutes && (
                        <Badge variant="secondary" className="text-xs">
                          <Clock className="size-3 mr-1" />
                          {section.estimated_minutes}m
                        </Badge>
                      )}
                    </div>
                    {section.summary && (
                      <p className="text-sm text-muted-foreground line-clamp-1 mt-1">
                        {section.summary}
                      </p>
                    )}
                  </div>
                  {expandedSections.includes(section.id) ? (
                    <ChevronDown className="size-4 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="size-4 text-muted-foreground" />
                  )}
                </div>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="px-4 pb-4 pt-0 border-t">
                  <div className="prose prose-sm max-w-none pt-4">
                    {section.content ? (
                      <div className="whitespace-pre-wrap">{section.content}</div>
                    ) : (
                      <p className="text-muted-foreground italic">No content yet</p>
                    )}
                  </div>

                  {section.resources?.length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-medium text-sm mb-2">Resources</h5>
                      <div className="space-y-1">
                        {section.resources.map((resource: any, i: number) => (
                          <a
                            key={i}
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-primary hover:underline"
                          >
                            <FileText className="size-3" />
                            {resource.title || resource.url}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {section.exercises?.length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-medium text-sm mb-2">Exercises</h5>
                      <ul className="space-y-2">
                        {section.exercises.map((exercise: any, i: number) => (
                          <li key={i} className="text-sm p-2 rounded bg-muted">
                            {exercise.description}
                            {exercise.difficulty && (
                              <Badge variant="outline" className="ml-2 text-xs">
                                {exercise.difficulty}
                              </Badge>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default function TopicDetailPage() {
  const router = useRouter();
  const params = useParams();
  const topicId = params.id as string;

  const { data: topic, isLoading: topicLoading, mutate: mutateTopic } = useLearningTopic(topicId);
  const { data: lessonPlan, isLoading: planLoading, mutate: mutatePlan } = useLessonPlan(
    topic?.lesson_plan_id || null
  );
  const { trigger: updateTopic } = useUpdateLearningTopic();
  const { trigger: generatePlan, isMutating: isGenerating } = useGenerateLessonPlan();
  const { trigger: updateSection } = useUpdateLessonSection();

  const handleGeneratePlan = async () => {
    try {
      await generatePlan({ topicId });
      toast.success("Lesson plan generated!");
      mutateTopic();
    } catch (error) {
      toast.error("Failed to generate lesson plan");
    }
  };

  const handleStartLearning = async () => {
    try {
      await updateTopic({ id: topicId, status: "in_progress" });
      toast.success("Started learning!");
      mutateTopic();
    } catch (error) {
      toast.error("Failed to update topic");
    }
  };

  const handleSectionComplete = async (sectionId: string, completed: boolean) => {
    if (!topic?.lesson_plan_id) return;

    try {
      await updateSection({
        planId: topic.lesson_plan_id,
        sectionId,
        is_completed: completed,
      });
      mutatePlan();

      // Update topic progress
      if (lessonPlan) {
        const totalSections = lessonPlan.total_sections || 1;
        const completedSections = Math.max(0, Math.min(
          totalSections,
          lessonPlan.completed_sections + (completed ? 1 : -1)
        ));
        const progress = (completedSections / totalSections) * 100;
        await updateTopic({ id: topicId, progress_percent: progress });
        mutateTopic();
      }
    } catch (error) {
      toast.error("Failed to update section");
    }
  };

  if (topicLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
          </div>
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!topic) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">Topic not found</p>
            <Button asChild className="mt-4">
              <Link href="/learning/topics">Back to Topics</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const difficulty = difficultyConfig[topic.difficulty_level] || difficultyConfig.intermediate;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/learning/topics">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{topic.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={difficulty.color}>{difficulty.label}</Badge>
              <Badge variant="outline" className="capitalize">
                {topic.status.replace(/_/g, " ")}
              </Badge>
              {topic.estimated_hours && (
                <span className="text-sm text-muted-foreground">
                  <Clock className="size-3 inline mr-1" />
                  {topic.estimated_hours}h estimated
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {topic.status === "not_started" && (
            <Button onClick={handleStartLearning}>
              <Play className="size-4 mr-2" />
              Start Learning
            </Button>
          )}
          {!topic.lesson_plan_id && (
            <Button variant="outline" onClick={handleGeneratePlan} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="size-4 mr-2" />
                  Generate Plan
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Progress Card */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm font-medium">
              {Math.round(topic.progress_percent || 0)}%
            </span>
          </div>
          <Progress value={topic.progress_percent || 0} className="h-3" />
          {topic.description && (
            <p className="text-sm text-muted-foreground mt-4">{topic.description}</p>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="lesson-plan">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="lesson-plan">
            <FileText className="size-4 mr-2" />
            Lesson Plan
          </TabsTrigger>
          <TabsTrigger value="chat">
            <MessageSquare className="size-4 mr-2" />
            AI Tutor
          </TabsTrigger>
          <TabsTrigger value="evaluations">
            <ClipboardCheck className="size-4 mr-2" />
            Evaluations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="lesson-plan" className="mt-4">
          {planLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-48" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
            </div>
          ) : lessonPlan ? (
            <LessonPlanViewer plan={lessonPlan} onSectionComplete={handleSectionComplete} />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <FileText className="size-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                  <h3 className="text-lg font-medium mb-2">No Lesson Plan Yet</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Generate an AI-powered lesson plan to structure your learning
                  </p>
                  <Button onClick={handleGeneratePlan} disabled={isGenerating}>
                    {isGenerating ? (
                      <>
                        <Loader2 className="size-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-4 mr-2" />
                        Generate Lesson Plan
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="chat" className="mt-4">
          <TopicChat topicId={topicId} topicName={topic.name} />
        </TabsContent>

        <TabsContent value="evaluations" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Evaluations</CardTitle>
              <CardDescription>
                Test your understanding with AI-graded assessments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <ClipboardCheck className="size-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-muted-foreground mb-4">No evaluations taken yet</p>
                <Button asChild>
                  <Link href={`/learning/evaluations?topic_id=${topicId}`}>
                    <ClipboardCheck className="size-4 mr-2" />
                    Start Evaluation
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
