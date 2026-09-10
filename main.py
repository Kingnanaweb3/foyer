"""CLI entry point for local testing. Run: python main.py"""
from orchestrator import foyer

def main():
    print("Foyer is ready. Type a message (or 'quit' to exit).\n")
    while True:
        message = input("> ")
        if message.strip().lower() in {"quit", "exit"}:
            break
        result = foyer(message)
        print(result)

if __name__ == "__main__":
    main()
