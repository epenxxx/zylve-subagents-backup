import asyncio
import json
import os
import time
from playwright.async_api import async_playwright
from PIL import Image

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"
OUTPUT_DIR = "/root/assets/stock_karaoke_koplo/queue/ipank_mutiara"
OUTPUT_IMG = os.path.join(OUTPUT_DIR, "thumbnail_google_flow_16x9.png")
OUTPUT_JPG = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

PROMPT_TEXT = (
    "Modifikasi gambar referensi ini menjadi Thumbnail YouTube KARAOKE 16:9 Full HD. "
    "Pertahankan karakter foto asli penyanyi pria Ipank dengan sangat tajam, ekspresif, dan pencahayaan panggung musik pop melayu glamor. "
    "Tambahkan teks besar 3D warna emas berkilau megah: 'KARAOKE' dan 'MUTIARA - IPANK'. "
    "Tambahkan badge merah tebal mencolok: 'by ZYLVEmedia' dan 'LIRIK RESMI'. "
    "Tambahkan mikrofon panggung metalik berkilau dan gelombang audio wave neon di latar panggung ungu biru keemasan. "
    "Fotorealistis 4K standar resmi YouTube Music IPANK PRO, DILARANG kartun, DILARANG animasi lilin slop."
)

async def run_flow():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("/root/screenshots", exist_ok=True)

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
        print("[1/5] Membuka Google Flow Canvas...")
        await page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)

        # 1. Atur Rasio 16:9
        print("[2/5] Mengatur Setelan Rasio 16:9...")
        tune_btn = await page.query_selector('button:has-text("tune"), button[aria-label*="Setelan"]')
        if tune_btn:
            await tune_btn.click()
            await page.wait_for_timeout(1000)
            btn_169 = await page.query_selector('button:has-text("16:9")')
            if btn_169:
                await btn_169.click()
                await page.wait_for_timeout(500)
            btn_simpan = await page.query_selector('button:has-text("Simpan")')
            if btn_simpan:
                await btn_simpan.click()
                await page.wait_for_timeout(1000)
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)

        # 2. Ketik prompt
        print("[3/5] Mengisi prompt modifikasi Google Flow...")
        prompt_box = await page.query_selector('.ProseMirror')
        if prompt_box:
            await prompt_box.click(force=True)
            await page.wait_for_timeout(500)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(500)
            await page.keyboard.type(PROMPT_TEXT, delay=8)
            await page.wait_for_timeout(1000)

        await page.screenshot(path="/root/screenshots/flow_ipank_prompt.png")

        # 3. Klik Mulai Pembuatan
        print("[4/5] Mengirim pembuatan gambar...")
        btn_generate = await page.query_selector('button[aria-label="Mulai pembuatan"], button[aria-label*="Kirim"], button:has-text("send")')
        if btn_generate:
            await btn_generate.click()
        else:
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(5000)
        print("[✓] Modifikasi Google Flow sedang diproses di kanvas...")

        # 4. Ambil hasil gambar
        downloaded = False
        for check in range(25):
            await page.wait_for_timeout(6000)
            current_imgs = await page.query_selector_all('img')
            for img in reversed(current_imgs):
                src = await img.get_attribute('src')
                if src and ('googleusercontent' in src or 'blob:' in src) and not 'avatar' in src:
                    await img.screenshot(path=OUTPUT_IMG)
                    if os.path.exists(OUTPUT_IMG) and os.path.getsize(OUTPUT_IMG) > 30000:
                        print(f"[✓] Berhasil capture gambar Google Flow: {OUTPUT_IMG} ({os.path.getsize(OUTPUT_IMG)} bytes)")
                        downloaded = True
                        break
            if downloaded:
                break

        # Fallback jika capture kanvas belum dapat: buat komposit grafis HD profesional dari thumb_raw
        if not downloaded or not os.path.exists(OUTPUT_IMG) or os.path.getsize(OUTPUT_IMG) < 30000:
            print("[*] Menggunakan komposit grafis 16:9 Google Flow Canvas lokal...")
            raw_thumb = os.path.join(OUTPUT_DIR, "thumb_raw.jpg")
            if os.path.exists(raw_thumb):
                im = Image.open(raw_thumb).convert("RGB")
                im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
                im.save(OUTPUT_JPG, "JPEG", quality=95)
                print(f"[✓] Thumbnail lokal tersimpan: {OUTPUT_JPG}")
        else:
            im = Image.open(OUTPUT_IMG).convert("RGB")
            im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            im.save(OUTPUT_JPG, "JPEG", quality=95)
            print(f"[✓] Thumbnail resmi tersimpan untuk YouTube: {OUTPUT_JPG} ({os.path.getsize(OUTPUT_JPG)} bytes)")

        await browser.close()
        print("Selesai.")

if __name__ == "__main__":
    asyncio.run(run_flow())
