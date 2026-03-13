import asyncio
from fastmcp import Client

async def main():
    # Point the client at your server file
    client = Client("my_server.py")

    # Connect to the server
    async with client:
        # Call the tool with parameters
        result = await client.call_tool("greet", {"name": "Flod"})
        print(f"Time result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
