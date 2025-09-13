import os
from dotenv import load_dotenv
import getpass
try:
    from graph import run_rag_graph
except ImportError:
    from backend.graph import run_rag_graph

load_dotenv()

# Environment variables should be set via Docker or .env file
if not os.getenv("LANGSMITH_API_KEY"):
    raise EnvironmentError("LANGSMITH_API_KEY environment variable is required")
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY environment variable is required")

if __name__ == "__main__":
    while True:
        question = input("What is your query?\n> ").strip()
        if question.lower() in ["quit", "exit"]:
            break
        response = run_rag_graph(question)
        print("\nAnswer:", response)