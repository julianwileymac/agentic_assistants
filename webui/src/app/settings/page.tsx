"use client";

import * as React from "react";
import { 
  Save, 
  Settings, 
  Server, 
  Key, 
  Database, 
  Zap, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Box,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronRight,
  HelpCircle,
  Lightbulb,
  RefreshCw,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useTestKubernetesConnection, useStorageStatus, useKubernetesDiagnostics, useTestMinioConnection } from "@/lib/api";

export default function SettingsPage() {
  const [isSaving, setIsSaving] = React.useState(false);
  
  const [settings, setSettings] = React.useState({
    backendUrl: "http://localhost:8080",
    ollamaUrl: "http://localhost:11434",
    mlflowUrl: "http://localhost:5000",
    jupyterUrl: "http://localhost:8888",
    defaultModel: "llama3.2",
    embeddingModel: "nomic-embed-text",
    vectorBackend: "lancedb",
    apiKey: "",
    // Kubernetes settings
    k8sEnabled: false,
    k8sKubeconfigPath: "",
    k8sContext: "",
    k8sNamespace: "agentic-workloads",
    // New Kubernetes debugging settings
    k8sAutodetectEnabled: true,
    k8sAutodetectExtraPaths: "",
    k8sRequestTimeout: 10,
    k8sInsecureSkipTls: false,
    k8sPreferIncluster: "auto",
    // MinIO settings
    minioEnabled: true,
    minioEndpoint: "",
    minioAccessKey: "",
    minioSecretKey: "",
    minioSecure: false,
    // PostgreSQL settings
    postgresEnabled: false,
    postgresHost: "",
    postgresPort: 5432,
    postgresDatabase: "mlflow",
    postgresUser: "",
    postgresPassword: "",
  });

  const [k8sTestResult, setK8sTestResult] = React.useState<{
    connected: boolean;
    version?: string;
    error?: string;
  } | null>(null);

  const { trigger: testK8sConnection, isMutating: isTestingK8s } = useTestKubernetesConnection();
  const { trigger: testMinioConnection, isMutating: isTestingMinio } = useTestMinioConnection();
  const { data: storageStatus, mutate: refreshStorageStatus } = useStorageStatus();
  const { data: k8sDiagnostics, mutate: refreshDiagnostics } = useKubernetesDiagnostics();
  const [showAdvancedK8s, setShowAdvancedK8s] = React.useState(false);
  const [minioTestResult, setMinioTestResult] = React.useState<{
    connected: boolean;
    endpoint?: string;
    error?: string;
  } | null>(null);

  React.useEffect(() => {
    // Load settings from localStorage
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('app_settings');
      if (saved) {
        setSettings(prev => ({ ...prev, ...JSON.parse(saved) }));
      }
    }
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      localStorage.setItem('app_settings', JSON.stringify(settings));
      if (settings.apiKey) {
        localStorage.setItem('api_key', settings.apiKey);
      }
      if (settings.backendUrl) {
        localStorage.setItem('backend_url', settings.backendUrl);
      }
      
      toast.success("Settings saved successfully");
    } catch (error) {
      toast.error("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure your development environment
          </p>
        </div>
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? (
            <>
              <Loader2 className="size-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="size-4 mr-2" />
              Save Settings
            </>
          )}
        </Button>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="connections">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="connections">
            <Server className="size-4 mr-2" />
            Connections
          </TabsTrigger>
          <TabsTrigger value="kubernetes">
            <Box className="size-4 mr-2" />
            Kubernetes
          </TabsTrigger>
          <TabsTrigger value="models">
            <Zap className="size-4 mr-2" />
            Models
          </TabsTrigger>
          <TabsTrigger value="api">
            <Key className="size-4 mr-2" />
            API Keys
          </TabsTrigger>
        </TabsList>

        {/* Connections Tab */}
        <TabsContent value="connections">
          <Card>
            <CardHeader>
              <CardTitle>Service Connections</CardTitle>
              <CardDescription>
                Configure URLs for backend services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="backend">Backend API URL</Label>
                <Input
                  id="backend"
                  placeholder="http://localhost:8080"
                  value={settings.backendUrl}
                  onChange={(e) => setSettings({ ...settings, backendUrl: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ollama">Ollama URL</Label>
                <Input
                  id="ollama"
                  placeholder="http://localhost:11434"
                  value={settings.ollamaUrl}
                  onChange={(e) => setSettings({ ...settings, ollamaUrl: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="mlflow">MLFlow URL</Label>
                <Input
                  id="mlflow"
                  placeholder="http://localhost:5000"
                  value={settings.mlflowUrl}
                  onChange={(e) => setSettings({ ...settings, mlflowUrl: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="jupyter">JupyterLab URL</Label>
                <Input
                  id="jupyter"
                  placeholder="http://localhost:8888"
                  value={settings.jupyterUrl}
                  onChange={(e) => setSettings({ ...settings, jupyterUrl: e.target.value })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Kubernetes Tab */}
        <TabsContent value="kubernetes">
          <TooltipProvider>
            <div className="space-y-6">
              {/* Connection Status Banner */}
              {k8sDiagnostics && (
                <Card className={k8sDiagnostics.connected ? "border-green-500/50 bg-green-500/5" : "border-destructive/50 bg-destructive/5"}>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-3">
                      {k8sDiagnostics.connected ? (
                        <CheckCircle className="size-5 text-green-500" />
                      ) : (
                        <XCircle className="size-5 text-destructive" />
                      )}
                      <div className="flex-1">
                        <p className="font-medium">
                          {k8sDiagnostics.connected ? "Connected to Cluster" : "Not Connected"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {k8sDiagnostics.connected 
                            ? `${k8sDiagnostics.version} via ${k8sDiagnostics.connection_method}`
                            : k8sDiagnostics.error}
                        </p>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => refreshDiagnostics()}>
                        <RefreshCw className="size-4" />
                      </Button>
                    </div>
                    
                    {/* Suggestions when not connected */}
                    {!k8sDiagnostics.connected && k8sDiagnostics.suggestions?.length > 0 && (
                      <div className="mt-3 pt-3 border-t space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <Lightbulb className="size-4 text-yellow-500" />
                          Suggestions
                        </div>
                        <ul className="text-xs text-muted-foreground space-y-1 ml-6">
                          {k8sDiagnostics.suggestions.map((s, i) => (
                            <li key={i} className="list-disc">{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Capabilities when connected */}
                    {k8sDiagnostics.connected && Object.keys(k8sDiagnostics.capabilities).length > 0 && (
                      <div className="mt-3 pt-3 border-t flex flex-wrap gap-2">
                        {Object.entries(k8sDiagnostics.capabilities).map(([cap, available]) => (
                          <Badge key={cap} variant={available ? "default" : "secondary"} className="text-xs">
                            {available ? <CheckCircle className="size-3 mr-1" /> : <XCircle className="size-3 mr-1" />}
                            {cap.replace(/_/g, " ")}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Kubernetes Cluster
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="size-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs">
                        <p>Configure connection to your RPi Kubernetes cluster. The framework will auto-discover kubeconfig files if not specified.</p>
                      </TooltipContent>
                    </Tooltip>
                  </CardTitle>
                  <CardDescription>
                    Configure connection to your RPi Kubernetes cluster
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Cluster Connection</Label>
                      <p className="text-xs text-muted-foreground">
                        Enable to manage deployments on Kubernetes
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {k8sTestResult && (
                        <Badge variant={k8sTestResult.connected ? "default" : "destructive"}>
                          {k8sTestResult.connected ? (
                            <>
                              <CheckCircle className="size-3 mr-1" />
                              {k8sTestResult.version}
                            </>
                          ) : (
                            <>
                              <XCircle className="size-3 mr-1" />
                              Failed
                            </>
                          )}
                        </Badge>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={async () => {
                          try {
                            const result = await testK8sConnection({
                              kubeconfig_path: settings.k8sKubeconfigPath || undefined,
                              context: settings.k8sContext || undefined,
                            });
                            setK8sTestResult(result);
                            refreshDiagnostics();
                            if (result.connected) {
                              toast.success("Connected to Kubernetes cluster");
                            } else {
                              toast.error(result.error || "Connection failed");
                            }
                          } catch (error) {
                            toast.error("Failed to test connection");
                          }
                        }}
                        disabled={isTestingK8s}
                      >
                        {isTestingK8s ? <Loader2 className="size-4 mr-2 animate-spin" /> : null}
                        Test Connection
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="kubeconfig">Kubeconfig Path</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <Info className="size-3 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-sm">
                          <p>Leave empty to auto-discover from:</p>
                          <ul className="text-xs mt-1 ml-4 list-disc">
                            <li>KUBECONFIG environment variable</li>
                            <li>~/.kube/config</li>
                            <li>rpi_kubernetes/kubeconfig.yaml</li>
                          </ul>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="kubeconfig"
                      placeholder="Auto-detect (or specify path)"
                      value={settings.k8sKubeconfigPath}
                      onChange={(e) => setSettings({ ...settings, k8sKubeconfigPath: e.target.value })}
                    />
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p>Leave empty to auto-discover kubeconfig files</p>
                      <p className="flex items-center gap-1">
                        <Lightbulb className="size-3" />
                        <span>
                          For rpi_kubernetes: <code className="bg-muted px-1 rounded">C:\Users\Julian Wiley\Documents\GitHub\rpi_kubernetes\kubeconfig.yaml</code>
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="context">Context</Label>
                    <Input
                      id="context"
                      placeholder="default"
                      value={settings.k8sContext}
                      onChange={(e) => setSettings({ ...settings, k8sContext: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">
                      Leave empty to use current context from kubeconfig
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="namespace">Default Namespace</Label>
                    <Input
                      id="namespace"
                      placeholder="agentic-workloads"
                      value={settings.k8sNamespace}
                      onChange={(e) => setSettings({ ...settings, k8sNamespace: e.target.value })}
                    />
                  </div>

                  {/* Advanced Settings */}
                  <Collapsible open={showAdvancedK8s} onOpenChange={setShowAdvancedK8s}>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" size="sm" className="w-full justify-start">
                        {showAdvancedK8s ? <ChevronDown className="size-4 mr-2" /> : <ChevronRight className="size-4 mr-2" />}
                        Advanced Settings
                      </Button>
                    </CollapsibleTrigger>
                    <CollapsibleContent className="space-y-4 pt-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label>Auto-detect Kubeconfig</Label>
                          <p className="text-xs text-muted-foreground">
                            Automatically search for kubeconfig files
                          </p>
                        </div>
                        <Switch
                          checked={settings.k8sAutodetectEnabled}
                          onCheckedChange={(checked) => setSettings({ ...settings, k8sAutodetectEnabled: checked })}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Label htmlFor="extraPaths">Extra Kubeconfig Paths</Label>
                          <Tooltip>
                            <TooltipTrigger>
                              <Info className="size-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Comma-separated list of additional kubeconfig paths to check</p>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                        <Input
                          id="extraPaths"
                          placeholder="/path/to/config1,/path/to/config2"
                          value={settings.k8sAutodetectExtraPaths}
                          onChange={(e) => setSettings({ ...settings, k8sAutodetectExtraPaths: e.target.value })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="timeout">Request Timeout (seconds)</Label>
                        <Input
                          id="timeout"
                          type="number"
                          min={1}
                          max={60}
                          value={settings.k8sRequestTimeout}
                          onChange={(e) => setSettings({ ...settings, k8sRequestTimeout: parseInt(e.target.value) || 10 })}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="flex items-center gap-2">
                            Skip TLS Verification
                            <Badge variant="destructive" className="text-xs">Insecure</Badge>
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            Disable SSL certificate verification (for testing only)
                          </p>
                        </div>
                        <Switch
                          checked={settings.k8sInsecureSkipTls}
                          onCheckedChange={(checked) => setSettings({ ...settings, k8sInsecureSkipTls: checked })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="preferIncluster">In-Cluster Config Preference</Label>
                        <Select
                          value={settings.k8sPreferIncluster}
                          onValueChange={(value) => setSettings({ ...settings, k8sPreferIncluster: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="auto">Auto-detect</SelectItem>
                            <SelectItem value="true">Prefer in-cluster</SelectItem>
                            <SelectItem value="false">Prefer kubeconfig</SelectItem>
                          </SelectContent>
                        </Select>
                        <p className="text-xs text-muted-foreground">
                          How to handle in-cluster vs kubeconfig when both are available
                        </p>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="size-5" />
                    MinIO Storage
                  </CardTitle>
                  <CardDescription>
                    Configure connection to MinIO object storage for artifacts and model files
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Enable MinIO Storage</Label>
                      <p className="text-xs text-muted-foreground">
                        S3-compatible object storage for artifacts and model files
                      </p>
                    </div>
                    <Switch
                      checked={settings.minioEnabled}
                      onCheckedChange={(checked) => setSettings({ ...settings, minioEnabled: checked })}
                    />
                  </div>

                  {settings.minioEnabled && (
                    <>
                      <div className="flex items-center justify-between">
                        <div>
                          <Label>Connection Status</Label>
                          <p className="text-xs text-muted-foreground">
                            Test your MinIO connection
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {minioTestResult && (
                            <Badge variant={minioTestResult.connected ? "default" : "destructive"}>
                              {minioTestResult.connected ? (
                                <>
                                  <CheckCircle className="size-3 mr-1" />
                                  Connected
                                </>
                              ) : (
                                <>
                                  <XCircle className="size-3 mr-1" />
                                  Failed
                                </>
                              )}
                            </Badge>
                          )}
                          {!minioTestResult && storageStatus && (
                            <Badge variant={storageStatus.connected ? "default" : "secondary"}>
                              {storageStatus.connected ? (
                                <>
                                  <CheckCircle className="size-3 mr-1" />
                                  Connected
                                </>
                              ) : (
                                <>
                                  <XCircle className="size-3 mr-1" />
                                  Not Connected
                                </>
                              )}
                            </Badge>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={async () => {
                              try {
                                const result = await testMinioConnection({
                                  endpoint: settings.minioEndpoint || undefined,
                                  access_key: settings.minioAccessKey || undefined,
                                  secret_key: settings.minioSecretKey || undefined,
                                  secure: settings.minioSecure,
                                });
                                setMinioTestResult(result);
                                refreshStorageStatus();
                                if (result.connected) {
                                  toast.success("Connected to MinIO storage");
                                } else {
                                  toast.error(result.error || "Connection failed");
                                }
                              } catch (error) {
                                toast.error("Failed to test MinIO connection");
                              }
                            }}
                            disabled={isTestingMinio}
                          >
                            {isTestingMinio ? <Loader2 className="size-4 mr-2 animate-spin" /> : null}
                            Test Connection
                          </Button>
                        </div>
                      </div>
                      
                      {minioTestResult && !minioTestResult.connected && minioTestResult.error && (
                        <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30">
                          <p className="text-sm text-destructive">{minioTestResult.error}</p>
                        </div>
                      )}
                      
                      <div className="space-y-2">
                        <Label htmlFor="minio-endpoint">MinIO Endpoint</Label>
                        <Input
                          id="minio-endpoint"
                          placeholder="localhost:9000 or minio.local:9000"
                          value={settings.minioEndpoint}
                          onChange={(e) => setSettings({ ...settings, minioEndpoint: e.target.value })}
                        />
                        <p className="text-xs text-muted-foreground">
                          For local: localhost:9000 | In-cluster: minio.data-services.svc.cluster.local:9000
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="minio-access">Access Key</Label>
                          <Input
                            id="minio-access"
                            placeholder="minioadmin"
                            value={settings.minioAccessKey}
                            onChange={(e) => setSettings({ ...settings, minioAccessKey: e.target.value })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="minio-secret">Secret Key</Label>
                          <Input
                            id="minio-secret"
                            type="password"
                            placeholder="••••••••"
                            value={settings.minioSecretKey}
                            onChange={(e) => setSettings({ ...settings, minioSecretKey: e.target.value })}
                          />
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <Label>Use HTTPS</Label>
                          <p className="text-xs text-muted-foreground">
                            Enable TLS for MinIO connections
                          </p>
                        </div>
                        <Switch
                          checked={settings.minioSecure}
                          onCheckedChange={(checked) => setSettings({ ...settings, minioSecure: checked })}
                        />
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>PostgreSQL Database</CardTitle>
                  <CardDescription>
                    Configure connection to PostgreSQL for persistence
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Enable PostgreSQL</Label>
                      <p className="text-xs text-muted-foreground">
                        Use PostgreSQL for MLflow backend store and metadata
                      </p>
                    </div>
                    <Switch
                      checked={settings.postgresEnabled}
                      onCheckedChange={(checked) => setSettings({ ...settings, postgresEnabled: checked })}
                    />
                  </div>
                  {settings.postgresEnabled && (
                    <>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="col-span-2 space-y-2">
                          <Label htmlFor="pg-host">Host</Label>
                          <Input
                            id="pg-host"
                            placeholder="postgresql.data-services.svc.cluster.local"
                            value={settings.postgresHost}
                            onChange={(e) => setSettings({ ...settings, postgresHost: e.target.value })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="pg-port">Port</Label>
                          <Input
                            id="pg-port"
                            type="number"
                            placeholder="5432"
                            value={settings.postgresPort}
                            onChange={(e) => setSettings({ ...settings, postgresPort: parseInt(e.target.value) || 5432 })}
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="pg-database">Database</Label>
                        <Input
                          id="pg-database"
                          placeholder="mlflow"
                          value={settings.postgresDatabase}
                          onChange={(e) => setSettings({ ...settings, postgresDatabase: e.target.value })}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="pg-user">Username</Label>
                          <Input
                            id="pg-user"
                            placeholder="mlflow"
                            value={settings.postgresUser}
                            onChange={(e) => setSettings({ ...settings, postgresUser: e.target.value })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="pg-password">Password</Label>
                          <Input
                            id="pg-password"
                            type="password"
                            placeholder="••••••••"
                            value={settings.postgresPassword}
                            onChange={(e) => setSettings({ ...settings, postgresPassword: e.target.value })}
                          />
                        </div>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </TooltipProvider>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models">
          <Card>
            <CardHeader>
              <CardTitle>Model Configuration</CardTitle>
              <CardDescription>
                Configure default models for agents and embeddings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="defaultModel">Default LLM Model</Label>
                <Select
                  value={settings.defaultModel}
                  onValueChange={(value) => setSettings({ ...settings, defaultModel: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="llama3.2">Llama 3.2</SelectItem>
                    <SelectItem value="llama3.1">Llama 3.1</SelectItem>
                    <SelectItem value="mistral">Mistral</SelectItem>
                    <SelectItem value="codellama">Code Llama</SelectItem>
                    <SelectItem value="phi3">Phi-3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="embeddingModel">Embedding Model</Label>
                <Select
                  value={settings.embeddingModel}
                  onValueChange={(value) => setSettings({ ...settings, embeddingModel: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="nomic-embed-text">Nomic Embed Text</SelectItem>
                    <SelectItem value="all-MiniLM-L6-v2">all-MiniLM-L6-v2</SelectItem>
                    <SelectItem value="mxbai-embed-large">MxBAI Embed Large</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vectorBackend">Vector Database Backend</Label>
                <Select
                  value={settings.vectorBackend}
                  onValueChange={(value) => setSettings({ ...settings, vectorBackend: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lancedb">LanceDB</SelectItem>
                    <SelectItem value="chroma">ChromaDB</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
              <CardDescription>
                Configure API keys for authentication and external services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="apiKey">Backend API Key</Label>
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="Enter API key..."
                  value={settings.apiKey}
                  onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Used for authenticating with the backend API. Leave empty for development.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

