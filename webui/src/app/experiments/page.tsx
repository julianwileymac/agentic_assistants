"use client";

import * as React from "react";
import Link from "next/link";
import { Plus, Search, FlaskConical, ExternalLink, RefreshCw, Play, Archive } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useExperiments, getMlflowUrl, openMlflowExperiment } from "@/lib/api";
import type { Experiment } from "@/lib/types";
import { TestingSection } from "@/components/testing/testing-section";

export default function ExperimentsPage() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const { data, isLoading, mutate } = useExperiments("ACTIVE_ONLY");

  const filteredExperiments = React.useMemo(() => {
    if (!data?.experiments) return [];
    if (!searchQuery) return data.experiments;
    
    const query = searchQuery.toLowerCase();
    return data.experiments.filter(
      (e) => e.name.toLowerCase().includes(query)
    );
  }, [data?.experiments, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Experiments</h1>
          <p className="text-muted-foreground">
            MLFlow experiment tracking and management
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => mutate()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" onClick={() => window.open(getMlflowUrl(), '_blank')}>
            <ExternalLink className="size-4 mr-2" />
            Open MLFlow UI
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search experiments..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Experiments Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredExperiments.length === 0 ? (
            <div className="text-center py-12">
              <FlaskConical className="size-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No experiments found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery
                  ? "Try a different search term"
                  : "Run an agent or flow to create experiments"}
              </p>
              <Button variant="outline" onClick={() => window.open(getMlflowUrl(), '_blank')}>
                <ExternalLink className="size-4 mr-2" />
                Open MLFlow UI
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>ID</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExperiments.map((experiment) => (
                  <TableRow key={experiment.experiment_id}>
                    <TableCell className="font-medium">
                      {experiment.name}
                    </TableCell>
                    <TableCell className="font-mono text-sm text-muted-foreground">
                      {experiment.experiment_id}
                    </TableCell>
                    <TableCell>
                      <Badge variant={experiment.lifecycle_stage === "active" ? "default" : "secondary"}>
                        {experiment.lifecycle_stage}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {experiment.creation_time 
                        ? new Date(parseInt(experiment.creation_time)).toLocaleDateString()
                        : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => openMlflowExperiment(experiment.experiment_id)}
                      >
                        <ExternalLink className="size-4 mr-2" />
                        View in MLFlow
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Info */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <FlaskConical className="size-8 text-muted-foreground" />
            <div>
              <h3 className="font-semibold">MLFlow Integration</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Experiments are automatically tracked when you run agents or flows. 
                Each run records parameters, metrics, and artifacts. Click &quot;View in MLFlow&quot; 
                to see detailed run information, compare experiments, and manage models.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <TestingSection
        resourceType="experiment"
        resourceName="Experiment"
        defaultCode={`# Experiment test\nresult = {\n    \"status\": \"ok\",\n    \"notes\": \"Validate tracking configuration\",\n}\n`}
      />
    </div>
  );
}

