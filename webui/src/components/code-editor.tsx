"use client";

import dynamic from "next/dynamic";
import * as React from "react";

import { cn } from "@/lib/utils";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

type CodeEditorProps = {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: number | string;
  readOnly?: boolean;
  className?: string;
};

export function CodeEditor({
  value,
  onChange,
  language = "python",
  height = 260,
  readOnly = false,
  className,
}: CodeEditorProps) {
  return (
    <div className={cn("rounded-md border bg-background", className)}>
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        theme="vs-dark"
        onChange={(val) => onChange(val ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 12,
          lineNumbers: "on",
          wordWrap: "on",
          scrollBeyondLastLine: false,
          readOnly,
        }}
      />
    </div>
  );
}
