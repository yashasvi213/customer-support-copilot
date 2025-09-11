from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.graph import run_rag_graph
from backend.resolution import resolve_query
from typing import List, Dict, Any
import json
import os
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Optional: fail fast if API keys missing
if not os.getenv("OPENAI_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
    raise EnvironmentError("Missing API keys in environment")

# Enable CORS for frontend dev server
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

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


@app.route("/resolve", methods=["POST", "OPTIONS"])
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

    result = resolve_query(classification_output)
    return jsonify(result.model_dump())

# Bulk classification endpoint
@app.route("/bulk_classify", methods=["POST", "OPTIONS"])
def bulk_classify():
    """
    Input: { "tickets": [ {"id": "...", "subject": "...", "body": "..."}, ... ] }
    Output: { "results": [ {"id": "...", "classification": {...}}, ... ] }
    If no body provided, will attempt to load from root ./sample_tickets.json or backend/sample_tickets.json
    """
    if request.method == "OPTIONS":
        return ("", 200)
    payload = request.json or {}
    tickets: List[Dict[str, Any]] = payload.get("tickets", [])
    load_errors: List[str] = []

    if not tickets:
        # prefer repo root sample, fallback to backend/sample_tickets.json
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "sample_tickets.json"))
        backend_path = os.path.join(os.path.dirname(__file__), "sample_tickets.json")
        for sample_path in [root_path, backend_path]:
            if os.path.exists(sample_path):
                try:
                    with open(sample_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list) and data:
                            tickets = data
                            break
                except Exception as e:
                    load_errors.append(f"Failed loading {sample_path}: {str(e)}")

    if not tickets:
        return jsonify({"error": "No tickets provided", "load_errors": load_errors}), 400

    from backend.graph import graph
    results = []
    for t in tickets:
        text = f"{t.get('subject','')}\n{t.get('body','')}".strip()
        classification_output = graph.invoke({"question": text}).get("classification", {})
        classification_output["original_question"] = text
        results.append({
            "id": t.get("id"),
            "classification": classification_output
        })

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
