import asyncio
import json
import os
import time
import urllib.request
from playwright.async_api import async_playwright
from PIL import Image

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"
OUTPUT_DIR = "/root/assets/stock_karaoke_koplo/queue/ipank_mutiara"
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "thumbnail_flow_modified_raw.png")
OUTPUT_JPG = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

PROMPT = (
    "Berdasarkan gambar referensi asli ini (thumb_raw.jpg), modifikasi menjadi Thumbnail YouTube KARAOKE 16:9 Full HD resmi. "
    "Pertahankan foto asli penyanyi Ipank berkacamata hitam dengan jaket kulit hitam di depan air terjun megah. "
    "Tambahkan teks 3D besar warna emas menyala megah di bagian atas: 'KARAOKE' dan 'MUTIARA - IPANK'. "
    "Tambahkan badge merah tebal menyala di sudut: 'by ZYLVEmedia' dan 'LIRIK RESMI'. "
    "Tambahkan mikrofon panggung metalik berkilau dan efek pencahayaan panggung musik glamor keemasan. "
    "Fotorealistis 8K YouTube Music resmi, teks tajam terbaca jelas, DILARANG kartun, DILARANG animasi lilin slop."
)

async def main():
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

        # 1. Buka menu Tambahkan bahan ke kotak perintah
        print("[2/5] Menautkan thumb_raw.jpg ke kotak perintah...")
        btn_add = await page.query_selector('button[aria-label="Tambahkan bahan ke kotak perintah"]')
        if btn_add:
            await btn_add.click()
            await page.wait_for_timeout(1000)
            
            # Pilih item thumb_raw.jpg di list
            item_raw = await page.query_selector('div:has-text("thumb_raw.jpg"), button:has-text("thumb_raw.jpg")')
            if item_raw:
                await item_raw.click()
                await page.wait_for_timeout(500)
                
            # Klik tombol "Tambahkan ke perintah"
            btn_add_prompt = await page.query_selector('button:has-text("Tambahkan ke perintah")')
            if btn_add_prompt:
                await btn_add_prompt.click()
                await page.wait_for_timeout(1000)
                print("[✓] thumb_raw.jpg berhasil ditautkan ke prompt!")

        # 2. Ketik prompt modifikasi di ProseMirror
        print("[3/5] Memasukkan prompt modifikasi karaoke...")
        pm = await page.query_selector('.ProseMirror')
        if pm:
            await pm.click(force=True)
            await page.wait_for_timeout(500)
            await page.keyboard.type(PROMPT, delay=5)
            await page.wait_for_timeout(1000)

        await page.screenshot(path="/root/screenshots/flow_prompt_with_raw_attached.png")

        # 3. Klik tombol Mulai pembuatan
        print("[4/5] Mengirim pembuatan ke Google Flow...")
        btn_send = await page.query_selector('button[aria-label="Mulai pembuatan"], button[type="submit"]')
        if btn_send:
            await btn_send.click(force=True)
            print("[✓] Tombol Mulai pembuatan diklik!")
        else:
            await page.keyboard.press("Enter")
            print("[✓] Enter ditekan!")

        # 4. Tunggu hasil pembuatan
        print("[5/5] Menunggu generasi gambar modifikasi selesai...")
        captured = False
        start_time = time.time()
        
        for i in range(25):
            await page.wait_for_timeout(6000)
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] Memeriksa hasil baru di Flow...")
            
            # Ambil screenshot live kanvas
            await page.screenshot(path="/root/screenshots/flow_generating_raw_mod.png")
            
            # Cek apakah ada gambar baru di panel chat kanan
            chat_imgs = await page.query_selector_all('div[role="log"] img, div.chat-panel img, img[src*="googleusercontent"]')
            for img in reversed(chat_imgs):
                box = await img.bounding_box()
                if not box or box["width"] < 150 or box["height"] < 80:
                    continue
                src = await img.get_attribute("src")
                if not src or "avatar" in src:
                    continue
                if src.startswith("http"):
                    try:
                        urllib.request.urlretrieve(src, OUTPUT_PNG)
                        if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 30000:
                            print(f"[✓] Berhasil download gambar modifikasi: {OUTPUT_PNG}")
                            captured = True
                            break
                    except Exception:
                        pass
                await img.screenshot(path=OUTPUT_PNG)
                if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 30000:
                    print(f"[✓] Berhasil capture gambar modifikasi: {OUTPUT_PNG}")
                    captured = True
                    break
            if captured:
                break

        # Ambil screenshot final kanvas
        await page.screenshot(path="/root/screenshots/flow_final_raw_canvas.png")

        await browser.close()
        print("Selesai proses Flow.")

if __name__ == "__main__":
    asyncio.run(main())
