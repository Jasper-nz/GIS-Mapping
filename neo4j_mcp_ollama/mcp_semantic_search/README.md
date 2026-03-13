# An Example Semantic Search MCP Server

This example implemented a semantic search based on LLM on ollama.

We used [MCPO](https://github.com/open-webui/mcpo) as main tool for doing that.


## Start MCP Server

### Start Stand FastMCP Server via `uv run` 

```bash
uv run -v python mcp_server_semantic_search.py
```

### Start MCPO (MCP to OpenApi proxy)

Program involves:
* *uvx*:
* *mcpo*:
    * *Configuration*:
        * --host
        * --port
        * --log-lvel
        * --server-type
        * -- Command that will run MCP Servers, like python program based on FastMCP, or other MCP Server.

```bash
uvx mcpo --host 0.0.0.0 --port 9000 --log-level DEBUG --server-type streamable-http --  http://192.168.88.38:8001/mcp
```
