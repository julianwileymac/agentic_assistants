"use client";

import * as React from "react";
import { AlertTriangle, Copy, ChevronDown, ChevronUp, RefreshCw, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";

// === Types ===

interface VerboseError {
  error_id: string;
  message: string;
  detail?: string;
  error_type: string;
  status_code: number;
  timestamp: string;
  path?: string;
  method?: string;
  traceback?: string;
  context: Record<string, unknown>;
}

interface ErrorDisplayProps {
  error: VerboseError;
  onDismiss?: () => void;
  showTraceback?: boolean;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

// === Error Display Component ===

export function ErrorDisplay({ error, onDismiss, showTraceback = true }: ErrorDisplayProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const handleCopyError = () => {
    const errorText = JSON.stringify(error, null, 2);
    navigator.clipboard.writeText(errorText);
    toast.success("Error details copied to clipboard");
  };

  const statusColorClass = error.status_code >= 500
    ? "bg-red-500/10 text-red-500 border-red-500/20"
    : error.status_code >= 400
      ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
      : "bg-blue-500/10 text-blue-500 border-blue-500/20";

  return (
    <Card className="border-destructive/50 bg-destructive/5">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-destructive/10">
              <AlertTriangle className="size-5 text-destructive" />
            </div>
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                {error.error_type}
                <Badge variant="outline" className={statusColorClass}>
                  {error.status_code}
                </Badge>
              </CardTitle>
              <CardDescription className="text-destructive/80">
                Error ID: {error.error_id}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" onClick={handleCopyError}>
              <Copy className="size-4" />
            </Button>
            {onDismiss && (
              <Button variant="ghost" size="icon" onClick={onDismiss}>
                <X className="size-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Message */}
        <div>
          <p className="font-medium text-destructive">{error.message}</p>
          {error.detail && (
            <p className="text-sm text-muted-foreground mt-1">{error.detail}</p>
          )}
        </div>

        {/* Request Info */}
        {(error.path || error.method) && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {error.method && (
              <Badge variant="secondary" className="font-mono">
                {error.method}
              </Badge>
            )}
            {error.path && <span className="font-mono">{error.path}</span>}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-muted-foreground">
          {new Date(error.timestamp).toLocaleString()}
        </p>

        {/* Expandable Details */}
        {(error.traceback || Object.keys(error.context).length > 0) && showTraceback && (
          <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="w-full justify-start">
                {isExpanded ? (
                  <ChevronUp className="size-4 mr-2" />
                ) : (
                  <ChevronDown className="size-4 mr-2" />
                )}
                {isExpanded ? "Hide" : "Show"} Details
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2 space-y-3">
              {/* Context */}
              {Object.keys(error.context).length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Context</p>
                  <pre className="text-xs bg-muted p-3 rounded-lg overflow-x-auto">
                    {JSON.stringify(error.context, null, 2)}
                  </pre>
                </div>
              )}

              {/* Traceback */}
              {error.traceback && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Stack Trace</p>
                  <ScrollArea className="h-48">
                    <pre className="text-xs bg-muted p-3 rounded-lg font-mono whitespace-pre-wrap">
                      {error.traceback}
                    </pre>
                  </ScrollArea>
                </div>
              )}
            </CollapsibleContent>
          </Collapsible>
        )}
      </CardContent>
    </Card>
  );
}

// === Error Boundary Class Component ===

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error to console
    console.error("Error caught by boundary:", error, errorInfo);
    
    // Optionally send to backend
    // fetch("/api/v1/errors", { method: "POST", body: JSON.stringify({ error: error.message, stack: errorInfo.componentStack }) });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="p-6">
          <Card className="border-destructive/50 bg-destructive/5 max-w-2xl mx-auto">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-destructive/10">
                  <AlertTriangle className="size-6 text-destructive" />
                </div>
                <div>
                  <CardTitle>Something went wrong</CardTitle>
                  <CardDescription>
                    An unexpected error occurred in the application
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-muted">
                <p className="font-mono text-sm text-destructive">
                  {this.state.error?.message || "Unknown error"}
                </p>
              </div>

              {this.state.errorInfo?.componentStack && (
                <Collapsible>
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <ChevronDown className="size-4 mr-2" />
                      Show Component Stack
                    </Button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <ScrollArea className="h-48 mt-2">
                      <pre className="text-xs bg-muted p-3 rounded-lg font-mono whitespace-pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </ScrollArea>
                  </CollapsibleContent>
                </Collapsible>
              )}

              <div className="flex items-center gap-2">
                <Button onClick={this.handleReset}>
                  <RefreshCw className="size-4 mr-2" />
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  Reload Page
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// === Enhanced Toast Helpers ===

interface ToastErrorOptions {
  error: VerboseError | Error | string;
  title?: string;
  duration?: number;
}

export function showErrorToast({ error, title, duration = 10000 }: ToastErrorOptions) {
  let errorObj: VerboseError;

  if (typeof error === "string") {
    errorObj = {
      error_id: Math.random().toString(36).substring(7),
      message: error,
      error_type: "Error",
      status_code: 500,
      timestamp: new Date().toISOString(),
      context: {},
    };
  } else if (error instanceof Error) {
    errorObj = {
      error_id: Math.random().toString(36).substring(7),
      message: error.message,
      error_type: error.name,
      status_code: 500,
      timestamp: new Date().toISOString(),
      traceback: error.stack,
      context: {},
    };
  } else {
    errorObj = error;
  }

  toast.error(title || errorObj.error_type, {
    description: errorObj.message,
    duration,
    action: errorObj.traceback || Object.keys(errorObj.context).length > 0
      ? {
          label: "Details",
          onClick: () => {
            // Show detailed error modal
            showDetailedError(errorObj);
          },
        }
      : undefined,
  });
}

// Store for showing detailed errors in a modal
let showDetailedErrorFn: ((error: VerboseError) => void) | null = null;

export function registerDetailedErrorHandler(handler: (error: VerboseError) => void) {
  showDetailedErrorFn = handler;
}

function showDetailedError(error: VerboseError) {
  if (showDetailedErrorFn) {
    showDetailedErrorFn(error);
  } else {
    // Fallback: log to console
    console.error("Detailed error:", error);
  }
}

// === API Error Handler ===

export async function handleApiError(response: Response): Promise<VerboseError | null> {
  if (response.ok) return null;

  try {
    const data = await response.json();
    if (data.error) {
      return data.error as VerboseError;
    }
    // Legacy error format
    return {
      error_id: Math.random().toString(36).substring(7),
      message: data.detail || data.message || "Unknown error",
      error_type: "APIError",
      status_code: response.status,
      timestamp: new Date().toISOString(),
      context: data,
    };
  } catch {
    return {
      error_id: Math.random().toString(36).substring(7),
      message: `HTTP ${response.status}: ${response.statusText}`,
      error_type: "HTTPError",
      status_code: response.status,
      timestamp: new Date().toISOString(),
      context: {},
    };
  }
}

// === Error Store Hook ===

interface ErrorStoreState {
  errors: VerboseError[];
  addError: (error: VerboseError) => void;
  removeError: (errorId: string) => void;
  clearErrors: () => void;
}

const ErrorStoreContext = React.createContext<ErrorStoreState | null>(null);

export function ErrorStoreProvider({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = React.useState<VerboseError[]>([]);

  const addError = React.useCallback((error: VerboseError) => {
    setErrors((prev) => [error, ...prev].slice(0, 50)); // Keep last 50 errors
  }, []);

  const removeError = React.useCallback((errorId: string) => {
    setErrors((prev) => prev.filter((e) => e.error_id !== errorId));
  }, []);

  const clearErrors = React.useCallback(() => {
    setErrors([]);
  }, []);

  // Register handler for detailed error display
  React.useEffect(() => {
    registerDetailedErrorHandler((error) => {
      addError(error);
    });
  }, [addError]);

  return (
    <ErrorStoreContext.Provider value={{ errors, addError, removeError, clearErrors }}>
      {children}
    </ErrorStoreContext.Provider>
  );
}

export function useErrorStore() {
  const context = React.useContext(ErrorStoreContext);
  if (!context) {
    throw new Error("useErrorStore must be used within ErrorStoreProvider");
  }
  return context;
}
