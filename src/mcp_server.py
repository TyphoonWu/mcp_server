from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import toml

env_path = Path(__file__).parent.parent / "./source/.env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print("Loaded .env:", env_path)
    print("MCP_SERVER_HOST:", os.getenv("MCP_SERVER_HOST"))
    print("MCP_SERVER_PORT:", os.getenv("MCP_SERVER_PORT"))

app = FastAPI()
# ... 定义初始端点 ...

# 从 pyproject.toml 读取 name 和 description
pyproject_path = Path(__file__).parent.parent / "./pyproject.toml"
if pyproject_path.exists():
    pyproject = toml.load(pyproject_path)
    project_info = pyproject.get("project", {})
    project_name = project_info.get("name", "mcp_server")
    project_desc = project_info.get("description", "A FastAPI server with MCP support")
    project_version = project_info.get("version", "0.1.0")
else:
    project_name = "mcp_server"
    project_desc = "A FastAPI server with MCP support"
    project_version = "0.1.0"

# 创建 MCP 服务器
mcp = FastApiMCP(app, name=project_name, description=project_desc)
mcp.mount()


@app.get("/")
def read_root():
    return {"name": project_name, "desc": project_desc, "version": project_version}


# 在 MCP 服务器创建后添加新端点
@app.get(
    "/mcp/tool_list/", operation_id="mcp_tool_list", summary="List available mcp tools"
)
async def mcp_tool_list():
    """
    list available mcp tools with json format

    returns:
        json: A JSON string representation of the available tools.

        sample：
        
        {
            "mcpServers": {
                "everything-search": {
                    "disabled": false,
                    "timeout": 60,
                    "type": "stdio",
                    "command": "...",
                    "args": [
                        "mcp-server-everything-search"
                    ],
                    "env": {
                        "EVERYTHING_SDK_PATH": "..."
                    }
                }
            }
        }
    """
    config_path = Path(__file__).parent.parent / "source/mcp-configs.json"
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# 刷新 MCP 服务器以包含新端点
mcp.setup_server()


def mcp_server():
    import uvicorn

    # 启动 FastAPI 应用
    uvicorn.run(
        app,
        host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_SERVER_PORT", "8000")),
        log_level="info",
    )
