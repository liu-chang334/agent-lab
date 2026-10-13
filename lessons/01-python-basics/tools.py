def convert_length(value: float) -> dict:
    """将毫米换算成米，并返回包含单位的结果。"""
    return {
        "input_value": value,
        "input_unit": "mm",
        "output_value": value / 1000,
        "output_unit": "m",
    }


def m_to_mm(value: float) -> dict:
    """将米换算成毫米"""
    return {
        "input_value": value,
        "input_unit": "m",
        "output_value": value * 1000,
        "output_unit": "mm",
    }
