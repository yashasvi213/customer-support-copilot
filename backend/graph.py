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

class AnswerConfidence(BaseModel):
    confidence: float = Field(description="Confidence 0-1 that the generated answer is correct and grounded")

structured_llm = llm.with_structured_output(Classification)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    answer_confidence: float
    classification: dict

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    answer_msg = llm.invoke(messages)

    # Confidence scoring for the generated answer
    confidence_prompt = ChatPromptTemplate.from_template(
        """
        You are evaluating the quality of an assistant's answer given retrieved context.
        Score a single number 'confidence' from 0 to 1 (float) for how well the answer is grounded,
        accurate, and complete according to the provided context.
        Return only the 'confidence' field.

        Question:\n{question}\n\nContext:\n{context}\n\nAnswer:\n{answer}
        """
    )
    conf_messages = confidence_prompt.invoke({
        "question": state["question"],
        "context": docs_content,
        "answer": answer_msg.content,
    })
    conf_llm = llm.with_structured_output(AnswerConfidence)
    conf_resp = conf_llm.invoke(conf_messages)

    return {"answer": answer_msg.content, "answer_confidence": float(getattr(conf_resp, 'confidence', 0.0))}

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

def run_rag_graph(question: str) -> dict:
    """Call this from rag_agent.py"""
    response = graph.invoke({"question": question})
    # Try to collect source URLs/identifiers from context metadata
    sources = []
    try:
        ctx = response.get("context", [])
        for d in ctx:
            meta = getattr(d, 'metadata', {}) or {}
            src = meta.get('source') or meta.get('url') or meta.get('path')
            if src:
                sources.append(src)
    except Exception:
        pass
    return {
        "answer": response.get("answer", ""),
        "confidence": response.get("answer_confidence", 0.0),
        "sources": sources,
    }
