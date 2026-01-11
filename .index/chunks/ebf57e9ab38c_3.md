# Chunk: ebf57e9ab38c_3

- source: `webui/src/app/library/page.tsx`
- lines: 219-253
- chunk: 4/4

```
         <h3 className="text-lg font-semibold mb-2">No components found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first component to get started"}
                  </p>
                  {!searchQuery && (
                    <Button asChild>
                      <Link href="/library/new">
                        <Plus className="size-4 mr-2" />
                        Create Component
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {components.map((component) => (
                <ComponentCard
                  key={component.id}
                  component={component}
                  onDelete={() => handleDelete(component.id, component.name)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

```
