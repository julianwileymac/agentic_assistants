"use client";

import * as React from "react";
import { Brain, Database, Cpu } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useWizard } from "../wizard-context";

const LLM_MODELS = [
  { value: "llama3.2", label: "Llama 3.2 (Default)", description: "Meta's latest open model" },
  { value: "llama3.1", label: "Llama 3.1", description: "Previous generation" },
  { value: "mistral", label: "Mistral 7B", description: "Fast and efficient" },
  { value: "codellama", label: "Code Llama", description: "Optimized for code" },
  { value: "gemma2", label: "Gemma 2", description: "Google's open model" },
  { value: "phi3", label: "Phi-3", description: "Microsoft's compact model" },
];

const EMBEDDING_MODELS = [
  { value: "nomic-embed-text", label: "Nomic Embed Text (Default)", description: "768 dimensions" },
  { value: "mxbai-embed-large", label: "mxbai Embed Large", description: "1024 dimensions" },
  { value: "all-minilm", label: "all-MiniLM-L6-v2", description: "384 dimensions, fast" },
];

const VECTOR_BACKENDS = [
  { value: "chroma", label: "ChromaDB (Default)", description: "Simple embedded vector store" },
  { value: "lancedb", label: "LanceDB", description: "Fast columnar storage" },
];

export function ConfigurationStep() {
  const { formData, updateFormData } = useWizard();

  const handleLlmModelChange = (value: string) => {
    updateFormData({ llmModel: value });
  };

  const handleEmbeddingModelChange = (value: string) => {
    updateFormData({ embeddingModel: value });
  };

  const handleVectorDbBackendChange = (value: string) => {
    updateFormData({ vectorDbBackend: value });
  };

  const handleVectorDbPathChange = (path: string) => {
    updateFormData({ vectorDbPath: path });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Configuration</h2>
        <p className="text-muted-foreground mt-1">
          Configure AI models and storage for your project
        </p>
      </div>

      {/* LLM Model */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Brain className="size-5" />
            Language Model
          </CardTitle>
          <CardDescription>
            Select the default LLM for your agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="llm-model">Model</Label>
            <Select value={formData.llmModel} onValueChange={handleLlmModelChange}>
              <SelectTrigger id="llm-model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS.map((model) => (
                  <SelectItem key={model.value} value={model.value}>
                    <div className="flex flex-col">
                      <span>{model.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {model.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Requires Ollama with the selected model installed
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Embedding Model */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Cpu className="size-5" />
            Embedding Model
          </CardTitle>
          <CardDescription>
            Select the model for text embeddings and vector search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="embedding-model">Model</Label>
            <Select value={formData.embeddingModel} onValueChange={handleEmbeddingModelChange}>
              <SelectTrigger id="embedding-model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {EMBEDDING_MODELS.map((model) => (
                  <SelectItem key={model.value} value={model.value}>
                    <div className="flex flex-col">
                      <span>{model.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {model.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Vector Database */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Database className="size-5" />
            Vector Database
          </CardTitle>
          <CardDescription>
            Configure vector storage for semantic search
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="vector-backend">Backend</Label>
            <Select value={formData.vectorDbBackend} onValueChange={handleVectorDbBackendChange}>
              <SelectTrigger id="vector-backend">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {VECTOR_BACKENDS.map((backend) => (
                  <SelectItem key={backend.value} value={backend.value}>
                    <div className="flex flex-col">
                      <span>{backend.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {backend.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="vector-path">Storage Path</Label>
            <Input
              id="vector-path"
              value={formData.vectorDbPath}
              onChange={(e) => handleVectorDbPathChange(e.target.value)}
              placeholder="./data/vectors"
            />
            <p className="text-xs text-muted-foreground">
              Relative path for vector database storage
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
