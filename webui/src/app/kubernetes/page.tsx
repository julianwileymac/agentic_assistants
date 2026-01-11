"use client";

import * as React from "react";
import Link from "next/link";
import {
  Server,
  Cpu,
  HardDrive,
  Network,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Box,
  Layers,
  Container,
  ArrowRight,
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useClusterInfo, useKubernetesStatus } from "@/lib/api";

function StatusIndicator({ status }: { status: string }) {
  if (status === "Ready") {
    return <CheckCircle className="size-4 text-green-500" />;
  } else if (status === "NotReady") {
    return <XCircle className="size-4 text-red-500" />;
  }
  return <AlertCircle className="size-4 text-yellow-500" />;
}

function parseMemory(memStr: string): number {
  if (!memStr) return 0;
  if (memStr.endsWith("Gi")) return parseFloat(memStr.slice(0, -2));
  if (memStr.endsWith("Mi")) return parseFloat(memStr.slice(0, -2)) / 1024;
  if (memStr.endsWith("Ki")) return parseFloat(memStr.slice(0, -2)) / (1024 * 1024);
  return parseFloat(memStr);
}

export default function KubernetesPage() {
  const { data: cluster, isLoading, mutate } = useClusterInfo();
  const { data: status } = useKubernetesStatus();

  const isConnected = cluster?.is_connected ?? false;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Kubernetes Cluster</h1>
          <p className="text-muted-foreground">
            Manage your RPi Kubernetes cluster and deployments
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button variant="outline" onClick={() => mutate()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Connection Status */}
      {!isConnected && !isLoading && (
        <Card className="border-destructive bg-destructive/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <XCircle className="size-8 text-destructive" />
              <div>
                <h3 className="font-semibold">Cluster Not Connected</h3>
                <p className="text-sm text-muted-foreground">
                  Configure your Kubernetes connection in Settings to enable cluster management.
                </p>
                <Link href="/settings">
                  <Button variant="link" className="px-0 mt-2">
                    Go to Settings <ArrowRight className="size-4 ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cluster Overview */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : cluster && isConnected ? (
        <>
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Nodes</p>
                    <p className="text-2xl font-bold">
                      {cluster.ready_nodes}/{cluster.node_count}
                    </p>
                    <p className="text-xs text-muted-foreground">ready</p>
                  </div>
                  <div className="p-3 rounded-xl bg-blue-500/10">
                    <Server className="size-6 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Pods</p>
                    <p className="text-2xl font-bold">
                      {cluster.running_pods}/{cluster.total_pods}
                    </p>
                    <p className="text-xs text-muted-foreground">running</p>
                  </div>
                  <div className="p-3 rounded-xl bg-green-500/10">
                    <Container className="size-6 text-green-500" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total CPU</p>
                    <p className="text-2xl font-bold">{cluster.total_cpu}</p>
                    <p className="text-xs text-muted-foreground">cores</p>
                  </div>
                  <div className="p-3 rounded-xl bg-purple-500/10">
                    <Cpu className="size-6 text-purple-500" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Memory</p>
                    <p className="text-2xl font-bold">{cluster.total_memory}</p>
                    <p className="text-xs text-muted-foreground">available</p>
                  </div>
                  <div className="p-3 rounded-xl bg-orange-500/10">
                    <HardDrive className="size-6 text-orange-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Cluster Info */}
          <Card>
            <CardHeader>
              <CardTitle>Cluster Information</CardTitle>
              <CardDescription>
                {cluster.name} running Kubernetes {cluster.version}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Cluster Name</p>
                  <p className="font-medium">{cluster.name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Version</p>
                  <p className="font-medium">{cluster.version}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Context</p>
                  <p className="font-medium">{cluster.context || "default"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Namespaces</p>
                  <p className="font-medium">{cluster.namespaces?.length || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Nodes */}
          <Card>
            <CardHeader>
              <CardTitle>Nodes</CardTitle>
              <CardDescription>
                Cluster nodes and their resource utilization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {cluster.nodes?.map((node) => (
                  <div
                    key={node.name}
                    className="flex items-center gap-4 p-4 rounded-lg border bg-card"
                  >
                    <StatusIndicator status={node.status} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium truncate">{node.name}</p>
                        {node.roles.map((role) => (
                          <Badge key={role} variant="secondary" className="text-xs">
                            {role}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {node.ip_address} • {node.architecture} • {node.os_image}
                      </p>
                    </div>
                    {node.metrics && (
                      <div className="hidden md:flex items-center gap-6 text-sm">
                        <div className="text-right">
                          <p className="text-muted-foreground">CPU</p>
                          <p className="font-medium">{node.metrics.cpu_capacity}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-muted-foreground">Memory</p>
                          <p className="font-medium">{node.metrics.memory_capacity}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-muted-foreground">Pods</p>
                          <p className="font-medium">
                            {node.metrics.pods_running}/{node.metrics.pods_capacity}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/kubernetes/deployments">
              <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-blue-500/10">
                      <Layers className="size-6 text-blue-500" />
                    </div>
                    <div>
                      <p className="font-semibold">Deployments</p>
                      <p className="text-sm text-muted-foreground">
                        Manage agent and flow deployments
                      </p>
                    </div>
                    <ArrowRight className="size-4 ml-auto text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link href="/kubernetes/models">
              <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-purple-500/10">
                      <Box className="size-6 text-purple-500" />
                    </div>
                    <div>
                      <p className="font-semibold">Model Serving</p>
                      <p className="text-sm text-muted-foreground">
                        Deploy and manage LLM models
                      </p>
                    </div>
                    <ArrowRight className="size-4 ml-auto text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link href="/kubernetes/storage">
              <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-orange-500/10">
                      <HardDrive className="size-6 text-orange-500" />
                    </div>
                    <div>
                      <p className="font-semibold">Storage</p>
                      <p className="text-sm text-muted-foreground">
                        Browse MinIO object storage
                      </p>
                    </div>
                    <ArrowRight className="size-4 ml-auto text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* Namespaces */}
          <Card>
            <CardHeader>
              <CardTitle>Namespaces</CardTitle>
              <CardDescription>Available Kubernetes namespaces</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {cluster.namespaces?.map((ns) => (
                  <Badge key={ns} variant="outline">
                    {ns}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
