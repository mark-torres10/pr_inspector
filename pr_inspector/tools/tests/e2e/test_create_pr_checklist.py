"""End-to-end test for the create_pr_checklist tool."""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path so we can import pr_inspector
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import Client


async def main():
    """Test the create_pr_checklist tool via MCP server."""
    print("🚀 Testing create_pr_checklist tool...")
    print("   Make sure the MCP server is running\n")

    # Connect to the HTTP server (should be running on http://127.0.0.1:8000/mcp)
    client = Client("http://127.0.0.1:8000/mcp")
    
    try:
        async with client:
            print("✅ Connected to MCP server!\n")
            
            # Verify the tool is available
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            if "create_pr_checklist" not in tool_names:
                print(f"❌ Error: create_pr_checklist tool not found!")
                print(f"   Available tools: {tool_names}")
                sys.exit(1)
            
            print(f"✅ Found create_pr_checklist tool\n")
            
            # Test the tool with a real PR URL
            # Using a public PR for testing (you can change this to any public PR)
            test_pr_url = "https://github.com/METResearchGroup/bluesky-research/pull/273"
            
            print(f"📋 Calling create_pr_checklist with PR: {test_pr_url}")
            print("   This may take a moment as it fetches PR details and generates the checklist...\n")
            
            result = await client.call_tool("create_pr_checklist", {"pr_url": test_pr_url})
            
            # Extract text from TextContent objects
            if result.content:
                markdown_result = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            else:
                markdown_result = str(result)
            
            print("=" * 80)
            print("✅ SUCCESS - Generated Checklist Markdown:")
            print("=" * 80)
            print(markdown_result)
            print("=" * 80)
            print("\n✅ Test passed! The create_pr_checklist tool is working correctly.")
    
    except Exception as e:
        print(f"❌ Error testing create_pr_checklist: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

