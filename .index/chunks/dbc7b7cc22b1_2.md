# Chunk: dbc7b7cc22b1_2

- source: `webui/src/app/models/tuning/page.tsx`
- lines: 159-229
- chunk: 3/6

```
</TabsList>

        {/* Experiments Tab */}
        <TabsContent value="experiments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>RL Experiments</CardTitle>
              <CardDescription>
                DPO, PPO, and RLHF training experiments
              </CardDescription>
            </CardHeader>
            <CardContent>
              {experiments.length === 0 ? (
                <div className="text-center py-12">
                  <Sliders className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No experiments yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Start your first RL experiment to optimize model behavior
                  </p>
                  <Link href="/models/tuning/new">
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Create Experiment
                    </Button>
                  </Link>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Method</TableHead>
                      <TableHead>Base Model</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Reward</TableHead>
                      <TableHead>Created</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {experiments.map((exp) => (
                      <TableRow key={exp.id}>
                        <TableCell className="font-medium">{exp.name}</TableCell>
                        <TableCell>
                          <Badge className={getMethodBadgeColor(exp.method)}>
                            {exp.method.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {exp.base_model}
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(exp.status)}>
                            {exp.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {exp.metrics.mean_reward?.toFixed(4) || "-"}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {new Date(exp.created_at).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Method Selection Cards */}
```
