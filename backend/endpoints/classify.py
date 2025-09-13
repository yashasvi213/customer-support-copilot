from flask import request, jsonify
try:
    from graph import run_classification_only
except ImportError:
    from backend.graph import run_classification_only

def classify_ticket():
    #Input : question
    #Output : classification
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        result = run_classification_only(question)
        result["classification"]["original_question"] = question
        return jsonify({"classification": result["classification"]})
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500