# Web UI Control Panel

The Control Panel is a Next.js app in `webui/` that manages the framework through the FastAPI backend.

## Running

### Recommended (repo scripts)

```bash
# Windows PowerShell
.\scripts\start-webui.ps1

# Linux/macOS/Git Bash
./scripts/start-webui.sh
```

### From the `webui/` folder

```bash
cd webui
npm install
npm run dev
```

## Backend integration

The UI talks to the backend at `http://localhost:8080` by default.

- **Backend URL override**: stored in `localStorage` as `backend_url`
- **API key** (if enabled): stored in `localStorage` as `api_key` and sent as `X-API-Key`

The API client is implemented in `webui/src/lib/api.ts` and uses SWR (`useSWR`, `useSWRMutation`) for caching/mutations.

## Testing & terminal tools

The Control Panel now ships with testing and terminal panels to support component experimentation during development:

- **Testing sandbox**: free-form test runner with optional MLFlow tracking, agent evaluation, and RL metrics.
- **Snippet library**: save snippets from the testing panel into the component library (`category=snippet`).
- **Terminal panel**: run shell commands via the backend execution API.
- **Code editor**: Monaco-backed editor is used for code and YAML editing in key panels.

## Route map (high-level)

The app router pages live under `webui/src/app/`:

- `/` dashboard
- `/projects`, `/projects/new`, `/projects/[id]`
- `/agents`, `/agents/new`
- `/flows`, `/flows/new`
- `/pipelines`
- `/knowledge`
- `/datasources`, `/datasources/[id]`
- `/experiments`
- `/monitoring`
- `/kubernetes` (+ `/deployments`, `/storage`, `/models`)
- `/library`
- `/settings`

## Backend endpoints used (high-level)

- Control Panel APIs: `/api/v1/projects`, `/api/v1/agents`, `/api/v1/flows`, `/api/v1/components`, `/api/v1/notes`, `/api/v1/tags`, `/api/v1/datasources`, `/api/v1/generate`, `/api/v1/pipelines`, `/api/v1/kubernetes`
- Legacy APIs (still used in some places): `/chat`, `/search`, `/collections`, `/sessions`

