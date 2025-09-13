from flask import request, jsonify
try:
    from graph import run_classification_only
    from services.data_loader import load_sample_tickets
except ImportError:
    from backend.graph import run_classification_only
    from backend.services.data_loader import load_sample_tickets
from typing import List, Dict, Any

def bulk_classify():
    """
    Input: { "tickets": [ {"id": "...", "subject": "...", "body": "..."}, ... ] }
    Output: { "results": [ {"id": "...", "classification": {...}}, ... ] }
    If no body provided, will attempt to load from sample tickets
    """
    if request.method == "OPTIONS":
        return ("", 200)

    payload = request.json or {}
    tickets: List[Dict[str, Any]] = payload.get("tickets", [])

    if not tickets:
        tickets = load_sample_tickets()
        if not tickets:
            return jsonify({"error": "No tickets provided and no sample tickets found"}), 400

    try:
        results = []
        for ticket in tickets:
            text = f"{ticket.get('subject','')}\n{ticket.get('body','')}".strip()
            result = run_classification_only(text)
            result["classification"]["original_question"] = text
            results.append({
                "id": ticket.get("id"),
                "classification": result["classification"]
            })

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Bulk classification failed: {str(e)}"}), 500
