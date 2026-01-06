"use client";

import * as React from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Loader2, FileUp, Code, Eye } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

function LoadingFallback() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Skeleton className="h-10 w-64" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Skeleton className="h-[400px]" />
        <Skeleton className="h-[400px] lg:col-span-2" />
      </div>
    </div>
  );
}

const defaultFlowYAML = `# Flow Definition
name: My Flow
description: A multi-agent workflow
type: crew

# Define agents (or reference existing ones by id)
agents:
  - name: Researcher
    role: Research Analyst
    goal: Find and analyze information
    backstory: Expert researcher with attention to detail

  - name: Writer
    role: Content Writer
    goal: Create clear and engaging content
    backstory: Skilled technical writer

# Define tasks
tasks:
  - name: Research Task
    description: Research the given topic thoroughly
    agent: Researcher
    expected_output: A comprehensive research report

  - name: Writing Task
    description: Write a summary based on research
    agent: Writer
    expected_output: A well-written summary document

# Flow settings
process: sequential
verbose: true
`;

function NewFlowForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project_id');
  const isImport = searchParams.get('import') === 'true';
  
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState("yaml");
  
  const [formData, setFormData] = React.useState({
    name: "",
    description: "",
    flow_type: "crew",
    status: "draft",
    flow_yaml: defaultFlowYAML,
    tags: "",
    project_id: projectId || "",
  });

  // Load imported YAML on mount
  React.useEffect(() => {
    if (isImport && typeof window !== 'undefined') {
      const importedYAML = localStorage.getItem('importedFlowYAML');
      if (importedYAML) {
        setFormData(prev => ({ ...prev, flow_yaml: importedYAML }));
        localStorage.removeItem('importedFlowYAML');
        toast.success("YAML imported successfully");
      }
    }
  }, [isImport]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error("Flow name is required");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch("http://localhost:8080/api/v1/flows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          description: formData.description.trim(),
          flow_type: formData.flow_type,
          status: formData.status,
          flow_yaml: formData.flow_yaml,
          project_id: formData.project_id || null,
          agents: [],
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          metadata: {},
        }),
      });
      
      if (response.ok) {
        const flow = await response.json();
        toast.success("Flow created successfully");
        router.push(`/flows/${flow.id}`);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create flow");
      }
    } catch (error) {
      toast.error("Failed to create flow");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImportFile = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.yaml,.yml';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const text = await file.text();
      setFormData(prev => ({ ...prev, flow_yaml: text }));
      toast.success("YAML file loaded");
    };
    input.click();
  };

  const handleExport = () => {
    const blob = new Blob([formData.flow_yaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${formData.name || 'flow'}.yaml`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/flows">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Flow</h1>
          <p className="text-muted-foreground">
            Create a multi-agent workflow
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Basic Info */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Flow Details</CardTitle>
              <CardDescription>
                Basic flow information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name">Flow Name *</Label>
                <Input
                  id="name"
                  placeholder="Research Pipeline"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your flow..."
                  rows={3}
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>

              {/* Type */}
              <div className="space-y-2">
                <Label htmlFor="flow_type">Flow Type</Label>
                <Select
                  value={formData.flow_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, flow_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="crew">CrewAI Crew</SelectItem>
                    <SelectItem value="pipeline">Pipeline</SelectItem>
                    <SelectItem value="workflow">Workflow</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Status */}
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) =>
                    setFormData({ ...formData, status: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="paused">Paused</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Tags */}
              <div className="space-y-2">
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
                  placeholder="research, automation (comma separated)"
                  value={formData.tags}
                  onChange={(e) =>
                    setFormData({ ...formData, tags: e.target.value })
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Right: YAML Editor */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Flow Definition</CardTitle>
                  <CardDescription>
                    Define your flow in YAML
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button type="button" variant="outline" size="sm" onClick={handleImportFile}>
                    <FileUp className="size-4 mr-2" />
                    Import
                  </Button>
                  <Button type="button" variant="outline" size="sm" onClick={handleExport}>
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                  <TabsTrigger value="yaml">
                    <Code className="size-4 mr-2" />
                    YAML Editor
                  </TabsTrigger>
                  <TabsTrigger value="preview">
                    <Eye className="size-4 mr-2" />
                    Preview
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="yaml" className="mt-4">
                  <Textarea
                    className="font-mono text-sm min-h-[400px]"
                    value={formData.flow_yaml}
                    onChange={(e) =>
                      setFormData({ ...formData, flow_yaml: e.target.value })
                    }
                  />
                </TabsContent>
                
                <TabsContent value="preview" className="mt-4">
                  <div className="bg-muted rounded-lg p-4 min-h-[400px]">
                    <pre className="text-sm whitespace-pre-wrap font-mono">
                      {formData.flow_yaml}
                    </pre>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/flows">Cancel</Link>
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
                Create Flow
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

export default function NewFlowPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <NewFlowForm />
    </Suspense>
  );
}

