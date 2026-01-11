# Chunk: 7562c0ecfaff_2

- source: `webui/src/app/monitoring/page.tsx`
- lines: 140-223
- chunk: 3/4

```
               <p className="text-xs text-muted-foreground mt-2">
                      {health.mlflow.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">JupyterLab</p>
                      <p className="font-semibold">localhost:8888</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.jupyter.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.jupyter.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.jupyter.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="col-span-full">
              <CardContent className="pt-6 text-center text-muted-foreground">
                Unable to fetch system health
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* Performance Metrics */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard
            title="Total Requests"
            value={mockMetrics.totalRequests.toLocaleString()}
            icon={Activity}
            trend="up"
          />
          <MetricCard
            title="Avg Response Time"
            value={mockMetrics.avgLatency}
            unit="ms"
            icon={Clock}
            trend="down"
          />
          <MetricCard
            title="Error Rate"
            value={(mockMetrics.errorRate * 100).toFixed(1)}
            unit="%"
            icon={AlertCircle}
            trend="neutral"
          />
          <MetricCard
            title="Active Agents"
            value={mockMetrics.activeAgents}
            icon={Cpu}
          />
          <MetricCard
            title="Active Sessions"
            value={mockMetrics.activeSessions}
            icon={Database}
          />
          <MetricCard
            title="Queued Tasks"
            value={mockMetrics.queuedTasks}
            icon={Zap}
          />
        </div>
      </section>

      {/* OpenTelemetry Info */}
      <section>
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <Activity className="size-8 text-muted-foreground" />
              <div>
                <h3 className="font-semibold">OpenTelemetry Integration</h3>
```
