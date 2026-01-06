"use client";

import * as React from "react";
import { Save, Settings, Server, Key, Database, Zap, Loader2 } from "lucide-react";

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
import { toast } from "sonner";

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
  });

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
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="connections">
            <Server className="size-4 mr-2" />
            Connections
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

