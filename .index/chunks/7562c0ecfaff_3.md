# Chunk: 7562c0ecfaff_3

- source: `webui/src/app/monitoring/page.tsx`
- lines: 217-257
- chunk: 4/4

```
    <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <Activity className="size-8 text-muted-foreground" />
              <div>
                <h3 className="font-semibold">OpenTelemetry Integration</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  This page shows basic system health and mock metrics. For detailed distributed tracing 
                  and metrics, configure an OpenTelemetry collector and connect to a backend like Jaeger, 
                  Zipkin, or Grafana. The framework automatically instruments agent runs, API calls, 
                  and database operations.
                </p>
                <div className="flex items-center gap-2 mt-4">
                  <Badge variant="outline">Traces: Enabled</Badge>
                  <Badge variant="outline">Metrics: Enabled</Badge>
                  <Badge variant="secondary">Collector: Not Configured</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Recent Traces Placeholder */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recent Traces</h2>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <Activity className="size-12 mx-auto mb-4 opacity-50" />
              <p>No recent traces</p>
              <p className="text-sm">Configure an OpenTelemetry collector to view traces</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

```
