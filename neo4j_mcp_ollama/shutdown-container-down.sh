#!/bin/bash

# Stop and remove the containers
docker compose down
# Optionally, remove the volumes to clean up data
# docker compose down -v
# Remove Neo4j data directory
#rm -rf data/neo4j/*

# Delete all containers
docker rmi neo4j-mcp-server mcp_semantic_search ollama open-webui neo4j

# Delete all images
docker image rm neo4j-mcp-server mcp_semantic_search ollama open-webui neo4j

echo "Containers stopped and Neo4j data directory cleaned."
# Note: Uncomment the above line to remove Neo4j data if desired.