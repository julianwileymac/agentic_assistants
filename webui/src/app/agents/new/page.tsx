"use client";

import * as React from "react";
import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Loader2 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

function NewAgentForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project_id');
  
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  
  const [formData, setFormData] = React.useState({
    name: "",
    role: "",
    goal: "",
    backstory: "",
    model: "llama3.2",
    status: "drafted",
    tools: "",
    tags: "",
    project_id: projectId || "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.role.trim()) {
      toast.error("Agent name and role are required");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch("http://localhost:8080/api/v1/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          role: formData.role.trim(),
          goal: formData.goal.trim(),
          backstory: formData.backstory.trim(),
          model: formData.model,
          status: formData.status,
          project_id: formData.project_id || null,
          tools: formData.tools
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          tags: formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          metadata: {},
        }),
      });
      
      if (response.ok) {
        const agent = await response.json();
        toast.success("Agent created successfully");
        router.push(`/agents/${agent.id}`);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create agent");
      }
    } catch (error) {
      toast.error("Failed to create agent");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/agents">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Agent</h1>
          <p className="text-muted-foreground">
            Create a new AI agent
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Agent Details</CardTitle>
            <CardDescription>
              Define your agent&apos;s role and capabilities
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Agent Name *</Label>
              <Input
                id="name"
                placeholder="Research Assistant"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>

            {/* Role */}
            <div className="space-y-2">
              <Label htmlFor="role">Role *</Label>
              <Input
                id="role"
                placeholder="Senior Research Analyst"
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value })
                }
                required
              />
            </div>

            {/* Goal */}
            <div className="space-y-2">
              <Label htmlFor="goal">Goal</Label>
              <Textarea
                id="goal"
                placeholder="Analyze and synthesize information to provide comprehensive insights..."
                rows={2}
                value={formData.goal}
                onChange={(e) =>
                  setFormData({ ...formData, goal: e.target.value })
                }
              />
            </div>

            {/* Backstory */}
            <div className="space-y-2">
              <Label htmlFor="backstory">Backstory</Label>
              <Textarea
                id="backstory"
                placeholder="You are an expert researcher with 10 years of experience..."
                rows={3}
                value={formData.backstory}
                onChange={(e) =>
                  setFormData({ ...formData, backstory: e.target.value })
                }
              />
            </div>

            {/* Model */}
            <div className="space-y-2">
              <Label htmlFor="model">LLM Model</Label>
              <Select
                value={formData.model}
                onValueChange={(value) =>
                  setFormData({ ...formData, model: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llama3.2">Llama 3.2</SelectItem>
                  <SelectItem value="llama3.1">Llama 3.1</SelectItem>
                  <SelectItem value="mistral">Mistral</SelectItem>
                  <SelectItem value="codellama">Code Llama</SelectItem>
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
                  <SelectItem value="drafted">Draft</SelectItem>
                  <SelectItem value="created">Created</SelectItem>
                  <SelectItem value="in_development">In Development</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Tools */}
            <div className="space-y-2">
              <Label htmlFor="tools">Tools</Label>
              <Input
                id="tools"
                placeholder="web_search, code_interpreter (comma separated)"
                value={formData.tools}
                onChange={(e) =>
                  setFormData({ ...formData, tools: e.target.value })
                }
              />
            </div>

            {/* Tags */}
            <div className="space-y-2">
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                placeholder="research, nlp (comma separated)"
                value={formData.tags}
                onChange={(e) =>
                  setFormData({ ...formData, tags: e.target.value })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/agents">Cancel</Link>
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
                Create Agent
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-[600px] w-full" />
    </div>
  );
}

export default function NewAgentPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <NewAgentForm />
    </Suspense>
  );
}

