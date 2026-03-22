import time
from flask import current_app

def translate(text,source_language,dest_language):
    time.sleep(1)

    if not current_app.config["TRANSLATE_KEY"]:
        return "Error: API key not found"
    return f"[翻訳済({dest_language})]:{text}の模擬翻訳です"