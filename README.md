# Customer Support Copilot

An **AI-powered support assistant** that ingests, classifies, and responds to customer support tickets. It enhances user experience by automating responses, categorizing tickets, and prioritizing customer needs while working alongside the human support team.

---

## 🎯 Goals

* **Efficient Ticket Handling** → Reduce manual effort by automating classification & analysis.
* **Prioritize Urgent Needs** → Detect sentiment (frustration/urgency) and escalate faster.
* **Faster, Accurate Responses** → Use AI (docs + APIs) to auto-answer common queries.
* **Scalable Support** → Handle more customers & tickets without overwhelming the team.

---

## 🏗️ System Overview
<p align="center">
  <img src="https://i.postimg.cc/D06r0NgT/Screenshot-from-2025-09-14-12-12-03.png" alt="AI Pipeline Nodes"/>
</p>

### Optimisation

* **Parallel Processing** → Classification & retrieval run simultaneously.
* **Optimized LangGraph Workflow** → Efficient, modular AI pipeline.
* **Streaming Support** → Real-time ticket processing & smoother UX.

### Evaluation

* **Performance Metrics** → Accuracy of classification, processing time.
* **Visualizations** → Charts for topic distribution, confidence scores.
* **Reports** → JSON-based detailed reports for analysis.

### Modularity

* **Separate Endpoints** → Each API function isolated for maintainability.
* **Service Layer** → Clean separation of business logic from API handlers.
* **Clear Dependencies** → Independent, testable components.

---

## 🔮 AI Pipeline Design

The AI copilot is powered by a modular LangGraph pipeline, combining classification and RAG. The pipeline is structured as nodes that handle specific tasks, with support for parallel execution where possible to optimize latency.
<p align="center">
  <img src="https://i.postimg.cc/vZHPrrgh/Screenshot-from-2025-09-14-12-22-52.png" alt="AI Pipeline Diagram"/>
</p>


* **Classification** → Topic, sentiment, priority detection.
* **Retrieval-Augmented Generation (RAG)** → ChromaDB-backed document search for accurate answers.
* **Parallel Execution** → Multiple nodes (classification & retrieval) running concurrently to reduce latency.

---

## 💻 Application Design

### Frontend

* **React + Vite** → Deployed on **Vercel**
* Interactive dashboards & ticket management UI

### Backend

* **Flask API** → Deployed on **Google Cloud Run**
* Endpoints for classification, RAG responses, and reports

### AI Layer

* **OpenAI GPT models** → For classification & response generation
* **ChromaDB** → Lightweight vector store for embeddings

<p align="center">
  <img src="https://i.postimg.cc/mgJQPCQt/Screenshot-from-2025-09-14-13-00-52.png" alt="Another Diagram" />
</p>


---

## 📡 Data Flow

1. User submits a ticket via frontend.
2. Backend:
   * Classifies ticket (topic, sentiment, priority)
   * Retrieves docs from ChromaDB if needed
   * Generates AI response
3. Backend returns **analysis + response** to frontend.
4. Reports generated and visualized via frontend charts.

---

## ⚙️ Implementation Design

### Major Design Decisions & Trade-offs

* **URL Loading & Scraping**
  * ✅ `SeleniumURLLoader` → Captures dynamic JS pages & ensures full coverage.

* **Bulk Ticket Display**
  * ✅ Streaming responses for faster rendering & smooth UX.

* **Indexing vs Classification**
  * ✅ Separate indexing pipeline → avoids reloading docs on every classification.

* **Parallelization in LangGraph**
  * ✅ Classification & retrieval run in parallel → lower latency.

* **API Design**
  * ✅ Each functionality (classification, RAG, reports) exposed as separate REST endpoints.

---

## 📁 Project Structure

```
customer-support-copilot/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   └── SupportUI.jsx    # Main application component
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Flask backend API
│   ├── endpoints/           # API endpoints
│   ├── services/            # Business logic
│   └── api.py              # Main Flask app
├── vercel.json              # Vercel deployment config
└── README.md
```


## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /classify` - Classify a single ticket
- `POST /resolve` - Generate response for classified ticket
- `POST /bulk_classify` - Classify multiple tickets
- `POST /bulk_classify_stream` - Stream classification results
- `POST /reports` - Generate analytics reports

## 🛠️ Local Setup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python api.py
```


## 🔗 Live Demo

- **Frontend**: [Deploy to Vercel](https://vercel.com)
- **Backend**: `https://customer-support-backend-1052532391820.asia-south1.run.app`

