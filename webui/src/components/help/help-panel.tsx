"use client";

import * as React from "react";
import { LifeBuoy, X } from "lucide-react";

import { useHelpStore } from "@/lib/store";
import { useIsMobile } from "@/hooks/use-mobile";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { DocsBrowser } from "./docs-browser";
import { AssistantChat } from "./assistant-chat";

const PANEL_WIDTH = 380;

export function HelpPanel({ projectId }: { projectId?: string }) {
  const { isOpen, toggle, activeTab, setTab } = useHelpStore();
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Sheet open={isOpen} onOpenChange={toggle}>
        <SheetContent side="right" className="w-[95vw] max-w-xl">
          <SheetHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-md bg-gradient-to-br from-violet-500 to-purple-600 text-white">
                  <LifeBuoy className="size-4" />
                </div>
                <SheetTitle>Help & Docs</SheetTitle>
              </div>
            </div>
          </SheetHeader>
          <div className="mt-4">
            <HelpTabs activeTab={activeTab} onTabChange={setTab} projectId={projectId} />
          </div>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <aside
      className={`fixed right-0 top-14 bottom-0 z-20 transition-transform duration-200 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
      style={{ width: PANEL_WIDTH }}
    >
      <div className="h-full border-l bg-background shadow-lg flex flex-col">
        <div className="flex items-center justify-between px-3 py-2 border-b">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-md bg-gradient-to-br from-violet-500 to-purple-600 text-white">
              <LifeBuoy className="size-4" />
            </div>
            <div>
              <p className="text-sm font-semibold">Help & Docs</p>
              <p className="text-xs text-muted-foreground">Framework guidance & local LLM</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={toggle}>
            <X className="size-4" />
          </Button>
        </div>
        <div className="p-3 flex-1 overflow-hidden">
          <HelpTabs activeTab={activeTab} onTabChange={setTab} projectId={projectId} />
        </div>
      </div>
    </aside>
  );
}

type HelpTabsProps = {
  activeTab: "docs" | "assistant";
  onTabChange: (tab: "docs" | "assistant") => void;
  projectId?: string;
};

function HelpTabs({ activeTab, onTabChange, projectId }: HelpTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={(val) => onTabChange(val as "docs" | "assistant")} className="h-full flex flex-col">
      <TabsList className="grid grid-cols-2 mb-3">
        <TabsTrigger value="docs">Docs</TabsTrigger>
        <TabsTrigger value="assistant">Assistant</TabsTrigger>
      </TabsList>
      <TabsContent value="docs" className="flex-1">
        <DocsBrowser />
      </TabsContent>
      <TabsContent value="assistant" className="flex-1">
        <AssistantChat projectId={projectId} />
      </TabsContent>
    </Tabs>
  );
}

