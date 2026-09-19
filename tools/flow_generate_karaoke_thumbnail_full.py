#!/usr/bin/env python3
"""
Eksekutor Thumbnail Karaoke YouTube via Google Flow (Agent 4)
Versi DINAMIS — menerima parameter lagu (judul, artis, path thumbnail asli).
"""
import asyncio
import json
import os
import sys
import time
import argparse
from playwright.async_api import async_playwright

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
FLOW_BASE_URL = "https://flow.google.com/"
SCREENSHOTS_DIR = "/root/screenshots"

def build_prompt(song_title, artist, extra=""):
    """Buat prompt dinamis berdasarkan judul lagu dan artis."""
    return (
        f"Berdasarkan gambar referensi ini, modifikasi menjadi Thumbnail YouTube KARAOKE VERSION 16:9 Full HD. "
        f"Pertahankan foto asli artis dengan resolusi sangat tajam dan pencahayaan panggung musik glamor. "
        f"Tambahkan teks besar 3D warna emas mencolok: 'KARAOKE' dan '{song_title.upper()} - {artist.upper()}'. "
        f"Tambahkan badge merah tebal: 'TANPA VOKAL / by ZYLVEmedia' dan 'LIRIK BERJALAN'. "
        f"Tambahkan mikrofon panggung metalik bercahaya dan gelombang audio wave neon di latar panggung ungu-biru. "
        f"Fotorealistis 4K standar grafis YouTube Music resmi, DILARANG kartun, DILARANG animasi lilin slop. "
        f"{extra}"
    ).strip()

async def generate_thumbnail(song_title, artist, thumb_ref_path, output_path, project_url=None):
    """
    Eksekusi Google Flow untuk generate thumbnail karaoke.
    
    Args:
        song_title: Judul lagu (misal: "Mutiara")
        artist: Nama artis (misal: "Ipank")
        thumb_ref_path: Path thumbnail asli sebagai referensi
        output_path: Path output thumbnail hasil Google Flow
        project_url: URL project Google Flow (opsional, buat baru jika None)
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    if not os.path.exists(FLOW_COOKIES):
        print(f"[!] Cookies Google Flow tidak ditemukan: {FLOW_COOKIES}")
        return False

    prompt_text = build_prompt(song_title, artist)
    print(f"[*] Prompt: {prompt_text[:100]}...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--ignore-certificate-errors'])
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            cookies = json.load(open(FLOW_COOKIES))
            clean_cookies = [{"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c.get("path", "/"), "secure": c.get("secure", False), "httpOnly": c.get("httpOnly", False)} for c in cookies]
            await context.add_cookies(clean_cookies)

            page = await context.new_page()

            # 1. Buka Google Flow
            target_url = project_url or FLOW_BASE_URL
            print(f"[1/6] Membuka Google Flow: {target_url}")
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            # 2. Set mode Gambar & rasio 16:9
            print("[2/6] Mengatur Setelan Rasio 16:9 dan Mode Gambar...")
            tune_btn = await page.query_selector('button:has-text("tune"), button[aria-label*="Setelan"]')
            if tune_btn:
                await tune_btn.click()
                await page.wait_for_timeout(1000)
                img_mode = await page.query_selector('button:has-text("Gambar"), [role="tab"]:has-text("Gambar")')
                if img_mode:
                    await img_mode.click()
                    await page.wait_for_timeout(500)
                btn_169 = await page.query_selector('button:has-text("16:9")')
                if btn_169:
                    await btn_169.click()
                    await page.wait_for_timeout(500)
                btn_simpan = await page.query_selector('button:has-text("Simpan")')
                if btn_simpan:
                    await btn_simpan.click()
                    await page.wait_for_timeout(1000)
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
                try:
                    bd = await page.query_selector('.cdk-overlay-backdrop')
                    if bd:
                        await bd.click(force=True)
                except Exception:
                    pass
                await page.wait_for_timeout(1000)

            # 3. Upload thumbnail referensi jika ada
            if thumb_ref_path and os.path.exists(thumb_ref_path):
                print(f"[3/6] Mengunggah thumbnail referensi: {os.path.basename(thumb_ref_path)}")
                btn_add = await page.query_selector('button[aria-label="Tambahkan bahan ke kotak perintah"], button[aria-label*="Tambahkan bahan"], button[aria-label*="Add materials"]')
                if btn_add:
                    await btn_add.click()
                    await page.wait_for_timeout(2000)
                    # Coba upload file langsung
                    file_input = await page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(thumb_ref_path)
                        await page.wait_for_timeout(3000)
                        print("[✓] Thumbnail referensi terunggah.")
                    attach_btn = await page.query_selector('button:has-text("Tambahkan ke perintah"), button:has-text("Add to prompt")')
                    if attach_btn:
                        await attach_btn.click()
                        await page.wait_for_timeout(2000)
            else:
                print("[3/6] Tidak ada thumbnail referensi, skip upload.")

            # 4. Ketik prompt
            print("[4/6] Mengisi prompt dinamis...")
            prompt_box = await page.query_selector('.ProseMirror')
            if prompt_box:
                await prompt_box.click()
                await page.wait_for_timeout(500)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await page.wait_for_timeout(500)
                await page.keyboard.type(prompt_text, delay=8)
                await page.wait_for_timeout(1000)

            await page.screenshot(path=f"{SCREENSHOTS_DIR}/flow_thumb_{song_title.lower().replace(' ','_')}_prompt.png")

            # 5. Klik generate
            print("[5/6] Mengklik tombol Mulai pembuatan...")
            btn_generate = await page.query_selector('button[aria-label="Mulai pembuatan"], button[aria-label*="Kirim"], button:has-text("send")')
            if btn_generate:
                await btn_generate.click()
            else:
                await page.keyboard.press("Enter")

            await page.wait_for_timeout(5000)
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/flow_thumb_{song_title.lower().replace(' ','_')}_generating.png")

            # 6. Tunggu hasil (maks 200 detik)
            print("[6/6] Menunggu hasil render Google Flow...")
            downloaded = False
            for check in range(25):
                await page.wait_for_timeout(8000)
                current_imgs = await page.query_selector_all('img')
                print(f"[{check*8}s] Cek kanvas... (img count: {len(current_imgs)})")
                for img in reversed(current_imgs):
                    src = await img.get_attribute('src')
                    if src and ('googleusercontent' in src or 'blob:' in src) and 'avatar' not in src:
                        await img.screenshot(path=output_path)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 30000:
                            print(f"[✓] Thumbnail berhasil disimpan: {output_path} ({os.path.getsize(output_path)} bytes)")
                            downloaded = True
                            break
                if downloaded:
                    break

            if not downloaded:
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/flow_thumb_GAGAL_{song_title.lower().replace(' ','_')}.png")
                print("[!] Gagal mendapatkan hasil thumbnail dari Google Flow. Menjalankan Fallback Gemini Web...")
                downloaded = fallback_gemini_web(song_title, artist, output_path)

            await browser.close()
            return downloaded
    except Exception as e_gen:
        print(f"[!] Exception pada Google Flow: {e_gen}. Menjalankan Fallback Gemini Web...")
        return fallback_gemini_web(song_title, artist, output_path)

def fallback_gemini_web(song_title, artist, output_path):
    print("[Fallback] Memulai fallback otomatis ke Gemini Web Imagen Engine via subprocess...")
    try:
        import subprocess
        code = f"""
import sys, os
sys.path.append('/root/zylve_automation')
from storyboard_hybrid_engine import fetch_imagen_background
prompt = "Desain Thumbnail YouTube Karaoke 16:9 Full HD panggung musik glamor sinematik. Teks besar 3D warna emas: 'KARAOKE' dan '{song_title.upper()} - {artist.upper()}'. Badge merah: 'TANPA VOKAL / by ZYLVEmedia'. Fotorealistis 4K."
ok = fetch_imagen_background(prompt, '{output_path}')
sys.exit(0 if ok else 1)
"""
        res = subprocess.run([sys.executable, "-c", code], timeout=120)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            print(f"[✓ Fallback Gemini Web] Sukses simpan thumbnail: {output_path}")
            return True
    except Exception as e:
        print(f"[Fallback Gemini Web] Error: {e}")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 4: Generate Thumbnail Karaoke YouTube via Google Flow (Dinamis)")
    parser.add_argument("--title", required=True, help="Judul lagu (misal: Mutiara)")
    parser.add_argument("--artist", required=True, help="Nama artis (misal: Ipank)")
    parser.add_argument("--ref", default=None, help="Path thumbnail asli sebagai referensi")
    parser.add_argument("-o", "--output", default=None, help="Path output thumbnail hasil")
    parser.add_argument("--project-url", default=None, help="URL project Google Flow (opsional)")
    args = parser.parse_args()

    output = args.output or f"/root/assets/thumbnail_{args.title.lower().replace(' ','_')}/thumbnail_google_flow_16x9.png"
    
    ok = asyncio.run(generate_thumbnail(args.title, args.artist, args.ref, output, args.project_url))
    sys.exit(0 if ok else 1)
