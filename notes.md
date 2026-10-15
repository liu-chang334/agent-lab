<!-- omit from toc -->
# Agent Lab 学习笔记
- [1. uv 环境管理](#1-uv-环境管理)
- [2. JSON](#2-json)
- [3. HTTP 通信](#3-http-通信)
- [4. FastAPI 与 Uvicorn](#4-fastapi-与-uvicorn)
- [5. 接口与状态码](#5-接口与状态码)
- [6. HTTPX 客户端](#6-httpx-客户端)
- [7. 格式化](#7-格式化)
- [8. 连接大模型与请求对话](#8-连接大模型与请求对话)
- [9. 工具说明与工具调用](#9-工具说明与工具调用)
- [10. 工具结果与第二次请求](#10-工具结果与第二次请求)
- [11. MCP 工作原理](#11-mcp-工作原理)
- [12. 搭建 MCP 服务端](#12-搭建-mcp-服务端)
- [13. MCP 客户端与模型对接](#13-mcp-客户端与模型对接)

## 1. uv 环境管理

uv 是一个 python 包和环境管理工具, 同 Ruff 均由 *Astral* 开发
负责安装依赖、管理虚拟环境、管理 python 版本, 再环境中运行程序

1. 固定 python 版本

```powershell
uv python pin 3.12        # pin 表示固定
```
- 执行后在`.python-version`文件中记录 python 版本

2. 创建或同步项目环境及依赖

```powershell
uv sync                  
```
- 根据 `pyproject.toml` 和 `uv.lock` 创建或同步虚拟环境`.venv`
- 安装项目依赖, 并更新 `uv.lock` 文件
- 移除`.venv`中未使用的依赖

3. 添加依赖

```powershell
uv add 包名              
```
- 在 `venv` 中安装依赖
- 在 `uv.lock` 中记录依赖版本
- 更新 `pyproject.toml` 中的依赖配置
  
4. 添加开发工具依赖

```powershell
uv add --dev ruff      
```

5. 运行脚本

```powershell
uv run python 文件路径.py 
```

## 2. JSON

字典是 Python 内部的数据结构, JSON 是用于传递数据的文本格式

1. python 数据 -> json 文本

```python
json.dumps(data) 
```

例子:

```python
import json

data = {
    "name": "单位换算",
    "value": 2.5,
    "success": True,
    "error": None,
}
text = json.dumps(data, ensure_ascii=False)
print(text)
print(type(text))
```

``` powershell
{"name": "单位换算", "value": 2.5, "success": true, "error": null}
<class 'str'>
```

2. json 文本 -> python 数据

```python
json.loads(text) 
```

例子:

```python
import json

text = '{"name": "单位换算", "value": 2.5, "success": true, "error": null}'
data = json.loads(text)
print(data)
print(type(data))
print(data["value"])
```

```powershell
{'name': '单位换算', 'value': 2.5, 'success': True, 'error': None}
<class 'dict'>
2.5
```
## 3. HTTP 通信

```text
客户端发送请求 → 服务端处理 → 返回响应
```

浏览器和 Python 脚本都可以充当客户端. 本机通信不需要互联网

```text
http://127.0.0.1:8000/convert?value=2500
```

- `http`: 通信协议
- `127.0.0.1`: 当前电脑
- `8000`: 服务器监听端口
- `/convert`: 接口路径
- `value=2500`: 查询参数

客户端临时端口与服务器端口不同, 端口使用由操作系统管理

## 4. FastAPI 与 Uvicorn

- FastAPI: 定义接口、校验参数、执行函数
- Uvicorn: 运行服务、接收请求、发送响应

```powershell
uv run uvicorn app:app --app-dir .\lessons\02-http-and-json --reload
```

- `app:app`：加载 `app.py` 中的 `app` 对象。
- `--reload`：修改代码后自动重新加载。
- `Ctrl+C`：停止服务。

## 5. 接口与状态码

- `@app.get("/路径")`: 登记 GET 接口, 常用于获取信息
- `@app.post("/路径")`: 登记 POST 接口, 常用于提交数据
- 接口通过“请求方法 + 路径”区分。
- Pydantic 的 `BaseModel`: 定义请求结构, 供 FastAPI 校验数据

| 状态码 | 含义 |
|---|---|
| 200 | 请求成功 |
| 404 | 未找到接口或资源 |
| 422 | 请求数据校验失败 |

## 6. HTTPX 客户端

第三方库, 用于发送HTTP请求, 接收响应, 使python脚本可以充当客户端

```python
response = httpx.post(url, json=data)
response.raise_for_status()
result = response.json()
```

url = uniform resource locator, 统一资源定位符

分别完成发送请求、检查状态、读取 JSON 结果

## 7. 格式化

统一代码格式

```powershell
uv run ruff format lessons
```

检查并自动整理导入语句

```powershell
uv run ruff check --select I --fix lessons
```

## 8. 连接大模型与请求对话

对应 `lessons/02-http-and-json/agent.py`, 使用 OpenAI SDK 请求 DeepSeek 接口

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
```

- `api_key`: 接口密钥, 从环境变量读取
- `base_url`: 模型服务地址, 使用 OpenAI SDK 不代表请求的是 OpenAI 模型
- 当前脚本在创建客户端前将环境变量设为空字符串, 运行时需要提供有效密钥; 这行赋值也会覆盖外部已有的同名环境变量

```python
messages = [
    {"role": "system", "content": "你是一个单位换算助手。进行单位换算时，请使用提供的工具。"},
    {"role": "user", "content": question},
]

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    tools=tools,
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

assistant_message = response.choices[0].message
```

- `model`: 本次请求使用的模型名称
- `messages`: 本次发给模型的对话历史; `system` 是助手要求, `user` 是用户问题
- `tools`: 本次提供给模型的工具说明
- `stream=False`: 等待完整响应后读取结果
- `reasoning_effort`、`extra_body`: 当前代码传给模型服务的思考相关配置
- `choices[0].message`: 取第一个候选回答中的助手消息
- `content`: 回答正文; `tool_calls`: 模型请求执行的工具调用

## 9. 工具说明与工具调用

模型读取工具说明, 生成工具名和参数; Python 程序负责实际执行函数

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "m_to_mm",
            "description": "将长度从米换算成毫米。",
            "parameters": {
                "type": "object",
                "properties": {"value": {"type": "number", "description": "以米为单位的长度"}},
                "required": ["value"],
            },
        },
    }
]
```

- `name`: 工具名称, 用于查找实际函数
- `description`: 工具用途, 帮助模型选择工具
- `parameters`: 用 JSON Schema 描述参数结构
- `properties`: 参数名及类型; `required`: 必须提供的参数
- 工具说明不包含函数实现, 也不等于执行结果

`agent.py` 手动编写工具说明, 并用工具注册表把名称映射到本地函数

```python
tool_functions = {
    "m_to_mm": m_to_mm,
    "convert_length": convert_length,
}

for tool_call in assistant_message.tool_calls:
    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    function = tool_functions[tool_name]
    result = function(value=arguments["value"])
```

- `function.arguments`: 模型生成的 JSON 文本, 需要用 `json.loads()` 转成 Python 字典
- 当前代码在执行前检查 `value` 是否为数字、工具名是否存在
- 一条助手消息可以包含多个工具调用, 代码逐个执行
- 没有 `tool_calls` 时, 直接输出模型回答

## 10. 工具结果与第二次请求

```text
用户问题 + 工具说明 → 第一次模型请求 → 模型返回工具名和参数
→ 程序执行工具 → 补充对话历史 → 第二次模型请求 → 最终回答
```

先保存模型发出的完整助手消息, 再加入对应的工具结果

```python
messages.append(assistant_message)

messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result, ensure_ascii=False),
    }
)
```

- `assistant_message`: 保留模型的工具调用及思考相关内容
- `role="tool"`: 表示这条消息是工具执行结果
- `tool_call_id`: 与模型返回的调用 ID 一致, 将结果关联到对应调用
- `content`: 将结果字典转成 JSON 字符串; `ensure_ascii=False` 保留中文显示

以“2.5 米换成毫米”为例, 第二次请求中的历史顺序为

```text
system: 单位换算助手的要求
user: 2.5 米换成毫米
assistant: 请求调用 m_to_mm, 参数为 {"value": 2.5}, 并附有调用 ID
tool: 对应调用 ID 的结果, 包含 output_value=2500.0、output_unit="mm"
```

```python
final_response = client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    tools=tools,
    tool_choice="none",
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

print(final_response.choices[0].message.content)
```

- 第二次请求再次传入完整 `messages`, 模型才能读到问题、工具调用和执行结果
- `tool_choice="none"`: 本次不再调用工具, 根据已有结果生成回答
- 当前代码是一轮工具执行后生成最终回答, 没有继续循环调用工具

## 11. MCP 工作原理

MCP = Model Context Protocol, 模型上下文协议. 当前项目用它统一获取工具说明和调用工具

```text
                    模型接口
                   ↑       ↓
              提交对话    返回工具调用
                   ↑       ↓
               mcp_client.py
                   ↕ stdio
               mcp_server.py
                   ↓
                tools.py
```

- 模型客户端 `model_client`: 请求 DeepSeek, 获取工具调用或最终回答
- MCP 客户端 `client`: 获取服务端工具列表, 将工具名和参数发给服务端执行
- MCP 服务端: 注册工具, 接收调用, 执行函数并返回结果
- `stdio`: 客户端与本地服务端进程通过标准输入、标准输出通信, 当前 MCP 服务不使用 HTTP 地址和端口
- 模型不直接连接 MCP 服务端, 由 `mcp_client.py` 在两者之间传递信息

`agent.py` 使用手写工具说明和本地函数注册表; `mcp_client.py` 从 MCP 服务端获取工具说明, 并通过 MCP 调用工具. 两者使用相同的两次模型请求流程

## 12. 搭建 MCP 服务端

项目已在 `pyproject.toml` 中声明 `mcp[cli]`、`openai` 等依赖

```powershell
uv sync
```

对应 `lessons/02-http-and-json/mcp_server.py`

```python
from mcp.server import MCPServer
from tools import m_to_mm as convert_m_to_mm

mcp = MCPServer("UnitConverter")

@mcp.tool()
def m_to_mm(value: float) -> dict[str, float | str]:
    """将长度从米换算成毫米, value是以米为单位的长度"""
    return convert_m_to_mm(value=value)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

- `MCPServer(...)`: 创建并命名服务
- `@mcp.tool()`: 将函数注册为 MCP 工具
- 函数名、文档字符串、参数类型注解: 用于生成工具名、说明和输入参数结构
- `dict[str, float | str]`: 返回字典, 键为字符串, 值为浮点数或字符串
- `as convert_m_to_mm`: 给导入函数起别名, 避免与工具包装函数重名
- `mcp.run(transport="stdio")`: 启动服务, 等待客户端通过 stdio 通信
- 当前注册两个工具: `m_to_mm` 和 `mm_to_m`; 后者内部调用 `tools.py` 中的 `convert_length`

## 13. MCP 客户端与模型对接

对应 `lessons/02-http-and-json/mcp_client.py`, 从项目根目录运行

```powershell
uv run python lessons/02-http-and-json/mcp_client.py
```

客户端负责启动服务端, 再获取工具列表

```python
server_path = Path(__file__).with_name("mcp_server.py")
server = StdioServerParameters(
    command=sys.executable,
    args=[str(server_path)],
)

async with Client(server) as client:
    result = await client.list_tools()
```

- `Path(__file__).with_name(...)`: 定位当前脚本同目录的服务端文件
- `sys.executable`: 使用运行客户端的 Python 解释器启动服务端
- `async with`: 建立连接, 离开代码块时自动关闭连接及服务进程
- `async def`、`await`: 定义异步函数并等待 MCP 操作完成; 入口用 `asyncio.run(main())` 运行
- `result.tools`: 服务端返回的工具列表, 每个工具包含 `name`、`description`、`input_schema`

将 MCP 工具信息转换成模型接口需要的格式, 作为第一次请求的 `tools` 参数

```python
model_tools = [
    {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }
    for tool in result.tools
]
```

模型返回工具调用后, 先检查工具名是否在服务端提供的列表中, 再解析参数并执行

```python
arguments = json.loads(tool_call.function.arguments)
call_result = await client.call_tool(tool_call.function.name, arguments)
```

- `is_error`: 工具调用是否失败; 当前代码发现失败后打印错误并 `return`, 不发起第二次模型请求
- `structured_content`: 结构化结果, 有值时用 `json.dumps()` 转成字符串
- `content`: 返回的内容块; 没有结构化结果时, 将各块通过 `model_dump(mode="json")` 转为可序列化数据, 再转成 JSON 字符串

最后按第 11 节的方式保存完整助手消息和 `role="tool"` 消息, 第二次请求传入更新后的 `messages`、`tools=model_tools` 和 `tool_choice="none"`, 获取最终回答
