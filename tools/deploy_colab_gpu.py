#!/usr/bin/env python3
import os
import sys
import time
import json
import base64
from playwright.sync_api import sync_playwright

COLAB_URL = "https://colab.research.google.com/drive/1AMbpmoip7e_ZDgYHujHVA69RdZILJi5d?usp=sharing"
COOKIES_PATH = "/root/zylve_automation/gemini_cookies.json"

WORKER_PY = """import os, subprocess, sys, time

print("[Colab GPU] 1/4 Menyiapkan modul GPU (FastAPI, Faster-Whisper, Demucs)...")
pkgs = ["fastapi", "uvicorn", "python-multipart", "faster-whisper", "demucs"]
subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + pkgs, check=True)

if not os.path.exists("/usr/local/bin/cloudflared"):
    print("[Colab GPU] 2/4 Mengunduh Cloudflared Tunnel...")
    subprocess.run("wget -qO /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x /usr/local/bin/cloudflared", shell=True, check=True)

app_code = '''import os, subprocess, torch, time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel

app = FastAPI(title="ZYLVE Colab GPU Server")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[ZYLVE] Loading Faster-Whisper Large-v3 on {device}...")
whisper_model = WhisperModel("large-v3", device=device, compute_type="float16")
print("[ZYLVE] Whisper Ready!")

@app.get("/health")
def health():
    return {
        "status": "online",
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "vram_mb": round(torch.cuda.memory_allocated(0) / 1024 / 1024, 2) if torch.cuda.is_available() else 0
    }

@app.post("/separate")
async def separate(file: UploadFile = File(...)):
    work_dir = "/content/work"
    os.makedirs(f"{work_dir}/input", exist_ok=True)
    os.makedirs(f"{work_dir}/output", exist_ok=True)
    in_file = f"{work_dir}/input/{file.filename}"
    with open(in_file, "wb") as f:
        f.write(await file.read())
    
    cmd = f"demucs -d cuda -n htdemucs --two-stems vocals '{in_file}' -o '{work_dir}/output'"
    subprocess.run(cmd, shell=True, check=True)
    
    base = os.path.splitext(file.filename)[0]
    out_path = f"{work_dir}/output/htdemucs/{base}/no_vocals.wav"
    return FileResponse(out_path, media_type="audio/wav", filename=f"karaoke_{base}.wav")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    work_dir = "/content/work"
    os.makedirs(f"{work_dir}/input", exist_ok=True)
    in_file = f"{work_dir}/input/{file.filename}"
    with open(in_file, "wb") as f:
        f.write(await file.read())
    
    segments, info = whisper_model.transcribe(in_file, word_timestamps=True)
    items = []
    for s in segments:
        words = []
        if s.words:
            for w in s.words:
                words.append({"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3), "prob": round(w.probability, 3)})
        items.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words})
    return {"language": info.language, "duration": round(info.duration, 2), "segments": items}

@app.post("/render_video")
async def render_video(cmd: str = Form(...)):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"returncode": p.returncode, "stdout": p.stdout[-400:], "stderr": p.stderr[-400:]}
'''

with open("/content/server.py", "w") as f:
    f.write(app_code)

print("[Colab GPU] 3/4 Menjalankan server FastAPI di background...")
srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"])
time.sleep(3)

print("[Colab GPU] 4/4 Membuka Cloudflare Tunnel publik...")
subprocess.run("pkill cloudflared || true", shell=True)
cf = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
tunnel_url = None
for line in cf.stdout:
    print(line, end="")
    if ".trycloudflare.com" in line:
        for word in line.split():
            if "trycloudflare.com" in word and ("https://" in word or "http://" in word):
                tunnel_url = word.strip().strip("| ")
                break
        if tunnel_url:
            break

if tunnel_url:
    print("\\n" + "="*60)
    print(">>> TUNNEL_READY:", tunnel_url)
    print("="*60 + "\\n")
    with open("/content/tunnel_url.txt", "w") as f_out:
        f_out.write(tunnel_url)
cf.wait()
"""

b64_script = base64.b64encode(WORKER_PY.encode("utf-8")).decode("utf-8")
ONE_LINER = f'import base64; exec(base64.b64decode("{b64_script}").decode("utf-8"))'

def load_cookies():
    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    pw = []
    for c in raw:
        d = c.get("domain", "")
        if not d.startswith(".google.com") and not d.endswith("google.com"):
            continue
        item = {"name": c["name"], "value": c["value"], "domain": d, "path": c.get("path", "/"), "secure": c.get("secure", True)}
        s = c.get("sameSite", "")
        if s in ["Strict", "Lax", "None"]:
            item["sameSite"] = s
        pw.append(item)
    return pw

def main():
    cookies = load_cookies()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        context.add_cookies(cookies)
        page = context.new_page()

        print("Membuka Google Colab...")
        page.goto(COLAB_URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(6000)

        # Cek tombol connect
        btn = page.query_selector("colab-connect-button")
        if btn and ("Connect" in btn.inner_text() or btn.inner_text().strip() == ""):
            print("Menghubungkan runtime GPU...")
            btn.click()
            page.wait_for_timeout(5000)

        # Fokus ke cell
        cell = page.query_selector(".cell, colab-cell")
        if cell:
            print("Menyuntikkan payload eksekusi (Base64 One-Liner)...")
            cell.click()
            page.keyboard.press("Control+A")
            page.keyboard.insert_text(ONE_LINER)
            page.wait_for_timeout(1000)

            print("Menjalankan worker di GPU Colab (Control+Enter)...")
            page.keyboard.press("Control+Enter")

            # Pantau log output cell selama 2 menit
            print("Memantau peluncuran & tunnel URL...")
            tunnel_found = None
            for sec in range(1, 30):
                time.sleep(4)
                text = page.inner_text("body")
                if "TUNNEL_READY:" in text:
                    idx = text.find("TUNNEL_READY:")
                    after = text[idx:idx+200]
                    for part in after.split():
                        if ".trycloudflare.com" in part:
                            clean_url = part.strip().strip("'\"()[],.")
                            if not clean_url.startswith("http"): clean_url = "https://" + clean_url
                            tunnel_found = clean_url
                            print(f"BINGO! Tunnel URL Ditemukan: {tunnel_found}")
                            os.makedirs("/root/.config/colab", exist_ok=True)
                            with open("/root/.config/colab/tunnel_url.txt", "w") as f:
                                f.write(tunnel_found)
                            break
                    if tunnel_found:
                        break
                print(f"Menunggu worker aktif... ({sec*4}s)")
                page.screenshot(path="/root/screenshots/colab_deploy_live.png")

        page.screenshot(path="/root/screenshots/colab_deploy_final.png")
        print("Selesai! Tangkapan layar tersimpan di /root/screenshots/colab_deploy_final.png")
        browser.close()

if __name__ == "__main__":
    main()
