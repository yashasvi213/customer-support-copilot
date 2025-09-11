from flask import Flask, request, jsonify
from backend.graph import run_rag_graph
from backend.resolution import resolve_query
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Optional: fail fast if API keys missing
if not os.getenv("OPENAI_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
    raise EnvironmentError("Missing API keys in environment")

@app.route("/classify", methods=["POST"])
def classify_ticket():
    """
    Input: { "question": "..." }
    Output: { "classification": {...} }
    """
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Use structured classification from graph
    from backend.graph import graph  # Your existing graph
    classification_output = graph.invoke({"question": question}).get("classification", {})
    classification_output["original_question"] = question
    return jsonify({"classification": classification_output})


@app.route("/resolve", methods=["POST"])
def resolve_query_api():
    """
    Input: { "classification": {...} }
    Output: { "needs_rag": True/False, "response": "...", "reason": "..." }
    """
    data = request.json
    classification_output = data.get("classification", {})
    if not classification_output:
        return jsonify({"error": "Classification data required"}), 400

    result = resolve_query(classification_output)
    return jsonify(result.model_dump())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
