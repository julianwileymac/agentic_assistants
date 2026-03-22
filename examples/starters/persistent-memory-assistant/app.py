"""Persistent memory assistant starter."""

from agentic_assistants.memory import get_memory_store


def main() -> None:
    memory = get_memory_store(backend="mem0", user_id="demo-user")
    memory.add_memory("User likes concise architecture summaries.", metadata={"type": "preference"})
    hits = memory.search_memories("summary preference", limit=3)
    print(f"Memories found: {hits.total}")


if __name__ == "__main__":
    main()

