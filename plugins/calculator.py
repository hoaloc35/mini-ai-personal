"""
Example Plugin -- Tinh toan
Minh hoa cach tao plugin cho AI 383
"""

PLUGIN_INFO = {
    "name": "calculator",
    "description": "May tinh -- tinh toan bieu thuc toan hoc",
    "version": "1.0",
    "author": "AI 383",
    "config": {}
}


async def execute(params: dict) -> dict:
    """
    Calculate a math expression.
    params: {"expression": "2 + 3 * 4"}
    """
    expression = params.get("expression", "")
    if not expression:
        return {"status": "error", "message": "Can bieu thuc toan hoc"}

    try:
        # Safe eval -- only allow math operations
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return {"status": "error", "message": "Bieu thuc khong hop le"}

        result = eval(expression)
        return {
            "status": "success",
            "expression": expression,
            "result": result,
            "message": f"{expression} = {result}"
        }
    except Exception as e:
        return {"status": "error", "message": f"Loi tinh toan: {str(e)}"}
