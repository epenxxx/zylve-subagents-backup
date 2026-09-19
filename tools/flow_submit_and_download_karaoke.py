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
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "thumbnail_flow_generated.png")
OUTPUT_JPG = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

PROMPT = (
    "Thumbnail YouTube KARAOKE 16:9 Full HD lagu MUTIARA - IPANK. "
    "Teks besar 3D warna emas menyala megah di tengah atas: 'KARAOKE'. "
    "Teks judul 3D warna emas berkilau: 'MUTIARA - IPANK'. "
    "Badge merah tebal menyala di sudut: 'by ZYLVEmedia' dan 'LIRIK RESMI'. "
    "Foto penyanyi pria Ipank bernyanyi dengan penuh penghayatan di depan mikrofon panggung metalik vintage berkilau. "
    "Latar belakang konser megah dengan tata lampu sorot panggung ungu keemasan dan gelombang neon audio wave biru. "
    "Kualitas visual 8K fotorealistis YouTube Music resmi, teks tajam terbaca jelas, DILARANG kartun, DILARANG animasi lilin slop."
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
        await page.wait_for_timeout(5000)

        # 1. Pastikan Setelan Rasio 16:9
        print("[2/5] Memeriksa Setelan Rasio 16:9...")
        tune_btn = await page.query_selector('button[aria-label*="Setelan"], button:has-text("tune")')
        if tune_btn:
            try:
                await tune_btn.click()
                await page.wait_for_timeout(1000)
                btn_169 = await page.query_selector('button:has-text("16:9")')
                if btn_169:
                    await btn_169.click()
                    await page.wait_for_timeout(500)
                btn_simpan = await page.query_selector('button:has-text("Simpan")')
                if btn_simpan:
                    await btn_simpan.click()
                    await page.wait_for_timeout(800)
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"Catatan setelan: {e}")

        # 2. Ketik prompt di ProseMirror
        print("[3/5] Memasukkan prompt teks 3D KARAOKE...")
        pm = await page.query_selector('.ProseMirror')
        if pm:
            await pm.click(force=True)
            await page.wait_for_timeout(500)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(300)
            await page.keyboard.type(PROMPT, delay=5)
            await page.wait_for_timeout(1000)

        # 3. Klik tombol submit / Mulai pembuatan
        print("[4/5] Mengirim pembuatan ke Google Flow...")
        btn_send = await page.query_selector('button[aria-label="Mulai pembuatan"], button[type="submit"]')
        if btn_send:
            await btn_send.click(force=True)
            print("[✓] Tombol 'Mulai pembuatan' berhasil diklik!")
        else:
            await page.keyboard.press("Enter")
            print("[✓] Enter dikirim ke prompt!")

        await page.wait_for_timeout(5000)
        await page.screenshot(path="/root/screenshots/flow_generating_ipank.png")

        # 4. Tunggu hasil generasi di kanvas / chat panel
        print("[5/5] Menunggu generasi gambar Google Flow selesai...")
        captured = False
        start_time = time.time()
        
        # Monitor selama maks 2.5 menit (30 iterasi x 5 detik)
        for i in range(30):
            await page.wait_for_timeout(5000)
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] Memeriksa gambar hasil Google Flow...")

            # Ambil semua gambar di halaman
            imgs = await page.query_selector_all('img[src*="googleusercontent"], img[src*="blob:"]')
            print(f"Ditemukan {len(imgs)} elemen gambar.")
            
            # Cari gambar terbaru di chat kanan atau kanvas
            for img in reversed(imgs):
                box = await img.bounding_box()
                if not box or box["width"] < 200 or box["height"] < 120:
                    continue
                src = await img.get_attribute("src")
                if not src or "avatar" in src:
                    continue

                # Coba unduh via urlretrieve jika http
                if src.startswith("http"):
                    try:
                        urllib.request.urlretrieve(src, OUTPUT_PNG)
                        if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 40000:
                            print(f"[✓] Berhasil download gambar via URL ({os.path.getsize(OUTPUT_PNG)} bytes)!")
                            captured = True
                            break
                    except Exception:
                        pass

                # Fallback: screenshot bounding box elemen
                await img.screenshot(path=OUTPUT_PNG)
                if os.path.exists(OUTPUT_PNG) and os.path.getsize(OUTPUT_PNG) > 40000:
                    print(f"[✓] Berhasil screenshot elemen gambar ({os.path.getsize(OUTPUT_PNG)} bytes)!")
                    captured = True
                    break

            if captured:
                break

        # Simpan screenshot live kanvas untuk audit
        await page.screenshot(path="/root/screenshots/flow_ipank_result.png")

        # Jika berhasil didapatkan, proses ke 1920x1080 JPEG 95%
        if captured and os.path.exists(OUTPUT_PNG):
            im = Image.open(OUTPUT_PNG).convert("RGB")
            im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            im.save(OUTPUT_JPG, "JPEG", quality=95)
            print(f"[✓] Thumbnail resmi Google Flow tersimpan: {OUTPUT_JPG} ({os.path.getsize(OUTPUT_JPG)} bytes)")
        else:
            print("[!] Belum terambil via selector, memeriksa screenshot kanvas...")
            # Cek screenshot kanvas live jika ada kartu media terbaru
            if os.path.exists("/root/screenshots/flow_ipank_result.png"):
                print("[✓] Screenshot kanvas tersimpan di /root/screenshots/flow_ipank_result.png")

        await browser.close()
        print("Selesai.")

if __name__ == "__main__":
    asyncio.run(main())
