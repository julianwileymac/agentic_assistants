"use client";

import * as React from "react";
import { X } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useWizard } from "../wizard-context";

export function BasicInfoStep() {
  const { formData, updateFormData, errors, setError, clearError } = useWizard();
  const [tagInput, setTagInput] = React.useState("");

  const handleNameChange = (name: string) => {
    updateFormData({ name });
    if (name.trim()) {
      clearError("name");
    } else {
      setError("name", "Project name is required");
    }
  };

  const handleDescriptionChange = (description: string) => {
    updateFormData({ description });
  };

  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !formData.tags.includes(tag)) {
      updateFormData({ tags: [...formData.tags, tag] });
    }
    setTagInput("");
  };

  const handleRemoveTag = (tagToRemove: string) => {
    updateFormData({ tags: formData.tags.filter((t) => t !== tagToRemove) });
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Project Information</h2>
        <p className="text-muted-foreground mt-1">
          Enter the basic details for your project
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Basic Details</CardTitle>
          <CardDescription>
            Give your project a name and description
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="project-name">
              Project Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="project-name"
              value={formData.name}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder="My Agentic Project"
              className={errors.name ? "border-destructive" : ""}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="project-description">Description</Label>
            <Textarea
              id="project-description"
              value={formData.description}
              onChange={(e) => handleDescriptionChange(e.target.value)}
              placeholder="A brief description of what this project does..."
              rows={4}
            />
            <p className="text-xs text-muted-foreground">
              Optional but recommended for documentation purposes
            </p>
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label htmlFor="project-tags">Tags</Label>
            <div className="flex items-center gap-2">
              <Input
                id="project-tags"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagKeyDown}
                placeholder="Add a tag..."
                className="flex-1"
              />
              <Button
                type="button"
                variant="secondary"
                onClick={handleAddTag}
                disabled={!tagInput.trim()}
              >
                Add
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Press Enter or click Add to add tags
            </p>
            
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {formData.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="gap-1 pr-1"
                  >
                    {tag}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-4 p-0 hover:bg-transparent"
                      onClick={() => handleRemoveTag(tag)}
                    >
                      <X className="size-3" />
                    </Button>
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
