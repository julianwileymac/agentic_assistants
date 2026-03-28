'use client';

import React, { useState } from 'react';
import {
  Play,
  Upload,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertTriangle,
  Code2,
  Clock,
  Settings2,
  FileCode2,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl();

// Code templates
const TEMPLATES: Record<string, { label: string; description: string; code: string }> = {
  blank: {
    label: 'Blank',
    description: 'Start from scratch',
    code: `import dagster as dg


@dg.op(description="My custom op")
def my_op(context: dg.OpExecutionContext):
    context.log.info("Running custom op")
    return {"result": "success"}


@dg.job(description="My custom job")
def my_job():
    my_op()
`,
  },
  web_search: {
    label: 'Web Search',
    description: 'Fetch and process web search results',
    code: `import dagster as dg
import httpx


@dg.op(description="Search the web for a query")
def search_op(context: dg.OpExecutionContext) -> list:
    query = context.op_config.get("query", "dagster orchestration")
    context.log.info(f"Searching for: {query}")
    
    response = httpx.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_html": 1},
        timeout=15,
    )
    data = response.json()
    results = [
        {"url": t.get("FirstURL", ""), "text": t.get("Text", "")}
        for t in data.get("RelatedTopics", [])[:10]
        if isinstance(t, dict) and "Text" in t
    ]
    context.log.info(f"Found {len(results)} results")
    return results


@dg.op(description="Process search results")
def process_results_op(context: dg.OpExecutionContext, results: list) -> dict:
    context.log.info(f"Processing {len(results)} results")
    return {"count": len(results), "results": results}


@dg.job(description="Web search pipeline")
def web_search_pipeline():
    results = search_op()
    process_results_op(results)
`,
  },
  data_fetch: {
    label: 'Data Fetch',
    description: 'Fetch data from an API and transform it',
    code: `import dagster as dg


@dg.asset(
    description="Fetch raw data from external API",
    group_name="data",
)
def raw_api_data(context: dg.AssetExecutionContext) -> dict:
    import httpx
    
    url = "https://jsonplaceholder.typicode.com/posts"
    context.log.info(f"Fetching data from {url}")
    response = httpx.get(url, timeout=10)
    data = response.json()
    context.log.info(f"Fetched {len(data)} records")
    return {"records": data, "count": len(data)}


@dg.asset(
    description="Transform and clean API data",
    group_name="data",
    deps=[raw_api_data],
)
def cleaned_data(context: dg.AssetExecutionContext) -> dict:
    # In production, this would read from the upstream asset
    context.log.info("Cleaning data")
    return {"status": "cleaned"}
`,
  },
  llm_inference: {
    label: 'LLM Inference',
    description: 'Run LLM inference with prompt templates',
    code: `import dagster as dg


@dg.op(description="Generate text using an LLM")
def llm_generate_op(context: dg.OpExecutionContext) -> str:
    prompt = context.op_config.get("prompt", "Explain data orchestration in 3 sentences.")
    model = context.op_config.get("model", "llama3.2")
    
    context.log.info(f"Running LLM inference: model={model}")
    
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=model, temperature=0.7)
        response = llm.invoke(prompt)
        context.log.info(f"Generated {len(response)} chars")
        return response
    except Exception as e:
        context.log.warning(f"LLM failed: {e}")
        return f"Error: {e}"


@dg.op(description="Post-process LLM output")
def post_process_op(context: dg.OpExecutionContext, text: str) -> dict:
    context.log.info(f"Post-processing {len(text)} chars")
    return {
        "text": text,
        "char_count": len(text),
        "word_count": len(text.split()),
    }


@dg.job(description="LLM inference pipeline")
def llm_pipeline():
    text = llm_generate_op()
    post_process_op(text)
`,
  },
  scheduled_cleanup: {
    label: 'Scheduled Cleanup',
    description: 'Periodic workspace maintenance',
    code: `import dagster as dg
from pathlib import Path
import time


@dg.op(description="Clean temporary files from workspace")
def cleanup_temp_files(context: dg.OpExecutionContext) -> dict:
    workspace = context.op_config.get("workspace_path", ".")
    max_age_days = context.op_config.get("max_age_days", 7)
    
    context.log.info(f"Cleaning files older than {max_age_days} days in {workspace}")
    
    cutoff = time.time() - (max_age_days * 86400)
    cleaned = 0
    
    for pattern in ["*.tmp", "*.log", "*.pyc"]:
        for path in Path(workspace).rglob(pattern):
            if path.is_file() and path.stat().st_mtime < cutoff:
                cleaned += 1
                # path.unlink()  # Uncomment to actually delete
    
    context.log.info(f"Would clean {cleaned} files")
    return {"files_cleaned": cleaned}


@dg.job(description="Workspace cleanup job")
def cleanup_job():
    cleanup_temp_files()


# Schedule: run daily at 2 AM
cleanup_schedule = dg.ScheduleDefinition(
    job=cleanup_job,
    cron_schedule="0 2 * * *",
    name="daily_cleanup",
    description="Run workspace cleanup daily at 2 AM",
)
`,
  },
};

// Validation response
interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export default function DagsterDevelopPage() {
  const [code, setCode] = useState(TEMPLATES.blank.code);
  const [selectedTemplate, setSelectedTemplate] = useState('blank');
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [validating, setValidating] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [testing, setTesting] = useState(false);
  const [deployResult, setDeployResult] = useState<any>(null);
  const [testOutput, setTestOutput] = useState<string | null>(null);

  // Schedule wizard state
  const [scheduleName, setScheduleName] = useState('my_job');
  const [cronExpression, setCronExpression] = useState('');
  const [scheduleEnabled, setScheduleEnabled] = useState(false);

  const handleTemplateChange = (templateKey: string) => {
    setSelectedTemplate(templateKey);
    setCode(TEMPLATES[templateKey].code);
    setValidation(null);
    setDeployResult(null);
    setTestOutput(null);
  };

  const handleValidate = async () => {
    setValidating(true);
    setValidation(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/dagster/code/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const result = await res.json();
      setValidation(result);
    } catch (e) {
      setValidation({ valid: false, errors: ['Failed to connect to API'], warnings: [] });
    } finally {
      setValidating(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestOutput(null);
    try {
      // First validate
      const valRes = await fetch(`${API_BASE}/api/v1/dagster/code/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const valResult = await valRes.json();

      if (!valResult.valid) {
        setTestOutput(`Validation failed:\n${valResult.errors.join('\n')}`);
        setValidation(valResult);
        return;
      }

      // Deploy and run
      const deployRes = await fetch(`${API_BASE}/api/v1/dagster/code/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          name: `test_${Date.now()}`,
          description: 'Test run from IDE',
        }),
      });
      const deploy = await deployRes.json();
      setTestOutput(`Test deployment: ${JSON.stringify(deploy, null, 2)}`);
    } catch (e: any) {
      setTestOutput(`Test failed: ${e.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleDeploy = async () => {
    setDeploying(true);
    setDeployResult(null);
    try {
      const body: any = {
        code,
        name: scheduleName,
        description: `Deployed from Dagster IDE`,
      };
      if (scheduleEnabled && cronExpression) {
        body.schedule = cronExpression;
      }

      const res = await fetch(`${API_BASE}/api/v1/dagster/code/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const result = await res.json();
      setDeployResult(result);
    } catch (e: any) {
      setDeployResult({ error: e.message });
    } finally {
      setDeploying(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dagster Development Environment</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Write, test, and deploy Python code to Dagster
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Panel - Templates & Settings */}
        <div className="space-y-4">
          {/* Template Selector */}
          <div className="border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <FileCode2 className="w-4 h-4" />
              Templates
            </div>
            <div className="space-y-1">
              {Object.entries(TEMPLATES).map(([key, tmpl]) => (
                <button
                  key={key}
                  onClick={() => handleTemplateChange(key)}
                  className={cn(
                    'w-full text-left px-3 py-2 rounded-md text-sm transition-colors',
                    selectedTemplate === key
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent'
                  )}
                >
                  <div className="font-medium">{tmpl.label}</div>
                  <div className={cn(
                    'text-xs mt-0.5',
                    selectedTemplate === key ? 'text-primary-foreground/70' : 'text-muted-foreground'
                  )}>
                    {tmpl.description}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Schedule Wizard */}
          <div className="border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Clock className="w-4 h-4" />
              Schedule
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={scheduleEnabled}
                onChange={e => setScheduleEnabled(e.target.checked)}
                className="rounded"
              />
              Enable scheduling
            </label>
            {scheduleEnabled && (
              <div className="space-y-2">
                <input
                  type="text"
                  value={cronExpression}
                  onChange={e => setCronExpression(e.target.value)}
                  placeholder="0 * * * * (cron)"
                  className="w-full px-3 py-1.5 text-sm border rounded-md bg-background"
                />
                <div className="text-xs text-muted-foreground space-y-1">
                  <p>Common patterns:</p>
                  <div className="grid grid-cols-2 gap-1">
                    {[
                      ['*/5 * * * *', '5 min'],
                      ['0 * * * *', 'Hourly'],
                      ['0 */6 * * *', '6 hours'],
                      ['0 0 * * *', 'Daily'],
                      ['0 2 * * *', '2 AM'],
                      ['0 0 * * 0', 'Weekly'],
                    ].map(([cron, label]) => (
                      <button
                        key={cron}
                        onClick={() => setCronExpression(cron)}
                        className="text-left px-2 py-1 rounded hover:bg-accent text-xs"
                      >
                        <code>{cron}</code>
                        <span className="text-muted-foreground ml-1">({label})</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Deploy Settings */}
          <div className="border rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Settings2 className="w-4 h-4" />
              Deploy Settings
            </div>
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">Job Name</label>
              <input
                type="text"
                value={scheduleName}
                onChange={e => setScheduleName(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border rounded-md bg-background"
                placeholder="my_job"
              />
            </div>
          </div>
        </div>

        {/* Center - Code Editor */}
        <div className="lg:col-span-2 space-y-4">
          <div className="border rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/50">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Code2 className="w-4 h-4" />
                Code Editor
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleValidate}
                  disabled={validating}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs border rounded hover:bg-accent transition-colors"
                >
                  {validating ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />}
                  Validate
                </button>
                <button
                  onClick={handleTest}
                  disabled={testing}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs border rounded hover:bg-accent transition-colors"
                >
                  {testing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
                  Test Run
                </button>
                <button
                  onClick={handleDeploy}
                  disabled={deploying}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
                >
                  {deploying ? <Loader2 className="w-3 h-3 animate-spin" /> : <Upload className="w-3 h-3" />}
                  Deploy
                </button>
              </div>
            </div>
            <textarea
              value={code}
              onChange={e => {
                setCode(e.target.value);
                setValidation(null);
                setDeployResult(null);
              }}
              className="w-full h-[500px] p-4 font-mono text-sm bg-background resize-none focus:outline-none"
              spellCheck={false}
            />
          </div>
        </div>

        {/* Right Panel - Output */}
        <div className="space-y-4">
          {/* Validation Result */}
          {validation && (
            <div className={cn(
              'border rounded-lg p-4 space-y-2',
              validation.valid ? 'border-green-200 dark:border-green-900' : 'border-red-200 dark:border-red-900'
            )}>
              <div className="flex items-center gap-2 text-sm font-semibold">
                {validation.valid ? (
                  <><CheckCircle2 className="w-4 h-4 text-green-600" /> Valid</>
                ) : (
                  <><XCircle className="w-4 h-4 text-red-600" /> Invalid</>
                )}
              </div>
              {validation.errors.length > 0 && (
                <div className="space-y-1">
                  {validation.errors.map((err, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-red-600">
                      <XCircle className="w-3 h-3 mt-0.5 shrink-0" />
                      {err}
                    </div>
                  ))}
                </div>
              )}
              {validation.warnings.length > 0 && (
                <div className="space-y-1">
                  {validation.warnings.map((warn, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-yellow-600">
                      <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
                      {warn}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Deploy Result */}
          {deployResult && (
            <div className="border rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <Sparkles className="w-4 h-4" />
                Deploy Result
              </div>
              <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                {JSON.stringify(deployResult, null, 2)}
              </pre>
            </div>
          )}

          {/* Test Output */}
          {testOutput && (
            <div className="border rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <Play className="w-4 h-4" />
                Test Output
              </div>
              <pre className="text-xs bg-muted p-2 rounded overflow-x-auto whitespace-pre-wrap max-h-64">
                {testOutput}
              </pre>
            </div>
          )}

          {/* Quick Reference */}
          <div className="border rounded-lg p-4 space-y-2">
            <div className="text-sm font-semibold">Quick Reference</div>
            <div className="text-xs text-muted-foreground space-y-2">
              <div>
                <code className="bg-muted px-1 rounded">@dg.op</code> - Unit of computation
              </div>
              <div>
                <code className="bg-muted px-1 rounded">@dg.job</code> - Graph of ops
              </div>
              <div>
                <code className="bg-muted px-1 rounded">@dg.asset</code> - Data asset
              </div>
              <div>
                <code className="bg-muted px-1 rounded">@dg.schedule</code> - Cron schedule
              </div>
              <div>
                <code className="bg-muted px-1 rounded">@dg.sensor</code> - Event trigger
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
