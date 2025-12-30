# End-to-End Tests for PR Inspector Tools

This directory contains end-to-end (e2e) tests for PR Inspector MCP Server tools. These tests verify that tools work correctly when called through the MCP server interface.

## Structure

- **One test file per tool**: Each tool has its own e2e test file named `test_<tool_name>.py`
- **Test runner script**: `run_e2e_tests.sh` orchestrates running all tests
- **This README**: Documentation for the e2e test suite

## How It Works

### Test Execution Flow

1. **Server Startup**: The test runner starts the MCP server in the background
2. **Health Check**: Waits for the server to be ready (checks if port 8000 is accessible)
3. **Test Execution**: Runs each e2e test file sequentially
4. **Cleanup**: Stops the server when all tests complete (or on error)

### Test Files

Each test file:
- Connects to the MCP server running on `http://127.0.0.1:8000/mcp`
- Verifies the tool is available in the server's tool list
- Calls the tool with appropriate test data
- Prints the result (typically markdown output for checklist tools)
- Exits with code 0 on success, non-zero on failure

## Running the Tests

### Prerequisites

- The project dependencies must be installed (`uv sync`)
- Environment variables must be set (e.g., `GITHUB_TOKEN`, `OPENAI_API_KEY`)
- The MCP server must not already be running on port 8000

### Quick Start

Run all e2e tests:

```bash
cd pr_inspector/tools/tests/e2e
chmod +x run_e2e_tests.sh
./run_e2e_tests.sh
```

Or from the project root:

```bash
chmod +x pr_inspector/tools/tests/e2e/run_e2e_tests.sh
./pr_inspector/tools/tests/e2e/run_e2e_tests.sh
```

### Running Individual Tests

You can also run individual test files directly, but you'll need to start the server manually first:

```bash
# Terminal 1: Start the server
uv run pr-inspector

# Terminal 2: Run a specific test
uv run python pr_inspector/tools/tests/e2e/test_create_pr_checklist.py
```

## Adding New Tests

To add an e2e test for a new tool:

1. Create a new file: `test_<tool_name>.py`
2. Follow the pattern from `test_create_pr_checklist.py`:
   - Import necessary modules
   - Create an async `main()` function
   - Connect to the MCP server
   - Verify the tool exists
   - Call the tool with test data
   - Print results
   - Handle errors appropriately

Example template:

```python
"""End-to-end test for the <tool_name> tool."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import Client


async def main():
    """Test the <tool_name> tool via MCP server."""
    print("🚀 Testing <tool_name> tool...")
    
    client = Client("http://127.0.0.1:8000/mcp")
    
    try:
        async with client:
            # Verify tool exists
            tools = await client.list_tools()
            if "<tool_name>" not in [tool.name for tool in tools]:
                print("❌ Tool not found!")
                sys.exit(1)
            
            # Call the tool
            result = await client.call_tool("<tool_name>", {"param": "value"})
            
            # Print result
            if result.content:
                output = result.content[0].text
                print(output)
            
            print("✅ Test passed!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
```

## Test Output

On success, tests print:
- Connection status
- Tool verification
- The tool's output (e.g., markdown checklist)
- Success confirmation

On failure, tests print:
- Error messages
- Stack traces (if applicable)
- Exit with non-zero code

## Troubleshooting

### Server Won't Start

- Check if port 8000 is already in use: `lsof -i :8000`
- Check server logs: `/tmp/pr_inspector_server.log`
- Verify environment variables are set correctly

### Tests Fail to Connect

- Ensure the server started successfully
- Check that the server is listening on `http://127.0.0.1:8000/mcp`
- Verify network connectivity (though this is localhost)

### Tool Not Found

- Ensure the tool is imported in `pr_inspector/server.py`
- Check that the tool is properly decorated with `@mcp.tool()`
- Verify the tool name matches exactly (case-sensitive)

## Notes

- Tests use real API calls (GitHub API, OpenAI API), so they require valid credentials
- Tests may take time to complete (especially LLM calls)
- Server logs are written to `/tmp/pr_inspector_server.log` for debugging
- The test runner automatically cleans up the server process on exit

