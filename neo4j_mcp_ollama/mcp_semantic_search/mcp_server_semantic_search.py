import os
from fastmcp import Context, FastMCP

from semantic_ssearch import WebSearchAssistant

# Create the MCP Server instance
mcp = FastMCP(
    name="TANZ Semantic Search Server", 
    version="2.0.1"
)

@mcp.tool()
def semantic_search(query: str) -> str:
    """
    Perform a semantic web search for the given query.
    Best used for questions related to farming, agriculture, dairy, technology, or New Zealand context.
    
    Args:
        query: The user's natural language question or search phrase
        
    Returns:
        Final summarized answer based on the best web information found
    """
    try:
        assistant = WebSearchAssistant()
        
        # Step 1: Generate optimized search query
        search_query = assistant.generate_search_query(query)
        
        # Step 2: Search the web
        results = assistant.browse_web(search_query)
        
        # Step 3: Select the most relevant result
        result = assistant.select_best_result(query, search_query, results)
        if not result:
            return "No suitable web results found for this query."
            
        title, url = result
        
        # Step 4: Get content from the best page
        content = assistant.retrieve_page_information(url)
        
        # Step 5: Generate final natural language answer
        final_answer = assistant.generate_final_answer(
            question=query,
            query=search_query,
            title=title,
            content=content
        )
        
        return final_answer
        
    except Exception as e:
        return f"Error during semantic search: {str(e)}"


@mcp.tool()
def semantic_welcome(query: str) -> str:
    """
    Simple welcome message for the TANZ Semantic Search Server.
    Can be used as a test tool or greeting.
    """
    message = """
        Welcome to TANZ Farm Identity Semantic Search Server!\n\n"
        "I'm ready to help you find the latest information about:\n"
        "• Dairy farming in New Zealand\n"
        "• Agricultural technology & innovation\n"
        "• Sustainable farming practices\n"
        "• Generate a farmer report based on the data that were collected from various sources.\n"
        "• Farm management & identity systems\n\n"
        "Just ask me anything!
    """
    return message.strip()
    
@mcp.tool
def hello(ctx: Context = None):
    """Say hello"""
    if ctx:
        ctx.info("in Hello!")
    return {"Response": "Hello!"}  #typo

    

@mcp.resource("config://version")
def get_version():
    """Returns the current version of the server"""
    return "0.0.2"


if __name__ == "__main__":
    print("Starting TANZ Semantic Search MCP server...")
    print("Recommended start command:")
    print("  uv run python this_file.py")
    print("\nServer will run on: http://0.0.0.0:8001/mcp")
    print("Use MCPO proxy for Open WebUI:")
    print("  uvx mcpo --host 0.0.0.0 --port 9000 --server-type streamable-http http://127.0.0.1:8001/mcp")
    print()

    # Run with native Streamable HTTP transport
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        host="0.0.0.0",
        port=8001
    )