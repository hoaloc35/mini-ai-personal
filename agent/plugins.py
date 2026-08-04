"""
AI 383 - Plugin System
He thong plugin mo rong
"""
import importlib.util
import json
from pathlib import Path
from agent import database as db

LOADED_PLUGINS = {}

async def load_plugins(plugins_dir: Path):
    global LOADED_PLUGINS
    registered = await db.get_plugins(enabled_only=True)
    for plugin_info in registered:
        name = plugin_info["name"]
        filepath = plugin_info["filepath"]
        try:
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "execute"):
                LOADED_PLUGINS[name] = {
                    "module": module,
                    "execute": module.execute,
                    "description": plugin_info.get("description", ""),
                    "config": json.loads(plugin_info.get("config", "{}")),
                }
                print(f"  Plugin loaded: {name}")
        except Exception as e:
            print(f"  Plugin '{name}' error: {e}")
    if plugins_dir.exists():
        for py_file in plugins_dir.glob("*.py"):
            if py_file.stem.startswith("_") or py_file.stem in LOADED_PLUGINS:
                continue
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, str(py_file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "PLUGIN_INFO") and hasattr(module, "execute"):
                    info = module.PLUGIN_INFO
                    await db.register_plugin(
                        name=info.get("name", py_file.stem),
                        description=info.get("description", ""),
                        filepath=str(py_file),
                        config=info.get("config", {})
                    )
                    LOADED_PLUGINS[py_file.stem] = {
                        "module": module,
                        "execute": module.execute,
                        "description": info.get("description", ""),
                        "config": info.get("config", {}),
                    }
                    print(f"  Auto-registered plugin: {py_file.stem}")
            except Exception as e:
                print(f"  Skip {py_file.name}: {e}")

def get_plugin(name):
    return LOADED_PLUGINS.get(name)

def list_plugins():
    return {name: {"description": p["description"], "config": p["config"]} for name, p in LOADED_PLUGINS.items()}

async def execute_plugin(name, params):
    plugin = LOADED_PLUGINS.get(name)
    if not plugin:
        return {"status": "error", "message": f"Plugin '{name}' not found"}
    try:
        return await plugin["execute"](params)
    except Exception as e:
        return {"status": "error", "message": f"Plugin error: {str(e)}"}
