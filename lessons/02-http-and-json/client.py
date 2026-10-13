import httpx

response = httpx.post(
    "http://127.0.0.1:8000/tools/call",
    json={
        "name": "m_to_mm",
        "arguments": {"value": 2.5},
    },
    timeout=10.0,
)

print("状态码: ", response.status_code)
response.raise_for_status()

result = response.json()
print("换算结果: ", result["output_value"], result["output_unit"])
