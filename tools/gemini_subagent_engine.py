#!/usr/bin/env python3
"""
gemini_subagent_engine.py
Adapter Engine Gemini API resmi untuk Tim Subagen Workspace (Cimoy & Dewan AI).
Model Target: gemini-3.8-flash (dengan auto-fallback cerdas ke gemini-3.6-flash & gemini-2.5-flash).
"""

import sys
import json
import urllib.request
import urllib.error

API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# Urutan prioritas model
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash"
]

def generate_subagent_response(prompt: str, system_prompt: str = None, thinking_budget: int = 2048) -> dict:
    """
    Kirim prompt ke Gemini API dengan penalaran mendalam (Medium/High Thinking: 2048-4096 tokens).
    Anti-tolol, penalaran logis, CoT (Chain-of-Thought) aktif.
    """
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    
    payload = {
        "contents": contents,
        "generationConfig": {}
    }
    
    if thinking_budget is not None:
        payload["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": thinking_budget
        }
        
    if system_prompt:
        payload["systemInstruction"] = {
            "parts": [{"text": system_prompt}]
        }

    last_error = None

    for model_name in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return {
                        "success": True,
                        "model_used": model_name,
                        "text": text,
                        "usage": data.get("usageMetadata", {})
                    }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_error = f"{model_name} HTTP {e.code}: {err_body}"
            # Jika 503 (High Demand) atau 429 (Rate Limit) atau 404, fallback ke model berikutnya
            if e.code in [404, 429, 503]:
                continue
            else:
                break
        except Exception as e:
            last_error = f"{model_name} Error: {str(e)}"
            continue

    return {
        "success": False,
        "error": last_error
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Halo, konfirmasi status kesiapan Gemini untuk tim subagent."
    
    res = generate_subagent_response(query)
    if res["success"]:
        print(f"[{res['model_used']}] {res['text']}")
    else:
        print(f"FAILED: {res['error']}")
