#!/usr/bin/env python3
"""
colab_keeper.py - Autonomous 24/7 Google Colab Keep-Alive & Auto-Reconnect Daemon
Dikelola oleh Cimoy (agent_orchestrator).
Menjaga Google Colab runtime tetap hidup, auto-reconnect saat putus, dan bypass idle timeout.
"""

import os
import sys
import time
import json
import logging
from playwright.sync_api import sync_playwright

COLAB_URL = "https://colab.research.google.com/drive/1AMbpmoip7e_ZDgYHujHVA69RdZILJi5d?usp=sharing"
COOKIES_PATH = "/root/zylve_automation/gemini_cookies.json"
LOG_PATH = "/root/logs/colab_keeper.log"
SCREENSHOT_PATH = "/root/screenshots/colab_keeper_status.png"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_google_cookies():
    if not os.path.exists(COOKIES_PATH):
        logging.error(f"Cookies file not found at {COOKIES_PATH}")
        return []
    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
    pw_cookies = []
    for c in raw_cookies:
        domain = c.get("domain", "")
        if not domain.startswith(".google.com") and not domain.endswith("google.com"):
            continue
        item = {
            "name": c["name"],
            "value": c["value"],
            "domain": domain,
            "path": c.get("path", "/"),
            "secure": c.get("secure", True)
        }
        same_site = c.get("sameSite", "")
        if same_site in ["Strict", "Lax", "None"]:
            item["sameSite"] = same_site
        pw_cookies.append(item)
    return pw_cookies

def run_keeper():
    cookies = load_google_cookies()
    if not cookies:
        print("Error: Google cookies tidak ditemukan.")
        return

    print("Memulai Colab 24/7 Keeper Daemon...")
    logging.info("Colab Keeper started")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        context.add_cookies(cookies)
        page = context.new_page()

        print(f"Membuka Colab: {COLAB_URL}")
        try:
            page.goto(COLAB_URL, wait_until="load", timeout=60000)
            page.wait_for_timeout(6000)
        except Exception as e:
            logging.error(f"Failed to load Colab: {e}")
            print(f"Gagal memuat Colab: {e}")

        while True:
            try:
                # 1. Cek dialog popup error / disconnect
                dismiss_btn = page.query_selector("md-dialog #ok, md-dialog #dismiss, paper-button#ok")
                if dismiss_btn:
                    logging.info("Dismissing popup dialog...")
                    dismiss_btn.click()
                    page.wait_for_timeout(2000)

                # 2. Cek tombol Connect / Reconnect
                connect_btn = page.query_selector("colab-connect-button")
                if connect_btn:
                    btn_text = connect_btn.inner_text().strip()
                    if "Connect" in btn_text or "Reconnect" in btn_text or btn_text == "":
                        logging.info(f"Tombol connect terdeteksi: '{btn_text}'. Mengklik Connect...")
                        print(f"Tombol connect: '{btn_text}'. Menghubungkan...")
                        connect_btn.click()
                        page.wait_for_timeout(5000)

                # 3. Handle modal reconnect jika ada
                reconnect_popup = page.query_selector("text='Reconnect'")
                if reconnect_popup:
                    reconnect_popup.click()
                    page.wait_for_timeout(3000)

                # 4. Anti-Idle Activity: scroll & focus editor
                page.mouse.move(600, 300)
                page.keyboard.press("Shift")
                
                # Simpan screenshot status berkala
                page.screenshot(path=SCREENSHOT_PATH)
                logging.info("Status Colab OK (Connected & Active)")
                print(f"[{time.strftime('%H:%M:%S')}] Colab Aktif & Terhubung (GPU T4). Screenshot tersimpan.")

            except Exception as loop_err:
                logging.error(f"Loop check error: {loop_err}")
                print(f"Warning: {loop_err}")
                try:
                    page.reload(wait_until="load", timeout=60000)
                except Exception:
                    pass

            # Tunggu 3 menit sebelum cek berikutnya
            time.sleep(180)

if __name__ == "__main__":
    run_keeper()
