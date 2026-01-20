"use client";

import * as React from "react";

// === Types ===

export type StartMethod = "scratch" | "example" | "clone";

export interface WizardFormData {
  // Step 1: Start method
  startMethod: StartMethod;
  exampleSlug?: string;
  cloneUrl?: string;

  // Step 2: Basic Info
  name: string;
  description: string;
  tags: string[];

  // Step 3: VCS Setup
  initGit: boolean;
  gitRemoteUrl?: string;
  gitBranch: string;
  gitAutoSync: boolean;

  // Step 4: Configuration
  llmModel: string;
  embeddingModel: string;
  vectorDbBackend: string;
  vectorDbPath: string;

  // Step 5: Data Sources (optional)
  linkedDataSources: string[];
}

export interface WizardState {
  currentStep: number;
  totalSteps: number;
  formData: WizardFormData;
  isSubmitting: boolean;
  errors: Record<string, string>;
}

export interface WizardContextValue extends WizardState {
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  updateFormData: (data: Partial<WizardFormData>) => void;
  setError: (field: string, message: string) => void;
  clearError: (field: string) => void;
  clearAllErrors: () => void;
  setSubmitting: (isSubmitting: boolean) => void;
  reset: () => void;
  canProceed: () => boolean;
}

// === Default Values ===

const defaultFormData: WizardFormData = {
  startMethod: "scratch",
  name: "",
  description: "",
  tags: [],
  initGit: true,
  gitBranch: "main",
  gitAutoSync: false,
  llmModel: "llama3.2",
  embeddingModel: "nomic-embed-text",
  vectorDbBackend: "chroma",
  vectorDbPath: "./data/vectors",
  linkedDataSources: [],
};

const defaultState: WizardState = {
  currentStep: 0,
  totalSteps: 5,
  formData: defaultFormData,
  isSubmitting: false,
  errors: {},
};

// === Context ===

const WizardContext = React.createContext<WizardContextValue | null>(null);

// === Provider ===

export function WizardProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = React.useState<WizardState>(defaultState);

  const nextStep = React.useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.min(prev.currentStep + 1, prev.totalSteps - 1),
    }));
  }, []);

  const prevStep = React.useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.max(prev.currentStep - 1, 0),
    }));
  }, []);

  const goToStep = React.useCallback((step: number) => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.max(0, Math.min(step, prev.totalSteps - 1)),
    }));
  }, []);

  const updateFormData = React.useCallback((data: Partial<WizardFormData>) => {
    setState((prev) => ({
      ...prev,
      formData: { ...prev.formData, ...data },
    }));
  }, []);

  const setError = React.useCallback((field: string, message: string) => {
    setState((prev) => ({
      ...prev,
      errors: { ...prev.errors, [field]: message },
    }));
  }, []);

  const clearError = React.useCallback((field: string) => {
    setState((prev) => {
      const { [field]: _, ...rest } = prev.errors;
      return { ...prev, errors: rest };
    });
  }, []);

  const clearAllErrors = React.useCallback(() => {
    setState((prev) => ({ ...prev, errors: {} }));
  }, []);

  const setSubmitting = React.useCallback((isSubmitting: boolean) => {
    setState((prev) => ({ ...prev, isSubmitting }));
  }, []);

  const reset = React.useCallback(() => {
    setState(defaultState);
  }, []);

  const canProceed = React.useCallback(() => {
    const { currentStep, formData, errors } = state;

    // Check for any errors
    if (Object.keys(errors).length > 0) return false;

    switch (currentStep) {
      case 0: // Start method
        if (formData.startMethod === "example" && !formData.exampleSlug) return false;
        if (formData.startMethod === "clone" && !formData.cloneUrl) return false;
        return true;
      case 1: // Basic info
        return formData.name.trim().length > 0;
      case 2: // VCS setup
        if (formData.initGit && formData.gitRemoteUrl) {
          // Validate URL format
          try {
            new URL(formData.gitRemoteUrl);
          } catch {
            if (!formData.gitRemoteUrl.includes("@")) return false;
          }
        }
        return true;
      case 3: // Configuration
        return true;
      case 4: // Review
        return true;
      default:
        return true;
    }
  }, [state]);

  const value: WizardContextValue = {
    ...state,
    nextStep,
    prevStep,
    goToStep,
    updateFormData,
    setError,
    clearError,
    clearAllErrors,
    setSubmitting,
    reset,
    canProceed,
  };

  return (
    <WizardContext.Provider value={value}>
      {children}
    </WizardContext.Provider>
  );
}

// === Hook ===

export function useWizard() {
  const context = React.useContext(WizardContext);
  if (!context) {
    throw new Error("useWizard must be used within WizardProvider");
  }
  return context;
}

// === Step Info ===

export interface StepInfo {
  id: string;
  title: string;
  description: string;
}

export const WIZARD_STEPS: StepInfo[] = [
  {
    id: "start",
    title: "Start Method",
    description: "Choose how to create your project",
  },
  {
    id: "basic",
    title: "Basic Information",
    description: "Name and describe your project",
  },
  {
    id: "vcs",
    title: "Version Control",
    description: "Set up Git for your project",
  },
  {
    id: "config",
    title: "Configuration",
    description: "Configure models and storage",
  },
  {
    id: "review",
    title: "Review & Create",
    description: "Review and create your project",
  },
];
