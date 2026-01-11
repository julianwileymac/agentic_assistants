# Chunk: ebf57e9ab38c_1

- source: `webui/src/app/library/page.tsx`
- lines: 71-161
- chunk: 2/4

```
   </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/library/${component.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleCopyCode}>
                <Copy className="size-4 mr-2" />
                Copy Code
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="size-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Badge variant="secondary" className={categoryColors[component.category]}>
              {component.category}
            </Badge>
            <span className="text-xs text-muted-foreground">
              v{component.version}
            </span>
          </div>
          
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Code className="size-3" />
            {component.language}
          </div>

          {component.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {component.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function LibraryPage() {
  const [categoryFilter, setCategoryFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  
  const { data, isLoading, mutate } = useComponents({
    category: categoryFilter === "all" ? undefined : categoryFilter,
    search: searchQuery || undefined,
  });

  const handleDelete = async (componentId: string, componentName: string) => {
    if (!confirm(`Are you sure you want to delete "${componentName}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8080/api/v1/components/${componentId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast.success(`Component "${componentName}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete component");
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
```
