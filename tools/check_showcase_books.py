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

    print("[*] Membuka TikTok Studio Upload...")
    page.goto('https://www.tiktok.com/tiktokstudio/upload', wait_until='domcontentloaded', timeout=45000)
    page.wait_for_timeout(3000)

    # Tutup popup
    for sel in ['button:has-text("Cancel")', 'button:has-text("Got it")', 'button[aria-label="Close"]']:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.click(force=True)
        except:
            pass

    # Buka dialog anchor
    print("[*] Mencari tombol anchor container...")
    page.locator('div[data-e2e="anchor_container"]').scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    btn = page.locator('div[data-e2e="anchor_container"] button').first
    btn.click(force=True)
    page.wait_for_timeout(2000)

    # Next ke dialog 2
    d1_next = page.locator('div[role="dialog"] button:has-text("Next")').first
    if d1_next.is_visible() and d1_next.is_enabled():
        d1_next.click(force=True)
        page.wait_for_timeout(3000)

    # Cari kata kunci "buku"
    search_input = page.locator('div[role="dialog"] input').first
    if search_input.is_visible():
        search_input.click()
        search_input.fill("buku")
        search_input.press("Enter")
        page.wait_for_timeout(3000)

    page.screenshot(path='/root/screenshots/showcase_search_buku.png')
    
    # Ambil semua teks item produk di dialog
    items = page.locator('div[role="dialog"] div').all_text_contents()
    print("=== HASIL SEARCH 'buku' ===")
    seen = set()
    for text in items:
        clean = " ".join(text.split())
        if len(clean) > 10 and clean not in seen and any(w in clean.lower() for w in ['rp', 'buku', 'psychology', 'habits', 'money', 'novel']):
            seen.add(clean)
            print("-", clean[:120])

    if not seen:
        print("[!] Tidak ada produk buku yang cocok dengan query 'buku'. Mencoba search 'money' / 'psikologi'...")
        search_input.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        search_input.fill("money")
        search_input.press("Enter")
        page.wait_for_timeout(3000)
        page.screenshot(path='/root/screenshots/showcase_search_money.png')
        items2 = page.locator('div[role="dialog"] div').all_text_contents()
        for text in items2:
            clean = " ".join(text.split())
            if len(clean) > 10 and clean not in seen and any(w in clean.lower() for w in ['rp', 'money', 'buku']):
                seen.add(clean)
                print("-", clean[:120])

    # Ambil juga semua produk tanpa search filter untuk melihat daftar lengkap
    search_input.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    search_input.press("Enter")
    page.wait_for_timeout(3000)
    page.screenshot(path='/root/screenshots/showcase_all_items.png')

    browser.close()
