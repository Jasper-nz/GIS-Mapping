#!/usr/bin/env bash
set -euo pipefail

# redirect all logs to stdout/stderr so `docker logs` shows everything
exec > >(tee -a /var/log/mcp_semantic_search.log) 2>&1

# start the uvx server with mcpo app
uv run -v python mcp_server_semantic_search.py >> /var/log/mcp_semantic_search.log 2>&1 &

sleep 5

# Start MCPO semantic search service
uvx mcpo --host 0.0.0.0 --port 9000 --log-level DEBUG --server-type streamable-http --  http://127.0.0.1:8001/mcp  >> /var/log/mcp_semantic_search.log 2>&1
