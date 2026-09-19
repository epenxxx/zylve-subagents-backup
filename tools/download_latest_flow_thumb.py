#!/usr/bin/env python3
"""
Ekstraktor Thumbnail Terbaru dari Google Flow (Agent 4)
Membuka project Google Flow dan mengambil gambar hasil generasi terakhir untuk SALAH APA.
"""
import asyncio
import json
import os
import time
import urllib.request
from playwright.async_api import async_playwright
from PIL import Image

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"
OUTPUT_DIR = "/root/assets/stock_karaoke_koplo/queue/salah_apa_simpatik"
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "thumbnail_flow_generated.png")
OUTPUT_JPG = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

async def main():
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
        print("[*] Membuka Google Flow...")
        await page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(6000)

        # Ambil screenshot kondisi terkini
        await page.screenshot(path="/root/screenshots/flow_latest_check.png")

        # Cari semua gambar
        imgs = await page.query_selector_all('img[src*="googleusercontent"], img[src*="blob:"]')
        print(f"Ditemukan {len(imgs)} elemen gambar.")

        found = False
        for img in reversed(imgs):
            box = await img.bounding_box()
            if not box or box["width"] < 200 or box["height"] < 120:
                continue
            src = await img.get_attribute("src")
            if not src or "avatar" in src:
                continue

            # Prioritaskan gambar yang berada di sisi kanan (chat panel) atau kartu kanvas terbaru
            if box["x"] > 1400 or (box["width"] > 300 and box["height"] > 160):
                print(f"Mengambil gambar pada koordinat x={box['x']}, y={box['y']}, w={box['width']}, h={box['height']}")
                if src.startswith("http"):
                    try:
                        urllib.request.urlretrieve(src, OUTPUT_PNG)
                        if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 40000:
                            print(f"[✓] Berhasil download dari URL Google Flow ({os.path.getsize(OUTPUT_PNG)} bytes)!")
                            found = True
                            break
                    except Exception as e:
                        print(f"Download URL error: {e}")

                await img.screenshot(path=OUTPUT_PNG)
                if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 40000:
                    print(f"[✓] Berhasil screenshot elemen Google Flow ({os.path.getsize(OUTPUT_PNG)} bytes)!")
                    found = True
                    break

        if found and os.path.exists(OUTPUT_PNG):
            im = Image.open(OUTPUT_PNG).convert("RGB")
            im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            im.save(OUTPUT_JPG, "JPEG", quality=95)
            im.save(os.path.join(OUTPUT_DIR, "thumbnail_google_flow_16x9.png"))
            print(f"[✓] SUKSES! Thumbnail Google Flow tersimpan ke: {OUTPUT_JPG} ({os.path.getsize(OUTPUT_JPG)} bytes)")
        else:
            print("[!] Belum menemukan elemen spesifik, memeriksa screenshot...")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
