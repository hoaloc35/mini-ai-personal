"""AI 383 - Safe Code Runner (Sandboxed Python)"""
import subprocess
import ast
import sys
from config import SANDBOX_TIMEOUT

BLOCKED_MODULES = {"os", "sys", "subprocess", "shutil", "socket", "requests", "urllib", "http", "ftplib", "smtplib", "ctypes", "importlib", "pathlib"}
BLOCKED_BUILTINS = {"exec", "eval", "compile", "__import__", "open", "input", "breakpoint", "exit", "quit"}

def validate_code(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"valid": False, "error": f"Loi cu phap dong {e.lineno}: {e.msg}"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in BLOCKED_MODULES:
                    return {"valid": False, "error": f"Module '{mod}' bi chan vi ly do bao mat"}
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod in BLOCKED_MODULES:
                    return {"valid": False, "error": f"Module '{mod}' bi chan vi ly do bao mat"}
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_BUILTINS:
                return {"valid": False, "error": f"Ham '{node.func.id}' bi chan vi ly do bao mat"}
    return {"valid": True}

async def execute(params: dict) -> dict:
    code = params.get("code", "")
    timeout = min(params.get("timeout", SANDBOX_TIMEOUT), 60)
    if not code: return {"status": "error", "message": "Can code Python de chay"}
    validation = validate_code(code)
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"], "type": "validation"}
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=timeout,
            env={"PATH": "", "HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
        )
        stdout = result.stdout[:10000] if result.stdout else ""
        stderr = result.stderr[:5000] if result.stderr else ""
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": stdout,
            "stderr": stderr,
            "return_code": result.returncode,
            "message": "Code chay thanh cong!" if result.returncode == 0 else "Code co loi"
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Code chay qua {timeout}s — da bi dung", "type": "timeout"}
    except Exception as e:
        return {"status": "error", "message": f"Loi chay code: {str(e)}"}
