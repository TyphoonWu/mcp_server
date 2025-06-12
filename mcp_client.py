from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import requests

# 调用mcp server
query = "Please search file Everything64.dll"
mcp_url = "http://127.0.0.1:8001/mcp/tool_select/"
payload = {"query": query}
headers = {"accept": "application/json", "Content-Type": "application/json"}

mcp_resp = requests.post(mcp_url, json=payload, headers=headers)
if not mcp_resp.ok:
    print("MCP请求失败：", mcp_resp.text)
    exit(1)

tool_info = mcp_resp.json()
print("MCP工具信息：", tool_info)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command=tool_info.get("command", "python"),  # 从tool_info获取command，默认"python"
    args=tool_info.get("args", []),              # 可选：从tool_info获取args，默认空列表
    env=tool_info.get("env"),                    # 可选：从tool_info获取env，默认None
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    print("Received sampling message:", message)
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            # Call a tool
            result = await session.call_tool("search_files", arguments={"query": "README.md","maxResults": 20})
            print("Tool call result:", result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())