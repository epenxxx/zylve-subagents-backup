import asyncio
import json
import os
from playwright.async_api import async_playwright

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"

PROMPT_TEXT = (
    "Modifikasi gambar thumbnail referensi ini menjadi Thumbnail YouTube KARAOKE 16:9 Full HD yang sangat menarik dan elegan. "
    "Pertahankan foto asli Irwan dan Laila Ayu dengan resolusi tinggi tajam dan pencahayaan panggung dramatis. "
    "Tambahkan judul besar tebal 3D berwarna kuning keemasan: 'KARAOKE' dan subtitle: 'MUTIARA - LAILA AYU FT IRWAN'. "
    "Tambahkan badge mencolok 'TANPA VOKAL / by ZYLVEmedia' dengan warna merah elegan. "
    "Tambahkan visual mikrofon panggung metalik dan aksen gelombang audio neon. "
    "Latar belakang panggung megah konser dengan lighting ungu dan biru sinematik. Fotorealistis tajam 4K, DILARANG kartun atau lilin."
)

async def submit():
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
        await page.wait_for_timeout(4000)

        # Cari input box
        print("[1/3] Menemukan input box...")
        # Coba klik area teks
        input_el = page.locator('textarea, [contenteditable="true"], div[role="textbox"]').last
        if not await input_el.is_visible():
            input_el = page.locator('div:has-text("Apa yang ingin Anda buat?")').last
        
        await input_el.click()
        await page.wait_for_timeout(500)
        
        # Ketik prompt
        print("[2/3] Mengetik prompt...")
        # Jika contenteditable
        await page.keyboard.type(PROMPT_TEXT, delay=5)
        await page.wait_for_timeout(1000)

        # Klik tombol panah submit
        print("[3/3] Mengirim prompt...")
        send_btn = page.locator('button:has(svg), button[aria-label*="Kirim"], button:has-text("send"), button:has-text("arrow_forward")').last
        # Cek tombol bulat di sebelah kanan input box
        buttons = await page.locator('div:has-text("Apa yang ingin Anda buat?") button, div.input-container button').all()
        
        # Kirim dengan Enter atau klik
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)

        await page.screenshot(path="/root/screenshots/flow_generating_thumbnail.png")
        print("Terkirim! Screenshot tersimpan.")
        await browser.close()

asyncio.run(submit())
