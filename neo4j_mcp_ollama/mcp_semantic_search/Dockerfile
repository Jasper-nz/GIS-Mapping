FROM python:3.11-slim

# Install tini if not already present (very small)
RUN apt-get update && apt-get install -y tini || \
    apk add --no-cache tini     # for alpine

# Set working directory
WORKDIR /app

# Add application files, install dependencies, and set permissions
ADD *.py .
ADD config.json .
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD entry_point.sh .

# Make the entrypoint script executable
RUN chmod +x entry_point.sh

# Expose necessary ports
# MCP Semantic Search API port 8001 - this is the internal API used by the MCP service
EXPOSE 8001 
# MCPO Semantic Search Service port 9000 - this is the port that MCPO clients will connect to 
EXPOSE 9000

# Define the entrypoint, and start the services
ENTRYPOINT ["tini", "--", "/app/entry_point.sh"]
