from flask import request, Response
try:
    from graph import run_classification_only
    from services.data_loader import load_sample_tickets
except ImportError:
    from backend.graph import run_classification_only
    from backend.services.data_loader import load_sample_tickets
from typing import List, Dict, Any
import json

def bulk_classify_stream():
    """
    Input: { "tickets": [ {"id": "...", "subject": "...", "body": "..."}, ... ] }
    Output: Server-Sent Events stream with individual ticket results
    If no body provided, will attempt to load from sample tickets
    """
    if request.method == "OPTIONS":
        return ("", 200)

    payload = request.json or {}
    tickets: List[Dict[str, Any]] = payload.get("tickets", [])

    if not tickets:
        tickets = load_sample_tickets()
        if not tickets:
            return Response(
                json.dumps({"error": "No tickets provided and no sample tickets found"}),
                status=400,
                mimetype='application/json'
            )

    def generate_stream():
        yield f"data: {json.dumps({'type': 'start', 'total': len(tickets)})}\n\n"
        
        for i, ticket in enumerate(tickets):
            try:
                text = f"{ticket.get('subject','')}\n{ticket.get('body','')}".strip()
                result = run_classification_only(text)
                result["classification"]["original_question"] = text
                
                ticket_result = {
                    "id": ticket.get("id"),
                    "classification": result["classification"],
                    "index": i,
                    "total": len(tickets)
                }
                
                yield f"data: {json.dumps({'type': 'ticket', 'data': ticket_result})}\n\n"
                
            except Exception as e:
                error_result = {
                    "id": ticket.get("id"),
                    "error": str(e),
                    "index": i,
                    "total": len(tickets)
                }
                yield f"data: {json.dumps({'type': 'error', 'data': error_result})}\n\n"
        
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )