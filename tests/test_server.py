#!/usr/bin/env python3
"""Tests for reverse text MCP server"""

import json
import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "reverse-text-mcp"
    assert "timestamp" in data
    assert data["tools_count"] == 2  # reverse_text and text_info


def test_discover_endpoint(client):
    """Test service discovery endpoint"""
    response = client.get("/mcp/discover")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service_name"] == "reverse-text-mcp"
    assert len(data["tools"]) == 2
    
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "reverse_text" in tool_names
    assert "text_info" in tool_names


def test_tools_list(client):
    """Test MCP tools/list method"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    assert len(data["result"]["tools"]) == 2


def test_reverse_text_tool(client):
    """Test reverse_text tool"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "reverse_text",
            "arguments": {"text": "Hello World"}
        },
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    
    result_text = data["result"]["content"][0]["text"]
    result_json = json.loads(result_text)
    
    assert result_json["original_text"] == "Hello World"
    assert result_json["reversed_text"] == "dlroW olleH"
    assert result_json["length"] == 11


def test_text_info_tool(client):
    """Test text_info tool"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "text_info",
            "arguments": {"text": "Hello World 123"}
        },
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    result_text = data["result"]["content"][0]["text"]
    result_json = json.loads(result_text)
    
    assert result_json["text"] == "Hello World 123"
    assert result_json["length"] == 15
    assert result_json["word_count"] == 3
    assert result_json["uppercase_count"] == 2  # H, W
    assert result_json["lowercase_count"] == 8
    assert result_json["digit_count"] == 3


def test_invalid_tool(client):
    """Test calling invalid tool"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "invalid_tool",
            "arguments": {}
        },
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601


def test_invalid_method(client):
    """Test invalid MCP method"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "invalid/method",
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601


def test_mcp_initialize(client):
    """Test MCP initialization handshake"""
    request_data = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    
    result = data["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert "capabilities" in result
    assert "serverInfo" in result
    assert result["serverInfo"]["name"] == "reverse-text-mcp"


def test_mcp_initialized_notification(client):
    """Test MCP initialized notification (no response expected)"""
    request_data = {
        "jsonrpc": "2.0", 
        "method": "initialized",
        "params": {}
    }
    
    response = client.post("/mcp", json=request_data)
    # Notification should return empty response
    assert response.status_code == 200