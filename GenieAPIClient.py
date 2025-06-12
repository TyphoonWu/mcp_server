#==============================================================================
#
#  Copyright (c) 2024 Qualcomm Technologies, Inc.
#  All Rights Reserved.
#  Confidential and Proprietary - Qualcomm Technologies, Inc.
#
#==============================================================================

# python GenieAPIClient.py --prompt "How to fish?"
# python GenieAPIClient.py --prompt "How to fish?" --stream

import argparse
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import requests
import asyncio

#HOST="10.239.29.102"
# HOST="127.0.0.1"
HOST="localhost"
PORT="8910"

parser = argparse.ArgumentParser()
parser.add_argument("--stream", action="store_true")
parser.add_argument("--prompt", default="你好", type=str)
args = parser.parse_args()

client = OpenAI(base_url="http://" + HOST + ":" + PORT + "/v1", api_key="123")

messages = [{"role": "system", "content": "You are a math teacher who teaches algebra."}, {"role": "user", "content": args.prompt}]
extra_body = {"size": 4096, "seed": 146, "temp": 1.5, "top_k": 13, "top_p": 0.6, "penalty_last_n": 64, "penalty_repeat": 1.3}

model_name = "Qwen2.0-7B-SSD"

# 调用mcp server
mcp_url = "http://127.0.0.1:8001/mcp/tool_select/"
payload = {"query": args.prompt}
headers = {"accept": "application/json", "Content-Type": "application/json"}

# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    print("Received sampling message:", message)

async def call_openai_client(messages, stream, tools=None):
    # 增加tools参数，并传递给openai接口
    if stream:
        response = client.chat.completions.create(
            model=model_name,
            stream=True,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        for chunk in response:
            # print(chunk)
            content = chunk.choices[0].delta.content
            if content is not None:
                print(content, end="", flush=True)
    else:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        # print(response)
        print(response.choices[0].message.content)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_list = await session.list_tools()
            # print("Available tools:", tools_list)
            # 转换tools为dict格式
            tools_json = []
            if hasattr(tools_list, "tools"):
                for t in tools_list.tools:
                    # 保证parameters字段有type/object结构
                    parameters = t.inputSchema
                    if "type" not in parameters:
                        parameters = {
                            "type": "object",
                            "properties": parameters.get("properties", {}),
                            "required": parameters.get("required", []),
                        }
                    tool_dict = {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": parameters,
                        }
                    }
                    tools_json.append(tool_dict)
            print("Tools in JSON format:", tools_json)
            # Call a tool
            # result = await session.call_tool("search_files", arguments={"query": "README.md","maxResults": 20})
            # print("Tool call result:", result)
            # messages = [{"role": "system", "content": f"Help user find files, please output {result} to user format as markdown"}, {"role": "user", "content": args.prompt}]
            # 新增：调用模型生成消息，触发 sampling_callback
            await call_openai_client(messages, args.stream, tools=tools_json)

mcp_resp = requests.post(mcp_url, json=payload, headers=headers)
if not mcp_resp.ok:
    print("MCP请求失败：", mcp_resp.text)
else:
    print("MCP请求成功")
    tool_info = mcp_resp.json()
    print("MCP工具信息：", tool_info)
    if tool_info.get("command") is None or tool_info.get("name") is None:
        print("没有找到相关mcp tools")
        asyncio.run(call_openai_client(messages, args.stream))
    else:
        print("找到相关mcp tools:", tool_info.get("name", "unknown"))
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command=tool_info.get("command", "node"),  # 从tool_info获取command，默认"python"
            args=tool_info.get("args", []),              # 可选：从tool_info获取args，默认空列表
            env=tool_info.get("env"),                    # 可选：从tool_info获取env，默认None
        )
        asyncio.run(run())