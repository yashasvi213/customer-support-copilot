import os
from dotenv import load_dotenv
import getpass
from backend.graph import run_rag_graph

load_dotenv()

# Load API keys interactively if missing
if not os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter LangSmith API key: ")
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter OpenAI API key: ")

if __name__ == "__main__":
    while True:
        question = input("What is your query?\n> ").strip()
        if question.lower() in ["quit", "exit"]:
            break
        response = run_rag_graph(question)
        print("\nAnswer:", response)