# Chunk: 0b9dfd0e7fd9_3

- source: `webui/src/app/agents/new/page.tsx`
- lines: 245-285
- chunk: 4/4

```
    <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/agents">Cancel</Link>
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="size-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="size-4 mr-2" />
                Create Agent
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-[600px] w-full" />
    </div>
  );
}

export default function NewAgentPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <NewAgentForm />
    </Suspense>
  );
}

```
