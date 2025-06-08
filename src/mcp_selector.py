from sentence_transformers import SentenceTransformer
import numpy as np

# paraphrase-multilingual-MiniLM-L12-v2 是专为文本嵌入（Embedding）设计的预训练模型
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./models"
)

# tools_config示例
tools = [
    {
        "name": "get_weather",
        "description": "查询城市天气数据",
        "parameters": {"city": "string"},
    },
    {
        "name": "search_file",
        "description": "查找本地文件路径，支持输入文件名、目录名、英文或中文描述，如'readme.txt在哪个目录？'或'Where is readme.txt?'",
        "parameters": {"file": "string"},
    },
    {
        "name": "test",
        "description": "test",

        "parameters": {"test": "string"},
    }
]

# 余弦相似度Cosine Similarity）的标准范围是[-1, 1]
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def select_tool(query: str, tools_config: list) -> dict:
    # 编码查询和工具描述
    query_embed = model.encode(query)
    tool_embeds = [model.encode(tool["description"]) for tool in tools_config]

    # 计算标准余弦相似度
    similarities = [cosine_similarity(query_embed, tool_embed) for tool_embed in tool_embeds]

    # 返回最佳匹配
    best_idx = np.argmax(similarities)
    print(f"Query: {query}, Best Tool: {tools_config[best_idx]['name']}, Similarity: {similarities[best_idx]}")
    return tools_config[best_idx] if similarities[best_idx] > 0.4 else None


if __name__ == "__main__":
    print(select_tool("这是一个测试用例", tools))
    print(select_tool("北京的天气", tools))
    print(select_tool("文件ttt.txt在哪里", tools))
    print(select_tool("readme.txt在哪个目录", tools))
    print(select_tool("what is the weather of shanghai?", tools))
    print(select_tool("上海今天天气怎么样?", tools))
    print(select_tool("I want to find the file of ttt.txt", tools))
    print(select_tool("你好", tools))
    print(select_tool("hello world", tools))
    print(select_tool("哪里的美食最受欢迎", tools))
