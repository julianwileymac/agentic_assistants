"use client";

import * as React from "react";
import { 
  FolderKanban, 
  GitBranch, 
  Brain, 
  Database, 
  Tag, 
  CheckCircle2,
  Download,
  Globe,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useWizard } from "../wizard-context";

export function ReviewStep() {
  const { formData } = useWizard();

  const startMethodLabels = {
    scratch: "Create from Scratch",
    example: "Import from Example",
    clone: "Clone from Repository",
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Review & Create</h2>
        <p className="text-muted-foreground mt-1">
          Review your project settings before creating
        </p>
      </div>

      {/* Project Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <FolderKanban className="size-5" />
            Project Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium">{formData.name || "Unnamed Project"}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Creation Method</p>
              <div className="flex items-center gap-2">
                {formData.startMethod === "example" && <Download className="size-4" />}
                {formData.startMethod === "clone" && <Globe className="size-4" />}
                <span className="font-medium">{startMethodLabels[formData.startMethod]}</span>
              </div>
            </div>
          </div>

          {formData.description && (
            <div>
              <p className="text-sm text-muted-foreground">Description</p>
              <p className="text-sm">{formData.description}</p>
            </div>
          )}

          {formData.tags.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Tags</p>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    <Tag className="size-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {formData.startMethod === "example" && formData.exampleSlug && (
            <div>
              <p className="text-sm text-muted-foreground">Example Template</p>
              <p className="font-medium">{formData.exampleSlug}</p>
            </div>
          )}

          {formData.startMethod === "clone" && formData.cloneUrl && (
            <div>
              <p className="text-sm text-muted-foreground">Clone URL</p>
              <p className="font-mono text-sm break-all">{formData.cloneUrl}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Version Control */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <GitBranch className="size-5" />
            Version Control
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            {formData.initGit || formData.startMethod === "clone" ? (
              <>
                <CheckCircle2 className="size-4 text-green-500" />
                <span>Git repository will be {formData.startMethod === "clone" ? "cloned" : "initialized"}</span>
              </>
            ) : (
              <span className="text-muted-foreground">Git will not be initialized</span>
            )}
          </div>

          {(formData.initGit || formData.startMethod === "clone") && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Branch</p>
                <p className="font-medium">{formData.gitBranch}</p>
              </div>
              {formData.gitRemoteUrl && (
                <div>
                  <p className="text-sm text-muted-foreground">Remote URL</p>
                  <p className="font-mono text-sm truncate">{formData.gitRemoteUrl}</p>
                </div>
              )}
              {formData.gitAutoSync && (
                <div className="col-span-2">
                  <Badge variant="secondary">Auto Sync Enabled</Badge>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Brain className="size-5" />
            Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">LLM Model</p>
              <p className="font-medium">{formData.llmModel}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Embedding Model</p>
              <p className="font-medium">{formData.embeddingModel}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Vector Database</p>
              <p className="font-medium">{formData.vectorDbBackend}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Storage Path</p>
              <p className="font-mono text-sm">{formData.vectorDbPath}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ready Message */}
      <Card className="border-green-500/50 bg-green-500/5">
        <CardContent className="py-6">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="size-6 text-green-500" />
            <div>
              <p className="font-medium">Ready to create!</p>
              <p className="text-sm text-muted-foreground">
                Click &quot;Create Project&quot; to finish setup
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
