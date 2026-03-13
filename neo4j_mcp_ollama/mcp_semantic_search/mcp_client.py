import asyncio
from fastmcp import Client

client = Client("http://192.168.88.38:8001/mcp")


async def call_ssemantic_welcome():
    async with client:
        result = await client.call_tool("semantic_welcome",{"query":"Use the semantic_search tool to find information about AG & JMJ Benny Limited and it's address 367 Southbridge Rakaia Road, Southbridge in New Zealand."})
        print(result)

asyncio.run(call_ssemantic_welcome())


async def call_semantic_search():
    async with client:
        result = await client.call_tool("semantic_search",{"query":"Use the semantic_search tool to find information about AG & JMJ Benny Limited and it's address 367 Southbridge Rakaia Road, Southbridge in New Zealand."})
        print(result)

asyncio.run(call_semantic_search())

