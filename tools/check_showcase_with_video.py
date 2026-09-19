import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "/root/zylve_automation/tiktok_cookies_acc2.json"
VIDEO_PATH = "/root/assets/podcast_raymond_theo_PRO_9x16.mp4"

with open(COOKIES_PATH, 'r') as f:
    cookies_raw = json.load(f)
cookies = [{'name': c['name'], 'value': c['value'], 'domain': c['domain'], 'path': c.get('path', '/'), 'secure': c.get('secure', True), 'httpOnly': c.get('httpOnly', False)} for c in cookies_raw]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--ignore-certificate-errors'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, user_agent='Mozilla/5.0 (Linux; Infinix X6731)')
    context.add_cookies(cookies)
    page = context.new_page()

    print("[1] Membuka TikTok Studio Upload...")
    page.goto('https://www.tiktok.com/tiktokstudio/upload', wait_until='domcontentloaded', timeout=45000)
    page.wait_for_timeout(3000)

    print("[2] Mengunggah video untuk membuka form...")
    page.locator('input[type="file"]').first.set_input_files([VIDEO_PATH])
    page.wait_for_selector('div.public-DraftEditor-content, div[contenteditable="true"]', timeout=45000)
    page.wait_for_timeout(3000)

    # Tutup popup modal
    for sel in ['button:has-text("Cancel")', 'button:has-text("Got it")', 'button[aria-label="Close"]']:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.click(force=True)
        except:
            pass
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    print("[3] Mencari anchor container produk...")
    page.locator('div[data-e2e="anchor_container"]').scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    page.locator('div[data-e2e="anchor_container"] button').first.click(force=True)
    page.wait_for_timeout(2000)

    d1_next = page.locator('div[role="dialog"] button:has-text("Next")').first
    if d1_next.is_visible() and d1_next.is_enabled():
        d1_next.click(force=True)
        page.wait_for_timeout(3000)

        search_input = page.locator('div[role="dialog"] input').first
        
        # Test query 1: buku
        print("[4] Mencari 'buku'...")
        search_input.click()
        search_input.fill("buku")
        search_input.press("Enter")
        page.wait_for_timeout(3000)
        page.screenshot(path='/root/screenshots/showcase_check_buku.png')

        # Ambil daftar item
        rows = page.locator('div[role="dialog"] div').all_text_contents()
        matched = []
        for r in rows:
            clean = " ".join(r.split())
            if any(k in clean.lower() for k in ['rp', 'buku', 'book', 'psychology', 'habits', 'money']):
                if len(clean) > 8 and len(clean) < 150 and clean not in matched:
                    matched.append(clean)
        
        print("MATCHED BUKU:", matched)

        # Test query 2: tanpa search (semua barang etalase)
        print("[5] Mengambil semua produk di etalase showcase...")
        search_input.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        search_input.press("Enter")
        page.wait_for_timeout(3000)
        page.screenshot(path='/root/screenshots/showcase_check_all.png')

        all_rows = page.locator('div[role="dialog"] div').all_text_contents()
        all_items = []
        for r in all_rows:
            clean = " ".join(r.split())
            if 'Rp' in clean and len(clean) < 120 and clean not in all_items:
                all_items.append(clean)
        
        print(f"TOTAL ITEM TERDETEKSI: {len(all_items)}")
        for idx, it in enumerate(all_items[:15]):
            print(f"  {idx+1}. {it}")

    browser.close()
