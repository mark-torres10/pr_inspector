"""PR Inspector MCP Server - A basic MCP server with hello world endpoint."""

from fastmcp import FastMCP
from pr_inspector.config import get_server_config

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


def main():
    """Main entry point for running the MCP server."""
    # Load server configuration from config.yaml
    server_config = get_server_config()
    
    # Run the server with configuration from config.yaml
    mcp.run(
        transport=server_config["transport"],
        host=server_config["host"],
        port=server_config["port"]
    )


if __name__ == "__main__":
    main()

