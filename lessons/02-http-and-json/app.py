from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tools import convert_length, m_to_mm

app = FastAPI()


@app.get("/")
def home() -> dict:
    return {"message": "欢迎使用 Agent Lab"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/convert")
def convert(value: float) -> dict:
    return {
        "input_value": value,
        "input_unit": "mm",
        "output_value": value / 1000,
        "output_unit": "m",
    }


class ConversionRequest(BaseModel):
    value: float


@app.post("/convert")
def convert_from_json(request: ConversionRequest) -> dict:
    return {
        "input_value": request.value,
        "input_unit": "mm",
        "output_value": request.value / 1000,
        "output_unit": "m",
    }


class ToolArguments(BaseModel):
    value: float


class ToolRequest(BaseModel):
    name: str
    arguments: ToolArguments


tools = {
    "convert_length": convert_length,
    "m_to_mm": m_to_mm,
}


@app.post("/tools/call")
def call_tool(request: ToolRequest) -> dict:
    if request.name not in tools:
        raise HTTPException(status_code=404, detail="找不到该工具")

    tool = tools[request.name]
    return tool(value=request.arguments.value)
