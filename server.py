#!/usr/bin/env python3
"""
Reverse Text MCP Server - Minimal Implementation
Self-contained MCP server with no external dependencies
"""

import json
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Reverse Text MCP Server")

# Tool definitions
TOOLS = [
    {
        "name": "reverse_text",
        "description": "Reverse the characters in a text string",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to reverse"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "text_info", 
        "description": "Get information about a text string",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                }
            },
            "required": ["text"]
        }
    }
]


def reverse_text(text: str) -> str:
    """Reverse the characters in the provided text"""
    result = {
        "original_text": text,
        "reversed_text": text[::-1],
        "length": len(text),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return json.dumps(result, indent=2)


def text_info(text: str) -> str:
    """Get detailed information about a text string"""
    info = {
        "text": text,
        "length": len(text),
        "word_count": len(text.split()),
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(" ", "")),
        "uppercase_count": sum(1 for c in text if c.isupper()),
        "lowercase_count": sum(1 for c in text if c.islower()),
        "digit_count": sum(1 for c in text if c.isdigit()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return json.dumps(info, indent=2)


# Map tool names to functions
TOOL_FUNCTIONS = {
    "reverse_text": reverse_text,
    "text_info": text_info
}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reverse-text-mcp",
        "tools_count": len(TOOLS),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/mcp/discover")
async def discover():
    """Service discovery endpoint"""
    return {
        "service_name": "reverse-text-mcp", 
        "description": "Text manipulation service with reverse and analysis tools",
        "tools": TOOLS,
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp",
            "discover": "/mcp/discover"
        }
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint - fully compliant with JSON-RPC 2.0 and MCP spec"""
    try:
        request_data = await request.json()
        logger.debug(f"MCP request: {request_data}")
        
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id")
        
        # Handle initialization handshake
        if method == "initialize":
            # MCP requires initialization handshake
            client_info = params.get("clientInfo", {})
            protocol_version = params.get("protocolVersion", "2024-11-05")
            capabilities = params.get("capabilities", {})
            
            logger.info(f"Initializing MCP connection - Client: {client_info}, Protocol: {protocol_version}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}  # We support tools
                    },
                    "serverInfo": {
                        "name": "reverse-text-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "initialized":
            # This is a notification - no response required
            logger.info("MCP connection initialized")
            return None  # FastAPI will not send a response for None
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": TOOLS}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in TOOL_FUNCTIONS:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
            
            try:
                tool_func = TOOL_FUNCTIONS[tool_name]
                result = tool_func(**arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
                
            except Exception as e:
                logger.error(f"Tool execution error for '{tool_name}': {e}")
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution failed: {str(e)}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id, 
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
            
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
        )
    
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": request_data.get("id") if 'request_data' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
        )


def main():
    """Main entry point"""
    logger.info(f"Starting MCP server with {len(TOOLS)} tools")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()