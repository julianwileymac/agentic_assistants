# Chunk: f2aea81d8baf_0

- source: `webui/src/components/ui/skeleton.tsx`
- lines: 1-14
- chunk: 1/1

```
import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn("bg-accent animate-pulse rounded-md", className)}
      {...props}
    />
  )
}

export { Skeleton }
```
