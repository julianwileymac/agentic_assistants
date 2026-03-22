"""Quickstart chat loop."""

from agentic_assistants import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager


def main() -> None:
    config = AgenticConfig()
    ollama = OllamaManager(config)
    if not ollama.is_running():
        print("Ollama is not running. Start it with: agentic ollama start")
        return

    print("Type 'exit' to quit.")
    while True:
        prompt = input("you> ").strip()
        if not prompt or prompt.lower() == "exit":
            break
        response = ollama.chat([{"role": "user", "content": prompt}])
        print(f"assistant> {response['message']['content']}\n")


if __name__ == "__main__":
    main()

