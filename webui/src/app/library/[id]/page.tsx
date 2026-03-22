"use client";

import * as React from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Save, 
  Loader2, 
  Trash2, 
  Code,
  Puzzle,
  Copy,
  BookOpen,
  Clock,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { CodeEditor } from "@/components/code-editor";
import { TestingSection } from "@/components/testing/testing-section";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useComponent } from "@/lib/api";
import { toast } from "sonner";

const COMPONENT_CATEGORIES = [
  { value: "tool", label: "Tool", description: "Reusable agent tools" },
  { value: "agent", label: "Agent", description: "Agent templates" },
  { value: "task", label: "Task", description: "Task definitions" },
  { value: "pattern", label: "Pattern", description: "Agentic patterns" },
  { value: "utility", label: "Utility", description: "Utility functions" },
  { value: "template", label: "Template", description: "Project templates" },
  { value: "snippet", label: "Snippet", description: "Reusable code snippets" },
  { value: "datasource_handler", label: "Data Source Handler", description: "Data source handlers" },
  { value: "embedding_model", label: "Embedding Model", description: "Embedding configurations" },
  { value: "prompt_template", label: "Prompt Template", description: "Reusable prompts" },
  { value: "workflow_node", label: "Workflow Node", description: "Workflow nodes" },
  { value: "retrieval_strategy", label: "Retrieval Strategy", description: "RAG retrieval strategies" },
  { value: "llm_wrapper", label: "LLM Wrapper", description: "LLM integrations" },
  { value: "crew_config", label: "Crew Configuration", description: "CrewAI configurations" },
];

const LANGUAGES = [
  { value: "python", label: "Python" },
  { value: "typescript", label: "TypeScript" },
  { value: "javascript", label: "JavaScript" },
  { value: "yaml", label: "YAML" },
  { value: "json", label: "JSON" },
  { value: "markdown", label: "Markdown" },
];

const categoryColors: Record<string, string> = {
  tool: "bg-blue-500/10 text-blue-500",
  agent: "bg-violet-500/10 text-violet-500",
  task: "bg-emerald-500/10 text-emerald-500",
  pattern: "bg-orange-500/10 text-orange-500",
  utility: "bg-gray-500/10 text-gray-500",
  template: "bg-pink-500/10 text-pink-500",
  snippet: "bg-slate-500/10 text-slate-500",
  datasource_handler: "bg-cyan-500/10 text-cyan-500",
  embedding_model: "bg-indigo-500/10 text-indigo-500",
  prompt_template: "bg-yellow-500/10 text-yellow-600",
  workflow_node: "bg-rose-500/10 text-rose-500",
  retrieval_strategy: "bg-teal-500/10 text-teal-500",
  llm_wrapper: "bg-purple-500/10 text-purple-500",
  crew_config: "bg-amber-500/10 text-amber-600",
};

export default function ComponentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const componentId = params.id as string;

  const { data: component, isLoading, mutate } = useComponent(componentId);

  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const [formData, setFormData] = React.useState({
    name: "",
    category: "tool",
    code: "",
    language: "python",
    description: "",
    usage_example: "",
    version: "1.0.0",
    tags: "",
  });

  React.useEffect(() => {
    if (component) {
      setFormData({
        name: component.name,
        category: component.category,
        code: component.code,
        language: component.language,
        description: component.description,
        usage_example: component.usage_example,
        version: component.version,
        tags: component.tags.join(", "),
      });
    }
  }, [component]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error("Name is required");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`http://localhost:8080/api/v1/components/${componentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          category: formData.category,
          code: formData.code,
          language: formData.language,
          description: formData.description.trim(),
          usage_example: formData.usage_example,
          version: formData.version,
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
        }),
      });

      if (response.ok) {
        toast.success("Component updated successfully");
        mutate();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to update component");
      }
    } catch (error) {
      toast.error("Failed to update component");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/v1/components/${componentId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Component deleted");
        router.push("/library");
      } else {
        toast.error("Failed to delete component");
      }
    } catch (error) {
      toast.error("Failed to delete component");
    }
  };

  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(formData.code);
    toast.success("Code copied to clipboard");
  };

  if (isLoading) {
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

  if (!component) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6 text-center">
            <Puzzle className="size-12 mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground">Component not found</p>
            <Button asChild className="mt-4">
              <Link href="/library">Back to Library</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/library">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 text-white">
              <Puzzle className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold tracking-tight">{component.name}</h1>
                <Badge variant="secondary" className={categoryColors[component.category]}>
                  {component.category}
                </Badge>
              </div>
              <p className="text-muted-foreground">
                v{component.version} • {component.language}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleCopyCode}>
            <Copy className="size-4 mr-2" />
            Copy Code
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" size="sm">
                <Trash2 className="size-4 mr-2" />
                Delete
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Component?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete &quot;{component.name}&quot;.
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Metadata Banner */}
      <Card className="border-l-4 border-l-orange-500 bg-orange-500/5">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <Clock className="size-4 text-muted-foreground" />
                <span className="text-muted-foreground">Created:</span>
                <span>{new Date(component.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="size-4 text-muted-foreground" />
                <span className="text-muted-foreground">Updated:</span>
                <span>{new Date(component.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
            {component.tags.length > 0 && (
              <div className="flex gap-1">
                {component.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="edit">
        <TabsList>
          <TabsTrigger value="edit">Edit</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
        </TabsList>

        {/* Edit Tab */}
        <TabsContent value="edit">
          <form onSubmit={handleSubmit}>
            <div className="grid gap-6">
              {/* Basic Info Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Component Details</CardTitle>
                  <CardDescription>
                    Edit your component&apos;s metadata
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Name */}
                  <div className="space-y-2">
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>

                  {/* Category & Language Row */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="category">Category</Label>
                      <Select
                        value={formData.category}
                        onValueChange={(v) => setFormData({ ...formData, category: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {COMPONENT_CATEGORIES.map((cat) => (
                            <SelectItem key={cat.value} value={cat.value}>
                              {cat.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="language">Language</Label>
                      <Select
                        value={formData.language}
                        onValueChange={(v) => setFormData({ ...formData, language: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {LANGUAGES.map((lang) => (
                            <SelectItem key={lang.value} value={lang.value}>
                              {lang.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Description */}
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      rows={3}
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                  </div>

                  {/* Version & Tags Row */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="version">Version</Label>
                      <Input
                        id="version"
                        value={formData.version}
                        onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="tags">Tags</Label>
                      <Input
                        id="tags"
                        placeholder="Comma separated"
                        value={formData.tags}
                        onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Code Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="size-5" />
                    Source Code
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CodeEditor
                    value={formData.code}
                    onChange={(value) => setFormData({ ...formData, code: value })}
                    language={formData.language || "python"}
                    height={360}
                  />
                </CardContent>
              </Card>

              {/* Usage Example Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="size-5" />
                    Usage Example
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CodeEditor
                    value={formData.usage_example}
                    onChange={(value) => setFormData({ ...formData, usage_example: value })}
                    language={formData.language || "python"}
                    height={220}
                  />
                </CardContent>
              </Card>

              {/* Save Button */}
              <div className="flex justify-end">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="size-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </div>
          </form>
        </TabsContent>

        {/* Preview Tab */}
        <TabsContent value="preview">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="size-5" />
                    Code Preview
                  </CardTitle>
                  <CardDescription>
                    {component.language} • {component.code.split('\n').length} lines
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={handleCopyCode}>
                  <Copy className="size-4 mr-2" />
                  Copy
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/50 rounded-lg p-4 overflow-auto max-h-[600px]">
                <pre className="text-sm font-mono whitespace-pre-wrap">
                  {component.code || "No code provided"}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usage Tab */}
        <TabsContent value="usage">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="size-5" />
                Usage Example
              </CardTitle>
              <CardDescription>
                How to use this component in your projects
              </CardDescription>
            </CardHeader>
            <CardContent>
              {component.usage_example ? (
                <div className="bg-muted/50 rounded-lg p-4 overflow-auto max-h-[400px]">
                  <pre className="text-sm font-mono whitespace-pre-wrap">
                    {component.usage_example}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <BookOpen className="size-12 mx-auto mb-4 opacity-50" />
                  <p>No usage example provided</p>
                  <p className="text-sm mt-1">Add one in the Edit tab to help others use this component</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Description Card */}
          {component.description && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{component.description}</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      <TestingSection
        resourceType="component"
        resourceId={component.id}
        resourceName={component.name}
        defaultLanguage={component.language || "python"}
        defaultCode={component.code}
      />
    </div>
  );
}
