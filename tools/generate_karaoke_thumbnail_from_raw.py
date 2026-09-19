#!/usr/bin/env python3
"""
Generator Thumbnail YouTube Karaoke 16:9 Full HD Profesional
100% Berbasis Referensi Thumbnail Asli Lagu Resmi Ipank (Anti-AI-Slop)
Tipografi 3D Emas Menyala Megah, Bebas Tabrakan Objek, Badge Standar YouTube Music.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAW_THUMB = "/root/assets/stock_karaoke_koplo/queue/ipank_mutiara/thumb_raw.jpg"
OUTPUT_JPG = "/root/assets/stock_karaoke_koplo/queue/ipank_mutiara/thumbnail.jpg"
OUTPUT_PNG = "/root/assets/stock_karaoke_koplo/queue/ipank_mutiara/thumbnail_google_flow_16x9.png"

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def draw_luxurious_gold_text(img, text, font, center_x, center_y, stroke_width=6):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = int(center_x - tw / 2)
    ty = int(center_y - th / 2)

    # 1. Outer Deep Drop Shadow (Hitam blur pekat)
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    for off in range(6, 22, 2):
        sdraw.text((tx + off, ty + off), text, font=font, fill=(0, 0, 0, 200), stroke_width=stroke_width + 4, stroke_fill=(0, 0, 0, 200))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=6))
    img.alpha_composite(shadow_layer)

    # 2. 3D Bevel Extrusion (Tembaga / Bronze berbayang ke bawah)
    draw = ImageDraw.Draw(img)
    for off in range(12, 0, -1):
        shade = max(20, 100 - off * 6)
        draw.text((tx + off, ty + off), text, font=font, fill=(shade + 50, shade + 20, 0, 255), stroke_width=stroke_width + 2, stroke_fill=(30, 15, 0, 255))

    # 3. Outer Border Emas Tua / Bronze
    draw.text((tx, ty), text, font=font, fill=(180, 120, 10, 255), stroke_width=stroke_width, stroke_fill=(50, 25, 0, 255))

    # 4. Teks Emas Menyala (Kuning Emas Mengkilap #FFD700)
    draw.text((tx, ty), text, font=font, fill=(255, 220, 40, 255), stroke_width=stroke_width - 2, stroke_fill=(200, 140, 10, 255))

    # 5. Highlight Kilau Emas Putih di Atas (#FFF7C2)
    draw.text((tx, ty - 1), text, font=font, fill=(255, 248, 190, 255), stroke_width=1, stroke_fill=(255, 255, 220, 255))

def draw_badge(img, x, y, text, is_left=True):
    font_badge = ImageFont.truetype(FONT_PATH, 32)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font_badge)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x = 24
    pad_y = 14
    bw = tw + pad_x * 2
    bh = th + pad_y * 2

    bx = x if is_left else x - bw
    by = y

    # Drop shadow badge
    draw.rounded_rectangle([bx + 4, by + 4, bx + bw + 4, by + bh + 4], radius=14, fill=(0, 0, 0, 180))
    # Badan badge merah neon
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=(220, 20, 20, 245), outline=(255, 255, 255, 255), width=3)
    # Teks putih tajam
    draw.text((bx + pad_x, by + pad_y - 2), text, font=font_badge, fill=(255, 255, 255, 255))

def generate_karaoke_thumbnail():
    print(f"[*] Membuka gambar referensi asli: {RAW_THUMB}")
    base = Image.open(RAW_THUMB).convert("RGBA")
    base = base.resize((1920, 1080), Image.Resampling.LANCZOS)

    # Tambahkan pencahayaan atas tipis agar teks emas sangat kontras
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(300):
        alpha = int(160 * (1 - y / 300))
        ov_draw.line([(0, y), (1920, y)], fill=(5, 5, 20, alpha))
    base = Image.alpha_composite(base, overlay)

    # 1. Teks 3D Emas Megah "KARAOKE" (Besar, megah di tengah atas)
    font_karaoke = ImageFont.truetype(FONT_PATH, 160)
    draw_luxurious_gold_text(base, "KARAOKE", font_karaoke, 960, 115, stroke_width=8)

    # 2. Teks 3D Emas Judul "MUTIARA - IPANK" (Tepat di bawah Karaoke, proporsional)
    font_judul = ImageFont.truetype(FONT_PATH, 85)
    draw_luxurious_gold_text(base, "MUTIARA - IPANK", font_judul, 960, 235, stroke_width=6)

    # 3. Badge Merah di Sudut Kiri & Kanan Atas
    draw_badge(base, 50, 45, "by ZYLVEmedia", is_left=True)
    draw_badge(base, 1870, 45, "LIRIK RESMI", is_left=False)

    # Simpan hasil akhir kualitas 96%
    rgb_result = base.convert("RGB")
    rgb_result.save(OUTPUT_JPG, "JPEG", quality=96)
    base.save(OUTPUT_PNG, "PNG")

    print(f"[✓] Thumbnail resmi berbasis foto asli berhasil diperbarui:")
    print(f"    - {OUTPUT_JPG} ({os.path.getsize(OUTPUT_JPG)} bytes)")

if __name__ == "__main__":
    generate_karaoke_thumbnail()
