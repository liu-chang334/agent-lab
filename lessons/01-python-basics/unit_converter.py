import json

from tools import convert_length, m_to_mm

request = {
    "name": "m_to_mm",
    "arguments": {
        "value": 2.5,
    },
}
request_text = json.dumps(request, ensure_ascii=False, indent=2)
request_data = json.loads(request_text)

# 工具注册表
tools = {
    "convert_length": convert_length,
    "m_to_mm": m_to_mm,
}

tool_name = request_data["name"]
arguments = request_data["arguments"]

if tool_name not in tools:
    result = {"error": f"找不到工具: {tool_name}"}
else:
    tool = tools[tool_name]
    result = tool(**arguments)

print(json.dumps(result, ensure_ascii=False, indent=2))
