#!/usr/bin/env python3
"""
generate_flow_karaoke_thumbnail.py
Tool Universal Agent 4 (Karaoke Thumbnail Designer)
- Mengambil acuan thumbnail asli (thumbnail_raw.jpg / thumb_raw.webp) dari folder proyek
- Membuka Google Flow Canvas (flow.google.com)
- Mengunggah prompt modifikasi visual berorientasi YouTube Karaoke 16:9 Full HD
- Mempertahankan foto/wajah asli penyanyi dan komposisi resmi
- Menambahkan teks 3D emas megah 'KARAOKE' & Judul, badge 'by ZYLVEmedia'
- Mengunduh dan menyimpan output resmi ke thumbnail.jpg (1920x1080) di direktori proyek
"""

import asyncio
import json
import os
import sys
import argparse
from playwright.async_api import async_playwright
from PIL import Image

FLOW_COOKIES = "/root/zylve_automation/google_flow_cookies.json"
PROJECT_URL = "https://flow.google.com/project/7883155e-9272-4e7f-bbb2-d9bc24f6490b"

async def generate_thumbnail(project_dir):
    if not os.path.exists(project_dir):
        print(f"[!] Direktori proyek tidak ditemukan: {project_dir}")
        return False

    # Baca metadata jika ada
    meta_file = os.path.join(project_dir, "seo_metadata.json")
    song_title = os.path.basename(project_dir).replace("_", " ").upper()
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                song_title = meta.get("title", song_title).split("|")[0].split("(")[0].strip()
        except Exception:
            pass

    out_png = os.path.join(project_dir, "thumbnail_google_flow_16x9.png")
    out_jpg = os.path.join(project_dir, "thumbnail.jpg")

    prompt = (
        f"Thumbnail YouTube KARAOKE 16:9 Full HD lagu {song_title}. "
        f"Acuan visual utama berpatokan pada thumbnail lagu resmi. Pertahankan pose, postur, dan wajah asli penyanyi secara tajam dan fotorealistis. "
        f"Teks besar 3D warna emas menyala megah di tengah atas: 'KARAOKE'. "
        f"Teks judul 3D warna emas berkilau: '{song_title}'. "
        f"Badge merah tebal menyala di sudut: 'by ZYLVEmedia' dan 'LIRIK RESMI'. "
        f"Latar belakang panggung konser musik megah dengan tata lampu sorot ungu keemasan dan gelombang neon audio wave biru. "
        f"Kualitas visual 8K fotorealistis YouTube Music resmi, teks tajam terbaca jelas dari kejauhan, DILARANG kartun, DILARANG animasi lilin slop."
    )

    print(f"[*] [Agent 4] Memproses thumbnail Google Flow untuk: {song_title}")
    print(f"[*] Folder output: {project_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--ignore-certificate-errors'])
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        
        if os.path.exists(FLOW_COOKIES):
            cookies = json.load(open(FLOW_COOKIES))
            clean_cookies = [{"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c.get("path", "/"), "secure": c.get("secure", False), "httpOnly": c.get("httpOnly", False)} for c in cookies]
            await context.add_cookies(clean_cookies)

        page = await context.new_page()
        print("[1/4] Membuka Google Flow Canvas...")
        await page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)

        print("[2/4] Memasukkan prompt ke kotak perintah Flow...")
        prompt_box = await page.query_selector('.ProseMirror') or await page.query_selector('div[contenteditable="true"]')
        if prompt_box:
            await prompt_box.click()
            await page.wait_for_timeout(500)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(500)
            await page.keyboard.type(prompt, delay=5)
            await page.wait_for_timeout(1000)

            send_btn = await page.query_selector('button:has-text("arrow_forward"), button[aria-label*="Kirim"], button[aria-label*="Send"]')
            if send_btn:
                await send_btn.click()
            else:
                await page.keyboard.press("Enter")

            print("[3/4] Menunggu hasil render visual di Google Flow...")
            await page.wait_for_timeout(15000)

            for _ in range(10):
                imgs = await page.query_selector_all('img[src*="googleusercontent.com"], img[src*="blob:"]')
                if len(imgs) > 0:
                    break
                await page.wait_for_timeout(4000)

            imgs = await page.query_selector_all('img')
            valid_imgs = []
            for img in imgs:
                box = await img.bounding_box()
                if box and box['width'] > 300 and box['height'] > 200:
                    valid_imgs.append(img)

            if valid_imgs:
                target_img = valid_imgs[-1]
                await target_img.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                await target_img.screenshot(path=out_png)
                print(f"[✓] Render Flow tersimpan: {out_png}")

                im = Image.open(out_png).convert("RGB")
                im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
                im.save(out_jpg, quality=95)
                print(f"[✓] Thumbnail resmi 16:9 tersimpan: {out_jpg} ({os.path.getsize(out_jpg)} bytes)")
                await browser.close()
                return True
            else:
                print("[!] Tidak ada gambar kandidat yang ditemukan di Flow.")
        else:
            print("[!] Kotak input prompt Flow tidak ditemukan.")
        await browser.close()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Flow Karaoke Thumbnail Generator")
    parser.add_argument("project_dir", nargs="?", default="/root/assets/stock_karaoke_koplo/queue/kangen_band_kamu", help="Path direktori proyek karaoke")
    args = parser.parse_args()
    asyncio.run(generate_thumbnail(args.project_dir))
