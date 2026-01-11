# Chunk: 0b9dfd0e7fd9_0

- source: `webui/src/app/agents/new/page.tsx`
- lines: 1-99
- chunk: 1/4

```
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
```
