# Chunk: dbc7b7cc22b1_5

- source: `webui/src/app/models/tuning/page.tsx`
- lines: 340-390
- chunk: 6/6

```
          <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Machine learning is a subset of artificial intelligence that...
                      </p>
                    </CardContent>
                  </Card>
                </div>

                <div className="flex justify-center gap-4">
                  <Button variant="outline" disabled>
                    <ThumbsDown className="mr-2 h-4 w-4" />
                    Both Bad
                  </Button>
                  <Button variant="outline" disabled>
                    Skip
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reward Models Tab */}
        <TabsContent value="rewards" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reward Models</CardTitle>
              <CardDescription>
                Train and manage reward models for RLHF
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No reward models yet</h3>
                <p className="text-muted-foreground mb-4">
                  Train a reward model from preference data
                </p>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Train Reward Model
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```
