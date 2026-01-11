# Chunk: aaf75bcf26b9_0

- source: `webui/src/components/providers.tsx`
- lines: 1-21
- chunk: 1/1

```
"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      {children}
      <Toaster richColors position="top-right" />
    </NextThemesProvider>
  );
}

```
