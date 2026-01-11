# Chunk: 7562c0ecfaff_1

- source: `webui/src/app/monitoring/page.tsx`
- lines: 82-148
- chunk: 2/4

```
tem Health */}
      <section>
        <h2 className="text-lg font-semibold mb-4">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <Skeleton className="h-16 w-full" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : health ? (
            <>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Backend API</p>
                      <p className="font-semibold">localhost:8080</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.backend.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.backend.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.backend.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Ollama</p>
                      <p className="font-semibold">localhost:11434</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.ollama.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.ollama.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.ollama.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">MLFlow</p>
                      <p className="font-semibold">localhost:5000</p>
                    </div>
                    <div className={`size-3 rounded-full ${health.mlflow.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  </div>
                  {health.mlflow.latency_ms && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {health.mlflow.latency_ms}ms latency
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
```
