# Chunk: ebf57e9ab38c_2

- source: `webui/src/app/library/page.tsx`
- lines: 147-224
- chunk: 3/4

```
component");
      }
    } catch (error) {
      toast.error("Failed to delete component");
    }
  };

  const components = data?.items || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Component Library</h1>
          <p className="text-muted-foreground">
            Reusable code snippets and templates
          </p>
        </div>
        <Button asChild>
          <Link href="/library/new">
            <Plus className="size-4 mr-2" />
            New Component
          </Link>
        </Button>
      </div>

      {/* Category Tabs */}
      <Tabs defaultValue="all" value={categoryFilter} onValueChange={setCategoryFilter}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="tool">Tools</TabsTrigger>
            <TabsTrigger value="agent">Agents</TabsTrigger>
            <TabsTrigger value="task">Tasks</TabsTrigger>
            <TabsTrigger value="pattern">Patterns</TabsTrigger>
            <TabsTrigger value="utility">Utilities</TabsTrigger>
            <TabsTrigger value="template">Templates</TabsTrigger>
          </TabsList>
          
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search components..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Components Grid */}
        <TabsContent value={categoryFilter} className="mt-6">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-1/4" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : components.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Puzzle className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No components found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first component to get started"}
```
