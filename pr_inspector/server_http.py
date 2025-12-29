"""FastAPI HTTP adapter for PR Inspector MCP Server.

This adapter exposes MCP tools as REST endpoints for GitHub Actions integration.
All business logic remains in the MCP tools themselves.
"""

import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse

# Import the MCP tools directly
from pr_inspector.server import say_hello

app = FastAPI(title="PR Inspector HTTP Adapter", version="0.1.0")

# Get shared secret from environment variable
MCP_SHARED_SECRET = os.getenv("MCP_SHARED_SECRET", "")


def verify_auth(auth_header: Optional[str] = None) -> None:
    """
    Verify the X-MCP-Auth header matches the shared secret.
    
    Args:
        auth_header: The value of the X-MCP-Auth header
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    if not MCP_SHARED_SECRET:
        raise HTTPException(
            status_code=500,
            detail="MCP_SHARED_SECRET not configured on server"
        )
    
    if not auth_header or auth_header != MCP_SHARED_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-MCP-Auth header"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway (no auth required)."""
    return {"status": "ok"}


@app.post("/tools/say_hello")
async def say_hello_endpoint(
    request: Request,
    x_mcp_auth: Optional[str] = Header(None, alias="X-MCP-Auth")
):
    """
    Call the say_hello MCP tool.
    
    Accepts optional JSON body with parameters:
    - name (str, optional): Name to greet (defaults to "World")
    
    Returns:
        Plain text response with greeting message
    """
    # Verify authentication
    verify_auth(x_mcp_auth)
    
    # Parse request body if provided
    body = {}
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            # If JSON parsing fails, use empty dict (will use default "World")
            pass
    name = body.get("name", "World")
    
    try:
        # Call the underlying function from the MCP tool
        result = say_hello.fn(name=name)
        return PlainTextResponse(content=result, media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling tool: {str(e)}"
        )

