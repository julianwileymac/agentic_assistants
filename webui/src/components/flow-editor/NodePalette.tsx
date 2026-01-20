"use client";

import * as React from "react";
import {
  Play,
  Square,
  GitBranch,
  Repeat,
  GitMerge,
  Search,
  ArrowUpDown,
  Binary,
  Database,
  Brain,
  FileText,
  MessageSquare,
  Scale,
  CheckCircle,
  Target,
  User,
  ShieldCheck,
  ThumbsUp,
  Wrench,
  Globe,
  Code,
  Download,
  Upload,
  Shuffle,
  Workflow,
  ChevronDown,
  ChevronRight,
  GripVertical,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import { nodeCategories, type NodeDefinition } from "./nodes";

// Icon mapping
const iconMap: Record<string, React.ReactNode> = {
  Play: <Play className="size-4" />,
  Square: <Square className="size-4" />,
  GitBranch: <GitBranch className="size-4" />,
  Repeat: <Repeat className="size-4" />,
  GitMerge: <GitMerge className="size-4" />,
  Search: <Search className="size-4" />,
  ArrowUpDown: <ArrowUpDown className="size-4" />,
  Binary: <Binary className="size-4" />,
  Database: <Database className="size-4" />,
  Brain: <Brain className="size-4" />,
  FileText: <FileText className="size-4" />,
  MessageSquare: <MessageSquare className="size-4" />,
  Scale: <Scale className="size-4" />,
  CheckCircle: <CheckCircle className="size-4" />,
  Target: <Target className="size-4" />,
  User: <User className="size-4" />,
  ShieldCheck: <ShieldCheck className="size-4" />,
  ThumbsUp: <ThumbsUp className="size-4" />,
  Wrench: <Wrench className="size-4" />,
  Globe: <Globe className="size-4" />,
  Code: <Code className="size-4" />,
  Download: <Download className="size-4" />,
  Upload: <Upload className="size-4" />,
  Shuffle: <Shuffle className="size-4" />,
  Workflow: <Workflow className="size-4" />,
};

interface DraggableNodeProps {
  node: NodeDefinition;
  color: string;
}

function DraggableNode({ node, color }: DraggableNodeProps) {
  const onDragStart = (event: React.DragEvent) => {
    event.dataTransfer.setData("application/reactflow/type", node.type);
    event.dataTransfer.setData("application/reactflow/label", node.label);
    event.dataTransfer.setData("application/reactflow/nodeType", node.type.replace("Node", ""));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div
      draggable
      onDragStart={onDragStart}
      className="group flex items-center gap-2 p-2 rounded-md border bg-card hover:bg-accent cursor-grab active:cursor-grabbing transition-colors"
    >
      <div className={cn("p-1.5 rounded text-white bg-gradient-to-br", color)}>
        {iconMap[node.icon] || <Workflow className="size-4" />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{node.label}</p>
        <p className="text-xs text-muted-foreground truncate">{node.description}</p>
      </div>
      <GripVertical className="size-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  );
}

export function NodePalette() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [expandedCategories, setExpandedCategories] = React.useState<Set<string>>(
    new Set(nodeCategories.map((c) => c.id))
  );

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(categoryId)) {
        next.delete(categoryId);
      } else {
        next.add(categoryId);
      }
      return next;
    });
  };

  // Filter nodes based on search
  const filteredCategories = React.useMemo(() => {
    if (!searchQuery.trim()) return nodeCategories;

    const query = searchQuery.toLowerCase();
    return nodeCategories
      .map((category) => ({
        ...category,
        nodes: category.nodes.filter(
          (node) =>
            node.label.toLowerCase().includes(query) ||
            node.description.toLowerCase().includes(query)
        ),
      }))
      .filter((category) => category.nodes.length > 0);
  }, [searchQuery]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b">
        <h3 className="font-semibold text-sm mb-2">Node Palette</h3>
        <Input
          placeholder="Search nodes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="h-8 text-sm"
        />
      </div>

      {/* Node Categories */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredCategories.map((category) => (
            <Collapsible
              key={category.id}
              open={expandedCategories.has(category.id)}
              onOpenChange={() => toggleCategory(category.id)}
            >
              <CollapsibleTrigger className="flex items-center justify-between w-full p-2 rounded-md hover:bg-accent text-sm font-medium">
                <div className="flex items-center gap-2">
                  <div
                    className={cn(
                      "w-2 h-2 rounded-full bg-gradient-to-br",
                      category.color
                    )}
                  />
                  <span>{category.name}</span>
                  <span className="text-xs text-muted-foreground">
                    ({category.nodes.length})
                  </span>
                </div>
                {expandedCategories.has(category.id) ? (
                  <ChevronDown className="size-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="size-4 text-muted-foreground" />
                )}
              </CollapsibleTrigger>
              <CollapsibleContent className="pl-4 space-y-1 mt-1">
                {category.nodes.map((node) => (
                  <DraggableNode key={node.type} node={node} color={category.color} />
                ))}
              </CollapsibleContent>
            </Collapsible>
          ))}

          {filteredCategories.length === 0 && (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No nodes found matching &quot;{searchQuery}&quot;
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer with instructions */}
      <div className="p-3 border-t bg-muted/30">
        <p className="text-xs text-muted-foreground">
          Drag nodes onto the canvas to add them to your flow.
        </p>
      </div>
    </div>
  );
}

export default NodePalette;
