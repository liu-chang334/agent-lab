from mcp.server import MCPServer
from tools import convert_length as convert_mm_to_m
from tools import m_to_mm as convert_m_to_mm

# 创建 MCP 服务
mcp = MCPServer("UnitConverter")


# 注册工具
@mcp.tool()
def m_to_mm(value: float) -> dict[str, float | str]:
    """将长度从米换算成毫米, value是以米为单位的长度"""
    return convert_m_to_mm(value=value)


@mcp.tool()
def mm_to_m(value: float) -> dict[str, float | str]:
    """将长度从毫米换算成米, value是以毫米为单位的长度"""
    return convert_mm_to_m(value=value)


# 启动服务
if __name__ == "__main__":
    mcp.run(transport="stdio")
