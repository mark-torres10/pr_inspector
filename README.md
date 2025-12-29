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

3. Run the MCP server:
   ```bash
   uv run python server.py
   ```

## Development

The MCP server exposes tools for PR inspection. Currently available:

- `say_hello`: A hello world endpoint that greets the specified name
