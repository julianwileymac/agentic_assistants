"use client";

import * as React from "react";
import {
  CheckCircle2,
  XCircle,
  MinusCircle,
  Play,
  FolderOpen,
  FileCode,
  RefreshCw,
  ChevronRight,
} from "lucide-react";

import { apiFetch } from "@/lib/api";
import type { TestSuite, TestCase, TestRun, TestResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface SuiteWithCases extends TestSuite {
  cases: TestCase[];
}

interface CaseResult {
  status: "pass" | "fail" | "skip" | "running" | "idle";
  runId?: string;
}

type SuiteStats = { pass: number; fail: number; skip: number };

function computeStats(
  suiteId: string,
  testIds: string[],
  results: Map<string, CaseResult>,
): SuiteStats {
  let pass = 0,
    fail = 0,
    skip = 0;
  for (const id of testIds) {
    const r = results.get(id);
    if (!r || r.status === "idle") skip++;
    else if (r.status === "pass") pass++;
    else if (r.status === "fail") fail++;
    else skip++;
  }
  return { pass, fail, skip };
}

function StatusIcon({ status }: { status: CaseResult["status"] }) {
  switch (status) {
    case "pass":
      return <CheckCircle2 className="size-4 text-emerald-500" />;
    case "fail":
      return <XCircle className="size-4 text-red-500" />;
    case "running":
      return <RefreshCw className="size-4 animate-spin text-blue-500" />;
    default:
      return <MinusCircle className="size-4 text-yellow-500" />;
  }
}

export function TestSuiteManager() {
  const [suites, setSuites] = React.useState<SuiteWithCases[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [caseResults, setCaseResults] = React.useState<Map<string, CaseResult>>(
    new Map(),
  );
  const [expandedSuites, setExpandedSuites] = React.useState<Set<string>>(
    new Set(),
  );
  const [runningSuites, setRunningSuites] = React.useState<Set<string>>(
    new Set(),
  );
  const [runningCases, setRunningCases] = React.useState<Set<string>>(
    new Set(),
  );

  const fetchData = React.useCallback(async () => {
    setLoading(true);
    try {
      const [suitesRes, casesRes] = await Promise.all([
        apiFetch<{ items: TestSuite[] }>("/api/v1/testing/suites"),
        apiFetch<{ items: TestCase[] }>("/api/v1/testing/test-cases"),
      ]);

      const allSuites = suitesRes.items ?? [];
      const allCases = casesRes.items ?? [];
      const caseMap = new Map(allCases.map((c) => [c.id, c]));

      const enriched: SuiteWithCases[] = allSuites.map((s) => ({
        ...s,
        cases: (s.test_ids ?? [])
          .map((id) => caseMap.get(id))
          .filter(Boolean) as TestCase[],
      }));

      setSuites(enriched);
    } catch {
      setSuites([]);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleSuite = (id: string) => {
    setExpandedSuites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const runSingleTest = React.useCallback(
    async (testCase: TestCase) => {
      setRunningCases((prev) => new Set(prev).add(testCase.id));
      setCaseResults((prev) => {
        const next = new Map(prev);
        next.set(testCase.id, { status: "running" });
        return next;
      });

      try {
        const res = await apiFetch<{ run: TestRun; results: TestResult[] }>(
          "/api/v1/testing/runs",
          {
            method: "POST",
            body: JSON.stringify({
              test_case_id: testCase.id,
              code: testCase.code,
              language: testCase.language,
              input_data: testCase.input_data,
              expected_output: testCase.expected_output,
            }),
          },
        );

        const passed = res.results?.every((r) => r.passed) ?? false;
        setCaseResults((prev) => {
          const next = new Map(prev);
          next.set(testCase.id, {
            status: passed ? "pass" : "fail",
            runId: res.run?.id,
          });
          return next;
        });
      } catch {
        setCaseResults((prev) => {
          const next = new Map(prev);
          next.set(testCase.id, { status: "fail" });
          return next;
        });
      } finally {
        setRunningCases((prev) => {
          const next = new Set(prev);
          next.delete(testCase.id);
          return next;
        });
      }
    },
    [],
  );

  const runSuite = React.useCallback(
    async (suite: SuiteWithCases) => {
      setRunningSuites((prev) => new Set(prev).add(suite.id));

      for (const tc of suite.cases) {
        await runSingleTest(tc);
      }

      setRunningSuites((prev) => {
        const next = new Set(prev);
        next.delete(suite.id);
        return next;
      });
    },
    [runSingleTest],
  );

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="size-5 text-indigo-500" />
            Test Suites
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full rounded-md" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="size-5 text-indigo-500" />
            Test Suites
          </CardTitle>
          <Button size="sm" variant="outline" onClick={fetchData}>
            <RefreshCw className="mr-1.5 size-3.5" />
            Refresh
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-6 pb-6">
          {suites.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No test suites found. Create suites via the API.
            </p>
          ) : (
            <div className="space-y-2">
              {suites.map((suite) => {
                const stats = computeStats(
                  suite.id,
                  suite.test_ids,
                  caseResults,
                );
                const isExpanded = expandedSuites.has(suite.id);
                const isSuiteRunning = runningSuites.has(suite.id);

                return (
                  <Collapsible
                    key={suite.id}
                    open={isExpanded}
                    onOpenChange={() => toggleSuite(suite.id)}
                  >
                    <div className="rounded-lg border">
                      <CollapsibleTrigger asChild>
                        <button className="flex w-full items-center gap-2 px-4 py-3 text-left hover:bg-muted/50 transition-colors">
                          <ChevronRight
                            className={cn(
                              "size-4 shrink-0 transition-transform",
                              isExpanded && "rotate-90",
                            )}
                          />
                          <FolderOpen className="size-4 shrink-0 text-indigo-400" />
                          <span className="flex-1 truncate text-sm font-medium">
                            {suite.name}
                          </span>

                          <div className="flex items-center gap-1.5">
                            {stats.pass > 0 && (
                              <Badge
                                variant="outline"
                                className="border-emerald-500/40 bg-emerald-500/10 text-emerald-600 text-xs"
                              >
                                {stats.pass}
                              </Badge>
                            )}
                            {stats.fail > 0 && (
                              <Badge
                                variant="outline"
                                className="border-red-500/40 bg-red-500/10 text-red-600 text-xs"
                              >
                                {stats.fail}
                              </Badge>
                            )}
                            {stats.skip > 0 && (
                              <Badge
                                variant="outline"
                                className="border-yellow-500/40 bg-yellow-500/10 text-yellow-600 text-xs"
                              >
                                {stats.skip}
                              </Badge>
                            )}
                            <Badge variant="secondary" className="text-xs">
                              {suite.cases.length} tests
                            </Badge>
                          </div>
                        </button>
                      </CollapsibleTrigger>

                      <CollapsibleContent>
                        <div className="border-t">
                          <div className="flex items-center justify-between bg-muted/30 px-4 py-2">
                            <p className="text-xs text-muted-foreground">
                              {suite.description || "No description"}
                            </p>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => runSuite(suite)}
                              disabled={isSuiteRunning}
                              className="h-7 text-xs"
                            >
                              {isSuiteRunning ? (
                                <RefreshCw className="mr-1 size-3 animate-spin" />
                              ) : (
                                <Play className="mr-1 size-3" />
                              )}
                              {isSuiteRunning ? "Running..." : "Run All"}
                            </Button>
                          </div>

                          <div className="divide-y">
                            {suite.cases.map((tc) => {
                              const result = caseResults.get(tc.id);
                              const caseStatus = result?.status ?? "idle";
                              const isCaseRunning = runningCases.has(tc.id);

                              return (
                                <div
                                  key={tc.id}
                                  className="flex items-center gap-3 px-4 py-2.5 pl-10 hover:bg-muted/30 transition-colors"
                                >
                                  <StatusIcon status={caseStatus} />
                                  <FileCode className="size-3.5 shrink-0 text-muted-foreground" />
                                  <div className="flex-1 min-w-0">
                                    <p className="truncate text-sm">
                                      {tc.name}
                                    </p>
                                    {tc.description && (
                                      <p className="truncate text-xs text-muted-foreground">
                                        {tc.description}
                                      </p>
                                    )}
                                  </div>
                                  <Badge
                                    variant="outline"
                                    className="text-xs shrink-0"
                                  >
                                    {tc.language}
                                  </Badge>
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="size-7 shrink-0"
                                    onClick={() => runSingleTest(tc)}
                                    disabled={isCaseRunning}
                                  >
                                    {isCaseRunning ? (
                                      <RefreshCw className="size-3.5 animate-spin" />
                                    ) : (
                                      <Play className="size-3.5" />
                                    )}
                                  </Button>
                                </div>
                              );
                            })}

                            {suite.cases.length === 0 && (
                              <p className="px-4 py-3 text-center text-xs text-muted-foreground">
                                No test cases linked to this suite.
                              </p>
                            )}
                          </div>
                        </div>
                      </CollapsibleContent>
                    </div>
                  </Collapsible>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
