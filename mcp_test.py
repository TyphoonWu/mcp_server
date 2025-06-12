import subprocess
import json
import sys
import time
import threading
from queue import Queue, Empty
import requests

# 启动 MCP server 进程
proc = subprocess.Popen(
    ["node", "C:\\Users\\wostest\\workspace\\mcp_server\\tools\\everything-mcp-server\\build\\index.js"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# 构造 JSON-RPC 格式的 search_files_advanced 请求
request = {
    "method": "tools/call",
    "params": {
        "name": "search_files",  # 工具名
        "arguments": {
            "query": "README.md",  # 搜索关键词
            "maxResults": 20
        },
        "_meta": {"progressToken": 0},
    },
    "jsonrpc": "2.0",
    "id": 2,
}

# 发送请求
proc.stdin.write(json.dumps(request) + "\n")
proc.stdin.flush()


# 读取 server stderr 输出，便于调试
def print_stderr():
    for line in proc.stderr:
        print("[server stderr]", line, end="")


t = threading.Thread(target=print_stderr, daemon=True)
t.start()

# 用队列异步读取 server stdout
q = Queue()


def read_stdout():
    for line in proc.stdout:
        q.put(line)


t2 = threading.Thread(target=read_stdout, daemon=True)
t2.start()

output = ""
timeout = 10  # 最多等待10秒
start = time.time()
while True:
    try:
        line = q.get(timeout=0.5)
        output += line
        if (
            "No files found" in line
            or "Error" in line
            or "result" in line
        ):
            break
    except Empty:
        if time.time() - start > timeout:
            print("Timeout waiting for server response.")
            break

print("Server response:")
print(output)

# 关闭 server 进程
proc.terminate()
