"use client";

import * as React from "react";
import { FlaskConical, FolderOpen, BarChart3, Terminal } from "lucide-react";

import { TestingPanel } from "@/components/testing/testing-panel";
import { TerminalPanel } from "@/components/testing/terminal-panel";
import { TestSuiteManager } from "@/components/testing/test-suite-manager";
import { TestResultsDashboard } from "@/components/testing/test-results-dashboard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type TestingSectionProps = {
  resourceType?: string;
  resourceId?: string;
  resourceName?: string;
  defaultLanguage?: string;
  defaultCode?: string;
};

export function TestingSection(props: TestingSectionProps) {
  return (
    <Tabs defaultValue="sandbox" className="w-full">
      <TabsList className="w-full justify-start">
        <TabsTrigger value="sandbox" className="gap-1.5">
          <FlaskConical className="size-3.5" />
          Sandbox
        </TabsTrigger>
        <TabsTrigger value="suites" className="gap-1.5">
          <FolderOpen className="size-3.5" />
          Test Suites
        </TabsTrigger>
        <TabsTrigger value="results" className="gap-1.5">
          <BarChart3 className="size-3.5" />
          Results
        </TabsTrigger>
        <TabsTrigger value="terminal" className="gap-1.5">
          <Terminal className="size-3.5" />
          Terminal
        </TabsTrigger>
      </TabsList>

      <TabsContent value="sandbox" className="mt-4">
        <TestingPanel {...props} />
      </TabsContent>

      <TabsContent value="suites" className="mt-4">
        <TestSuiteManager />
      </TabsContent>

      <TabsContent value="results" className="mt-4">
        <TestResultsDashboard />
      </TabsContent>

      <TabsContent value="terminal" className="mt-4">
        <div className="h-[600px]">
          <TerminalPanel />
        </div>
      </TabsContent>
    </Tabs>
  );
}
