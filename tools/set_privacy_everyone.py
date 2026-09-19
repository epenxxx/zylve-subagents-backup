import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "/root/zylve_automation/tiktok_cookies_acc2.json"

with open(COOKIES_PATH, 'r') as f:
    cookies_raw = json.load(f)
cookies = [{'name': c['name'], 'value': c['value'], 'domain': c['domain'], 'path': c.get('path', '/'), 'secure': c.get('secure', True), 'httpOnly': c.get('httpOnly', False)} for c in cookies_raw]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--ignore-certificate-errors'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, user_agent='Mozilla/5.0 (Linux; Infinix X6731)')
    context.add_cookies(cookies)
    page = context.new_page()

    print("[*] Buka halaman Manage Posts...")
    page.goto('https://www.tiktok.com/tiktokstudio/content', wait_until='domcontentloaded', timeout=45000)
    page.wait_for_timeout(3000)

    # Cek dropdown privacy di baris pertama
    dropdown = page.locator('button:has-text("Only me"), div:has-text("Only me")').first
    if dropdown.is_visible():
        print("[*] Mengubah privacy ke Everyone...")
        dropdown.click(force=True)
        page.wait_for_timeout(1000)
        opt = page.locator('div[role="option"]:has-text("Everyone"), li:has-text("Everyone"), span:has-text("Everyone")').first
        if opt.is_visible():
            opt.click(force=True)
            page.wait_for_timeout(2000)
            print("[✓] Berhasil diubah ke Everyone!")

    page.screenshot(path='/root/screenshots/tiktok_acc2_privacy_updated.png')
    browser.close()
