from fastapi import FastAPI, Body
from fastapi_mcp import FastApiMCP
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import toml
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
from src.utils import cosine_similarity
import uvicorn
from uvicorn.server import logger
import requests

# 加载环境变量
env_path = Path(__file__).parent.parent / "./source/.env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"Loaded .env: {env_path}")
    print(f"set MCP_SERVER_HOST: {os.getenv('MCP_SERVER_HOST')}")
    print(f"set MCP_SERVER_PORT: {os.getenv('MCP_SERVER_PORT')}")

# 初始化 SentenceTransformer 模型, 使用本地已下载的模型
model_path = str(Path(__file__).parent.parent / "models" / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2" / "snapshots" / "86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d")
if not Path(model_path).exists():
    # 下载并初始化 SentenceTransformer 模型, 是专为文本嵌入（Embedding）设计的预训练模型
    model_embedding = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2", cache_folder=Path(__file__).parent.parent / "./models"
    )
else:
    print(f"Loading model from: {model_path}")
    model_embedding = SentenceTransformer(model_path, cache_folder=Path(__file__).parent.parent / "./models")

# FastAPI 应用实例
app = FastAPI()

class McpItem(BaseModel):
    name: str | None = None
    description: str | None = None
    disabled: bool = False
    timeout: int = 60
    type: str | None = None
    command: str | None = None
    args: list[str] = []
    env: dict[str, str] = {}

class McpServers(BaseModel):
    # mcpServers 的 key 应与 McpItem.name 对应，但类型注解只能用 str
    mcpServers: dict[str, McpItem]

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
@app.post(
    "/mcp/tool_list/", operation_id="mcp_tool_list", summary="List available mcp tools", response_model=McpServers
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
                    "name": "everything-search",
                    "description": "Search files using Everything SDK",
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
    if not config_path.exists():
        return {"mcpServers": {}}

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.post(
    "/mcp/tool_select/", operation_id="mcp_tool_select", summary="Select the best matching mcp tool", response_model=McpItem
)
async def mcp_tool_select(query: str = Body(..., embed=True)) -> McpItem:
    """
    according the query, select the best matching mcp tool

    param query: The query string to match against available tools.

    returns:
        json: A JSON string representation of the available tools.

        sample：

        {
            "name": "everything-search",
            "description": "Search files using Everything SDK",
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
    """
    # 获取工具配置
    data = await mcp_tool_list()
    tools_config = data.get("mcpServers", {})
    if not isinstance(tools_config, dict) or not tools_config:
        return {}
    tool_items = [McpItem(**tool) if not isinstance(tool, McpItem) else tool for tool in tools_config.values()]

    # 编码查询和工具描述
    query_embed = model_embedding.encode(query)
    tool_embeds = [model_embedding.encode(tool.description or "") for tool in tool_items]

    # 计算标准余弦相似度
    similarities = [cosine_similarity(query_embed, tool_embed) for tool_embed in tool_embeds]

    # 返回最佳匹配
    best_idx = np.argmax(similarities)
    logger.info(f"Query: {query}, Best Tool: {tool_items[best_idx].name}, Similarity: {similarities[best_idx]}")
    return tool_items[best_idx].dict() if similarities[best_idx] > 0.3 else {}

# 刷新 MCP 服务器以包含新端点
mcp.setup_server()

def mcp_server():
    # 启动 FastAPI 应用
    uvicorn.run(
        app,
        host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_SERVER_PORT", "8000")),
        log_level="info",
    )
