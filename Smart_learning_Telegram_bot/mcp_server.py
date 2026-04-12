from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_tools import MCP_TOOLS

app = FastAPI(title="Smart Learning MCP Server")


class MCPRequest(BaseModel):
    tool: str
    arguments: dict


@app.get("/")
def root():
    return {"message": "Smart Learning MCP Server is running"}


@app.get("/tools")
def list_tools():
    return {
        "available_tools": list(MCP_TOOLS.keys())
    }


@app.post("/call")
def call_tool(request: MCPRequest):
    tool_name = request.tool
    arguments = request.arguments

    if tool_name not in MCP_TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )

    try:
        result = MCP_TOOLS[tool_name](**arguments)
        return {"result": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )