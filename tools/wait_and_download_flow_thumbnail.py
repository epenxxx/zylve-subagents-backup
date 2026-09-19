import asyncio
import json
import os
import urllib.request
from playwright.async_api import async_playwright

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"
OUTPUT_DIR = "/root/assets/thumbnail_mutiara"
OUTPUT_IMG = os.path.join(OUTPUT_DIR, "thumbnail_karaoke_youtube_flow.png")
ARTIFACT_DIR = "/root/.gemini/antigravity-cli/brain/1e762963-a2a4-4982-b3f1-9626ac5bbc2c"

async def check_and_download():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
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
        await page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=60000)
        
        print("[1/4] Menunggu proses generasi selesai di Google Flow...")
        for i in range(30):
            await page.wait_for_timeout(5000)
            # Cek apakah indikator stop/tiga titik masih ada
            generating = await page.locator('button:has(svg rect), [aria-label*="Hentikan"], div:has-text("...")').count()
            print(f"[{i*5}s] Pengecekan status... (indikator aktif: {generating})")
            
            # Ambil screenshot kanvas
            await page.screenshot(path="/root/screenshots/flow_generation_live.png")
            
            # Cek jika ada gambar baru di panel chat kanan atau kanvas
            chat_imgs = await page.locator('div[role="log"] img, div.chat-panel img, div:has-text("KARAOKE") img, img[src*="googleusercontent"]').all()
            if len(chat_imgs) > 0:
                print(f"[✓] Ditemukan {len(chat_imgs)} gambar di Google Flow!")
                for idx, img in enumerate(chat_imgs):
                    src = await img.get_attribute("src")
                    if src and ("googleusercontent" in src or "blob:" in src or "http" in src):
                        print(f"Gambar #{idx} src: {src[:100]}...")
                        # Jika http, download langsung
                        if src.startswith("http"):
                            try:
                                urllib.request.urlretrieve(src, OUTPUT_IMG)
                                print(f"[✓] Berhasil unduh gambar ke: {OUTPUT_IMG}")
                                break
                            except Exception as e:
                                print(f"Gagal urlretrieve: {e}")
                        else:
                            # Screenshot elemen gambar
                            await img.screenshot(path=OUTPUT_IMG)
                            print(f"[✓] Berhasil screenshot elemen gambar ke: {OUTPUT_IMG}")
                            break
            
            if os.path.exists(OUTPUT_IMG) and os.path.getsize(OUTPUT_IMG) > 50000:
                print("[✓] Gambar thumbnail berhasil didapatkan!")
                break
                
        # Jika belum tersimpan dari chat, coba dari kanvas kartu terbaru
        if not os.path.exists(OUTPUT_IMG) or os.path.getsize(OUTPUT_IMG) < 50000:
            print("[!] Mencoba screenshot kartu media terbaru di kanvas...")
            cards = await page.locator('div[role="gridcell"] img, div.media-card img').all()
            if cards:
                await cards[0].screenshot(path=OUTPUT_IMG)
                print(f"[✓] Screenshot kartu media #0 tersimpan: {OUTPUT_IMG}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_and_download())
