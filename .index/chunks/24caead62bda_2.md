# Chunk: 24caead62bda_2

- source: `webui/src/app/page.tsx`
- lines: 186-273
- chunk: 3/4

```
ction.color} text-white`}>
                      <action.icon className="size-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold group-hover:text-primary transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Stats Overview */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsConfig.map((stat) => (
            <StatsCard
              key={stat.key}
              label={stat.label}
              value={stats[stat.key as keyof typeof stats]}
              icon={stat.icon}
              href={stat.href}
            />
          ))}
        </div>
      </section>

      {/* System Status */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">System Status</h2>
          <div className="flex items-center gap-2">
            {health && (
              <Badge variant={
                Object.values(health).every(s => s.status === 'healthy') 
                  ? 'default' 
                  : 'destructive'
              }>
                {Object.values(health).filter(s => s.status === 'healthy').length} / {Object.values(health).length} Services Healthy
              </Badge>
            )}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {healthLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <Skeleton className="h-12 w-full" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : health ? (
            <>
              <ServiceStatusCard
                name="Backend API"
                status={health.backend.status}
                url="localhost:8080"
                latency={health.backend.latency_ms}
                icon={Server}
              />
              <ServiceStatusCard
                name="Ollama"
                status={health.ollama.status}
                url="localhost:11434"
                latency={health.ollama.latency_ms}
                icon={Zap}
              />
              <ServiceStatusCard
                name="MLFlow"
                status={health.mlflow.status}
                url="localhost:5000"
                latency={health.mlflow.latency_ms}
                icon={FlaskConical}
              />
              <ServiceStatusCard
                name="JupyterLab"
```
