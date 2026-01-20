"use client";

import * as React from "react";
import { GitBranch, Globe, Key } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useWizard } from "../wizard-context";

export function VcsSetupStep() {
  const { formData, updateFormData, errors, setError, clearError } = useWizard();

  const handleInitGitChange = (checked: boolean) => {
    updateFormData({ initGit: checked });
  };

  const handleRemoteUrlChange = (url: string) => {
    updateFormData({ gitRemoteUrl: url });
    if (url) {
      // Basic validation
      try {
        new URL(url);
        clearError("gitRemoteUrl");
      } catch {
        if (url.includes("@") && url.includes(":")) {
          // SSH URL format
          clearError("gitRemoteUrl");
        } else {
          setError("gitRemoteUrl", "Invalid URL format");
        }
      }
    } else {
      clearError("gitRemoteUrl");
    }
  };

  const handleBranchChange = (branch: string) => {
    updateFormData({ gitBranch: branch });
  };

  const handleAutoSyncChange = (checked: boolean) => {
    updateFormData({ gitAutoSync: checked });
  };

  // If cloning, show simplified view
  if (formData.startMethod === "clone") {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Version Control</h2>
          <p className="text-muted-foreground mt-1">
            Configure Git settings for your cloned repository
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <GitBranch className="size-5" />
              Repository Settings
            </CardTitle>
            <CardDescription>
              The repository will be cloned from: {formData.cloneUrl}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Branch */}
            <div className="space-y-2">
              <Label htmlFor="git-branch">Default Branch</Label>
              <Input
                id="git-branch"
                value={formData.gitBranch}
                onChange={(e) => handleBranchChange(e.target.value)}
                placeholder="main"
              />
            </div>

            {/* Auto Sync */}
            <div className="flex items-center justify-between p-4 rounded-lg border">
              <div className="space-y-0.5">
                <Label htmlFor="auto-sync">Auto Sync</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically sync changes with remote
                </p>
              </div>
              <Switch
                id="auto-sync"
                checked={formData.gitAutoSync}
                onCheckedChange={handleAutoSyncChange}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Version Control</h2>
        <p className="text-muted-foreground mt-1">
          Set up Git version control for your project
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <GitBranch className="size-5" />
            Git Repository
          </CardTitle>
          <CardDescription>
            Initialize a Git repository for version control
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Initialize Git */}
          <div className="flex items-center justify-between p-4 rounded-lg border">
            <div className="space-y-0.5">
              <Label htmlFor="init-git">Initialize Git Repository</Label>
              <p className="text-sm text-muted-foreground">
                Create a new Git repository in the project directory
              </p>
            </div>
            <Switch
              id="init-git"
              checked={formData.initGit}
              onCheckedChange={handleInitGitChange}
            />
          </div>

          {formData.initGit && (
            <>
              {/* Remote URL */}
              <div className="space-y-2">
                <Label htmlFor="remote-url">
                  Remote Repository URL
                  <span className="text-muted-foreground ml-1">(optional)</span>
                </Label>
                <Input
                  id="remote-url"
                  value={formData.gitRemoteUrl || ""}
                  onChange={(e) => handleRemoteUrlChange(e.target.value)}
                  placeholder="https://github.com/user/repo.git"
                  className={errors.gitRemoteUrl ? "border-destructive" : ""}
                />
                {errors.gitRemoteUrl && (
                  <p className="text-sm text-destructive">{errors.gitRemoteUrl}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Connect to a remote repository (GitHub, GitLab, etc.)
                </p>
              </div>

              {/* Branch */}
              <div className="space-y-2">
                <Label htmlFor="git-branch">Default Branch</Label>
                <Input
                  id="git-branch"
                  value={formData.gitBranch}
                  onChange={(e) => handleBranchChange(e.target.value)}
                  placeholder="main"
                />
              </div>

              {/* Auto Sync */}
              {formData.gitRemoteUrl && (
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="space-y-0.5">
                    <Label htmlFor="auto-sync">Auto Sync</Label>
                    <p className="text-sm text-muted-foreground">
                      Automatically sync changes with remote
                    </p>
                  </div>
                  <Switch
                    id="auto-sync"
                    checked={formData.gitAutoSync}
                    onCheckedChange={handleAutoSyncChange}
                  />
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {!formData.initGit && (
        <Card className="border-dashed">
          <CardContent className="py-8">
            <div className="text-center text-muted-foreground">
              <GitBranch className="size-10 mx-auto mb-3 opacity-50" />
              <p>Git will not be initialized for this project</p>
              <p className="text-sm mt-1">You can set it up later from the project settings</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
