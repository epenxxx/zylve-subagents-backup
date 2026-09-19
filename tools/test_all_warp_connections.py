#!/usr/bin/env python3
"""
test_all_warp_connections.py
Uji coba komprehensif seluruh jalur upload sosmed via Cloudflare WARP 1.1.1.1:
1. YouTube Data API v3 (Channel 1)
2. YouTube Studio Playwright (Channel 2)
3. TikTok Studio Playwright
4. Bilibili Creator Studio Playwright
"""

import os
import sys
import json
import time
import subprocess
from playwright.sync_api import sync_playwright

WARP_PROXY = "http://127.0.0.1:8118"
SCREENSHOT_DIR = "/root/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = {}

print("==================================================")
print("  UJI COBA KOMPREHENSIF KONEKSI SOSMED VIA WARP   ")
print("==================================================")

# --- 1. UJI IP DASAR & STATUS WARP ---
print("\n[1/5] Memeriksa IP Sistem vs IP Cloudflare WARP...")
try:
    direct = subprocess.run(["curl", "-s", "https://cloudflare.com/cdn-cgi/trace"], capture_output=True, text=True, timeout=10)
    warp_trace = subprocess.run(["curl", "-s", "-x", WARP_PROXY, "https://cloudflare.com/cdn-cgi/trace"], capture_output=True, text=True, timeout=10)
    
    direct_ip = [l for l in direct.stdout.split("\n") if "ip=" in l]
    direct_warp = [l for l in direct.stdout.split("\n") if "warp=" in l]
    
    warp_ip = [l for l in warp_trace.stdout.split("\n") if "ip=" in l]
    warp_status = [l for l in warp_trace.stdout.split("\n") if "warp=" in l]
    
    print(f"  -> IP Asli Server : {direct_ip[0] if direct_ip else 'N/A'} ({direct_warp[0] if direct_warp else ''})")
    print(f"  -> IP Lewat WARP  : {warp_ip[0] if warp_ip else 'N/A'} ({warp_status[0] if warp_status else ''})")
    
    if warp_status and "warp=on" in warp_status[0]:
        results["WARP_CORE"] = "PASSED ✅"
    else:
        results["WARP_CORE"] = "FAILED ❌"
except Exception as e:
    results["WARP_CORE"] = f"ERROR: {e}"

# --- 2. UJI YOUTUBE DATA API V3 VIA WARP ---
print("\n[2/5] Memeriksa YouTube Data API v3 (Channel 1) via WARP...")
try:
    with open("/root/zylve_automation/youtube_token.json") as f:
        t = json.load(f)
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(
        token=t.get("token"),
        refresh_token=t.get("refresh_token"),
        token_uri=t.get("token_uri"),
        client_id=t.get("client_id"),
        client_secret=t.get("client_secret"),
        scopes=t.get("scopes")
    )
    os.environ["http_proxy"] = WARP_PROXY
    os.environ["https_proxy"] = WARP_PROXY
    os.environ["HTTP_PROXY"] = WARP_PROXY
    os.environ["HTTPS_PROXY"] = WARP_PROXY

    yt = build("youtube", "v3", credentials=creds)
    channels = yt.channels().list(part="snippet", mine=True).execute()
    ch_title = channels["items"][0]["snippet"]["title"]
    print(f"  -> Terhubung ke Channel: {ch_title}")
    results["YOUTUBE_API_CH1"] = f"PASSED ✅ ({ch_title})"
except Exception as e:
    results["YOUTUBE_API_CH1"] = f"FAILED ❌: {e}"
    print(f"  -> Gagal YouTube API: {e}")

# --- 3. UJI PLAYWRIGHT BROWSER SESSIONS VIA WARP ---
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium",
        headless=True,
        args=["--no-sandbox", "--ignore-certificate-errors", "--disable-blink-features=AutomationControlled"]
    )

    # 3A. YouTube Studio (Akun 2)
    print("\n[3/5] Memeriksa YouTube Studio Akun 2 (@zylvemedia02) via Playwright WARP...")
    try:
        with open("/root/zylve_automation/youtube_cookies.json") as f:
            yt_cookies_raw = json.load(f)
        pw_yt_cookies = []
        for c in yt_cookies_raw:
            cookie = {
                'name': c['name'],
                'value': c['value'],
                'domain': c['domain'],
                'path': c.get('path', '/'),
                'secure': c.get('secure', True),
                'httpOnly': c.get('httpOnly', False)
            }
            if c.get('sameSite') in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = c['sameSite']
            elif c.get('sameSite') == 'no_restriction':
                cookie['sameSite'] = 'None'
            pw_yt_cookies.append(cookie)

        ctx_yt = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 900},
            proxy={'server': WARP_PROXY}
        )
        ctx_yt.add_cookies(pw_yt_cookies)
        page_yt = ctx_yt.new_page()
        page_yt.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=40000)
        page_yt.wait_for_timeout(5000)
        shot_yt = os.path.join(SCREENSHOT_DIR, "test_warp_yt.png")
        page_yt.screenshot(path=shot_yt)
        title_yt = page_yt.title()
        print(f"  -> Judul Halaman: {title_yt}")
        print(f"  -> Screenshot: {shot_yt}")
        if "YouTube" in title_yt or "Studio" in title_yt:
            results["YOUTUBE_STUDIO_ACC2"] = "PASSED ✅ (Studio Terbuka)"
        else:
            results["YOUTUBE_STUDIO_ACC2"] = f"WARNING ⚠️: {title_yt}"
        ctx_yt.close()
    except Exception as e:
        results["YOUTUBE_STUDIO_ACC2"] = f"FAILED ❌: {e}"
        print(f"  -> Error YouTube Studio: {e}")

    # 3B. TikTok Studio
    print("\n[4/5] Memeriksa TikTok Studio Upload via Playwright WARP...")
    try:
        with open("/root/zylve_automation/tiktok_cookies.json") as f:
            tt_cookies_raw = json.load(f)
        pw_tt_cookies = []
        for c in tt_cookies_raw:
            pw_tt_cookies.append({
                'name': c['name'],
                'value': c['value'],
                'domain': c['domain'],
                'path': c.get('path', '/')
            })

        ctx_tt = browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Linux; Infinix X6731) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.4.1.99 Safari/537.36',
            viewport={'width': 1440, 'height': 1000},
            proxy={'server': WARP_PROXY}
        )
        ctx_tt.add_cookies(pw_tt_cookies)
        page_tt = ctx_tt.new_page()
        page_tt.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded", timeout=45000)
        page_tt.wait_for_timeout(5000)
        shot_tt = os.path.join(SCREENSHOT_DIR, "test_warp_tiktok.png")
        page_tt.screenshot(path=shot_tt)
        title_tt = page_tt.title()
        print(f"  -> Judul Halaman: {title_tt}")
        print(f"  -> Screenshot: {shot_tt}")
        if "TikTok" in title_tt or "Studio" in title_tt:
            results["TIKTOK_STUDIO"] = "PASSED ✅ (Studio Terbuka)"
        else:
            results["TIKTOK_STUDIO"] = f"WARNING ⚠️: {title_tt}"
        ctx_tt.close()
    except Exception as e:
        results["TIKTOK_STUDIO"] = f"FAILED ❌: {e}"
        print(f"  -> Error TikTok Studio: {e}")

    # 3C. Bilibili Creator Studio
    print("\n[5/5] Memeriksa Bilibili Creator Studio Upload via Playwright WARP...")
    try:
        with open("/opt/zylvemedia/bilibili_cookies.json") as f:
            bili_cookies_raw = json.load(f)
        pw_bili_cookies = []
        for c in bili_cookies_raw:
            pw_bili_cookies.append({
                'name': c['name'],
                'value': c['value'],
                'domain': c['domain'],
                'path': c.get('path', '/')
            })

        ctx_bili = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            proxy={'server': WARP_PROXY}
        )
        ctx_bili.add_cookies(pw_bili_cookies)
        page_bili = ctx_bili.new_page()
        page_bili.goto("https://member.bilibili.com/platform/upload/video/frame", wait_until="domcontentloaded", timeout=45000)
        page_bili.wait_for_timeout(5000)
        shot_bili = os.path.join(SCREENSHOT_DIR, "test_warp_bilibili.png")
        page_bili.screenshot(path=shot_bili)
        title_bili = page_bili.title()
        print(f"  -> Judul Halaman: {title_bili}")
        print(f"  -> Screenshot: {shot_bili}")
        if "bilibili" in title_bili.lower() or "投稿" in title_bili or "创作" in title_bili:
            results["BILIBILI_STUDIO"] = "PASSED ✅ (Studio Terbuka)"
        else:
            results["BILIBILI_STUDIO"] = f"WARNING ⚠️: {title_bili}"
        ctx_bili.close()
    except Exception as e:
        results["BILIBILI_STUDIO"] = f"FAILED ❌: {e}"
        print(f"  -> Error Bilibili Studio: {e}")

    browser.close()

print("\n==================================================")
print("                   RINGKASAN HASIL                ")
print("==================================================")
for k, v in results.items():
    print(f"  - {k:<22}: {v}")
print("==================================================")
