"use client";

import * as React from "react";
import { Terminal, Play } from "lucide-react";

import { getBackendUrl, useRunScript } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";

export function TerminalPanel() {
  const [command, setCommand] = React.useState("");
  const [output, setOutput] = React.useState("");
  const [runId, setRunId] = React.useState<string | null>(null);
  const [runLogs, setRunLogs] = React.useState<string[]>([]);
  const [trackingEnabled, setTrackingEnabled] = React.useState(false);
  const [rlMetricsEnabled, setRlMetricsEnabled] = React.useState(false);

  const { trigger: runScript, isMutating: isRunning } = useRunScript();

  React.useEffect(() => {
    if (!runId) return;

    const wsUrl = getBackendUrl().replace(/^http/, "ws") + "/ws";
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          command: "subscribe",
          params: { topic: `run.${runId}` },
        })
      );
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "run.log" && payload.data?.message) {
          setRunLogs((prev) => [...prev, payload.data.message]);
        }
      } catch {
        // ignore parsing errors
      }
    };

    return () => {
      ws.close();
    };
  }, [runId]);

  const handleRun = async () => {
    setOutput("");
    setRunLogs([]);
    const response = await runScript({
      script_content: command,
      script_type: "shell",
      tracking_enabled: trackingEnabled,
      rl_metrics_enabled: rlMetricsEnabled,
    });
    if (response?.run_id) {
      setRunId(response.run_id);
    }
    if (response?.message) {
      setOutput(response.message);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Terminal className="size-5 text-emerald-500" />
          Terminal Access
        </CardTitle>
        <CardDescription>Run shell commands via the execution layer.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          placeholder="Enter a shell command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
        />
        <div className="grid gap-3 md:grid-cols-2">
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">Experiment Tracking</p>
              <p className="text-xs text-muted-foreground">Log command metrics</p>
            </div>
            <Switch checked={trackingEnabled} onCheckedChange={setTrackingEnabled} />
          </div>
          <div className="flex items-center justify-between rounded-md border px-3 py-2">
            <div>
              <p className="text-sm font-medium">RL Metrics</p>
              <p className="text-xs text-muted-foreground">Emit reward signals</p>
            </div>
            <Switch checked={rlMetricsEnabled} onCheckedChange={setRlMetricsEnabled} />
          </div>
        </div>
        <Button onClick={handleRun} disabled={!command.trim() || isRunning}>
          <Play className="size-4 mr-2" />
          {isRunning ? "Running..." : "Run Command"}
        </Button>
        <div className="rounded-md border bg-muted/30 p-3 text-xs">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary">Output</Badge>
            {runId && <span className="text-muted-foreground">Run {runId}</span>}
          </div>
          <Textarea
            value={
              runLogs.length > 0
                ? runLogs.join("\n")
                : output || "No output yet."
            }
            readOnly
            rows={8}
            className="font-mono text-xs"
          />
        </div>
      </CardContent>
    </Card>
  );
}
