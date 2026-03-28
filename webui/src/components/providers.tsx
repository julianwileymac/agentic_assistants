"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";
import { ErrorBoundary, ErrorStoreProvider } from "@/components/error-display";
import { CopilotProvider } from "@/components/copilot/CopilotProvider";
import { initTelemetry } from "@/lib/telemetry";

export function Providers({ children }: { children: React.ReactNode }) {
  React.useEffect(() => {
    if (typeof window === "undefined") return;
    if (localStorage.getItem("otel_disabled") === "true") return;
    const otelEndpoint = localStorage.getItem("otel_collector_url") || undefined;
    void initTelemetry(otelEndpoint);
  }, []);

  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <CopilotProvider>
        <ErrorStoreProvider>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </ErrorStoreProvider>
      </CopilotProvider>
      <Toaster richColors position="top-right" closeButton />
    </NextThemesProvider>
  );
}

