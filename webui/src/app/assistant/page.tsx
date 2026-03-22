"use client";

import * as React from "react";
import { 
  Save, 
  Bot, 
  Code, 
  BookOpen, 
  Brain, 
  Database,
  BarChart3,
  Loader2,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings2,
  MessageSquare,
  Sparkles,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import type { AssistantModelCatalogEntry } from "@/lib/types";

const frameworks = [
  { id: "crewai", name: "CrewAI", description: "Multi-agent crew orchestration" },
  { id: "langgraph", name: "LangGraph", description: "Graph-based workflow orchestration" },
  { id: "autogen", name: "AutoGen", description: "Microsoft multi-agent conversations" },
  { id: "google_adk", name: "Google ADK", description: "Google Agent Development Kit" },
  { id: "agno", name: "Agno", description: "Modern framework with reasoning modes" },
  { id: "langflow", name: "LangFlow", description: "Visual workflow builder" },
];

// Default Ollama models to show when autodetection fails or as fallback options
const DEFAULT_OLLAMA_MODELS = [
  "llama3.2",
  "llama3.2:1b",
  "llama3.2:3b",
  "llama3.1",
  "llama3.1:8b",
  "llama3.1:70b",
  "llama3",
  "codellama",
  "codellama:7b",
  "codellama:13b",
  "codellama:34b",
  "mistral",
  "mistral:7b",
  "mixtral",
  "mixtral:8x7b",
  "phi3",
  "phi3:mini",
  "phi3:medium",
  "gemma2",
  "gemma2:2b",
  "gemma2:9b",
  "gemma2:27b",
  "qwen2.5",
  "qwen2.5:0.5b",
  "qwen2.5:7b",
  "qwen2.5:72b",
  "qwen2.5-coder",
  "qwen2.5-coder:7b",
  "deepseek-coder-v2",
  "deepseek-coder-v2:16b",
  "starcoder2",
  "starcoder2:3b",
  "starcoder2:7b",
  "starcoder2:15b",
  "nemotron-3-nano",
  "nemotron-3-nano:30b",
  "nomic-embed-text",
  "mxbai-embed-large",
];

const LLM_PROVIDERS = [
  { id: "ollama", label: "Ollama" },
  { id: "huggingface_local", label: "Hugging Face (local)" },
  { id: "openai_compatible", label: "OpenAI-compatible endpoint" },
];

export default function AssistantPage() {
  const [isSaving, setIsSaving] = React.useState(false);
  const [isTestingConnection, setIsTestingConnection] = React.useState(false);
  const [connectionStatus, setConnectionStatus] = React.useState<"connected" | "disconnected" | null>(null);
  const [modelCatalog, setModelCatalog] = React.useState<AssistantModelCatalogEntry[]>([]);

  const [config, setConfig] = React.useState({
    enabled: true,
    defaultFramework: "crewai",
    provider: "ollama",
    model: "llama3.2",
    endpoint: "",
    openaiCompatibleBaseUrl: "http://localhost:8000/v1",
    openaiCompatibleApiKeyEnv: "OPENAI_API_KEY",
    hfExecutionMode: "hybrid",
    hfLocalModel: "",
    enableCodingHelper: true,
    enableFrameworkGuide: true,
    enableMetaAnalysis: true,
    ragEnabled: true,
    memoryEnabled: true,
    codeKbProjectId: "",
    docsKbName: "framework_docs",
    usageTrackingEnabled: true,
    metaAnalysisIntervalHours: 24,
    maxContextMessages: 20,
    systemPrompt: "",
  });

  const fetchModelCatalog = React.useCallback(async () => {
    try {
      const data = await apiFetch<{ models: AssistantModelCatalogEntry[] }>("/api/v1/assistant/models/catalog");
      setModelCatalog(data.models || []);
      setConnectionStatus("connected");
    } catch {
      setModelCatalog(DEFAULT_OLLAMA_MODELS.map((model) => ({ provider: "ollama", model, source: "fallback" })));
      setConnectionStatus("disconnected");
    }
  }, []);

  const loadConfig = React.useCallback(async () => {
    try {
      const data = await apiFetch<typeof config>("/api/v1/assistant/config");
      setConfig(prev => ({
        ...prev,
        ...data,
      }));
    } catch (error) {
      console.error("Failed to load config:", error);
    }
  }, []);

  React.useEffect(() => {
    fetchModelCatalog();
    loadConfig();
  }, [fetchModelCatalog, loadConfig]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await apiFetch("/api/v1/assistant/config", {
        method: "PUT",
        body: JSON.stringify(config),
      });
      toast.success("Assistant configuration saved");
      fetchModelCatalog();
    } catch {
      toast.error("Failed to save configuration");
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    try {
      const data = await apiFetch<{ message?: string }>("/api/v1/assistant/test");
      toast.success(data.message || "Assistant connection successful");
      setConnectionStatus("connected");
    } catch {
      toast.error("Assistant connection failed");
      setConnectionStatus("disconnected");
    } finally {
      setIsTestingConnection(false);
    }
  };

  const availableModels = React.useMemo(() => {
    const provider = config.provider || "ollama";
    const catalog = modelCatalog.filter((entry) => {
      if (provider === "ollama") {
        return entry.provider === "ollama" || entry.provider === "custom";
      }
      return entry.provider === provider;
    });
    const deduped = Array.from(new Set(catalog.map((entry) => entry.model).filter(Boolean)));
    if (provider === "ollama") {
      for (const fallback of DEFAULT_OLLAMA_MODELS) {
        if (!deduped.includes(fallback)) deduped.push(fallback);
      }
    }
    if (config.model && !deduped.includes(config.model)) {
      deduped.unshift(config.model);
    }
    return deduped;
  }, [config.model, config.provider, modelCatalog]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 text-white">
            <Bot className="size-6" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Framework Assistant</h1>
            <p className="text-muted-foreground">
              Configure the built-in AI assistant for coding help and framework guidance
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {connectionStatus && (
            <Badge variant={connectionStatus === "connected" ? "default" : "destructive"}>
              {connectionStatus === "connected" ? (
                <><CheckCircle className="size-3 mr-1" /> Connected</>
              ) : (
                <><XCircle className="size-3 mr-1" /> Disconnected</>
              )}
            </Badge>
          )}
          <Button variant="outline" onClick={handleTestConnection} disabled={isTestingConnection}>
            {isTestingConnection ? <Loader2 className="size-4 mr-2 animate-spin" /> : <RefreshCw className="size-4 mr-2" />}
            Test
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? <Loader2 className="size-4 mr-2 animate-spin" /> : <Save className="size-4 mr-2" />}
            Save
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Code className="size-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">Coding</p>
                <p className="text-xs text-muted-foreground">
                  {config.enableCodingHelper ? "Enabled" : "Disabled"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-500/10">
                <BookOpen className="size-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">Guide</p>
                <p className="text-xs text-muted-foreground">
                  {config.enableFrameworkGuide ? "Enabled" : "Disabled"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <Brain className="size-5 text-purple-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">Meta</p>
                <p className="text-xs text-muted-foreground">
                  {config.enableMetaAnalysis ? "Enabled" : "Disabled"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-orange-500/10">
                <Database className="size-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">RAG</p>
                <p className="text-xs text-muted-foreground">
                  {config.ragEnabled ? "Enabled" : "Disabled"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Configuration Tabs */}
      <Tabs defaultValue="general">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">
            <Settings2 className="size-4 mr-2" />
            General
          </TabsTrigger>
          <TabsTrigger value="features">
            <Sparkles className="size-4 mr-2" />
            Features
          </TabsTrigger>
          <TabsTrigger value="framework">
            <Bot className="size-4 mr-2" />
            Framework
          </TabsTrigger>
          <TabsTrigger value="advanced">
            <BarChart3 className="size-4 mr-2" />
            Advanced
          </TabsTrigger>
        </TabsList>

        {/* General Tab */}
        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Basic configuration for the Framework Assistant
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Enable Assistant</Label>
                  <p className="text-xs text-muted-foreground">
                    Turn the Framework Assistant on or off
                  </p>
                </div>
                <Switch
                  checked={config.enabled}
                  onCheckedChange={(checked) => setConfig({ ...config, enabled: checked })}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>LLM Provider</Label>
                <Select
                  value={config.provider || "ollama"}
                  onValueChange={(value) => setConfig({ ...config, provider: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {LLM_PROVIDERS.map((provider) => (
                      <SelectItem key={provider.id} value={provider.id}>
                        {provider.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>LLM Model</Label>
                <Select
                  value={config.model || ""}
                  onValueChange={(value) => setConfig({ ...config, model: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.length === 0 && (
                      <SelectItem value="__none" disabled>
                        No models discovered
                      </SelectItem>
                    )}
                    {availableModels.map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Model picker combines Ollama, custom registry, and Hugging Face cache entries.
                </p>
              </div>

              {(config.provider === "ollama" || config.provider === "openai_compatible") && (
                <div className="space-y-2">
                  <Label>Endpoint Override</Label>
                  <Input
                    placeholder={config.provider === "ollama" ? "http://localhost:11434" : "http://localhost:8000/v1"}
                    value={config.endpoint ?? ""}
                    onChange={(e) => setConfig({ ...config, endpoint: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Optional endpoint override for this assistant profile.
                  </p>
                </div>
              )}

              {config.provider === "openai_compatible" && (
                <>
                  <div className="space-y-2">
                    <Label>OpenAI-Compatible Base URL</Label>
                    <Input
                      placeholder="http://localhost:8000/v1"
                      value={config.openaiCompatibleBaseUrl ?? ""}
                      onChange={(e) => setConfig({ ...config, openaiCompatibleBaseUrl: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>API Key Environment Variable</Label>
                    <Input
                      placeholder="OPENAI_API_KEY"
                      value={config.openaiCompatibleApiKeyEnv ?? ""}
                      onChange={(e) => setConfig({ ...config, openaiCompatibleApiKeyEnv: e.target.value })}
                    />
                  </div>
                </>
              )}

              {config.provider === "huggingface_local" && (
                <>
                  <div className="space-y-2">
                    <Label>HF Execution Mode</Label>
                    <Select
                      value={config.hfExecutionMode || "hybrid"}
                      onValueChange={(value) => setConfig({ ...config, hfExecutionMode: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="local">local</SelectItem>
                        <SelectItem value="remote">remote</SelectItem>
                        <SelectItem value="hybrid">hybrid</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>HF Local Model Override</Label>
                    <Input
                      placeholder="meta-llama/Llama-3.2-3B-Instruct"
                      value={config.hfLocalModel ?? ""}
                      onChange={(e) => setConfig({ ...config, hfLocalModel: e.target.value })}
                    />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label>Custom System Prompt</Label>
                <Textarea
                  placeholder="Leave empty to use default system prompt..."
                  rows={4}
                  value={config.systemPrompt ?? ""}
                  onChange={(e) => setConfig({ ...config, systemPrompt: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Custom system prompt for the assistant. Leave empty for default.
                </p>
              </div>

              <div className="space-y-2">
                <Label>Max Context Messages</Label>
                <Input
                  type="number"
                  min={5}
                  max={50}
                  value={config.maxContextMessages}
                  onChange={(e) => setConfig({ ...config, maxContextMessages: parseInt(e.target.value) || 20 })}
                />
                <p className="text-xs text-muted-foreground">
                  Maximum messages to include in conversation context
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Features Tab */}
        <TabsContent value="features">
          <Card>
            <CardHeader>
              <CardTitle>Feature Toggles</CardTitle>
              <CardDescription>
                Enable or disable specific assistant features
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/10">
                    <Code className="size-5 text-blue-500" />
                  </div>
                  <div>
                    <Label>Coding Helper</Label>
                    <p className="text-xs text-muted-foreground">
                      Code generation, review, debugging, and refactoring
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.enableCodingHelper}
                  onCheckedChange={(checked) => setConfig({ ...config, enableCodingHelper: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-green-500/10">
                    <BookOpen className="size-5 text-green-500" />
                  </div>
                  <div>
                    <Label>Framework Guide</Label>
                    <p className="text-xs text-muted-foreground">
                      Help with framework features, configuration, and deployment
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.enableFrameworkGuide}
                  onCheckedChange={(checked) => setConfig({ ...config, enableFrameworkGuide: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-purple-500/10">
                    <Brain className="size-5 text-purple-500" />
                  </div>
                  <div>
                    <Label>Meta-Analysis</Label>
                    <p className="text-xs text-muted-foreground">
                      Analyze usage patterns and suggest framework improvements
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.enableMetaAnalysis}
                  onCheckedChange={(checked) => setConfig({ ...config, enableMetaAnalysis: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-orange-500/10">
                    <Database className="size-5 text-orange-500" />
                  </div>
                  <div>
                    <Label>RAG Integration</Label>
                    <p className="text-xs text-muted-foreground">
                      Use knowledge bases for context-aware responses
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.ragEnabled}
                  onCheckedChange={(checked) => setConfig({ ...config, ragEnabled: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-cyan-500/10">
                    <MessageSquare className="size-5 text-cyan-500" />
                  </div>
                  <div>
                    <Label>Persistent Memory</Label>
                    <p className="text-xs text-muted-foreground">
                      Remember conversation context across sessions
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.memoryEnabled}
                  onCheckedChange={(checked) => setConfig({ ...config, memoryEnabled: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-pink-500/10">
                    <BarChart3 className="size-5 text-pink-500" />
                  </div>
                  <div>
                    <Label>Usage Tracking</Label>
                    <p className="text-xs text-muted-foreground">
                      Track usage for analytics and meta-analysis
                    </p>
                  </div>
                </div>
                <Switch
                  checked={config.usageTrackingEnabled}
                  onCheckedChange={(checked) => setConfig({ ...config, usageTrackingEnabled: checked })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Framework Tab */}
        <TabsContent value="framework">
          <Card>
            <CardHeader>
              <CardTitle>Default Agent Framework</CardTitle>
              <CardDescription>
                Choose the default framework for the assistant to use
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {frameworks.map((fw) => (
                  <Card 
                    key={fw.id}
                    className={`cursor-pointer transition-all ${
                      config.defaultFramework === fw.id 
                        ? "border-primary bg-primary/5" 
                        : "hover:bg-muted/50"
                    }`}
                    onClick={() => setConfig({ ...config, defaultFramework: fw.id })}
                  >
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{fw.name}</p>
                          <p className="text-xs text-muted-foreground">{fw.description}</p>
                        </div>
                        {config.defaultFramework === fw.id && (
                          <CheckCircle className="size-5 text-primary" />
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Knowledge bases and meta-analysis configuration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Code Knowledge Base Project ID</Label>
                <Input
                  placeholder="Leave empty to disable code KB"
                  value={config.codeKbProjectId ?? ""}
                  onChange={(e) => setConfig({ ...config, codeKbProjectId: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Project ID to use for code context in RAG
                </p>
              </div>

              <div className="space-y-2">
                <Label>Documentation Knowledge Base Name</Label>
                <Input
                  value={config.docsKbName ?? ""}
                  onChange={(e) => setConfig({ ...config, docsKbName: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Knowledge base name for framework documentation
                </p>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Meta-Analysis Interval (hours)</Label>
                <Input
                  type="number"
                  min={1}
                  max={168}
                  value={config.metaAnalysisIntervalHours}
                  onChange={(e) => setConfig({ ...config, metaAnalysisIntervalHours: parseInt(e.target.value) || 24 })}
                />
                <p className="text-xs text-muted-foreground">
                  How often to run automatic meta-analysis (1-168 hours)
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
