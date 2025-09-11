import os
import getpass
from typing_extensions import TypedDict, List
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()

if not os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter LangSmith API key: ")
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter OpenAI API key: ")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

prompt = hub.pull("rlm/rag-prompt")

tag_list = [
    "How-to", "Product", "Connector", "Lineage", "API/SDK", "SSO",
    "Glossary", "Best practices", "Sensitive data", "Bug", "Permissions"
]

tagging_prompt = ChatPromptTemplate.from_template(
    """
Extract the desired information from the following passage.

Only extract the properties mentioned in the 'Classification' function.

Passage:
{input}
"""
)

class Classification(BaseModel):
    label: List[str] = Field(
        description=f"The topic tags of the ticket. Only choose from: {tag_list}"
    )
    sentiment: str = Field(description="The sentiment of the ticket, e.g., 'Frustrated'")
    priority: str = Field(description="The priority level, e.g., 'P0'")

structured_llm = llm.with_structured_output(Classification)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    classification: dict

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

def classify(state: State):
    classification_prompt = tagging_prompt.invoke({"input": state["question"]})
    response = structured_llm.invoke(classification_prompt)
    return {"classification": response.model_dump()}

graph_builder = StateGraph(State)

graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_node("classify", classify)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", "classify")

graph = graph_builder.compile()

def run_rag_graph(question: str) -> str:
    """Call this from rag_agent.py"""
    response = graph.invoke({"question": question})
    return response.get("answer", "")
