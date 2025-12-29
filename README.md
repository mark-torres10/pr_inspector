# PR Inspector

A Model Context Protocol (MCP) server for inspecting and analyzing pull requests.

## Setup

This project uses `uv` for dependency management. To set up the environment:

1. Install `uv` (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure the server (optional):
   - Edit `config.yaml` to change the host, port, or transport settings
   - Default settings: `host: 127.0.0.1`, `port: 8000`, `transport: http`

4. Run the MCP server (in one terminal):
   ```bash
   # Option 1: Using the console script (recommended)
   uv run pr-inspector
   
   # Option 2: Using Python module syntax
   uv run python -m pr_inspector.server
   ```
   
   The server will start using the settings from `config.yaml` (default: `http://127.0.0.1:8000/mcp`) and wait for connections.

## Testing

To test the MCP server and verify it's working:

1. **First, start the server** (in one terminal):
   ```bash
   uv run pr-inspector
   ```
   The server will start on `http://127.0.0.1:8000/mcp`

2. **Then, run the test client** (in another terminal):
   ```bash
   uv run python -m pr_inspector.test_client
   ```

The test client will:
1. Connect to the running MCP server
2. List available tools
3. Call the `say_hello` endpoint with different parameters

## Development

The MCP server exposes tools for PR inspection. Currently available:

- `say_hello`: A hello world endpoint that greets the specified name

## Using the MCP Server

### Option 1: Test Client (Recommended for Development)

Use the included test client to verify functionality:

```bash
uv run python -m pr_inspector.test_client
```

### Option 2: Connect with MCP Client

The server can be connected to any MCP-compatible client. The server runs on HTTP at `http://127.0.0.1:8000/mcp`.

For stdio-based MCP clients, you can modify the server to use stdio transport by changing the last line in `pr_inspector/server.py` from:
```python
mcp.run(transport="http", host="127.0.0.1", port=8000)
```
to:
```python
mcp.run()  # Uses stdio transport by default
```

### Option 3: Programmatic Usage

You can also use the FastMCP Client in your own Python code to connect to the running HTTP server:

```python
import asyncio
from fastmcp import Client

async def main():
    # Connect to the HTTP server (make sure it's running first)
    client = Client("http://127.0.0.1:8000/mcp")
    
    async with client:
        result = await client.call_tool("say_hello", {"name": "YourName"})
        print(result.content[0].text)

asyncio.run(main())
```
