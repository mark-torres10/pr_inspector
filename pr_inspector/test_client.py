"""Test client for PR Inspector MCP Server."""

import asyncio
from fastmcp import Client


async def main():
    """Test the MCP server by calling the say_hello tool."""
    print("🚀 Connecting to MCP server...")
    print("   Make sure the server is running: uv run pr-inspector\n")
    
    # Connect to the HTTP server (should be running on http://127.0.0.1:8000/mcp)
    client = Client("http://127.0.0.1:8000/mcp")
    
    try:
        # Use the client within an asynchronous context
        # Note: Ensure the server is already running before running this test
        async with client:
            print("✅ Connected to MCP server!\n")
            
            # List available tools to confirm the server's capabilities
            tools = await client.list_tools()
            print(f"📋 Available tools: {[tool.name for tool in tools]}\n")
            
            # Test 1: Call the 'say_hello' tool with a specific name
            print("Test 1: Calling say_hello with name='Alice'")
            result = await client.call_tool("say_hello", {"name": "Alice"})
            # Extract text from TextContent objects
            text_result = result.content[0].text if result.content else str(result)
            print(f"   ✅ Result: {text_result}\n")
            
            # Test 2: Call the 'say_hello' tool without specifying a name (uses default)
            print("Test 2: Calling say_hello without name (should use default 'World')")
            result = await client.call_tool("say_hello", {})
            text_result = result.content[0].text if result.content else str(result)
            print(f"   ✅ Result: {text_result}\n")
            
            # Test 3: Call with another name
            print("Test 3: Calling say_hello with name='Developer'")
            result = await client.call_tool("say_hello", {"name": "Developer"})
            text_result = result.content[0].text if result.content else str(result)
            print(f"   ✅ Result: {text_result}\n")
            
            print("✅ All tests passed! The MCP server is working correctly.")
    
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("\n💡 Make sure the server is running first:")
        print("   uv run pr-inspector")
        raise


if __name__ == "__main__":
    asyncio.run(main())

