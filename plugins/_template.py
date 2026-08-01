"""
Plugin Template -- Tao plugin moi
Copy file nay va doi ten de tao plugin moi cho AI 383
"""

# === Thong tin plugin (BAT BUOC) ===
PLUGIN_INFO = {
    "name": "my_plugin",           # Ten plugin (unique)
    "description": "Mo ta plugin",  # Mo ta ngan
    "version": "1.0",
    "author": "Your Name",
    "config": {
        # Them config tuy chinh o day
        # "api_key": "",
    }
}


# === Ham thuc thi (BAT BUOC) ===
async def execute(params: dict) -> dict:
    """
    Ham chinh cua plugin.

    Args:
        params: Dict chua tham so tu AI hoac user

    Returns:
        Dict voi format:
        {
            "status": "success" hoac "error",
            "message": "Thong bao cho user",
            "data": ... (tuy chon)
        }
    """
    # TODO: Implement your plugin logic here
    action = params.get("action", "default")

    return {
        "status": "success",
        "message": f"Plugin '{PLUGIN_INFO['name']}' executed with action: {action}",
        "params_received": params
    }
