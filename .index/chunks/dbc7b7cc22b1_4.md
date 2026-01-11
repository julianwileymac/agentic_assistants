# Chunk: dbc7b7cc22b1_4

- source: `webui/src/app/models/tuning/page.tsx`
- lines: 282-348
- chunk: 5/6

```
ription>
                Collect preference data for RLHF training
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No feedback collected yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start collecting human preferences for your models
                </p>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Start Feedback Session
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Feedback Interface Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Feedback Interface</CardTitle>
              <CardDescription>
                Compare model responses and select the better one
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm font-medium mb-2">Prompt:</p>
                  <p className="text-muted-foreground">
                    "Explain the concept of machine learning in simple terms."
                  </p>
                </div>
                
                <div className="grid gap-4 md:grid-cols-2">
                  <Card className="border-2 hover:border-green-500/50 cursor-pointer transition-colors">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        Response A
                        <ThumbsUp className="h-4 w-4 text-muted-foreground" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Machine learning is like teaching a computer to learn from examples...
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="border-2 hover:border-green-500/50 cursor-pointer transition-colors">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        Response B
                        <ThumbsUp className="h-4 w-4 text-muted-foreground" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Machine learning is a subset of artificial intelligence that...
                      </p>
                    </CardContent>
                  </Card>
                </div>

```
