# 🐳 Docker Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- LangSmith API key

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd customer-support-copilot
   ./docker-setup.sh
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/health

## Manual Setup

1. **Environment Configuration:**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys
   ```

2. **Build and Run:**
   ```bash
   docker-compose up --build
   ```

## Services

### Backend (Port 5000)
- Flask API server
- LangChain RAG system
- ChromaDB vector store
- Persistent data in `./data/`

### Frontend (Port 3000)
- React application
- Vite build system
- Served with `serve`

## Data Persistence

- **ChromaDB**: Stored in `./data/chroma_db/`
- **Sample Tickets**: Copied to `./data/sample_tickets.json`
- **Reports**: Generated in `./data/`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `LANGSMITH_API_KEY` | LangSmith API key | Required |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | `/app/data/chroma_db` |
| `VITE_API_URL` | Backend API URL | `http://backend:5000` |

## Troubleshooting

### Common Issues

1. **API Keys Missing:**
   ```bash
   # Check if .env file exists and has correct keys
   cat .env
   ```

2. **Services Not Starting:**
   ```bash
   # Check logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

3. **Port Conflicts:**
   ```bash
   # Check if ports are in use
   lsof -i :3000
   lsof -i :5000
   ```

4. **Data Not Persisting:**
   ```bash
   # Check volume mounts
   docker-compose ps
   ls -la ./data/
   ```

### Health Checks

- Backend: `curl http://localhost:5000/health`
- Frontend: `curl http://localhost:3000`

### Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build

# Remove everything (including volumes)
docker-compose down -v
```

## Development

### Backend Development
```bash
# Run backend in development mode
cd backend
python api.py
```

### Frontend Development
```bash
# Run frontend in development mode
cd frontend
npm run dev
```

## Production Considerations

1. **Security:**
   - Use secrets management for API keys
   - Enable HTTPS
   - Restrict CORS origins

2. **Performance:**
   - Use production WSGI server (gunicorn)
   - Enable Redis caching
   - Optimize Docker images

3. **Monitoring:**
   - Add logging aggregation
   - Set up health monitoring
   - Monitor resource usage

## File Structure

```
customer-support-copilot/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile.backend          # Backend Docker image
├── Dockerfile.frontend         # Frontend Docker image
├── .dockerignore              # Docker ignore file
├── env.example                # Environment template
├── docker-setup.sh            # Setup script
├── backend/
│   ├── requirements.txt       # Python dependencies
│   └── ...
├── frontend/
│   ├── package.json           # Node dependencies
│   └── ...
└── data/                      # Persistent data (created by Docker)
    ├── chroma_db/            # ChromaDB storage
    └── sample_tickets.json   # Sample data
```
