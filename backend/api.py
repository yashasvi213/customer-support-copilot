from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import endpoint handlers
try:
    # For Docker deployment (files copied to /app)
    from endpoints.classify import classify_ticket
    from endpoints.resolve import resolve_query_api
    from endpoints.bulk_classify import bulk_classify
    from endpoints.bulk_classify_stream import bulk_classify_stream
    from endpoints.reports import generate_reports
except ImportError:
    # For local development (from backend directory)
    from backend.endpoints.classify import classify_ticket
    from backend.endpoints.resolve import resolve_query_api
    from backend.endpoints.bulk_classify import bulk_classify
    from backend.endpoints.bulk_classify_stream import bulk_classify_stream
    from backend.endpoints.reports import generate_reports

load_dotenv()

app = Flask(__name__)

# Check for API keys but don't fail if missing (for testing)
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not set")
if not os.getenv("LANGSMITH_API_KEY"):
    print("WARNING: LANGSMITH_API_KEY not set")


CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "service": "customer-support-copilot-backend"}, 200

app.add_url_rule("/classify", "classify_ticket", classify_ticket, methods=["POST"])
app.add_url_rule("/resolve", "resolve_query_api", resolve_query_api, methods=["POST", "OPTIONS"])
app.add_url_rule("/bulk_classify", "bulk_classify", bulk_classify, methods=["POST", "OPTIONS"])
app.add_url_rule("/bulk_classify_stream", "bulk_classify_stream", bulk_classify_stream, methods=["POST", "OPTIONS"])
app.add_url_rule("/reports", "generate_reports", generate_reports, methods=["POST", "OPTIONS"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app on port {port}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'not set')}")
    app.run(host="0.0.0.0", port=port, debug=False)
