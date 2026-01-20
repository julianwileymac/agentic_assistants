"use client";

import * as React from "react";
import {
  Database,
  HardDrive,
  Activity,
  CheckCircle,
  XCircle,
  Loader2,
  Plus,
  Server,
  AlertTriangle,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";

// Component types that can be added manually
const COMPONENT_TYPES = [
  {
    id: "minio",
    name: "MinIO Storage",
    description: "S3-compatible object storage for artifacts",
    icon: HardDrive,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10",
    fields: [
      { name: "endpoint", label: "Endpoint", placeholder: "minio.local:9000", required: true },
      { name: "accessKey", label: "Access Key", placeholder: "minioadmin", required: true },
      { name: "secretKey", label: "Secret Key", placeholder: "••••••••", type: "password", required: true },
      { name: "secure", label: "Use HTTPS", type: "switch", default: false },
      { name: "bucket", label: "Default Bucket", placeholder: "agentic-artifacts" },
    ],
    testEndpoint: "/api/v1/kubernetes/storage/status",
  },
  {
    id: "mlflow",
    name: "MLflow Tracking",
    description: "Experiment tracking and model registry",
    icon: Activity,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    fields: [
      { name: "trackingUri", label: "Tracking URI", placeholder: "http://mlflow.local:5000", required: true },
      { name: "backendStoreUri", label: "Backend Store URI", placeholder: "postgresql://...", required: false },
      { name: "artifactLocation", label: "Artifact Location", placeholder: "s3://mlflow-artifacts/", required: false },
    ],
    testEndpoint: null, // Custom test
  },
  {
    id: "postgresql",
    name: "PostgreSQL Database",
    description: "Database backend for persistence",
    icon: Database,
    color: "text-green-500",
    bgColor: "bg-green-500/10",
    fields: [
      { name: "host", label: "Host", placeholder: "postgresql.local", required: true },
      { name: "port", label: "Port", placeholder: "5432", type: "number", default: "5432" },
      { name: "database", label: "Database", placeholder: "mlflow", required: true },
      { name: "user", label: "Username", placeholder: "mlflow", required: true },
      { name: "password", label: "Password", placeholder: "••••••••", type: "password", required: true },
    ],
    testEndpoint: null,
  },
  {
    id: "custom",
    name: "Custom Service",
    description: "Add any service endpoint",
    icon: Server,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
    fields: [
      { name: "name", label: "Service Name", placeholder: "my-service", required: true },
      { name: "endpoint", label: "Endpoint URL", placeholder: "http://service.local:8080", required: true },
      { name: "healthEndpoint", label: "Health Endpoint", placeholder: "/health" },
      { name: "description", label: "Description", placeholder: "Description of the service" },
    ],
    testEndpoint: null,
  },
];

interface ComponentConfig {
  type: string;
  values: Record<string, string | boolean>;
  status: "pending" | "testing" | "connected" | "failed";
  error?: string;
}

interface KubernetesComponentWizardProps {
  onSave?: (configs: ComponentConfig[]) => void;
  existingConfigs?: ComponentConfig[];
}

export function KubernetesComponentWizard({ onSave, existingConfigs = [] }: KubernetesComponentWizardProps) {
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [selectedType, setSelectedType] = React.useState<string | null>(null);
  const [formValues, setFormValues] = React.useState<Record<string, string | boolean>>({});
  const [isTesting, setIsTesting] = React.useState(false);
  const [testResult, setTestResult] = React.useState<{ success: boolean; message: string } | null>(null);
  const [configs, setConfigs] = React.useState<ComponentConfig[]>(existingConfigs);

  // Load configs from localStorage
  React.useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("k8s_manual_components");
      if (saved) {
        try {
          setConfigs(JSON.parse(saved));
        } catch {
          // Invalid JSON, ignore
        }
      }
    }
  }, []);

  // Save configs to localStorage
  const saveConfigs = (newConfigs: ComponentConfig[]) => {
    setConfigs(newConfigs);
    if (typeof window !== "undefined") {
      localStorage.setItem("k8s_manual_components", JSON.stringify(newConfigs));
    }
    onSave?.(newConfigs);
  };

  const selectedComponent = COMPONENT_TYPES.find((c) => c.id === selectedType);

  const handleFieldChange = (name: string, value: string | boolean) => {
    setFormValues((prev) => ({ ...prev, [name]: value }));
    setTestResult(null);
  };

  const handleTest = async () => {
    if (!selectedComponent) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      // For MinIO, we can test via the storage status endpoint
      if (selectedType === "minio") {
        const response = await fetch(`${localStorage.getItem("backend_url") || "http://localhost:8080"}/api/v1/kubernetes/storage/status`);
        const data = await response.json();
        if (data.connected) {
          setTestResult({ success: true, message: "Connected successfully" });
        } else {
          setTestResult({ success: false, message: data.error || "Connection failed" });
        }
      } else if (selectedType === "mlflow") {
        // Test MLflow by hitting the tracking URI
        const trackingUri = formValues.trackingUri as string;
        if (trackingUri) {
          try {
            const response = await fetch(`${trackingUri}/api/2.0/mlflow/experiments/list?max_results=1`, {
              method: "GET",
              signal: AbortSignal.timeout(5000),
            });
            if (response.ok) {
              setTestResult({ success: true, message: "MLflow server reachable" });
            } else {
              setTestResult({ success: false, message: `HTTP ${response.status}` });
            }
          } catch (e) {
            setTestResult({ success: false, message: "Could not reach MLflow server" });
          }
        }
      } else {
        // Generic endpoint test
        const endpoint = formValues.endpoint as string;
        if (endpoint) {
          try {
            const healthPath = (formValues.healthEndpoint as string) || "/health";
            const url = endpoint.endsWith("/") ? endpoint.slice(0, -1) + healthPath : endpoint + healthPath;
            const response = await fetch(url, {
              method: "GET",
              signal: AbortSignal.timeout(5000),
            });
            if (response.ok) {
              setTestResult({ success: true, message: "Service reachable" });
            } else {
              setTestResult({ success: false, message: `HTTP ${response.status}` });
            }
          } catch (e) {
            setTestResult({ success: false, message: "Could not reach service" });
          }
        }
      }
    } catch (error) {
      setTestResult({ success: false, message: String(error) });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    if (!selectedComponent) return;

    const newConfig: ComponentConfig = {
      type: selectedType!,
      values: { ...formValues },
      status: testResult?.success ? "connected" : "pending",
    };

    const existingIndex = configs.findIndex((c) => c.type === selectedType);
    let newConfigs: ComponentConfig[];
    
    if (existingIndex >= 0) {
      newConfigs = [...configs];
      newConfigs[existingIndex] = newConfig;
    } else {
      newConfigs = [...configs, newConfig];
    }

    saveConfigs(newConfigs);
    toast.success(`${selectedComponent.name} configuration saved`);
    setDialogOpen(false);
    resetForm();
  };

  const handleRemove = (type: string) => {
    const newConfigs = configs.filter((c) => c.type !== type);
    saveConfigs(newConfigs);
    toast.success("Component removed");
  };

  const resetForm = () => {
    setSelectedType(null);
    setFormValues({});
    setTestResult(null);
  };

  const openEditDialog = (config: ComponentConfig) => {
    setSelectedType(config.type);
    setFormValues(config.values);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Manual Components</h3>
          <p className="text-sm text-muted-foreground">
            Configure service endpoints when cluster connection is unavailable
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) resetForm();
        }}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="size-4 mr-2" />
              Add Component
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>
                {selectedType ? `Configure ${selectedComponent?.name}` : "Add Component"}
              </DialogTitle>
              <DialogDescription>
                {selectedType 
                  ? selectedComponent?.description 
                  : "Select a component type to configure manually"}
              </DialogDescription>
            </DialogHeader>

            {!selectedType ? (
              <div className="grid grid-cols-2 gap-3 py-4">
                {COMPONENT_TYPES.map((comp) => (
                  <button
                    key={comp.id}
                    onClick={() => {
                      setSelectedType(comp.id);
                      // Set defaults
                      const defaults: Record<string, string | boolean> = {};
                      comp.fields.forEach((f) => {
                        if (f.default !== undefined) {
                          defaults[f.name] = f.default;
                        }
                      });
                      setFormValues(defaults);
                    }}
                    className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className={`p-3 rounded-xl ${comp.bgColor}`}>
                      <comp.icon className={`size-6 ${comp.color}`} />
                    </div>
                    <span className="font-medium text-sm">{comp.name}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-4 py-4">
                {selectedComponent?.fields.map((field) => (
                  <div key={field.name} className="space-y-2">
                    {field.type === "switch" ? (
                      <div className="flex items-center justify-between">
                        <Label htmlFor={field.name}>{field.label}</Label>
                        <Switch
                          id={field.name}
                          checked={formValues[field.name] as boolean || false}
                          onCheckedChange={(checked) => handleFieldChange(field.name, checked)}
                        />
                      </div>
                    ) : (
                      <>
                        <Label htmlFor={field.name}>
                          {field.label}
                          {field.required && <span className="text-destructive ml-1">*</span>}
                        </Label>
                        <Input
                          id={field.name}
                          type={field.type || "text"}
                          placeholder={field.placeholder}
                          value={(formValues[field.name] as string) || ""}
                          onChange={(e) => handleFieldChange(field.name, e.target.value)}
                        />
                      </>
                    )}
                  </div>
                ))}

                {/* Test Result */}
                {testResult && (
                  <div className={`flex items-center gap-2 p-3 rounded-lg ${
                    testResult.success ? "bg-green-500/10" : "bg-destructive/10"
                  }`}>
                    {testResult.success ? (
                      <CheckCircle className="size-4 text-green-500" />
                    ) : (
                      <XCircle className="size-4 text-destructive" />
                    )}
                    <span className="text-sm">{testResult.message}</span>
                  </div>
                )}
              </div>
            )}

            {selectedType && (
              <DialogFooter className="flex-col sm:flex-row gap-2">
                <Button variant="outline" onClick={() => setSelectedType(null)}>
                  Back
                </Button>
                <Button variant="outline" onClick={handleTest} disabled={isTesting}>
                  {isTesting ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    "Test Connection"
                  )}
                </Button>
                <Button onClick={handleSave}>
                  Save Configuration
                </Button>
              </DialogFooter>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {/* Configured Components */}
      {configs.length > 0 ? (
        <div className="grid gap-3">
          {configs.map((config) => {
            const comp = COMPONENT_TYPES.find((c) => c.id === config.type);
            if (!comp) return null;
            
            return (
              <Card key={config.type} className="cursor-pointer hover:bg-muted/30 transition-colors">
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${comp.bgColor}`}>
                      <comp.icon className={`size-5 ${comp.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{comp.name}</p>
                        <Badge 
                          variant={config.status === "connected" ? "default" : 
                                  config.status === "failed" ? "destructive" : "secondary"}
                          className="text-xs"
                        >
                          {config.status === "connected" && <CheckCircle className="size-3 mr-1" />}
                          {config.status === "failed" && <XCircle className="size-3 mr-1" />}
                          {config.status === "pending" && <AlertTriangle className="size-3 mr-1" />}
                          {config.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {config.values.endpoint as string || config.values.trackingUri as string || config.values.host as string}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openEditDialog(config)}>
                        Edit
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleRemove(config.type)}>
                        Remove
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card className="border-dashed">
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <Server className="size-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No components configured</p>
              <p className="text-xs">Add components to use services without cluster connection</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
