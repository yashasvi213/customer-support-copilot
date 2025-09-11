import os
import sys
from typing import Dict, Optional
from pydantic import BaseModel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph import run_rag_graph

class ResolutionOutput(BaseModel):
    needs_rag: bool
    response: Optional[str] = None
    reason: str
    routed_message: Optional[str] = None
    answer_confidence: Optional[float] = None

def resolve_query(classification_output: Dict) -> ResolutionOutput:
    """
    Decides what to do with a query based on its classification.
    - If labels indicate a knowledge base lookup is needed ("How-to", "Product", "Best practices", "API/SDK", "SSO") → Use RAG
    - Otherwise → Return routed message
    Confidence decisioning:
      - confidence >= 0.75 → send direct answer
      - 0.4 <= confidence < 0.75 → send templated reply to customer and queue for human review
      - confidence < 0.4 → escalate to human team with context (no customer answer)
    """
    
    # Extract classified labels
    labels = classification_output.get('label', [])
    priority = classification_output.get('priority', 'P2')
    
    # Define which labels should trigger RAG
    rag_labels = {'How-to', 'Product', 'Best practices', 'API/SDK', 'SSO'}
    
    # Check if any of the classified labels suggest using RAG
    needs_rag = bool(set(labels) & rag_labels)
    
    if needs_rag:
        try:
            # Get the original question from classification output
            question = classification_output.get('original_question', '')
            rag = run_rag_graph(question)
            confidence = float(rag.get("confidence", 0.0))
            answer = rag.get("answer")
            sources = rag.get("sources") or []

            if confidence >= 0.75:
                text = answer
                if sources:
                    text += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources[:5])
                return ResolutionOutput(
                    needs_rag=True,
                    response=text,
                    reason=f"High confidence ({confidence:.2f}) RAG answer.",
                    answer_confidence=confidence,
                )
            elif confidence >= 0.4:
                templated = (
                    "Thanks for reaching out! We believe the following may resolve your issue. "
                    "A specialist will also review and follow up if needed.\n\n" + (answer or "")
                )
                if sources:
                    templated += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources[:5])
                return ResolutionOutput(
                    needs_rag=True,
                    response=templated,
                    reason=f"Medium confidence ({confidence:.2f}). Sent templated reply and queued human review.",
                    answer_confidence=confidence,
                )
            else:
                return ResolutionOutput(
                    needs_rag=True,
                    response=None,
                    reason=f"Low confidence ({confidence:.2f}). Escalated to human team with context.",
                    answer_confidence=confidence,
                )
        except Exception as e:
            return ResolutionOutput(
                needs_rag=True,
                response=None,
                reason=f"RAG attempted but failed: {str(e)}"
            )
    
    # Build routed message for non-RAG topics
    routed_topic = labels[0] if isinstance(labels, list) and labels else 'General'
    routed_message = (
        f"This ticket has been classified as a '{routed_topic}' issue and routed to the appropriate team."
    )

    return ResolutionOutput(
        needs_rag=False,
        response=None,
        reason=f"No RAG needed for labels {labels}",
        routed_message=routed_message
    )

# Example usage
if __name__ == "__main__":
    sample_classification = {
        'label': ['How-to', 'Product'],
        'sentiment': 'Neutral',
        'priority': 'P1',
        'original_question': 'How do I connect Snowflake to Atlan?'
    }
    
    result = resolve_query(sample_classification)
    print(f"Resolution Output:\n{result.model_dump()}")