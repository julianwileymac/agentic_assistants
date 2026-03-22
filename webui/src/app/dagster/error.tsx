'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function DagsterError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Dagster page error:', error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="max-w-md text-center space-y-4">
        <div className="mx-auto w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-destructive" />
        </div>
        <h2 className="text-lg font-semibold">Dagster Dashboard Error</h2>
        <p className="text-sm text-muted-foreground">
          Something went wrong loading the Dagster dashboard. This usually means
          the backend API is unreachable or returned an unexpected response.
        </p>
        <pre className="text-xs text-left bg-muted rounded-md p-3 overflow-x-auto max-h-32">
          {error.message}
        </pre>
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm border rounded-md hover:bg-accent transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Try Again
        </button>
      </div>
    </div>
  );
}
