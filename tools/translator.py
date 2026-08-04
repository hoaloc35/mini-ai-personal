"""AI 383 - Translation Tool (16+ languages, Gemini AI)"""
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME

SUPPORTED_LANGUAGES = {
    "vi": "Vietnamese", "en": "English", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "fr": "French", "de": "German", "es": "Spanish",
    "pt": "Portuguese", "ru": "Russian", "ar": "Arabic", "hi": "Hindi",
    "th": "Thai", "id": "Indonesian", "ms": "Malay", "it": "Italian"
}

async def execute(params: dict) -> dict:
    text = params.get("text", "")
    target_lang = params.get("target_lang", "vi")
    source_lang = params.get("source_lang", "auto")
    if not text: return {"status": "error", "message": "Can van ban de dich"}
    if not GEMINI_API_KEY: return {"status": "error", "message": "Can GEMINI_API_KEY"}
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        target_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        if source_lang == "auto":
            prompt = f"Detect the language of the following text and translate it to {target_name}. Return ONLY the translation, nothing else:\n\n{text}"
        else:
            source_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
            prompt = f"Translate the following {source_name} text to {target_name}. Return ONLY the translation:\n\n{text}"
        response = model.generate_content(prompt)
        translated = response.text.strip()
        return {"status": "success", "original": text, "translated": translated, "target_lang": target_lang, "source_lang": source_lang}
    except Exception as e:
        return {"status": "error", "message": f"Loi dich: {str(e)}"}

def get_supported_languages():
    return SUPPORTED_LANGUAGES
