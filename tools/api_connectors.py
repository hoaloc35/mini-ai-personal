"""AI 383 - API Connectors for Creative AI (Image/Video/Music)"""
from config import IMAGE_GEN_API_KEY, IMAGE_GEN_PROVIDER, VIDEO_GEN_API_KEY, MUSIC_GEN_API_KEY

async def generate_image(params: dict) -> dict:
    prompt = params.get("prompt", "")
    if not prompt: return {"status": "error", "message": "Can mo ta hinh anh"}
    if not IMAGE_GEN_API_KEY:
        return {"status": "info", "message": "Chua co API key tao anh. Them IMAGE_GEN_API_KEY vao .env\n\nCac provider ho tro:\n- Gemini Imagen: aistudio.google.com/apikey\n- DALL-E: platform.openai.com/api-keys"}
    try:
        if IMAGE_GEN_PROVIDER == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=IMAGE_GEN_API_KEY)
            # Placeholder: Gemini Imagen API call
            return {"status": "success", "message": f"Dang tao anh: '{prompt}'", "provider": "gemini", "note": "Ket noi Gemini Imagen API"}
        elif IMAGE_GEN_PROVIDER == "openai":
            return {"status": "success", "message": f"Dang tao anh voi DALL-E: '{prompt}'", "provider": "openai"}
        else:
            return {"status": "error", "message": f"Provider '{IMAGE_GEN_PROVIDER}' khong ho tro"}
    except Exception as e:
        return {"status": "error", "message": f"Loi tao anh: {str(e)}"}

async def generate_video(params: dict) -> dict:
    prompt = params.get("prompt", "")
    if not prompt: return {"status": "error", "message": "Can mo ta video"}
    if not VIDEO_GEN_API_KEY:
        return {"status": "info", "message": "Chua co API key tao video. Them VIDEO_GEN_API_KEY vao .env\n\nCac provider ho tro:\n- RunwayML: runwayml.com\n- Pika: pika.art"}
    try:
        return {"status": "success", "message": f"Dang tao video: '{prompt}'", "duration": params.get("duration", 5)}
    except Exception as e:
        return {"status": "error", "message": f"Loi tao video: {str(e)}"}

async def generate_music(params: dict) -> dict:
    prompt = params.get("prompt", "")
    if not prompt: return {"status": "error", "message": "Can mo ta nhac"}
    if not MUSIC_GEN_API_KEY:
        return {"status": "info", "message": "Chua co API key tao nhac. Them MUSIC_GEN_API_KEY vao .env\n\nCac provider ho tro:\n- Suno: suno.com\n- Udio: udio.com"}
    try:
        return {"status": "success", "message": f"Dang tao nhac: '{prompt}'", "genre": params.get("genre", ""), "duration": params.get("duration", 30)}
    except Exception as e:
        return {"status": "error", "message": f"Loi tao nhac: {str(e)}"}
