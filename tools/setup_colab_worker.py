import json
import time
from playwright.sync_api import sync_playwright

COLAB_URL = "https://colab.research.google.com/drive/1AMbpmoip7e_ZDgYHujHVA69RdZILJi5d?usp=sharing"
COOKIES_PATH = "/root/zylve_automation/gemini_cookies.json"

WORKER_CODE = """
import os, subprocess, time, torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# 1. Install dependencies
print("[1/3] Menyiapkan modul GPU (Demucs + Faster-Whisper + FastAPI + Cloudflared)...")
subprocess.run("pip install -q fastapi uvicorn python-multipart faster-whisper demucs", shell=True)
subprocess.run("wget -qO /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x /usr/local/bin/cloudflared", shell=True)

from faster_whisper import WhisperModel

app = FastAPI(title="ZYLVE Colab GPU Worker")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[2/3] Memuat Whisper Large-v3 ke GPU ({device})...")
whisper_model = WhisperModel("large-v3", device=device, compute_type="float16")

@app.get("/health")
def health():
    return {
        "status": "online",
        "device": device,
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "vram_mb": round(torch.cuda.memory_allocated(0) / 1024 / 1024, 2) if torch.cuda.is_available() else 0
    }

@app.post("/separate")
async def separate(file: UploadFile = File(...)):
    os.makedirs("/content/work/input", exist_ok=True)
    os.makedirs("/content/work/output", exist_ok=True)
    in_path = f"/content/work/input/{file.filename}"
    with open(in_path, "wb") as f:
        f.write(await file.read())
    
    # Demucs v4 Hybrid Transformer
    cmd = f"demucs -d cuda -n htdemucs --two-stems vocals '{in_path}' -o /content/work/output"
    subprocess.run(cmd, shell=True, check=True)
    
    base_name = os.path.splitext(file.filename)[0]
    out_file = f"/content/work/output/htdemucs/{base_name}/no_vocals.wav"
    return FileResponse(out_file, media_type="audio/wav", filename=f"karaoke_{base_name}.wav")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    os.makedirs("/content/work/input", exist_ok=True)
    in_path = f"/content/work/input/{file.filename}"
    with open(in_path, "wb") as f:
        f.write(await file.read())
    
    segments, info = whisper_model.transcribe(in_path, word_timestamps=True)
    items = []
    for s in segments:
        words = []
        if s.words:
            for w in s.words:
                words.append({"word": w.word, "start": w.start, "end": w.end, "prob": round(w.probability, 3)})
        items.append({"start": s.start, "end": s.end, "text": s.text.strip(), "words": words})
    return {"language": info.language, "duration": round(info.duration, 2), "segments": items}

@app.post("/render_video")
async def render_video(cmd: str = Form(...)):
    # Render with FFmpeg NVENC
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"returncode": p.returncode, "stdout": p.stdout[-400:], "stderr": p.stderr[-400:]}

with open("/content/app.py", "w") as f:
    f.write('''import uvicorn
from __main__ import app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

# Jalankan Uvicorn di background
print("[3/3] Meluncurkan Worker & Cloudflare Tunnel...")
server = subprocess.Popen(["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"])
time.sleep(3)

# Jalankan Cloudflare Tunnel
tunnel = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in tunnel.stdout:
    if "trycloudflare.com" in line:
        print("\\n" + "="*60)
        print(">>> URL API COLAB GPU KAMU:")
        print(line.strip())
        print("="*60 + "\\n")
        break
tunnel.wait()
"""

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

def deploy():
    cookies = load_cookies()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        context.add_cookies(cookies)
        page = context.new_page()
        
        print("Membuka Google Colab...")
        page.goto(COLAB_URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(6000)
        
        # Connect if needed
        btn = page.query_selector("colab-connect-button")
        if btn and ("Connect" in btn.inner_text() or btn.inner_text().strip() == ""):
            print("Klik connect...")
            btn.click()
            page.wait_for_timeout(5000)
            
        # Write setup script to Colab via clipboard/injection
        print("Menyuntikkan kode worker ke cell...")
        editor = page.query_selector(".monaco-editor, .cell, colab-cell")
        if editor:
            editor.click()
            # Select all in cell
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            # Send code using insert_text
            page.keyboard.insert_text(WORKER_CODE)
            page.wait_for_timeout(2000)
            
            # Run cell
            print("Menjalankan cell (Control+Enter)...")
            page.keyboard.press("Control+Enter")
            
            print("Menunggu instalasi & peluncuran (60 detik)...")
            for i in range(12):
                time.sleep(5)
                page.screenshot(path="/root/screenshots/colab_deploy_progress.png")
                print(f"Status progress di-capture ({(i+1)*5} detik)...")
                
        page.screenshot(path="/root/screenshots/colab_worker_deployed.png")
        print("Selesai! Screenshot tersimpan di /root/screenshots/colab_worker_deployed.png")
        browser.close()

if __name__ == "__main__":
    deploy()
