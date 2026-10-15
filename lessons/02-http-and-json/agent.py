# Please install OpenAI SDK first: `pip3 install openai`
import json
import os

from openai import OpenAI
from tools import convert_length, m_to_mm

# api key
os.environ["DEEPSEEK_API_KEY"] = ""

# 从环境变量读取密钥，创建客户端。
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 工具注册表：通过名称找到本地函数。
tool_functions = {
    "m_to_mm": m_to_mm,
    "convert_length": convert_length,
}

# 提供给模型的工具说明。
tools = [
    {
        "type": "function",
        "function": {
            "name": "m_to_mm",
            "description": "将长度从米换算成毫米。",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "以米为单位的长度",
                    }
                },
                "required": ["value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_length",
            "description": "将长度从毫米换算成米。",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "以毫米为单位的长度",
                    }
                },
                "required": ["value"],
            },
        },
    },
]

# 读取问题，建立对话历史。
question = input("你：")

messages = [
    {
        "role": "system",
        "content": "你是一个单位换算助手。进行单位换算时，请使用提供的工具。",
    },
    {"role": "user", "content": question},
]

# 第一次请求：让模型选择工具并生成参数。
response = client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    tools=tools,
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

assistant_message = response.choices[0].message

if not assistant_message.tool_calls:
    # 模型没有调用工具，直接输出回答。
    print("模型直接回答，未调用工具。")
    print(assistant_message.content)
else:
    # 保存完整助手消息，包括工具调用和思考内容。
    messages.append(assistant_message)

    for tool_call in assistant_message.tool_calls:
        # 解析模型生成的参数。
        arguments = json.loads(tool_call.function.arguments)
        value = arguments["value"]

        if type(value) not in (int, float):
            raise ValueError("value 必须是数字")

        # 根据工具名称，从注册表中查找函数。
        tool_name = tool_call.function.name

        if tool_name not in tool_functions:
            raise ValueError(f"未知工具：{tool_name}")

        function = tool_functions[tool_name]

        # 在执行前打印工具名称及参数。
        print(f"调用工具：{tool_name}，参数：{arguments}")

        # 执行函数，获得换算结果。
        result = function(value=value)

        # 将工具结果加入对话历史。
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    # 第二次请求：根据工具结果生成最终回答。
    final_response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools,
        tool_choice="none",
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )

    print("助手：", final_response.choices[0].message.content)
