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

def resolve_query(classification_output: Dict) -> ResolutionOutput:
    """
    Decides what to do with a query based on its classification.
    - If labels indicate a knowledge base lookup is needed (e.g., "How-to", "Product", "Best practices") → Use RAG
    - Others → No action (for now)
    """
    
    # Extract classified labels
    labels = classification_output.get('label', [])
    priority = classification_output.get('priority', 'P2')
    
    # Define which labels should trigger RAG
    rag_labels = {'How-to', 'Product', 'Best practices'}
    
    # Check if any of the classified labels suggest using RAG
    needs_rag = bool(set(labels) & rag_labels)
    
    if needs_rag:
        try:
            # Get the original question from classification output
            question = classification_output.get('original_question', '')
            response = run_rag_graph(question)
            return ResolutionOutput(
                needs_rag=True,
                response=response,
                reason=f"Query contains labels {labels} that require knowledge base lookup"
            )
        except Exception as e:
            return ResolutionOutput(
                needs_rag=True,
                response=None,
                reason=f"RAG attempted but failed: {str(e)}"
            )
    
    return ResolutionOutput(
        needs_rag=False,
        response=None,
        reason=f"Query with labels {labels} doesn't require knowledge base lookup"
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