import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from openai import OpenAI

# api key
os.environ["DEEPSEEK_API_KEY"] = ""


async def main():
    # 找到同目录的服务端脚本
    server_path = Path(__file__).with_name("mcp_server.py")

    # 使用当前项目的Python启动服务端
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    # 启动服务端并建立 MCP 连接
    # 离开此代码块时, 自动关闭连接和服务进程
    async with Client(server) as client:
        # 向服务端询问工具列表
        result = await client.list_tools()

        # 将 MCP 工具信息转换成模型 API 使用的格式。
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

        print(json.dumps(model_tools, ensure_ascii=False, indent=2))

        for tool in result.tools:
            print("工具名: ", tool.name)
            print("工具说明: ", tool.description)

        # 模型客户端：负责让 DeepSeek 决定调用什么。
        model_client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )

        question = input("你：")

        messages = [
            {"role": "system", "content": "你是单位换算助手，换算时请使用提供的工具。"},
            {"role": "user", "content": question},
        ]

        response = model_client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            tools=model_tools,  # 使用从 MCP 获取并转换的工具说明。
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )

        assistant_message = response.choices[0].message
        print("模型请求调用：", assistant_message.tool_calls)

        if assistant_message.tool_calls:
            # 保存模型发出的完整工具调用消息。
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                # 模型只能调用 MCP 服务实际提供的工具。
                available_names = {tool.name for tool in result.tools}

                if tool_name not in available_names:
                    print(f"模型生成了未知工具名：{tool_name!r}")
                    print("可用工具：", available_names)
                    return

                arguments = json.loads(tool_call.function.arguments)

                print(f"通过 MCP 调用：{tool_name}，参数：{arguments}")

                call_result = await client.call_tool(
                    tool_name,
                    arguments,
                )

                # 工具执行失败时，显示错误并结束本次运行。
                if call_result.is_error:
                    print("MCP 调用失败：", call_result.content)
                    return

                print("工具执行成功：", call_result.structured_content)

                # 将 MCP 结果转换为模型可以读取的字符串。
                if call_result.is_error:
                    # 工具出错时，把错误内容交给模型。
                    result_text = call_result.model_dump_json()
                elif call_result.structured_content is not None:
                    result_text = json.dumps(
                        call_result.structured_content,
                        ensure_ascii=False,
                    )
                else:
                    # 没有结构化结果时，保留返回的内容块。
                    result_text = json.dumps(
                        [
                            block.model_dump(mode="json")
                            for block in call_result.content
                        ],
                        ensure_ascii=False,
                    )

                # 将结果与对应的工具调用关联起来。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    }
                )

            # 所有工具执行完毕后，让模型生成最终回答。
            final_response = model_client.chat.completions.create(
                model="deepseek-flash",
                messages=messages,
                tools=model_tools,
                tool_choice="none",
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
            )

            print("助手：", final_response.choices[0].message.content)
        else:
            print("助手：", assistant_message.content)


if __name__ == "__main__":
    asyncio.run(main())
