# Customer Support AI Agent - Backend

## Architecture Overview

The backend is now modularized with the following structure:

```
backend/
├── app.py                          # Main Flask application
├── graph.py                        # LangGraph workflow definition
├── services/                       # Business logic services
│   ├── data_loader.py             # Data loading utilities
│   ├── evaluation.py              # Performance evaluation
│   └── resolution.py              # Resolution logic (legacy)
├── endpoints/                      # API endpoint handlers
│   ├── classify.py                # Single ticket classification
│   ├── resolve.py                 # Query resolution
│   ├── bulk_classify.py           # Bulk classification
│   └── bulk_classify_stream.py    # Streaming bulk classification
└── requirements_evaluation.txt    # Evaluation dependencies
```

## LangGraph Workflow

The main workflow in `graph.py` includes:

1. **Parallel Processing**: Classification and retrieval run in parallel for optimization
2. **Retrieve**: Vector similarity search for relevant documents
3. **Generate**: RAG-based answer generation
4. **Classify**: Ticket classification (topic, sentiment, priority)
5. **Evaluate Confidence**: Answer quality assessment
6. **Decide Resolution**: Routing and RAG decision logic
7. **Format Response**: Final response formatting

## Key Features

### 🚀 **Optimization**
- **Parallel Processing**: Classification and retrieval run simultaneously
- **Efficient Graph**: Optimized LangGraph workflow
- **Streaming Support**: Real-time ticket processing

### 📊 **Evaluation**
- **Performance Metrics**: Classification accuracy, processing time
- **Visualizations**: Charts for topic distribution, confidence scores
- **Detailed Reports**: JSON reports with comprehensive metrics

### 🏗️ **Modularity**
- **Separate Endpoints**: Each API endpoint in its own file
- **Service Layer**: Business logic separated from API handlers
- **Clean Dependencies**: Clear separation of concerns

## Running the Application

### Start the API Server
```bash
cd backend
python app.py
```

### Run Evaluation
```bash
# Install evaluation dependencies
pip install -r requirements_evaluation.txt

# Run evaluation
python run_evaluation.py
```

## API Endpoints

- `POST /classify` - Classify a single ticket
- `POST /resolve` - Resolve a query with RAG
- `POST /bulk_classify` - Bulk classify tickets
- `POST /bulk_classify_stream` - Stream bulk classification

## Evaluation Output

The evaluation generates:
- **Charts**: Performance visualizations (PNG)
- **Report**: Detailed JSON metrics
- **Console Output**: Summary statistics

## Performance Improvements

1. **Parallel Processing**: 2x faster classification + retrieval
2. **Optimized Graph**: Streamlined workflow
3. **Efficient Streaming**: Real-time ticket processing
4. **Better Error Handling**: Robust error management
