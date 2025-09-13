#!/bin/bash

# Docker Setup Script for Customer Support Copilot

set -e

echo "🚀 Setting up Customer Support Copilot with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - LANGSMITH_API_KEY"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Copy sample tickets to data directory
if [ -f backend/sample_tickets.json ]; then
    echo "📋 Copying sample tickets..."
    cp backend/sample_tickets.json data/
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

echo ""
echo "🎉 Setup complete!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "🏥 Health Check: http://localhost:5000/health"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
