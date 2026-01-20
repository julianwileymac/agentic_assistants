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

export default function AssistantPage() {
  const [isSaving, setIsSaving] = React.useState(false);
  const [isTestingConnection, setIsTestingConnection] = React.useState(false);
  const [connectionStatus, setConnectionStatus] = React.useState<"connected" | "disconnected" | null>(null);
  const [ollamaModels, setOllamaModels] = React.useState<string[]>([]);

  const [config, setConfig] = React.useState({
    enabled: true,
    defaultFramework: "crewai",
    model: "llama3.2",
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

  // Fetch Ollama models on mount
  React.useEffect(() => {
    fetchOllamaModels();
    loadConfig();
  }, []);

  const fetchOllamaModels = async () => {
    try {
      const response = await fetch("http://localhost:8080/api/v1/ollama/models");
      if (response.ok) {
        const data = await response.json();
        const deployedModels = data.models?.map((m: any) => m.name) || [];
        // Merge deployed models with defaults, avoiding duplicates
        // Deployed models come first, then defaults that aren't already in deployed
        const allModels = [
          ...deployedModels,
          ...DEFAULT_OLLAMA_MODELS.filter(m => !deployedModels.includes(m)),
        ];
        setOllamaModels(allModels);
        setConnectionStatus("connected");
      } else {
        // Use defaults when connection fails
        setOllamaModels(DEFAULT_OLLAMA_MODELS);
        setConnectionStatus("disconnected");
      }
    } catch (error) {
      // Use defaults when connection fails
      setOllamaModels(DEFAULT_OLLAMA_MODELS);
      setConnectionStatus("disconnected");
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch("http://localhost:8080/api/v1/assistant/config");
      if (response.ok) {
        const data = await response.json();
        setConfig(prev => ({
          ...prev,
          ...data,
        }));
      }
    } catch (error) {
      console.error("Failed to load config:", error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("http://localhost:8080/api/v1/assistant/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        toast.success("Assistant configuration saved");
      } else {
        toast.error("Failed to save configuration");
      }
    } catch (error) {
      toast.error("Failed to save configuration");
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    try {
      const response = await fetch("http://localhost:8080/api/v1/assistant/test");
      if (response.ok) {
        toast.success("Assistant connection successful");
        setConnectionStatus("connected");
      } else {
        toast.error("Assistant connection failed");
        setConnectionStatus("disconnected");
      }
    } catch (error) {
      toast.error("Assistant connection failed");
      setConnectionStatus("disconnected");
    } finally {
      setIsTestingConnection(false);
    }
  };

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
                <Label>LLM Model</Label>
                <Select
                  value={config.model || "llama3.2"}
                  onValueChange={(value) => setConfig({ ...config, model: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {/* Ensure current model is always available, even if not in list */}
                    {config.model && !ollamaModels.includes(config.model) && (
                      <SelectItem key={config.model} value={config.model}>
                        {config.model} (current)
                      </SelectItem>
                    )}
                    {ollamaModels.map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  The LLM model used by the assistant. Deployed models are listed first.
                </p>
              </div>

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
