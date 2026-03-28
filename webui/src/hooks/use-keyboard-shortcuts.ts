"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

interface ShortcutConfig {
  enabled?: boolean;
}

/**
 * Global keyboard shortcuts for the application.
 * - Ctrl+K / Cmd+K: Focus search / open command palette
 * - Ctrl+Shift+E: Navigate to execution page
 * - Ctrl+Shift+L: Toggle logs panel
 * - Ctrl+Shift+M: Navigate to monitoring
 * - Ctrl+/: Toggle help panel
 */
export function useKeyboardShortcuts(config: ShortcutConfig = {}) {
  const { enabled = true } = config;
  const router = useRouter();

  useEffect(() => {
    if (!enabled) return;

    const handler = (e: KeyboardEvent) => {
      const isMod = e.ctrlKey || e.metaKey;
      const isShift = e.shiftKey;
      const target = e.target as HTMLElement;
      const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;

      if (isInput && !(isMod && e.key === 'k')) return;

      if (isMod && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>('[data-search-input]');
        searchInput?.focus();
        return;
      }

      if (isMod && isShift) {
        switch (e.key.toLowerCase()) {
          case 'e':
            e.preventDefault();
            router.push('/execution');
            break;
          case 'm':
            e.preventDefault();
            router.push('/monitoring');
            break;
          case 'p':
            e.preventDefault();
            router.push('/pipelines');
            break;
          case 'f':
            e.preventDefault();
            router.push('/flows');
            break;
        }
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [enabled, router]);
}
