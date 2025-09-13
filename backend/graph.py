import os
import getpass
from typing_extensions import TypedDict, List
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()

# Environment variables should be set via Docker or .env file
if not os.getenv("LANGSMITH_API_KEY"):
    raise EnvironmentError("LANGSMITH_API_KEY environment variable is required")
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY environment variable is required")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_langchain_db"),
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
confidence_llm = llm.with_structured_output(AnswerConfidence)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    answer_confidence: float
    classification: dict
    resolution_decision: dict
    final_response: str
    sources: List[str]

def classify(state: State):
    classification_prompt = tagging_prompt.invoke({"input": state["question"]})
    response = structured_llm.invoke(classification_prompt)
    return {"classification": response.model_dump()}

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    answer_msg = llm.invoke(messages)
    return {"answer": answer_msg.content}

def evaluate_confidence(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
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
        "answer": state["answer"],
    })
    conf_resp = confidence_llm.invoke(conf_messages)
    return {"answer_confidence": float(getattr(conf_resp, 'confidence', 0.0))}

def resolve_and_format(state: State):
    # Decision logic
    labels = state["classification"].get('label', [])
    confidence = state.get("answer_confidence", 0.0)
    
    rag_labels = {'How-to', 'Product', 'Best practices', 'API/SDK', 'SSO'}
    needs_rag = bool(set(labels) & rag_labels)
    
    if 'Bug' in labels:
        routing_team = 'Engineering'
    elif 'Permissions' in labels or 'SSO' in labels:
        routing_team = 'Security'
    elif 'Connector' in labels or 'Lineage' in labels:
        routing_team = 'Data Engineering'
    else:
        routing_team = 'General Support'
    
    # Extract sources
    sources = []
    try:
        ctx = state.get("context", [])
        for d in ctx:
            meta = getattr(d, 'metadata', {}) or {}
            src = meta.get('source') or meta.get('url') or meta.get('path')
            if src:
                sources.append(src)
    except Exception:
        pass
    
    # Format response
    answer = state.get("answer", "")
    
    if not needs_rag:
        routed_topic = labels[0] if labels else 'General'
        final_response = f"This ticket has been classified as a '{routed_topic}' issue and routed to the {routing_team} team."
    else:
        if confidence >= 0.75:
            final_response = answer
            if sources:
                final_response += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources[:5])
        elif confidence >= 0.4:
            final_response = (
                "Thanks for reaching out! We believe the following may resolve your issue. "
                "A specialist will also review and follow up if needed.\n\n" + answer
            )
            if sources:
                final_response += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources[:5])
        else:
            final_response = f"This query has been escalated to the {routing_team} team for specialized assistance."
    
    return {
        "resolution_decision": {
            "needs_rag": needs_rag,
            "confidence_threshold": confidence,
            "routing_team": routing_team
        },
        "sources": sources,
        "final_response": final_response
    }

graph_builder = StateGraph(State)

graph_builder.add_node("classify", classify)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_node("evaluate_confidence", evaluate_confidence)
graph_builder.add_node("resolve_and_format", resolve_and_format)

graph_builder.add_edge(START, "classify")
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("classify", "generate")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", "evaluate_confidence")
graph_builder.add_edge("evaluate_confidence", "resolve_and_format")
graph_builder.add_edge("resolve_and_format", END)

graph = graph_builder.compile()

def run_rag_graph(question: str) -> dict:
    response = graph.invoke({"question": question})
    return {
        "answer": response.get("answer", ""),
        "confidence": response.get("answer_confidence", 0.0),
        "sources": response.get("sources", []),
        "classification": response.get("classification", {}),
        "resolution_decision": response.get("resolution_decision", {}),
        "final_response": response.get("final_response", "")
    }

def run_classification_only(question: str) -> dict:
    response = graph.invoke({"question": question})
    return {
        "classification": response.get("classification", {}),
        "resolution_decision": response.get("resolution_decision", {})
    }

import matplotlib.pyplot as plt
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
print("Graph saved as graph.png")