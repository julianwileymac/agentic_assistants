"""
Generate a model-agnostic, file-based index under `.index/`.

Outputs are designed for small-context local LLM workflows:
- Markdown: human-readable overviews, surfaces, chunked file content
- JSON: manifests + symbol/surface tables for tooling
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

try:
    import pathspec  # type: ignore
except Exception:  # pragma: no cover
    pathspec = None


SCHEMA_VERSION = "1.0"

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".md": "markdown",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".sh": "shell",
    ".ps1": "powershell",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
}

# Conservative defaults; can be overridden via CLI.
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    ".index",
    ".cursor",
    ".vscode",
    ".idea",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "py11_venv",
    "node_modules",
    ".next",
    "data",
    "mlruns",
    "dist",
    "build",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.dll",
    "*.exe",
    "*.so",
    "*.dylib",
    "*.log",
    "*.log.err",
    "*.lock",
    "yarn.lock",
    "poetry.lock",
    "package-lock.json",
    "*.tsbuildinfo",
    "*.map",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_probably_binary(data: bytes) -> bool:
    if not data:
        return False
    # Null byte is a strong signal.
    if b"\x00" in data:
        return True
    # Heuristic: lots of non-text bytes in the first chunk.
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    nontext = data.translate(None, text_chars)
    return (len(nontext) / max(1, len(data))) > 0.30


def detect_language(path: Path) -> Optional[str]:
    return LANGUAGE_MAP.get(path.suffix.lower())


def safe_filename_from_path(path: str) -> str:
    # Keep it deterministic and filesystem-safe.
    return re.sub(r"[^A-Za-z0-9._-]+", "__", path).strip("_")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def load_gitignore_spec(repo_root: Path) -> Any:
    if pathspec is None:
        return None
    gi = repo_root / ".gitignore"
    if not gi.exists():
        return None
    patterns = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
    patterns = [p for p in patterns if p.strip() and not p.strip().startswith("#")]
    try:
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    except Exception:
        return None


def should_ignore(rel_path: str, ignore_spec: Any, extra_patterns: list[str]) -> bool:
    # Extra patterns first (fast).
    for pat in extra_patterns:
        if pathspec is not None:
            try:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", [pat])
                if spec.match_file(rel_path):
                    return True
            except Exception:
                pass
        # Fallback: substring-ish match for common directory names.
        if pat in {".git", ".index", "node_modules", "__pycache__", ".venv", "venv", "py11_venv", ".next"}:
            if f"/{pat}/" in f"/{rel_path}/":
                return True
    if ignore_spec is None:
        return False
    try:
        return bool(ignore_spec.match_file(rel_path))
    except Exception:
        return False


@dataclass(frozen=True)
class FileRecord:
    path: str
    sha256: str
    size_bytes: int
    mtime_epoch: float
    language: Optional[str]
    line_count: Optional[int]
    binary: bool


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    path: str
    source_path: str
    chunk_index: int
    total_chunks: int
    start_line: int
    end_line: int
    sha256: str


def iter_repo_files(repo_root: Path, ignore_spec: Any, extra_patterns: list[str]) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)
        # Prune ignored directories
        rel_root = root_path.relative_to(repo_root).as_posix()
        pruned = []
        for d in list(dirs):
            rel_dir = f"{rel_root}/{d}" if rel_root != "." else d
            if should_ignore(rel_dir, ignore_spec, extra_patterns):
                pruned.append(d)
        for d in pruned:
            dirs.remove(d)

        for name in files:
            file_path = root_path / name
            rel = file_path.relative_to(repo_root).as_posix()
            if should_ignore(rel, ignore_spec, extra_patterns):
                continue
            yield file_path


def chunk_text_by_chars(text: str, chunk_chars: int, overlap_chars: int) -> list[tuple[int, int, str]]:
    if not text:
        return []
    if chunk_chars <= 0:
        return [(1, max(1, text.count("\n") + 1), text)]

    chunks: list[tuple[int, int, str]] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_chars)
        # Prefer to break on newline in the last 25% of the window.
        if end < n:
            nl = text.rfind("\n", start + int(chunk_chars * 0.75), end)
            if nl != -1 and nl > start:
                end = nl + 1

        chunk = text[start:end]
        # Compute line numbers (1-based).
        start_line = text.count("\n", 0, start) + 1
        end_line = text.count("\n", 0, end) + 1
        chunks.append((start_line, end_line, chunk))

        if end == n:
            break
        start = max(0, end - overlap_chars)
    return chunks


def py_signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    a = fn.args
    parts: list[str] = []

    def fmt_arg(arg: ast.arg) -> str:
        return arg.arg

    posonly = [fmt_arg(x) for x in getattr(a, "posonlyargs", [])]
    args = [fmt_arg(x) for x in a.args]
    vararg = f"*{a.vararg.arg}" if a.vararg else None
    kwonly = [fmt_arg(x) for x in a.kwonlyargs]
    kwarg = f"**{a.kwarg.arg}" if a.kwarg else None

    parts.extend(posonly)
    if posonly:
        parts.append("/")
    parts.extend(args)
    if vararg:
        parts.append(vararg)
    elif kwonly:
        parts.append("*")
    parts.extend(kwonly)
    if kwarg:
        parts.append(kwarg)

    return f"{fn.name}({', '.join(parts)})"


def extract_python_symbols(path: Path, source: str) -> dict[str, Any]:
    out: dict[str, Any] = {"path": path.as_posix(), "symbols": []}
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        out["parse_error"] = f"{e}"
        return out

    module_doc = ast.get_docstring(tree)
    if module_doc:
        out["module_doc"] = module_doc

    def add_symbol(kind: str, name: str, qualname: str, node: ast.AST) -> None:
        doc = ast.get_docstring(node) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None
        out["symbols"].append(
            {
                "kind": kind,
                "name": name,
                "qualname": qualname,
                "lineno": getattr(node, "lineno", None),
                "end_lineno": getattr(node, "end_lineno", None),
                "doc": doc,
            }
        )

    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_symbol("function", n.name, n.name, n)
            out["symbols"][-1]["signature"] = py_signature(n)
        elif isinstance(n, ast.ClassDef):
            add_symbol("class", n.name, n.name, n)
            bases = []
            for b in n.bases:
                try:
                    bases.append(ast.unparse(b))
                except Exception:
                    bases.append("<base>")
            out["symbols"][-1]["bases"] = bases
            # Methods
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qual = f"{n.name}.{m.name}"
                    add_symbol("method", m.name, qual, m)
                    out["symbols"][-1]["signature"] = py_signature(m)

    return out


EXPORT_RE = re.compile(
    r"^\s*export\s+(?:default\s+)?"
    r"(?:async\s+)?"
    r"(function|class|const|let|var|interface|type)\s+([A-Za-z0-9_$]+)",
    re.MULTILINE,
)


def extract_ts_symbols(path: Path, source: str) -> dict[str, Any]:
    symbols: list[dict[str, Any]] = []
    for m in EXPORT_RE.finditer(source):
        kind = m.group(1)
        name = m.group(2)
        lineno = source.count("\n", 0, m.start()) + 1
        symbols.append({"kind": kind, "name": name, "lineno": lineno})
    return {"path": path.as_posix(), "symbols": symbols}


def extract_fastapi_routes_from_router(source: str, file_path: str) -> list[dict[str, Any]]:
    # Router prefix + tags
    prefix = ""
    tags: list[str] = []
    m = re.search(r"router\s*=\s*APIRouter\(([^)]*)\)", source, re.DOTALL)
    if m:
        args = m.group(1)
        pm = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', args)
        if pm:
            prefix = pm.group(1)
        tm = re.search(r"tags\s*=\s*\[([^\]]*)\]", args)
        if tm:
            raw = tm.group(1)
            tags = re.findall(r'["\']([^"\']+)["\']', raw)

    routes: list[dict[str, Any]] = []
    for rm in re.finditer(
        r'@router\.(get|post|put|delete|patch)\(\s*["\']([^"\']*)["\']',
        source,
    ):
        method = rm.group(1).upper()
        path = rm.group(2)
        lineno = source.count("\n", 0, rm.start()) + 1
        routes.append(
            {
                "method": method,
                "path": f"{prefix}{path}" if prefix else path,
                "router_prefix": prefix,
                "tags": tags,
                "file": file_path,
                "lineno": lineno,
            }
        )
    return routes


def extract_fastapi_routes_from_app(source: str, file_path: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for rm in re.finditer(
        r'@app\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']',
        source,
    ):
        method = rm.group(1).upper()
        path = rm.group(2)
        lineno = source.count("\n", 0, rm.start()) + 1
        routes.append({"method": method, "path": path, "file": file_path, "lineno": lineno, "tags": []})
    return routes


def extract_click_commands(cli_source: str, file_path: str) -> list[dict[str, Any]]:
    # Map group variable name -> command name (usually function name).
    group_defs: dict[str, str] = {}
    commands: list[dict[str, Any]] = []

    # Find `@cli.group()` / `@cli.group` blocks and capture the next `def name(...):`.
    for gm in re.finditer(r"@cli\.group\([^)]*\)\s*@click\.pass_context\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", cli_source):
        fn = gm.group(1)
        group_defs[fn] = fn
        commands.append({"type": "group", "command": fn, "file": file_path, "lineno": cli_source.count("\n", 0, gm.start()) + 1})

    # Also allow `@cli.group()` without pass_context (some groups).
    for gm in re.finditer(r"@cli\.group\([^)]*\)\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", cli_source):
        fn = gm.group(1)
        group_defs.setdefault(fn, fn)
        commands.append({"type": "group", "command": fn, "file": file_path, "lineno": cli_source.count("\n", 0, gm.start()) + 1})

    # Find `@cli.command("name") def ...`
    for cm in re.finditer(r'@cli\.command\(\s*["\']([^"\']+)["\']\s*\)\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', cli_source):
        name = cm.group(1)
        fn = cm.group(2)
        commands.append(
            {
                "type": "command",
                "command": name,
                "function": fn,
                "file": file_path,
                "lineno": cli_source.count("\n", 0, cm.start()) + 1,
            }
        )

    # Find `@<group>.command("name") def ...`
    for cm in re.finditer(r'@([a-zA-Z_][a-zA-Z0-9_]*)\.command\(\s*["\']([^"\']+)["\']\s*\)\s*(?:@[\s\S]*?)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', cli_source):
        group_var = cm.group(1)
        name = cm.group(2)
        fn = cm.group(3)
        group_name = group_defs.get(group_var, group_var)
        commands.append(
            {
                "type": "command",
                "command": f"{group_name} {name}",
                "group": group_name,
                "function": fn,
                "file": file_path,
                "lineno": cli_source.count("\n", 0, cm.start()) + 1,
            }
        )

    # Find `@cli.group() def X` + nested `@X.command("...")` already captured.
    # Sort and de-dup.
    seen = set()
    uniq = []
    for c in commands:
        key = (c.get("type"), c.get("command"), c.get("function"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return sorted(uniq, key=lambda x: (x.get("type", ""), x.get("command", "")))


def webui_routes_from_pages(repo_root: Path) -> list[dict[str, Any]]:
    base = repo_root / "webui" / "src" / "app"
    if not base.exists():
        return []
    routes: list[dict[str, Any]] = []
    for page in base.rglob("page.tsx"):
        rel = page.relative_to(base).as_posix()  # e.g. "projects/[id]/page.tsx"
        if rel == "page.tsx":
            route = "/"
        else:
            route = "/" + rel[: -len("/page.tsx")]
        # Convert dynamic segments [id] -> :id
        route = re.sub(r"\[([^\]]+)\]", r":\1", route)
        routes.append({"route": route, "file": page.relative_to(repo_root).as_posix()})
    # de-dup
    uniq = {(r["route"], r["file"]): r for r in routes}
    return sorted(uniq.values(), key=lambda x: x["route"])


def extract_public_api_from_init(init_path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"file": init_path.as_posix(), "exports": []}
    if not init_path.exists():
        return out
    src = init_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    try:
                        value = ast.literal_eval(n.value)
                        if isinstance(value, list):
                            out["exports"] = [str(x) for x in value]
                    except Exception:
                        pass
    return out


def build_context_files(repo_root: Path) -> dict[str, str]:
    exports = extract_public_api_from_init(repo_root / "src" / "agentic_assistants" / "__init__.py")
    exported = exports.get("exports", [])

    architecture = """# Agentic Assistants - Architecture (Index Context)

## High-level

- **CLI** (`agentic ...`): local operations (services, sessions, indexing/search, server)
- **FastAPI server**: REST (`/api/v1/*` + legacy endpoints), WebSocket (`/ws`), MCP (`/mcp`)
- **Web UI Control Panel**: Next.js app in `webui/` consuming the REST APIs
- **AgenticEngine**: programmatic façade (sessions, indexing/search, vector store, pipelines, knowledge)
- **LLM Lifecycle**: training, RL/RLHF, serving, data observability

## Key directories

- `src/agentic_assistants/`: Python framework
- `src/agentic_assistants/server/`: FastAPI REST/WS/MCP
- `src/agentic_assistants/training/`: LLM training (LoRA, QLoRA, full)
- `src/agentic_assistants/rl/`: RL/RLHF (DPO, PPO, RLHF)
- `src/agentic_assistants/serving/`: Model serving (Ollama, vLLM, TGI)
- `src/agentic_assistants/data/training/`: Data observability (tagging, lineage, quality)
- `webui/`: Control Panel UI
- `scripts/`: start/stop helpers + index generation
- `docker-compose.yml`, `docker/`, `k8s/`: infra
"""

    api_surface_lines = [
        "# Agentic Assistants - API Surface (Index Context)",
        "",
        "## Public Python exports (`agentic_assistants.__all__`)",
        "",
    ]
    if exported:
        api_surface_lines.extend([f"- `{name}`" for name in exported])
    else:
        api_surface_lines.append("- (could not extract `__all__`)")

    api_surface_lines.extend(
        [
            "",
            "## Primary CLIs",
            "",
            "- `agentic index/search/collections` for vector indexing + search",
            "- `agentic server start` for REST + MCP server",
            "- `agentic context show` for small-context context packs",
            "",
            "## Server endpoint groups",
            "",
            "- `/api/v1/projects`, `/api/v1/agents`, `/api/v1/flows`, `/api/v1/components`",
            "- `/api/v1/datasources` (+ catalog search/stats)",
            "- `/api/v1/pipelines`",
            "- `/api/v1/kubernetes`",
            "- `/api/v1/training` (training jobs, datasets, export, distillation)",
            "- `/api/v1/models/custom` (custom model registry, deployment)",
        ]
    )
    api_surface = "\n".join(api_surface_lines) + "\n"

    patterns = """# Agentic Assistants - Patterns (Index Context)

## Python patterns

- Prefer `AgenticEngine` as the main façade for new programmatic integrations.
- Keep configuration in `AgenticConfig` (env + persisted YAML) rather than ad-hoc globals.
- Server code uses FastAPI routers under `src/agentic_assistants/server/api/` and is assembled in `src/agentic_assistants/server/rest.py`.

## UI patterns

- `webui/src/lib/api.ts` is the primary API client. It uses SWR for caching/mutations.
- Backend URL and API key are stored in browser `localStorage`.

## Indexing patterns

- Vector indexing is chunk-based and stored in vector backends (LanceDB/Chroma).
- This `.index/` directory is file-based and model-agnostic: use it for small-context LLM workflows.
"""

    ollama_assistant = """# Agentic Assistants - Local LLM Usage Notes

## Typical workflow for small-context local LLMs

1. Load `.index/context/*` as your starting context.
2. Use `.index/surfaces/*` to locate relevant CLI commands, endpoints, and UI routes.
3. Use `.index/symbols/*` to jump to the most relevant files/symbols.
4. Pull the matching `.index/chunks/*` files for the exact implementation details.

## Index location

- This repo stores the model-agnostic index under `.index/`.
"""

    return {
        "architecture.md": architecture,
        "api-surface.md": api_surface,
        "patterns.md": patterns,
        "ollama-assistant.md": ollama_assistant,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate `.index/` for this repo.")
    parser.add_argument("--repo-root", default=".", help="Repo root (default: .)")
    parser.add_argument("--output-dir", default=".index", help="Output directory (default: .index)")
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000, help="Max bytes per file to index (default: 1MB)")
    parser.add_argument("--chunk-chars", type=int, default=3000, help="Chunk size in characters (default: 3000)")
    parser.add_argument("--chunk-overlap", type=int, default=300, help="Chunk overlap in characters (default: 300)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_root = (repo_root / args.output_dir).resolve()

    ignore_spec = load_gitignore_spec(repo_root)
    extra_patterns = list(DEFAULT_IGNORE_PATTERNS)

    # Output layout
    context_dir = out_root / "context"
    symbols_dir = out_root / "symbols"
    surfaces_dir = out_root / "surfaces"
    areas_dir = out_root / "areas"
    chunks_dir = out_root / "chunks"

    ensure_dir(out_root)
    ensure_dir(context_dir)
    ensure_dir(symbols_dir)
    ensure_dir(surfaces_dir)
    ensure_dir(areas_dir)
    ensure_dir(chunks_dir)

    files: list[FileRecord] = []
    chunks: list[ChunkRecord] = []
    py_symbols: list[dict[str, Any]] = []
    ts_symbols: list[dict[str, Any]] = []

    # Surfaces to fill
    rest_routes: list[dict[str, Any]] = []
    cli_cmds: list[dict[str, Any]] = []
    web_routes: list[dict[str, Any]] = webui_routes_from_pages(repo_root)

    # Pre-load CLI source if present
    cli_py = repo_root / "src" / "agentic_assistants" / "cli.py"
    if cli_py.exists():
        cli_src = cli_py.read_text(encoding="utf-8", errors="ignore")
        cli_cmds = extract_click_commands(cli_src, cli_py.relative_to(repo_root).as_posix())

    # Pre-load server routes if present
    rest_py = repo_root / "src" / "agentic_assistants" / "server" / "rest.py"
    if rest_py.exists():
        rest_src = rest_py.read_text(encoding="utf-8", errors="ignore")
        rest_routes.extend(extract_fastapi_routes_from_app(rest_src, rest_py.relative_to(repo_root).as_posix()))
    server_api_dir = repo_root / "src" / "agentic_assistants" / "server" / "api"
    if server_api_dir.exists():
        for f in sorted(server_api_dir.glob("*.py")):
            src = f.read_text(encoding="utf-8", errors="ignore")
            rest_routes.extend(extract_fastapi_routes_from_router(src, f.relative_to(repo_root).as_posix()))

    # Index files + chunks + symbols
    for path in iter_repo_files(repo_root, ignore_spec, extra_patterns):
        try:
            st = path.stat()
        except OSError:
            continue
        rel = path.relative_to(repo_root).as_posix()

        if st.st_size > args.max_file_bytes:
            # Still record metadata, but skip content-heavy steps.
            files.append(
                FileRecord(
                    path=rel,
                    sha256="",
                    size_bytes=st.st_size,
                    mtime_epoch=st.st_mtime,
                    language=detect_language(path),
                    line_count=None,
                    binary=True,
                )
            )
            continue

        raw = path.read_bytes()
        binary = is_probably_binary(raw)
        lang = detect_language(path)
        digest = sha256_bytes(raw) if raw else sha256_bytes(b"")

        if binary:
            files.append(
                FileRecord(
                    path=rel,
                    sha256=digest,
                    size_bytes=st.st_size,
                    mtime_epoch=st.st_mtime,
                    language=lang,
                    line_count=None,
                    binary=True,
                )
            )
            continue

        text = raw.decode("utf-8", errors="replace")
        line_count = text.count("\n") + 1 if text else 0
        files.append(
            FileRecord(
                path=rel,
                sha256=digest,
                size_bytes=st.st_size,
                mtime_epoch=st.st_mtime,
                language=lang,
                line_count=line_count,
                binary=False,
            )
        )

        # Chunk file
        file_chunks = chunk_text_by_chars(text, args.chunk_chars, args.chunk_overlap)
        total = len(file_chunks)
        for i, (start_line, end_line, chunk_text) in enumerate(file_chunks):
            chunk_id = f"{digest[:12]}_{i}"
            chunk_rel_path = f"chunks/{chunk_id}.md"
            chunk_abs = out_root / chunk_rel_path
            chunk_sha = sha256_bytes(chunk_text.encode("utf-8"))
            write_text(
                chunk_abs,
                "\n".join(
                    [
                        f"# Chunk: {chunk_id}",
                        "",
                        f"- source: `{rel}`",
                        f"- lines: {start_line}-{end_line}",
                        f"- chunk: {i + 1}/{total}",
                        "",
                        "```",
                        chunk_text.rstrip("\n"),
                        "```",
                        "",
                    ]
                ),
            )
            chunks.append(
                ChunkRecord(
                    id=chunk_id,
                    path=chunk_rel_path,
                    source_path=rel,
                    chunk_index=i,
                    total_chunks=total,
                    start_line=start_line,
                    end_line=end_line,
                    sha256=chunk_sha,
                )
            )

        # Symbols
        if lang == "python" and path.suffix.lower() == ".py":
            py_symbols.append(extract_python_symbols(Path(rel), text))
        elif lang in {"typescript", "javascript"} and path.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
            ts_symbols.append(extract_ts_symbols(Path(rel), text))

    # Write surfaces
    write_json(surfaces_dir / "cli_commands.json", {"generated_at": utc_now_iso(), "commands": cli_cmds})
    write_text(
        surfaces_dir / "cli_commands.md",
        "\n".join(
            [
                "# CLI Commands",
                "",
                "Generated from `src/agentic_assistants/cli.py`.",
                "",
                "```json",
                json.dumps(cli_cmds[:50], indent=2, ensure_ascii=False),
                "```",
                "",
                f"(Total commands/groups: {len(cli_cmds)})",
                "",
            ]
        ),
    )

    write_json(surfaces_dir / "rest_endpoints.json", {"generated_at": utc_now_iso(), "endpoints": rest_routes})
    write_text(
        surfaces_dir / "rest_endpoints.md",
        "\n".join(
            [
                "# REST Endpoints",
                "",
                "Generated from `src/agentic_assistants/server/rest.py` and `src/agentic_assistants/server/api/*.py`.",
                "",
                "```json",
                json.dumps(rest_routes[:50], indent=2, ensure_ascii=False),
                "```",
                "",
                f"(Total endpoints: {len(rest_routes)})",
                "",
            ]
        ),
    )

    write_json(surfaces_dir / "webui_routes.json", {"generated_at": utc_now_iso(), "routes": web_routes})
    write_text(
        surfaces_dir / "webui_routes.md",
        "\n".join(
            [
                "# Web UI Routes (Next.js app router)",
                "",
                "Generated from `webui/src/app/**/page.tsx`.",
                "",
                "```json",
                json.dumps(web_routes, indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        ),
    )

    # Write symbols
    write_json(symbols_dir / "python_symbols.json", {"generated_at": utc_now_iso(), "files": py_symbols})
    write_json(symbols_dir / "ts_symbols.json", {"generated_at": utc_now_iso(), "files": ts_symbols})

    # Write areas (structured, non-LLM summaries)
    write_text(
        areas_dir / "python_engine.md",
        "\n".join(
            [
                "# Python Area: Engine",
                "",
                "- Entry point: `src/agentic_assistants/engine.py`",
                "- Concept: façade for sessions, indexing/search, vector store, pipelines, chat",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_server.md",
        "\n".join(
            [
                "# Python Area: Server",
                "",
                "- REST assembly: `src/agentic_assistants/server/rest.py`",
                "- Combined app (REST + MCP): `src/agentic_assistants/server/app.py`",
                "- Routers: `src/agentic_assistants/server/api/*.py`",
                "- WebSocket: `src/agentic_assistants/server/websocket.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_indexing.md",
        "\n".join(
            [
                "# Python Area: Indexing",
                "",
                "- Chunker: `src/agentic_assistants/indexing/chunker.py`",
                "- Indexer: `src/agentic_assistants/indexing/codebase.py`",
                "- Loader: `src/agentic_assistants/indexing/loader.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_vectordb.md",
        "\n".join(
            [
                "# Python Area: Vector DB",
                "",
                "- Interface: `src/agentic_assistants/vectordb/base.py`",
                "- Backends: `src/agentic_assistants/vectordb/*`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_pipelines.md",
        "\n".join(
            [
                "# Python Area: Pipelines",
                "",
                "- Pipeline: `src/agentic_assistants/pipelines/pipeline.py`",
                "- Node: `src/agentic_assistants/pipelines/node.py`",
                "- Runners: `src/agentic_assistants/pipelines/runners/*`",
                "- Templates: `src/agentic_assistants/pipelines/templates/*`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_knowledge.md",
        "\n".join(
            [
                "# Python Area: Knowledge Bases",
                "",
                "- Base: `src/agentic_assistants/knowledge/base.py`",
                "- Vector/RAG/Hybrid: `src/agentic_assistants/knowledge/*_kb.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_kubernetes.md",
        "\n".join(
            [
                "# Python Area: Kubernetes",
                "",
                "- Client + models: `src/agentic_assistants/kubernetes/*`",
                "- REST router: `src/agentic_assistants/server/api/kubernetes.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "webui_app.md",
        "\n".join(
            [
                "# Web UI Area: Control Panel",
                "",
                "- App router pages: `webui/src/app/*`",
                "- API hooks: `webui/src/lib/api.ts`",
                "",
                "## Page inventory",
                "```json",
                json.dumps(web_routes, indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "infra_docker_k8s.md",
        "\n".join(
            [
                "# Infra Area: Docker + Kubernetes",
                "",
                "- Docker Compose: `docker-compose.yml`",
                "- Dockerfiles: `docker/`",
                "- Kubernetes: `k8s/` (kustomize)",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_training.md",
        "\n".join(
            [
                "# Python Area: LLM Training",
                "",
                "- Config: `src/agentic_assistants/training/config.py`",
                "- Jobs: `src/agentic_assistants/training/jobs.py`",
                "- Datasets: `src/agentic_assistants/training/datasets.py`",
                "- Frameworks: `src/agentic_assistants/training/frameworks/*`",
                "- Export: `src/agentic_assistants/training/export.py`",
                "- Quantization: `src/agentic_assistants/training/quantization.py`",
                "- Distillation: `src/agentic_assistants/training/distillation.py`",
                "- REST router: `src/agentic_assistants/server/api/training.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_rl.md",
        "\n".join(
            [
                "# Python Area: Reinforcement Learning",
                "",
                "- Config: `src/agentic_assistants/rl/config.py`",
                "- Experiments: `src/agentic_assistants/rl/experiments.py`",
                "- Adapters: `src/agentic_assistants/rl/adapters/*`",
                "- TRL integration: `src/agentic_assistants/rl/adapters/trl_adapter.py`",
                "",
                "## Supported Methods",
                "- DPO (Direct Preference Optimization)",
                "- PPO (Proximal Policy Optimization)",
                "- RLHF (Reinforcement Learning from Human Feedback)",
                "- ORPO, KTO",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_serving.md",
        "\n".join(
            [
                "# Python Area: Model Serving",
                "",
                "- Config: `src/agentic_assistants/serving/config.py`",
                "- Manager: `src/agentic_assistants/serving/manager.py`",
                "- Backends: `src/agentic_assistants/serving/backends/*`",
                "- Ollama backend: `src/agentic_assistants/serving/backends/ollama.py`",
                "- REST router: `src/agentic_assistants/server/api/models.py`",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_data_observability.md",
        "\n".join(
            [
                "# Python Area: Data Observability",
                "",
                "- Tagging: `src/agentic_assistants/data/training/tagging.py`",
                "- Lineage: `src/agentic_assistants/data/training/lineage.py`",
                "- Quality: `src/agentic_assistants/data/training/quality.py`",
                "",
                "## Features",
                "- Hierarchical data tagging system",
                "- Data lineage tracking for models",
                "- Quality metrics and validation",
                "",
            ]
        ),
    )
    write_text(
        areas_dir / "python_integrations.md",
        "\n".join(
            [
                "# Python Area: External Integrations",
                "",
                "- HuggingFace Hub: `src/agentic_assistants/integrations/huggingface.py`",
                "- Jupyter: `src/agentic_assistants/integrations/jupyter.py`",
                "- Kedro/Kubernetes: `src/agentic_assistants/integrations/kedro_kubernetes.py`",
                "",
            ]
        ),
    )

    # Context files (required by ContextLoader)
    context = build_context_files(repo_root)
    for name, content in context.items():
        write_text(context_dir / name, content)

    # README for `.index/`
    write_text(
        out_root / "README.md",
        "\n".join(
            [
                "# `.index/`",
                "",
                "This directory contains a **model-agnostic** index of the repo for small-context local LLM workflows.",
                "",
                "## Key files",
                "",
                "- `manifest.json`: file inventory + chunk inventory",
                "- `context/*`: small context packs (consumed by `ContextLoader` / `agentic context show`)",
                "- `surfaces/*`: CLI commands, REST endpoints, Web UI routes",
                "- `symbols/*`: Python + TS/TSX symbol tables",
                "- `chunks/*`: chunked file contents (Markdown)",
                "",
                "## Regenerate",
                "",
                "```bash",
                "python scripts/generate_index.py",
                "```",
                "",
            ]
        ),
    )

    # Manifest
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "repo_root": repo_root.as_posix(),
        "output_dir": out_root.relative_to(repo_root).as_posix(),
        "config": {
            "max_file_bytes": args.max_file_bytes,
            "chunk_chars": args.chunk_chars,
            "chunk_overlap": args.chunk_overlap,
        },
        "ignore": {
            "gitignore_loaded": bool(ignore_spec is not None),
            "extra_patterns": extra_patterns,
        },
        "stats": {
            "files_total": len(files),
            "chunks_total": len(chunks),
            "python_symbol_files": len(py_symbols),
            "ts_symbol_files": len(ts_symbols),
            "rest_endpoints": len(rest_routes),
            "cli_entries": len(cli_cmds),
            "webui_routes": len(web_routes),
        },
        "files": [f.__dict__ for f in files],
        "chunks": [c.__dict__ for c in chunks],
        "paths": {
            "context_dir": "context",
            "symbols_dir": "symbols",
            "surfaces_dir": "surfaces",
            "areas_dir": "areas",
            "chunks_dir": "chunks",
        },
    }
    write_json(out_root / "manifest.json", manifest)

    # Small smoke message for humans
    print(f"Wrote: {out_root.relative_to(repo_root)} (files={len(files)}, chunks={len(chunks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

