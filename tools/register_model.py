#!/usr/bin/env python3
"""
register_model.py
Skrip pendaftaran custom model otomatis ke state.vscdb Antigravity.
Mendukung Windows, macOS, dan Linux.
"""
import os
import sys
import sqlite3
import base64
import platform

def get_db_path():
    sys_name = platform.system()
    if sys_name == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(appdata, "Antigravity", "User", "globalStorage", "state.vscdb")
    elif sys_name == "Darwin":
        home = os.path.expanduser("~")
        return os.path.join(home, "Library", "Application Support", "Antigravity", "User", "globalStorage", "state.vscdb")
    else:
        home = os.path.expanduser("~")
        return os.path.join(home, ".config", "Antigravity", "User", "globalStorage", "state.vscdb")

def encode_varint(value):
    bytes_arr = bytearray()
    while value >= 0x80:
        bytes_arr.append((value & 0x7F) | 0x80)
        value >>= 7
    bytes_arr.append(value)
    return bytes(bytes_arr)

def encode_field(field_number, wire_type, data):
    header = (field_number << 3) | wire_type
    if wire_type == 2:  # length-delimited
        if isinstance(data, str):
            data = data.encode("utf-8")
        return encode_varint(header) + encode_varint(len(data)) + data
    elif wire_type == 0:  # varint
        return encode_varint(header) + encode_varint(data)
    raise ValueError("Wire type not supported")

def create_model_blob(label, proxy_url, max_tokens=64000):
    inner = encode_field(1, 2, label) + encode_field(2, 2, proxy_url) + encode_field(5, 0, max_tokens)
    row = base64.b64encode(inner)
    topic = encode_field(1, 2, "custom_models") + encode_field(2, 2, row)
    return base64.b64encode(topic).decode("ascii")

def main():
    db_path = get_db_path()
    label = sys.argv[1] if len(sys.argv) > 1 else "Custom Model (Claude Sonnet)"
    url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8085"

    print(f"[*] Menghubungkan ke database: {db_path}")
    if not os.path.exists(db_path):
        print(f"[!] File database tidak ditemukan di {db_path}.")
        print("[!] Pastikan Antigravity IDE sudah pernah dibuka dan ditutup kembali sebelum menjalankan skrip ini.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.modelPreferences'")
    row = cur.fetchone()
    
    blob = create_model_blob(label, url)
    if row:
        cur.execute("UPDATE ItemTable SET value = ? WHERE key = 'antigravityUnifiedStateSync.modelPreferences'", (blob,))
    else:
        cur.execute("INSERT INTO ItemTable (key, value) VALUES ('antigravityUnifiedStateSync.modelPreferences', ?)", (blob,))
    
    conn.commit()
    conn.close()
    print(f"[✓] Berhasil mendaftarkan '{label}' ({url}) ke /model Antigravity!")

if __name__ == "__main__":
    main()
