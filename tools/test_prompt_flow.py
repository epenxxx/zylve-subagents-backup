import asyncio
import json
import os
from playwright.async_api import async_playwright

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"

PROMPT_TEXT = (
    "Berdasarkan gambar thumbnail referensi ini. Modifikasi menjadi Thumbnail YouTube KARAOKE VERSION 16:9 Full HD yang megah dan profesional. "
    "Pertahankan foto asli penyanyi Irwan dan Laila Ayu dengan resolusi 4K tajam dan pencahayaan panggung konser. "
    "Tambahkan teks besar 3D warna kuning keemasan menyala: 'KARAOKE' dan 'MUTIARA'. "
    "Tambahkan badge merah mencolok di pojok: 'TANPA VOKAL / by ZYLVEmedia'. "
    "Tambahkan visual mikrofon panggung bercahaya dan efek audio wave neon biru-ungu. Fotorealistis tajam, DILARANG kartun atau lilin slop."
)

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
        print("1. Membuka Google Flow...")
        await page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)

        # Klik tombol tambah bahan (+) di sebelah kiri input box
        print("2. Klik tambah bahan...")
        add_btn = page.locator('button[aria-label*="bahan"], button[aria-label*="Tambahkan"]').last
        await add_btn.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/root/screenshots/flow_picker_open.png")

        # Cari kartu thumbnail mutiara di picker
        print("3. Memilih thumbnail di picker...")
        # Klik elemen pertama di dialog picker
        picker_cards = await page.locator('div[role="dialog"] div[role="button"], div[role="dialog"] img, div.cdk-overlay-pane div[role="button"]').all()
        print(f"Ditemukan {len(picker_cards)} kartu di picker")
        if picker_cards:
            await picker_cards[0].click()
            await page.wait_for_timeout(1000)

        # Klik Tambahkan ke perintah
        confirm_btn = page.locator('button:has-text("Tambahkan ke perintah"), button:has-text("Tambahkan")').last
        if await confirm_btn.is_visible():
            await confirm_btn.click()
            await page.wait_for_timeout(1500)

        await page.screenshot(path="/root/screenshots/flow_asset_attached.png")

        # Ketik prompt di .ProseMirror
        print("4. Mengisi prompt...")
        prose = page.locator('.ProseMirror, div[contenteditable="true"]').last
        await prose.click()
        await page.wait_for_timeout(500)
        await page.keyboard.type(PROMPT_TEXT, delay=5)
        await page.wait_for_timeout(1000)

        # Kirim prompt
        print("5. Mengirim prompt...")
        submit_btn = page.locator('button:has-text("arrow_forward"), button:has-text("send"), button[aria-label*="Kirim"], button[aria-label*="Mulai"]').last
        if await submit_btn.is_visible():
            await submit_btn.click()
        else:
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(5000)
        await page.screenshot(path="/root/screenshots/flow_prompt_sent.png")
        print("Prompt resmi dikirim ke Google Flow!")

        # Tunggu status proses
        for sec in range(12):
            await page.wait_for_timeout(10000)
            await page.screenshot(path=f"/root/screenshots/flow_wait_{sec}.png")
            print(f"Menunggu proses... {(sec+1)*10}s")
            
            # Cek apakah ada gambar output baru
            imgs = await page.locator('div[role="gridcell"] img, div[role="log"] img').all()
            print(f"Total img: {len(imgs)}")

        await browser.close()

asyncio.run(main())
