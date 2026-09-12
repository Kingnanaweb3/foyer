"""CLI entry point for local testing. Run: python main.py"""
import logging

# The Groq endpoint can't carry reasoning traces across turns and warns on
# every call. Harmless, but it drowns the actual replies, so quiet it.
logging.getLogger("strands").setLevel(logging.ERROR)

from orchestrator import foyer


def main():
    print("Foyer is ready. Type a message (or 'quit' to exit).\n")
    while True:
        message = input("> ")
        if message.strip().lower() in {"quit", "exit"}:
            break
        print(foyer(message))
        print()


if __name__ == "__main__":
    main()
