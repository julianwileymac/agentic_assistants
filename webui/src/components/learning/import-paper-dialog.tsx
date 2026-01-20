"use client";

import * as React from "react";
import {
  Upload,
  FileText,
  Link as LinkIcon,
  Loader2,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Sparkles,
  Plus,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useImportPaper, useLearningGoals } from "@/lib/api";
import { toast } from "sonner";

interface ImportPaperDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

type ImportStep = "upload" | "processing" | "preview" | "complete";

interface ExtractedTopic {
  name: string;
  description: string;
  difficulty: string;
  confidence: number;
  selected: boolean;
}

export function ImportPaperDialog({
  open,
  onOpenChange,
  onSuccess,
}: ImportPaperDialogProps) {
  const [step, setStep] = React.useState<ImportStep>("upload");
  const [inputType, setInputType] = React.useState<"file" | "url">("file");
  const [file, setFile] = React.useState<File | null>(null);
  const [url, setUrl] = React.useState("");
  const [title, setTitle] = React.useState("");
  const [goalId, setGoalId] = React.useState("");
  const [autoGeneratePlans, setAutoGeneratePlans] = React.useState(false);
  const [extractedTopics, setExtractedTopics] = React.useState<ExtractedTopic[]>([]);
  const [summary, setSummary] = React.useState("");
  const [artifactId, setArtifactId] = React.useState("");
  const [progress, setProgress] = React.useState(0);

  const { data: goals } = useLearningGoals({ status: "active" });
  const { trigger: importPaper, isMutating: isImporting } = useImportPaper();

  const resetState = () => {
    setStep("upload");
    setInputType("file");
    setFile(null);
    setUrl("");
    setTitle("");
    setGoalId("");
    setAutoGeneratePlans(false);
    setExtractedTopics([]);
    setSummary("");
    setArtifactId("");
    setProgress(0);
  };

  const handleClose = () => {
    onOpenChange(false);
    resetState();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleImport = async () => {
    if (inputType === "file" && !file) {
      toast.error("Please select a file");
      return;
    }
    if (inputType === "url" && !url) {
      toast.error("Please enter a URL");
      return;
    }

    setStep("processing");
    setProgress(10);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 10, 80));
    }, 500);

    try {
      const formData = new FormData();
      if (file) {
        formData.append("file", file);
      }
      if (url) {
        formData.append("url", url);
      }
      if (title) {
        formData.append("title", title);
      }
      if (goalId) {
        formData.append("goal_id", goalId);
      }
      formData.append("auto_generate_plans", String(autoGeneratePlans));

      const result = await importPaper(formData);

      clearInterval(progressInterval);
      setProgress(100);

      setArtifactId(result.artifact_id);
      setSummary(result.summary || "");
      setExtractedTopics(
        (result.extracted_topics || []).map((t: any) => ({
          ...t,
          selected: true,
        }))
      );

      setStep("preview");
    } catch (error) {
      clearInterval(progressInterval);
      toast.error("Failed to import paper");
      setStep("upload");
      setProgress(0);
    }
  };

  const toggleTopicSelection = (index: number) => {
    setExtractedTopics((prev) =>
      prev.map((t, i) => (i === index ? { ...t, selected: !t.selected } : t))
    );
  };

  const handleComplete = () => {
    const selectedCount = extractedTopics.filter((t) => t.selected).length;
    toast.success(
      `Paper imported${selectedCount > 0 ? ` with ${selectedCount} topics` : ""}`
    );
    handleClose();
    onSuccess?.();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="size-5" />
            Import Research Paper
          </DialogTitle>
          <DialogDescription>
            {step === "upload" && "Upload a paper or provide a URL to extract learning topics"}
            {step === "processing" && "Analyzing document and extracting topics..."}
            {step === "preview" && "Review extracted topics and select which ones to create"}
          </DialogDescription>
        </DialogHeader>

        {step === "upload" && (
          <>
            <Tabs value={inputType} onValueChange={(v) => setInputType(v as "file" | "url")}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="file">
                  <FileText className="size-4 mr-2" />
                  Upload File
                </TabsTrigger>
                <TabsTrigger value="url">
                  <LinkIcon className="size-4 mr-2" />
                  From URL
                </TabsTrigger>
              </TabsList>

              <TabsContent value="file" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="file">Paper File</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="file"
                      type="file"
                      accept=".pdf,.txt,.md"
                      onChange={handleFileChange}
                      className="flex-1"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Supported formats: PDF, TXT, Markdown
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="url" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="url">Paper URL</Label>
                  <Input
                    id="url"
                    type="url"
                    placeholder="https://arxiv.org/abs/..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </div>
              </TabsContent>
            </Tabs>

            <div className="space-y-4 pt-4 border-t">
              <div className="space-y-2">
                <Label htmlFor="title">Title (Optional)</Label>
                <Input
                  id="title"
                  placeholder="Paper title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              {goals?.items?.length > 0 && (
                <div className="space-y-2">
                  <Label>Link to Goal (Optional)</Label>
                  <Select value={goalId} onValueChange={setGoalId}>
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

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="auto-generate"
                  checked={autoGeneratePlans}
                  onCheckedChange={(checked) => setAutoGeneratePlans(checked as boolean)}
                />
                <Label htmlFor="auto-generate" className="text-sm cursor-pointer">
                  Automatically create topics from extracted content
                </Label>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleImport} disabled={isImporting}>
                {isImporting ? (
                  <>
                    <Loader2 className="size-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Sparkles className="size-4 mr-2" />
                    Analyze Paper
                  </>
                )}
              </Button>
            </DialogFooter>
          </>
        )}

        {step === "processing" && (
          <div className="py-8 space-y-4">
            <div className="text-center">
              <Loader2 className="size-12 mx-auto mb-4 animate-spin text-primary" />
              <p className="font-medium">Analyzing document...</p>
              <p className="text-sm text-muted-foreground mt-1">
                Extracting topics and generating summaries
              </p>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {step === "preview" && (
          <>
            <div className="space-y-4">
              {summary && (
                <div className="p-4 rounded-lg bg-muted">
                  <h4 className="font-medium text-sm mb-2">Summary</h4>
                  <p className="text-sm text-muted-foreground">{summary}</p>
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">Extracted Topics</h4>
                  <span className="text-xs text-muted-foreground">
                    {extractedTopics.filter((t) => t.selected).length} of {extractedTopics.length}{" "}
                    selected
                  </span>
                </div>

                <ScrollArea className="h-[200px] rounded-lg border">
                  <div className="p-2 space-y-2">
                    {extractedTopics.length > 0 ? (
                      extractedTopics.map((topic, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                            topic.selected
                              ? "bg-primary/5 border-primary"
                              : "bg-card hover:bg-muted/50"
                          }`}
                          onClick={() => toggleTopicSelection(index)}
                        >
                          <div className="flex items-start gap-3">
                            <Checkbox checked={topic.selected} className="mt-1" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-sm">{topic.name}</span>
                                <Badge variant="outline" className="text-xs capitalize">
                                  {topic.difficulty}
                                </Badge>
                              </div>
                              {topic.description && (
                                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                  {topic.description}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <AlertCircle className="size-8 mx-auto mb-2" />
                        <p className="text-sm">No topics could be extracted</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setStep("upload")}>
                Back
              </Button>
              <Button onClick={handleComplete}>
                <CheckCircle2 className="size-4 mr-2" />
                Complete Import
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default ImportPaperDialog;
