# Chunk: dbc7b7cc22b1_3

- source: `webui/src/app/models/tuning/page.tsx`
- lines: 218-289
- chunk: 4/6

```
created_at).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Method Selection Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="cursor-pointer hover:border-primary/50 transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Badge className="bg-purple-500/10 text-purple-500">DPO</Badge>
                  Direct Preference Optimization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Directly optimize the policy using preference data without a reward model.
                  Simpler and often more stable than PPO.
                </p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:border-primary/50 transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Badge className="bg-blue-500/10 text-blue-500">PPO</Badge>
                  Proximal Policy Optimization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Classic RLHF approach using a reward model and PPO algorithm
                  for policy optimization.
                </p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:border-primary/50 transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Badge className="bg-orange-500/10 text-orange-500">RM</Badge>
                  Reward Modeling
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Train a reward model from preference data to use with PPO
                  or for model evaluation.
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Human Feedback Tab */}
        <TabsContent value="feedback" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Human Feedback Collection</CardTitle>
              <CardDescription>
                Collect preference data for RLHF training
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
```
