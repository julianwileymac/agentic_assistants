"use client";

import * as React from "react";

import { TestingPanel } from "@/components/testing/testing-panel";
import { TerminalPanel } from "@/components/testing/terminal-panel";

type TestingSectionProps = {
  resourceType?: string;
  resourceId?: string;
  resourceName?: string;
  defaultLanguage?: string;
  defaultCode?: string;
};

export function TestingSection(props: TestingSectionProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <TestingPanel {...props} />
      <TerminalPanel />
    </div>
  );
}
