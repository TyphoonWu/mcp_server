from transformers import AutoModelForCausalLM, AutoTokenizer
import requests
import json
import subprocess
import os

device = "cpu"  # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-0.5B-Chat", torch_dtype="auto", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B-Chat")

prompt = "Please search file Everything64.dll"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
]
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(device)

# 调用mcp server
query = "找一下dll文件"
mcp_url = "http://127.0.0.1:8001/mcp/tool_select/"
payload = {"query": prompt}
headers = {"accept": "application/json", "Content-Type": "application/json"}

mcp_resp = requests.post(mcp_url, json=payload, headers=headers)
if not mcp_resp.ok:
    print("MCP请求失败：", resp.text)
    exit(1)

tool_info = mcp_resp.json()
print("MCP工具信息：", tool_info)

# 2. 组装命令和环境变量
command = [tool_info["command"]] + tool_info.get("args", [])
env = os.environ.copy()
env.update(tool_info.get("env", {}))

# 3. 调用工具（假设工具支持命令行交互）
try:
    # 假设 tool_info、command、env 已经准备好
    params = {
        "type": "object",
        "properties": {
            "base": {"query": "llmstest.py", "max_results": 3}
        },
        "required": ["base"],
    }
    input_str = json.dumps(params)  # 转为JSON字符串
    print("command:", command)
    print("input_str:", input_str.encode("utf-8"))
    result = subprocess.run(
        command,
        input=input_str.encode("utf-8"),  # 以字节流形式传递
        capture_output=True,
        env=env,
        timeout=tool_info.get("timeout", 60),
    )
    print("工具输出：", result.stdout.decode("utf-8"))
except Exception as e:
    print("工具调用异常：", e)

# generated_ids = model.generate(
#     model_inputs.input_ids,
#     max_new_tokens=512
# )
# generated_ids = [
#     output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
# ]

# response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
# print(response)
