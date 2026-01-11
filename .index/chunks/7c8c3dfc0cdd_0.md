# Chunk: 7c8c3dfc0cdd_0

- source: `webui/src/lib/utils.ts`
- lines: 1-7
- chunk: 1/1

```
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```
