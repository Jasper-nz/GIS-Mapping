#!/bin/bash

set -e  # Exit on any error


# Build the image for neo4j-mcp-server
echo "Building neo4j-mcp-server..."
docker build -f mcp/Dockerfile -t neo4j-mcp-server:latest mcp

# Build the image for neo4j-mcp-memory
echo "Building neo4j-mcp_memory..."
docker build -f mcp_memory/Dockerfile -t neo4j-mcp_memory:latest mcp_memory

# Build the image for mcp_semantic_search
echo "Building mcp_semantic_search..."
docker build -f mcp_semantic_search/Dockerfile -t mcp_semantic_search:latest mcp_semantic_search

# Start the containers
echo "Starting containers..."
docker compose up -d

# Wait a bit for Ollama to start
echo "Waiting for Ollama to start..."
sleep 10

# Pulling models (with error handling)
echo "Pulling Ollama models..."
docker exec ollama ollama pull llama3:latest || echo "Failed to pull llama3"
docker exec ollama ollama pull deepseek-r1:latest || echo "Failed to pull deepseek-r1"
docker exec ollama ollama pull qwen3:latest || echo "Failed to pull qwen3:latest"
docker exec ollama ollama pull qwen2.5:7b || echo "Failed to pull qwen2.5:7b"



echo "All containers are running."
