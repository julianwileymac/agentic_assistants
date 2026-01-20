"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";
import { ErrorBoundary, ErrorStoreProvider } from "@/components/error-display";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <ErrorStoreProvider>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </ErrorStoreProvider>
      <Toaster richColors position="top-right" closeButton />
    </NextThemesProvider>
  );
}

