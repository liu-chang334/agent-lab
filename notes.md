<!-- omit from toc -->
# Agent Lab 学习笔记
- [1. Python 基础](#1-python-基础)
- [2. uv 环境管理](#2-uv-环境管理)
- [3. JSON](#3-json)
- [4. HTTP 通信](#4-http-通信)
- [5. FastAPI 与 Uvicorn](#5-fastapi-与-uvicorn)
- [6. 接口与状态码](#6-接口与状态码)
- [7. HTTPX 客户端](#7-httpx-客户端)
- [8. 格式化](#8-格式化)


## 1. Python 基础

- `.py`: 源码; `.pyc`: 字节码缓存; `.pyd`: 编译后的扩展模块

## 2. uv 环境管理

```powershell
uv python pin 3.12       # 记录项目使用的 Python 版本
uv sync                  # 创建或同步项目环境及依赖
uv add 包名              # 添加依赖并更新项目环境
uv add --dev ruff        # 添加开发工具依赖
uv run python 文件路径.py # 在项目环境中运行脚本
```

- `pyproject.toml`: 项目信息与依赖配置
- `.python-version`: Python 版本记录
- `.venv/`: 项目独立环境
- `uv.lock`: 依赖版本锁定文件

## 3. JSON

字典是 Python 内部的数据结构, JSON 是用于传递数据的文本格式

```python
json.dumps(data)  # Python 数据 → JSON 文本
json.loads(text)  # JSON 文本 → Python 数据
```

## 4. HTTP 通信

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

## 5. FastAPI 与 Uvicorn

- FastAPI: 定义接口、校验参数、执行函数
- Uvicorn: 运行服务、接收请求、发送响应

```powershell
uv run uvicorn app:app --app-dir .\lessons\02-http-and-json --reload
```

- `app:app`：加载 `app.py` 中的 `app` 对象。
- `--reload`：修改代码后自动重新加载。
- `Ctrl+C`：停止服务。

## 6. 接口与状态码

- `@app.get("/路径")`: 登记 GET 接口, 常用于获取信息
- `@app.post("/路径")`: 登记 POST 接口, 常用于提交数据
- 接口通过“请求方法 + 路径”区分。
- Pydantic 的 `BaseModel`: 定义请求结构, 供 FastAPI 校验数据

| 状态码 | 含义 |
|---|---|
| 200 | 请求成功 |
| 404 | 未找到接口或资源 |
| 422 | 请求数据校验失败 |

## 7. HTTPX 客户端

第三方库, 用于发送HTTP请求, 接收响应, 使python脚本可以充当客户端

```python
response = httpx.post(url, json=data)
response.raise_for_status()
result = response.json()
```

url = uniform resource locator, 统一资源定位符

分别完成发送请求、检查状态、读取 JSON 结果

## 8. 格式化

统一代码格式

```powershell
uv run ruff format lessons
```

检查并自动整理导入语句

```powershell
uv run ruff check --select I --fix lessons
```
