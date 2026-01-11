# Chunk: ebf57e9ab38c_0

- source: `webui/src/app/library/page.tsx`
- lines: 1-79
- chunk: 1/4

```
"use client";

import * as React from "react";
import Link from "next/link";
import { Plus, Search, Puzzle, MoreHorizontal, Copy, Pencil, Trash2, Code } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useComponents } from "@/lib/api";
import type { Component } from "@/lib/types";
import { toast } from "sonner";

const categoryColors: Record<string, string> = {
  tool: "bg-blue-500/10 text-blue-500",
  agent: "bg-violet-500/10 text-violet-500",
  task: "bg-emerald-500/10 text-emerald-500",
  pattern: "bg-orange-500/10 text-orange-500",
  utility: "bg-gray-500/10 text-gray-500",
  template: "bg-pink-500/10 text-pink-500",
};

const categoryIcons: Record<string, string> = {
  tool: "🔧",
  agent: "🤖",
  task: "📋",
  pattern: "🧩",
  utility: "⚙️",
  template: "📄",
};

function ComponentCard({ component, onDelete }: { component: Component; onDelete: () => void }) {
  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(component.code);
    toast.success("Code copied to clipboard");
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 text-white text-lg">
              {categoryIcons[component.category] || "📦"}
            </div>
            <div>
              <CardTitle className="text-lg">
                <Link href={`/library/${component.id}`} className="hover:underline">
                  {component.name}
                </Link>
              </CardTitle>
              <CardDescription className="line-clamp-1">
                {component.description || "No description"}
              </CardDescription>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/library/${component.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
```
