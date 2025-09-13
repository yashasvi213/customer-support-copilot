from flask import request, jsonify
try:
    from graph import run_rag_graph
except ImportError:
    from backend.graph import run_rag_graph

def resolve_query_api():
    """
    Input: { "classification": {...} }
    Output: { "needs_rag": True/False, "response": "...", "reason": "..." }
    """
    if request.method == "OPTIONS":
        return ("", 200)

    data = request.json
    classification_output = data.get("classification", {})
    if not classification_output:
        return jsonify({"error": "Classification data required"}), 400

    try:
        question = classification_output.get('original_question', '')
        if not question:
            return jsonify({"error": "Original question required for resolution"}), 400
        
        result = run_rag_graph(question)
        
        needs_rag = result.get("resolution_decision", {}).get("needs_rag", False)
        confidence = result.get("confidence", 0.0)
        final_response = result.get("final_response", "")
        
        if needs_rag:
            if confidence >= 0.75:
                reason = f"High confidence ({confidence:.2f}) RAG answer."
            elif confidence >= 0.4:
                reason = f"Medium confidence ({confidence:.2f}). Sent templated reply and queued human review."
            else:
                reason = f"Low confidence ({confidence:.2f}). Escalated to human team with context."
                final_response = None
        else:
            reason = f"No RAG needed for labels {classification_output.get('label', [])}"
            final_response = result.get("final_response", "")

        return jsonify({
            "needs_rag": needs_rag,
            "response": final_response,
            "reason": reason,
            "answer_confidence": confidence,
            "routing_team": result.get("resolution_decision", {}).get("routing_team", "General Support")
        })
    except Exception as e:
        return jsonify({"error": f"Resolution failed: {str(e)}"}), 500