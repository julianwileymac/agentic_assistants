# Chunk: 24caead62bda_1

- source: `webui/src/app/page.tsx`
- lines: 103-193
- chunk: 2/4

```
v className={`size-3 rounded-full ${statusColors[status]}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatsCard({ 
  label, 
  value, 
  icon: Icon, 
  href 
}: { 
  label: string; 
  value: number | string; 
  icon: React.ElementType;
  href: string;
}) {
  return (
    <Link href={href}>
      <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="text-3xl font-bold">{value}</p>
            </div>
            <div className="p-3 rounded-xl bg-muted">
              <Icon className="size-6 text-muted-foreground" />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default function DashboardPage() {
  const { data: health, isLoading: healthLoading, mutate: refreshHealth } = useSystemHealth();

  // Mock stats for now - will be replaced with real API
  const stats = {
    projects: 3,
    agents: 12,
    flows: 5,
    components: 24,
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to the Agentic Control Panel
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refreshHealth()}>
            <RefreshCw className="size-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm" asChild>
            <Link href="/projects/new">
              <Plus className="size-4 mr-2" />
              New Project
            </Link>
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden">
                <CardContent className="pt-6 relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`} />
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${action.color} text-white`}>
                      <action.icon className="size-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold group-hover:text-primary transition-colors">
                        {action.title}
                      </h3>
```
