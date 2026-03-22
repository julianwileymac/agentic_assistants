"use client";

import * as React from "react";
import { Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Loader2, Code, Puzzle } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { CodeEditor } from "@/components/code-editor";
import { TestingSection } from "@/components/testing/testing-section";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

const COMPONENT_CATEGORIES = [
  { value: "tool", label: "Tool", description: "Reusable agent tools", group: "Core" },
  { value: "agent", label: "Agent", description: "Agent templates", group: "Core" },
  { value: "task", label: "Task", description: "Task definitions", group: "Core" },
  { value: "pattern", label: "Pattern", description: "Agentic patterns (RAG, ReAct, etc.)", group: "Core" },
  { value: "utility", label: "Utility", description: "Utility functions", group: "Core" },
  { value: "template", label: "Template", description: "Project templates", group: "Core" },
  { value: "snippet", label: "Snippet", description: "Reusable code snippets", group: "Core" },
  { value: "datasource_handler", label: "Data Source Handler", description: "Custom data source handlers", group: "Data" },
  { value: "embedding_model", label: "Embedding Model", description: "Embedding configurations", group: "AI" },
  { value: "prompt_template", label: "Prompt Template", description: "Reusable prompts", group: "AI" },
  { value: "workflow_node", label: "Workflow Node", description: "Workflow nodes", group: "Workflow" },
  { value: "retrieval_strategy", label: "Retrieval Strategy", description: "RAG retrieval strategies", group: "Data" },
  { value: "llm_wrapper", label: "LLM Wrapper", description: "LLM integrations", group: "AI" },
  { value: "crew_config", label: "Crew Configuration", description: "CrewAI configurations", group: "Workflow" },
];

const LANGUAGES = [
  { value: "python", label: "Python" },
  { value: "typescript", label: "TypeScript" },
  { value: "javascript", label: "JavaScript" },
  { value: "yaml", label: "YAML" },
  { value: "json", label: "JSON" },
  { value: "markdown", label: "Markdown" },
];

function NewComponentForm() {
  const router = useRouter();
  
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error("Component name is required");
      return;
    }
    
    if (!formData.category) {
      toast.error("Category is required");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch("http://localhost:8080/api/v1/components", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          category: formData.category,
          code: formData.code,
          language: formData.language,
          description: formData.description.trim(),
          usage_example: formData.usage_example,
          version: formData.version || "1.0.0",
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          metadata: {},
        }),
      });
      
      if (response.ok) {
        const component = await response.json();
        toast.success("Component created successfully");
        router.push(`/library/${component.id}`);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create component");
      }
    } catch (error) {
      toast.error("Failed to create component");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
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
            <h1 className="text-3xl font-bold tracking-tight">New Component</h1>
            <p className="text-muted-foreground">
              Create a reusable code component
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          {/* Basic Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>Component Details</CardTitle>
              <CardDescription>
                Define your component&apos;s metadata and categorization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name">Component Name *</Label>
                <Input
                  id="name"
                  placeholder="MyCustomTool"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                />
              </div>

              {/* Category & Language Row */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">Category *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) =>
                      setFormData({ ...formData, category: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {COMPONENT_CATEGORIES.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>
                          <div className="flex flex-col">
                            <span>{cat.label}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={formData.language}
                    onValueChange={(value) =>
                      setFormData({ ...formData, language: value })
                    }
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
                  placeholder="A brief description of what this component does..."
                  rows={2}
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>

              {/* Version & Tags Row */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="version">Version</Label>
                  <Input
                    id="version"
                    placeholder="1.0.0"
                    value={formData.version}
                    onChange={(e) =>
                      setFormData({ ...formData, version: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tags">Tags</Label>
                  <Input
                    id="tags"
                    placeholder="rag, llm, crewai (comma separated)"
                    value={formData.tags}
                    onChange={(e) =>
                      setFormData({ ...formData, tags: e.target.value })
                    }
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
              <CardDescription>
                The main implementation code for this component
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CodeEditor
                value={formData.code}
                onChange={(value) => setFormData({ ...formData, code: value })}
                language={formData.language || "python"}
                height={320}
              />
            </CardContent>
          </Card>

          {/* Usage Example Card */}
          <Card>
            <CardHeader>
              <CardTitle>Usage Example</CardTitle>
              <CardDescription>
                Show how to use this component (optional but recommended)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CodeEditor
                value={formData.usage_example}
                onChange={(value) =>
                  setFormData({ ...formData, usage_example: value })
                }
                language={formData.language || "python"}
                height={200}
              />
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/library">Cancel</Link>
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="size-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="size-4 mr-2" />
                Create Component
              </>
            )}
          </Button>
        </div>
      </form>

      <TestingSection
        resourceType="component"
        resourceName={formData.name || "New Component"}
        defaultLanguage={formData.language || "python"}
        defaultCode={formData.code}
      />
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-[400px] w-full" />
      <Skeleton className="h-[300px] w-full" />
    </div>
  );
}

export default function NewComponentPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <NewComponentForm />
    </Suspense>
  );
}
