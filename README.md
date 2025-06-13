# MCP Server
## Download
```git
git clone https://github.com/TyphoonWu/mcp_server.git
git submodule init
git submodule update
```
## 安装pyproject.toml中的dependencies
```python
pip install pdm
pdm install
```
## 如果需要更新pyproject.toml中的dependencies
```python
pip install pdm
pdm add sentence-transformers 
```

## 测试
确保llm 服务启动并提供相关API
```python
python GenieAPIClient.py --prompt "please help find file README.md?" --stream
```

## Documents:
https://fastapi.tiangolo.com/tutorial/#run-the-code
https://github.com/tadata-org/fastapi_mcp/tree/main
https://github.com/mamertofabian/mcp-everything-search/tree/main
https://github.com/peterparker57/everything-mcp-server
https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
https://github.com/modelcontextprotocol/inspector
https://modelcontextprotocol.io/docs/tools/debugging

### weather
https://weather.cma.cn/web/weather/map.html#

https://weather.cma.cn/api/map/weather/1
["54511","北京","中国",0,39.81,116.47,33.0,"多云",1,"东南风","微风",22.0,"阴",2,"东南风","微风","ABJ","110115"]

https://weather.cma.cn/api/now/54511
{
  "msg": "success",
  "code": 0,
  "data": {
    "location": {
      "id": "54511",
      "name": "北京",
      "path": "中国, 北京, 北京"
    },
    "now": {
      "precipitation": 0,
      "temperature": 25.6,
      "pressure": 1001,
      "humidity": 47,
      "windDirection": "东南风",
      "windDirectionDegree": 108,
      "windSpeed": 1.6,
      "windScale": "微风",
      "feelst": 26.7
    },
    "alarm": [],
    "jieQi": "",
    "lastUpdate": "2025/06/13 23:25"
  }
}