# Chunk: 24caead62bda_3

- source: `webui/src/app/page.tsx`
- lines: 264-350
- chunk: 4/4

```
rviceStatusCard
                name="MLFlow"
                status={health.mlflow.status}
                url="localhost:5000"
                latency={health.mlflow.latency_ms}
                icon={FlaskConical}
              />
              <ServiceStatusCard
                name="JupyterLab"
                status={health.jupyter.status}
                url="localhost:8888"
                latency={health.jupyter.latency_ms}
                icon={Database}
              />
            </>
          ) : (
            <Card className="col-span-full">
              <CardContent className="pt-6 text-center text-muted-foreground">
                Unable to fetch system status
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* External Tools */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Development Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="size-5" />
                JupyterLab
              </CardTitle>
              <CardDescription>
                Interactive notebooks for experimentation and development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => openJupyterLab()} className="w-full">
                <ExternalLink className="size-4 mr-2" />
                Open JupyterLab
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FlaskConical className="size-5" />
                MLFlow
              </CardTitle>
              <CardDescription>
                Experiment tracking, model registry, and deployment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => window.open(getMlflowUrl(), '_blank')} 
                className="w-full"
              >
                <ExternalLink className="size-4 mr-2" />
                Open MLFlow UI
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Recent Activity Placeholder */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="size-12 mx-auto mb-4 opacity-50" />
              <p>No recent activity</p>
              <p className="text-sm">Create a project or run an agent to see activity here</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
```
