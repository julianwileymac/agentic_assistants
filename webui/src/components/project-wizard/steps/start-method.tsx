"use client";

import * as React from "react";
import { FolderPlus, Download, GitBranch, ChevronRight, FileText, Tag, Loader2 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useWizard, StartMethod } from "../wizard-context";

const API_BASE = "http://localhost:8080/api/v1";

interface ExampleEntry {
  slug: string;
  name: string;
  description: string;
  tags: string[];
  has_config: boolean;
}

function useExamples() {
  const [data, setData] = React.useState<ExampleEntry[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    fetch(`${API_BASE}/examples`)
      .then((res) => res.json())
      .then((res) => {
        setData(res.items || []);
        setIsLoading(false);
      })
      .catch(() => {
        setData([]);
        setIsLoading(false);
      });
  }, []);

  return { data, isLoading };
}

interface MethodCardProps {
  method: StartMethod;
  icon: React.ReactNode;
  title: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}

function MethodCard({ method, icon, title, description, selected, onSelect }: MethodCardProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "w-full text-left p-6 rounded-lg border-2 transition-all",
        selected
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50 hover:bg-muted/50"
      )}
    >
      <div className="flex items-start gap-4">
        <div className={cn(
          "p-3 rounded-lg",
          selected ? "bg-primary text-primary-foreground" : "bg-muted"
        )}>
          {icon}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
        <ChevronRight className={cn(
          "size-5 text-muted-foreground transition-transform",
          selected && "text-primary"
        )} />
      </div>
    </button>
  );
}

export function StartMethodStep() {
  const { formData, updateFormData, clearError } = useWizard();
  const { data: examples, isLoading: isLoadingExamples } = useExamples();

  const handleMethodSelect = (method: StartMethod) => {
    updateFormData({ 
      startMethod: method,
      exampleSlug: undefined,
      cloneUrl: undefined,
    });
    clearError("startMethod");
  };

  const handleExampleSelect = (slug: string) => {
    updateFormData({ exampleSlug: slug });
    clearError("exampleSlug");
  };

  const handleCloneUrlChange = (url: string) => {
    updateFormData({ cloneUrl: url });
    clearError("cloneUrl");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">How would you like to start?</h2>
        <p className="text-muted-foreground mt-1">
          Choose a method to create your new project
        </p>
      </div>

      <div className="space-y-4">
        <MethodCard
          method="scratch"
          icon={<FolderPlus className="size-6" />}
          title="Start from Scratch"
          description="Create a new empty project with default configuration"
          selected={formData.startMethod === "scratch"}
          onSelect={() => handleMethodSelect("scratch")}
        />

        <MethodCard
          method="example"
          icon={<Download className="size-6" />}
          title="Import from Example"
          description="Use a pre-configured example as a starting point"
          selected={formData.startMethod === "example"}
          onSelect={() => handleMethodSelect("example")}
        />

        <MethodCard
          method="clone"
          icon={<GitBranch className="size-6" />}
          title="Clone from Repository"
          description="Clone an existing Git repository"
          selected={formData.startMethod === "clone"}
          onSelect={() => handleMethodSelect("clone")}
        />
      </div>

      {/* Example Selection */}
      {formData.startMethod === "example" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Select an Example</CardTitle>
            <CardDescription>
              Choose an example template to import
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingExamples ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : examples.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No examples available
              </p>
            ) : (
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {examples.map((example) => (
                    <button
                      key={example.slug}
                      onClick={() => handleExampleSelect(example.slug)}
                      className={cn(
                        "w-full text-left p-4 rounded-lg border transition-colors",
                        formData.exampleSlug === example.slug
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{example.name}</span>
                        {example.has_config && (
                          <Badge variant="secondary" className="text-xs">
                            <FileText className="size-3 mr-1" />
                            config.yaml
                          </Badge>
                        )}
                      </div>
                      {example.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {example.description}
                        </p>
                      )}
                      {example.tags.length > 0 && (
                        <div className="flex items-center gap-1 mt-2">
                          <Tag className="size-3 text-muted-foreground" />
                          {example.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      )}

      {/* Clone URL Input */}
      {formData.startMethod === "clone" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Repository URL</CardTitle>
            <CardDescription>
              Enter the URL of the Git repository to clone
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="clone-url">Repository URL</Label>
              <Input
                id="clone-url"
                value={formData.cloneUrl || ""}
                onChange={(e) => handleCloneUrlChange(e.target.value)}
                placeholder="https://github.com/user/repo.git"
              />
              <p className="text-xs text-muted-foreground">
                HTTPS or SSH URL (e.g., git@github.com:user/repo.git)
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
