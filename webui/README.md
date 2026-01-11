## Agentic Control Panel (Web UI)

The `webui/` app is the **Agentic Control Panel**: a Next.js UI for managing projects, agents, flows, pipelines, knowledge bases, and infrastructure via the FastAPI backend.

## Getting Started

### Prerequisites

- Node.js 18+
- The backend API running (default: `http://localhost:8080`)

### Run the UI (dev)

```bash
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

### Backend URL + API keys

The UI defaults to `http://localhost:8080`. You can override this in the Settings UI (stored in `localStorage` as `backend_url`). If an API key is required, set it via Settings (stored as `api_key`).

### What the UI talks to

The UI uses:

- `/api/v1/*` control panel endpoints (projects, agents, flows, components, notes, tags, datasources, generation, pipelines, kubernetes)
- legacy endpoints for search/chat/sessions (`/search`, `/chat`, `/sessions`) where applicable

## Repo Notes

- Main API implementation: `src/agentic_assistants/server/`
- UI routes (Next.js app router): `webui/src/app/`
- UI API client hooks: `webui/src/lib/api.ts`

For general Next.js documentation, see `https://nextjs.org/docs`.
