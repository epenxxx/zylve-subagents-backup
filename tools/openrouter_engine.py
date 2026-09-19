#!/usr/bin/env python3
"""
openrouter_engine.py
Engine Cadangan Multi-Model (OpenRouter API) untuk Subagen ZYLVEmedia.
Akses model gratis & premium: deepseek/deepseek-r1:free, meta-llama/llama-3.3-70b-instruct:free, dll.
"""

import sys
import os
import json
import urllib.request
import urllib.error

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"

# Model-model gratis aktif OpenRouter
FREE_MODELS = [
    "deepseek/deepseek-v4-flash-0731:free",
    "qwen/qwen3.8-27b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "z-ai/glm-5.2:free"
]

def generate_openrouter_response(prompt: str, system_prompt: str = None, model: str = None) -> dict:
    """Kirim prompt ke OpenRouter dengan auto-fallback antar model gratis."""
    models_to_try = [model] if model else FREE_MODELS
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    last_error = None
    for m in models_to_try:
        payload = {
            "model": m,
            "messages": messages,
            "temperature": 0.7
        }
        req = urllib.request.Request(
            URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://zylvemedia.web.id",
                "X-Title": "ZYLVEmedia Subagents"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    return {
                        "success": True,
                        "model_used": m,
                        "text": content,
                        "usage": data.get("usage", {})
                    }
        except Exception as e:
            last_error = f"{m} Error: {str(e)}"
            continue
            
    return {"success": False, "error": last_error}

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Tes integrasi OpenRouter ZYLVEmedia."
    res = generate_openrouter_response(q)
    if res["success"]:
        print(f"[{res['model_used']}]\n{res['text']}")
    else:
        print(f"FAILED: {res['error']}")
