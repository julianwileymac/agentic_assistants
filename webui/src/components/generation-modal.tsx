"use client";

import * as React from "react";
import { 
  Sparkles, 
  Loader2, 
  Copy, 
  Check, 
  MessageSquare,
  Code2,
  FileCode,
  Wand2,
  ChevronRight,
  Send,
  RefreshCw,
  Save,
  X,
  Maximize2,
  Minimize2,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  useGeneratePrompt, 
  useGenerateComponent,
  useGenerateFromNotes,
  useGenerationChat,
  useCreateComponent,
} from "@/lib/api";
import type { ComponentCategory, GeneratedComponent, GenerationChatMessage } from "@/lib/types";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface GenerationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialNotes?: string;
  initialComponentType?: ComponentCategory;
  onComponentGenerated?: (component: GeneratedComponent) => void;
}

const componentCategories: { value: ComponentCategory; label: string; description: string }[] = [
  { value: "tool", label: "Tool", description: "Agent tools and utilities" },
  { value: "agent", label: "Agent", description: "AI agent configurations" },
  { value: "task", label: "Task", description: "Task definitions" },
  { value: "pattern", label: "Pattern", description: "Design patterns" },
  { value: "utility", label: "Utility", description: "Helper functions" },
  { value: "template", label: "Template", description: "Code templates" },
  { value: "datasource_handler", label: "Data Source Handler", description: "Database/API connectors" },
  { value: "embedding_model", label: "Embedding Model", description: "Embedding configurations" },
  { value: "prompt_template", label: "Prompt Template", description: "LLM prompts" },
  { value: "workflow_node", label: "Workflow Node", description: "Flow components" },
  { value: "retrieval_strategy", label: "Retrieval Strategy", description: "RAG strategies" },
  { value: "llm_wrapper", label: "LLM Wrapper", description: "LLM integrations" },
  { value: "crew_config", label: "Crew Config", description: "CrewAI configurations" },
];

function ChatMessage({ message, isUser }: { message: GenerationChatMessage; isUser: boolean }) {
  return (
    <div className={cn(
      "flex gap-3 p-3 rounded-lg",
      isUser ? "bg-primary/10 ml-8" : "bg-muted/50 mr-8"
    )}>
      <div className={cn(
        "size-8 rounded-full flex items-center justify-center shrink-0",
        isUser ? "bg-primary text-primary-foreground" : "bg-gradient-to-br from-purple-500 to-pink-500 text-white"
      )}>
        {isUser ? "U" : <Sparkles className="size-4" />}
      </div>
      <div className="flex-1 space-y-2">
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}

function CodePreview({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative rounded-lg overflow-hidden border bg-zinc-950">
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <FileCode className="size-4 text-zinc-400" />
          <span className="text-sm text-zinc-400">{language}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="text-zinc-400 hover:text-white"
        >
          {copied ? (
            <>
              <Check className="size-4 mr-1" />
              Copied
            </>
          ) : (
            <>
              <Copy className="size-4 mr-1" />
              Copy
            </>
          )}
        </Button>
      </div>
      <ScrollArea className="max-h-[400px]">
        <pre className="p-4 text-sm">
          <code className="text-zinc-200">{code}</code>
        </pre>
      </ScrollArea>
    </div>
  );
}

export function GenerationModal({
  open,
  onOpenChange,
  initialNotes = "",
  initialComponentType = "utility",
  onComponentGenerated,
}: GenerationModalProps) {
  const [mode, setMode] = React.useState<"simple" | "chat">("simple");
  const [isExpanded, setIsExpanded] = React.useState(false);
  
  // Simple mode state
  const [notes, setNotes] = React.useState(initialNotes);
  const [componentType, setComponentType] = React.useState<ComponentCategory>(initialComponentType);
  const [componentName, setComponentName] = React.useState("");
  const [language, setLanguage] = React.useState("python");
  const [optimizedPrompt, setOptimizedPrompt] = React.useState<string | null>(null);
  const [generatedComponent, setGeneratedComponent] = React.useState<GeneratedComponent | null>(null);
  
  // Chat mode state
  const [chatMessages, setChatMessages] = React.useState<GenerationChatMessage[]>([]);
  const [chatInput, setChatInput] = React.useState("");
  const [componentPreview, setComponentPreview] = React.useState<GeneratedComponent | null>(null);
  
  // API hooks
  const { trigger: generatePrompt, isMutating: isGeneratingPrompt } = useGeneratePrompt();
  const { trigger: generateComponent, isMutating: isGeneratingComponent } = useGenerateComponent();
  const { trigger: generateFromNotes, isMutating: isGeneratingFromNotes } = useGenerateFromNotes();
  const { trigger: sendChatMessage, isMutating: isChatLoading } = useGenerationChat();
  const { trigger: createComponent, isMutating: isSaving } = useCreateComponent();
  
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (initialNotes) {
      setNotes(initialNotes);
    }
  }, [initialNotes]);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleReset = () => {
    setNotes("");
    setComponentName("");
    setOptimizedPrompt(null);
    setGeneratedComponent(null);
    setChatMessages([]);
    setChatInput("");
    setComponentPreview(null);
  };

  const handleGeneratePrompt = async () => {
    if (!notes.trim()) {
      toast.error("Please enter your notes first");
      return;
    }

    try {
      const result = await generatePrompt({
        notes: notes.trim(),
        component_type: componentType,
      });
      
      setOptimizedPrompt(result.optimized_prompt);
      toast.success("Prompt optimized!");
    } catch (error) {
      toast.error("Failed to generate prompt");
    }
  };

  const handleGenerateComponent = async () => {
    const promptToUse = optimizedPrompt || notes;
    if (!promptToUse.trim()) {
      toast.error("Please enter notes or generate a prompt first");
      return;
    }

    try {
      const result = await generateComponent({
        prompt: promptToUse.trim(),
        component_type: componentType,
        name: componentName || undefined,
        language,
      });
      
      setGeneratedComponent(result);
      onComponentGenerated?.(result);
      toast.success("Component generated!");
    } catch (error) {
      toast.error("Failed to generate component");
    }
  };

  const handleQuickGenerate = async () => {
    if (!notes.trim()) {
      toast.error("Please enter your notes first");
      return;
    }

    try {
      const result = await generateFromNotes({
        notes: notes.trim(),
        component_type: componentType,
        name: componentName || undefined,
        language,
        save_component: false,
      });
      
      setOptimizedPrompt(result.optimized_prompt);
      setGeneratedComponent(result.component);
      onComponentGenerated?.(result.component);
      toast.success("Component generated!");
    } catch (error) {
      toast.error("Failed to generate component");
    }
  };

  const handleSendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage: GenerationChatMessage = {
      role: "user",
      content: chatInput.trim(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput("");

    try {
      const result = await sendChatMessage({
        messages: [...chatMessages, userMessage],
        component_type: componentType,
      });
      
      setChatMessages(prev => [...prev, result.message]);
      
      if (result.component_preview) {
        setComponentPreview(result.component_preview);
      }
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  const handleSaveComponent = async () => {
    const componentToSave = generatedComponent || componentPreview;
    if (!componentToSave) {
      toast.error("No component to save");
      return;
    }

    try {
      await createComponent({
        name: componentToSave.name,
        category: componentToSave.category,
        code: componentToSave.code,
        description: componentToSave.description,
        usage_example: componentToSave.usage_example,
        language: componentToSave.language,
        tags: componentToSave.tags,
      });
      
      toast.success("Component saved to library!");
      onOpenChange(false);
    } catch (error) {
      toast.error("Failed to save component");
    }
  };

  const isGenerating = isGeneratingPrompt || isGeneratingComponent || isGeneratingFromNotes || isChatLoading;
  const hasGeneratedContent = generatedComponent || componentPreview;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={cn(
        "transition-all duration-300",
        isExpanded ? "max-w-[90vw] h-[90vh]" : "max-w-3xl max-h-[85vh]"
      )}>
        <DialogHeader className="space-y-1 pb-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 text-white">
                <Sparkles className="size-5" />
              </div>
              <div>
                <DialogTitle className="text-xl">AI Component Generator</DialogTitle>
                <DialogDescription>
                  Transform your notes into reusable code components
                </DialogDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? <Minimize2 className="size-4" /> : <Maximize2 className="size-4" />}
              </Button>
            </div>
          </div>
        </DialogHeader>

        <Tabs value={mode} onValueChange={(v) => setMode(v as "simple" | "chat")} className="flex-1">
          <TabsList className="grid grid-cols-2 w-[300px] mx-auto">
            <TabsTrigger value="simple" className="gap-2">
              <Wand2 className="size-4" />
              Quick Generate
            </TabsTrigger>
            <TabsTrigger value="chat" className="gap-2">
              <MessageSquare className="size-4" />
              Chat Mode
            </TabsTrigger>
          </TabsList>

          {/* Simple Mode */}
          <TabsContent value="simple" className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Input Section */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Your Notes</Label>
                  <Textarea
                    placeholder="Describe what you want to build...&#10;&#10;Example: I need a tool that can fetch weather data from an API and parse it into a structured format. It should handle errors gracefully and cache results."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={6}
                    className="resize-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label>Component Type</Label>
                    <Select value={componentType} onValueChange={(v) => setComponentType(v as ComponentCategory)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {componentCategories.map((cat) => (
                          <SelectItem key={cat.value} value={cat.value}>
                            <div className="flex flex-col">
                              <span>{cat.label}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="python">Python</SelectItem>
                        <SelectItem value="typescript">TypeScript</SelectItem>
                        <SelectItem value="javascript">JavaScript</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Component Name (optional)</Label>
                  <Input
                    placeholder="Auto-generated if empty"
                    value={componentName}
                    onChange={(e) => setComponentName(e.target.value)}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    className="flex-1"
                    onClick={handleQuickGenerate}
                    disabled={isGenerating || !notes.trim()}
                  >
                    {isGeneratingFromNotes ? (
                      <>
                        <Loader2 className="size-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-4 mr-2" />
                        Generate Component
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleGeneratePrompt}
                    disabled={isGenerating || !notes.trim()}
                  >
                    {isGeneratingPrompt ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Wand2 className="size-4" />
                    )}
                  </Button>
                </div>

                {optimizedPrompt && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-muted-foreground">Optimized Prompt</Label>
                      <Badge variant="secondary">AI Enhanced</Badge>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50 border text-sm max-h-[150px] overflow-auto">
                      {optimizedPrompt}
                    </div>
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={handleGenerateComponent}
                      disabled={isGenerating}
                    >
                      {isGeneratingComponent ? (
                        <>
                          <Loader2 className="size-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <ChevronRight className="size-4 mr-2" />
                          Use This Prompt
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Output Section */}
              <div className="space-y-4">
                {generatedComponent ? (
                  <>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Code2 className="size-4" />
                        <span className="font-medium">{generatedComponent.name}</span>
                        <Badge variant="outline">{generatedComponent.category}</Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={handleReset}>
                          <RefreshCw className="size-4 mr-1" />
                          Reset
                        </Button>
                        <Button size="sm" onClick={handleSaveComponent} disabled={isSaving}>
                          {isSaving ? (
                            <Loader2 className="size-4 mr-1 animate-spin" />
                          ) : (
                            <Save className="size-4 mr-1" />
                          )}
                          Save to Library
                        </Button>
                      </div>
                    </div>
                    <CodePreview code={generatedComponent.code} language={generatedComponent.language} />
                    {generatedComponent.usage_example && (
                      <div className="space-y-2">
                        <Label className="text-muted-foreground">Usage Example</Label>
                        <CodePreview code={generatedComponent.usage_example} language={generatedComponent.language} />
                      </div>
                    )}
                  </>
                ) : (
                  <div className="h-full flex items-center justify-center text-muted-foreground border rounded-lg border-dashed">
                    <div className="text-center p-8">
                      <Code2 className="size-12 mx-auto mb-4 opacity-30" />
                      <p>Generated code will appear here</p>
                      <p className="text-sm mt-1">Enter your notes and click Generate</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Chat Mode */}
          <TabsContent value="chat" className="mt-4 flex flex-col h-[500px]">
            <div className="grid grid-cols-2 gap-4 flex-1 min-h-0">
              {/* Chat Section */}
              <div className="flex flex-col border rounded-lg overflow-hidden">
                <div className="p-3 border-b bg-muted/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="size-4" />
                      <span className="font-medium">Conversation</span>
                    </div>
                    <Select value={componentType} onValueChange={(v) => setComponentType(v as ComponentCategory)}>
                      <SelectTrigger className="w-[150px] h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {componentCategories.map((cat) => (
                          <SelectItem key={cat.value} value={cat.value}>
                            {cat.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <ScrollArea className="flex-1 p-4">
                  {chatMessages.length === 0 ? (
                    <div className="text-center text-muted-foreground py-8">
                      <MessageSquare className="size-8 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">Start a conversation to build your component</p>
                      <p className="text-xs mt-1">Describe what you need, and I&apos;ll help you create it</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {chatMessages.map((msg, i) => (
                        <ChatMessage key={i} message={msg} isUser={msg.role === "user"} />
                      ))}
                      {isChatLoading && (
                        <div className="flex gap-3 p-3 rounded-lg bg-muted/50 mr-8">
                          <div className="size-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center">
                            <Sparkles className="size-4" />
                          </div>
                          <div className="flex items-center gap-2">
                            <Loader2 className="size-4 animate-spin" />
                            <span className="text-sm text-muted-foreground">Thinking...</span>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </ScrollArea>

                <div className="p-3 border-t bg-muted/30">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Describe what you want to build..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendChatMessage();
                        }
                      }}
                      disabled={isChatLoading}
                    />
                    <Button onClick={handleSendChatMessage} disabled={isChatLoading || !chatInput.trim()}>
                      <Send className="size-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Preview Section */}
              <div className="flex flex-col border rounded-lg overflow-hidden">
                <div className="p-3 border-b bg-muted/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Code2 className="size-4" />
                      <span className="font-medium">Component Preview</span>
                    </div>
                    {componentPreview && (
                      <Button size="sm" onClick={handleSaveComponent} disabled={isSaving}>
                        {isSaving ? (
                          <Loader2 className="size-4 mr-1 animate-spin" />
                        ) : (
                          <Save className="size-4 mr-1" />
                        )}
                        Save
                      </Button>
                    )}
                  </div>
                </div>
                
                <ScrollArea className="flex-1">
                  {componentPreview ? (
                    <div className="p-4 space-y-4">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{componentPreview.category}</Badge>
                        <span className="text-sm font-medium">{componentPreview.name}</span>
                      </div>
                      <CodePreview code={componentPreview.code} language={componentPreview.language} />
                    </div>
                  ) : (
                    <div className="h-full flex items-center justify-center text-muted-foreground p-8">
                      <div className="text-center">
                        <FileCode className="size-12 mx-auto mb-4 opacity-30" />
                        <p className="text-sm">Component preview will appear here</p>
                        <p className="text-xs mt-1">As you chat, I&apos;ll generate code</p>
                      </div>
                    </div>
                  )}
                </ScrollArea>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

// Export a hook for easy integration with notes
export function useGenerationModal() {
  const [open, setOpen] = React.useState(false);
  const [initialNotes, setInitialNotes] = React.useState("");
  const [initialType, setInitialType] = React.useState<ComponentCategory>("utility");

  const openWithNotes = (notes: string, componentType: ComponentCategory = "utility") => {
    setInitialNotes(notes);
    setInitialType(componentType);
    setOpen(true);
  };

  const close = () => {
    setOpen(false);
    setInitialNotes("");
    setInitialType("utility");
  };

  return {
    open,
    setOpen,
    openWithNotes,
    close,
    initialNotes,
    initialType,
  };
}



