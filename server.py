"""PR Inspector MCP Server - A basic MCP server with hello world endpoint."""

from fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("PR Inspector Server")


@mcp.tool()
def say_hello(name: str = "World") -> str:
    """
    Returns a greeting message.
    
    Args:
        name: The name to greet (defaults to "World")
    
    Returns:
        A greeting message string
    """
    return f"Hello, {name}! Welcome to PR Inspector."


if __name__ == "__main__":
    mcp.run()
