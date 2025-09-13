# Customer Support Copilot

An AI-powered customer support system that automatically classifies tickets, generates responses, and provides analytics.

## 🚀 Features

- **AI Ticket Classification**: Automatically categorizes support tickets by topic, sentiment, and priority
- **Smart Response Generation**: Provides appropriate responses based on ticket classification
- **Bulk Processing**: Handle multiple tickets at once with streaming updates
- **Analytics Dashboard**: Comprehensive reports with charts and insights
- **Interactive Agent**: Real-time ticket analysis and response generation

## 🏗️ Architecture

- **Frontend**: React + Vite (deployed on Vercel)
- **Backend**: Flask API (deployed on Google Cloud Run)
- **AI**: OpenAI GPT models for classification and response generation

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

## 🚀 Deployment

### Frontend (Vercel)
The frontend is configured for automatic deployment on Vercel:

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the frontend configuration
3. The app will be built from the `frontend/` directory
4. Frontend connects to the hosted backend API

### Backend (Google Cloud Run)
The backend is already deployed and running at:
`https://customer-support-backend-1052532391820.asia-south1.run.app`

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /classify` - Classify a single ticket
- `POST /resolve` - Generate response for classified ticket
- `POST /bulk_classify` - Classify multiple tickets
- `POST /bulk_classify_stream` - Stream classification results
- `POST /reports` - Generate analytics reports

## 🛠️ Local Development

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

## 📊 Features

### Ticket Classification
- **Topics**: Connector, Permissions, How-to, Lineage, etc.
- **Sentiment**: Angry, Frustrated, Neutral, Curious, Happy
- **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

### Analytics
- Topic distribution charts
- Sentiment analysis
- Priority breakdown
- High-priority ticket tracking
- Repeated query identification

## 🔗 Live Demo

- **Frontend**: [Deploy to Vercel](https://vercel.com)
- **Backend**: `https://customer-support-backend-1052532391820.asia-south1.run.app`

## 📝 License

This project is licensed under the MIT License.
