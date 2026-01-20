"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Loader2, Check, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

import { WizardProvider, useWizard, WIZARD_STEPS } from "./wizard-context";
import { StartMethodStep } from "./steps/start-method";
import { BasicInfoStep } from "./steps/basic-info";
import { VcsSetupStep } from "./steps/vcs-setup";
import { ConfigurationStep } from "./steps/configuration";
import { ReviewStep } from "./steps/review";

const API_BASE = "http://localhost:8080/api/v1";

// === Step Indicator ===

function StepIndicator() {
  const { currentStep, totalSteps, goToStep, canProceed } = useWizard();

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {WIZARD_STEPS.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep;
          const isClickable = index < currentStep; // Only allow going back

          return (
            <React.Fragment key={step.id}>
              <button
                onClick={() => isClickable && goToStep(index)}
                disabled={!isClickable}
                className={cn(
                  "flex items-center gap-2 transition-colors",
                  isClickable && "cursor-pointer hover:text-primary",
                  !isClickable && "cursor-default"
                )}
              >
                <div
                  className={cn(
                    "size-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                    isCompleted && "bg-primary text-primary-foreground",
                    isCurrent && "bg-primary/20 text-primary border-2 border-primary",
                    !isCompleted && !isCurrent && "bg-muted text-muted-foreground"
                  )}
                >
                  {isCompleted ? <Check className="size-4" /> : index + 1}
                </div>
                <div className="hidden md:block">
                  <p className={cn(
                    "text-sm font-medium",
                    isCurrent && "text-primary",
                    !isCurrent && "text-muted-foreground"
                  )}>
                    {step.title}
                  </p>
                </div>
              </button>
              {index < totalSteps - 1 && (
                <div className={cn(
                  "flex-1 h-0.5 mx-4",
                  index < currentStep ? "bg-primary" : "bg-muted"
                )} />
              )}
            </React.Fragment>
          );
        })}
      </div>
      <Progress value={(currentStep / (totalSteps - 1)) * 100} className="h-1" />
    </div>
  );
}

// === Wizard Content ===

function WizardContent() {
  const router = useRouter();
  const {
    currentStep,
    totalSteps,
    formData,
    isSubmitting,
    nextStep,
    prevStep,
    canProceed,
    setSubmitting,
    reset,
  } = useWizard();

  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      // Generate config YAML
      const configYaml = `# Project Configuration
llm_model: ${formData.llmModel}
embedding_model: ${formData.embeddingModel}

vectordb:
  backend: ${formData.vectorDbBackend}
  path: ${formData.vectorDbPath}
`;

      let projectId: string | null = null;

      if (formData.startMethod === "example" && formData.exampleSlug) {
        // Import from example
        const response = await fetch(`${API_BASE}/examples/import`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            example_slug: formData.exampleSlug,
            project_name: formData.name,
            description: formData.description || null,
            tags: formData.tags.length > 0 ? formData.tags : null,
            copy_files: true,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Failed to import example");
        }

        const result = await response.json();
        projectId = result.project_id;
      } else {
        // Create new project
        const response = await fetch(`${API_BASE}/projects`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: formData.name,
            description: formData.description,
            config_yaml: configYaml,
            status: "draft",
            tags: formData.tags,
            metadata: {
              creation_method: formData.startMethod,
            },
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Failed to create project");
        }

        const project = await response.json();
        projectId = project.id;

        // Handle Git operations
        if (formData.startMethod === "clone" && formData.cloneUrl) {
          // Clone repository
          const cloneResponse = await fetch(`${API_BASE}/projects/${projectId}/git/clone`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              url: formData.cloneUrl,
              branch: formData.gitBranch || null,
            }),
          });

          if (!cloneResponse.ok) {
            console.warn("Failed to clone repository");
          }
        } else if (formData.initGit) {
          // Initialize git repository
          const initResponse = await fetch(`${API_BASE}/projects/${projectId}/git/init`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              initial_branch: formData.gitBranch,
            }),
          });

          if (!initResponse.ok) {
            console.warn("Failed to initialize git repository");
          }

          // Set up remote if provided
          if (formData.gitRemoteUrl) {
            await fetch(`${API_BASE}/projects/${projectId}/git`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                remote_url: formData.gitRemoteUrl,
                branch: formData.gitBranch,
                auto_sync: formData.gitAutoSync,
              }),
            });
          }
        }
      }

      toast.success("Project created successfully!");
      router.push(`/projects/${projectId}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <StartMethodStep />;
      case 1:
        return <BasicInfoStep />;
      case 2:
        return <VcsSetupStep />;
      case 3:
        return <ConfigurationStep />;
      case 4:
        return <ReviewStep />;
      default:
        return null;
    }
  };

  const isLastStep = currentStep === totalSteps - 1;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/projects">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Create New Project</h1>
          <p className="text-muted-foreground">
            {WIZARD_STEPS[currentStep].description}
          </p>
        </div>
      </div>

      {/* Progress */}
      <StepIndicator />

      {/* Step Content */}
      <div className="mb-8">{renderStep()}</div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-6 border-t">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          <ArrowLeft className="size-4 mr-2" />
          Back
        </Button>

        <div className="flex items-center gap-2">
          <Button variant="ghost" asChild>
            <Link href="/projects">Cancel</Link>
          </Button>

          {isLastStep ? (
            <Button
              onClick={handleSubmit}
              disabled={!canProceed() || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Check className="size-4 mr-2" />
                  Create Project
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={nextStep}
              disabled={!canProceed()}
            >
              Next
              <ArrowRight className="size-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// === Main Export ===

export function ProjectWizard() {
  return (
    <WizardProvider>
      <WizardContent />
    </WizardProvider>
  );
}
