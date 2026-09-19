#!/usr/bin/env python3
"""
Gmail Multi-Account Switcher for Antigravity CLI
Simpan dan ganti token Google OAuth (Gmail) tanpa logout.
"""

import os
import sys
import json
import base64
import shutil

ACCOUNTS_DIR = "/root/.gemini/antigravity-cli/accounts"
TOKEN_FILE = "/root/.gemini/antigravity-cli/antigravity-oauth-token"


def get_token_email(token_path):
    """Ambil email dari JWT id_token di file oauth token."""
    if not os.path.exists(token_path):
        return None
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        idt = data.get("id_token", "")
        if not idt:
            return None
        payload = idt.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        info = json.loads(base64.urlsafe_b64decode(payload))
        return info.get("email")
    except Exception:
        return None


def sync_current_token():
    """Simpan token yang sedang aktif ke pool accounts/ jika belum ada."""
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    if not os.path.exists(TOKEN_FILE):
        return None
    email = get_token_email(TOKEN_FILE)
    if email:
        target = os.path.join(ACCOUNTS_DIR, f"{email}.json")
        shutil.copyfile(TOKEN_FILE, target)
        return email
    return None


def list_accounts():
    """Daftar seluruh akun Gmail yang tersimpan."""
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    active_email = get_token_email(TOKEN_FILE)

    accs = []
    for fname in sorted(os.listdir(ACCOUNTS_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(ACCOUNTS_DIR, fname)
            email = get_token_email(path) or fname[:-5]
            accs.append({
                "email": email,
                "file": fname,
                "active": (email == active_email)
            })
    return accs, active_email


def switch_account(target_email):
    """Pindah ke akun Gmail target."""
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    # Simpan token aktif sekarang dulu
    sync_current_token()

    # Cari file akun yang cocok
    target_file = None
    target_clean = target_email.strip().lower()
    matched_email = None

    for fname in os.listdir(ACCOUNTS_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(ACCOUNTS_DIR, fname)
        email = (get_token_email(path) or fname[:-5]).lower()
        if target_clean in email or target_clean == fname[:-5].lower():
            target_file = path
            matched_email = get_token_email(path) or fname[:-5]
            break

    if not target_file:
        return False, f"Akun '{target_email}' tidak ditemukan di pool!"

    # Salin ke antigravity-oauth-token
    try:
        shutil.copyfile(target_file, TOKEN_FILE)
        os.chmod(TOKEN_FILE, 0o600)
        return True, f"Sukses beralih ke: {matched_email}"
    except Exception as e:
        return False, f"Gagal switch: {e}"


import datetime
import http.server
import socketserver
import threading
import urllib.parse
import urllib.request

CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
SCOPES = "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/experimentsandconfigs https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/aicode https://www.googleapis.com/auth/cclog openid"
REDIRECT_URI = "http://localhost:8085/auth/callback"


def generate_auth_url(email):
    """Buat URL otorisasi Google OAuth resmi."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "login_hint": email
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code, target_email=None):
    """Tukar auth code menjadi access & refresh token lalu simpan ke pool."""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }).encode("utf-8")

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            token_res = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return False, f"Gagal tukar auth code: {err_msg}"
    except Exception as e:
        return False, f"Error koneksi: {e}"

    # Hitung expiry
    expires_in = token_res.get("expires_in", 3600)
    now = datetime.datetime.now(datetime.timezone.utc)
    expiry = (now + datetime.timedelta(seconds=expires_in)).isoformat()

    oauth_payload = {
        "token": {
            "access_token": token_res.get("access_token"),
            "token_type": token_res.get("token_type", "Bearer"),
            "refresh_token": token_res.get("refresh_token"),
            "expiry": expiry
        },
        "auth_method": "consumer",
        "id_token": token_res.get("id_token")
    }

    # Ambil email dari id_token jika tidak ada target_email
    email = None
    if oauth_payload.get("id_token"):
        try:
            payload = oauth_payload["id_token"].split(".")[1]
            payload += "=" * (-len(payload) % 4)
            info = json.loads(base64.urlsafe_b64decode(payload))
            email = info.get("email")
        except Exception:
            pass

    if not email:
        email = target_email

    if not email:
        return False, "Gagal mendeteksi email dari token!"

    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    target_path = os.path.join(ACCOUNTS_DIR, f"{email}.json")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(oauth_payload, f, indent=2)

    return True, f"Sukses menambahkan akun '{email}' ke pool accounts!"


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    captured_code = None
    target_email = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/auth/callback":
            qs = urllib.parse.parse_qs(parsed.query)
            if "code" in qs:
                CallbackHandler.captured_code = qs["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                html = """
                <html><body style="font-family:sans-serif;text-align:center;padding:50px;">
                <h1 style="color:green;">✅ Otorisasi Berhasil!</h1>
                <p>Akun berhasil diotorisasi. Anda dapat menutup tab ini dan kembali ke terminal/chat.</p>
                </body></html>
                """
                self.wfile.write(html.encode("utf-8"))
                return
        self.send_response(400)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def run_auth_server(target_email, timeout_sec=120):
    """Jalankan server callback lokal untuk menangkap code otomatis."""
    CallbackHandler.captured_code = None
    CallbackHandler.target_email = target_email

    with socketserver.TCPServer(("127.0.0.1", 8085), CallbackHandler) as httpd:
        httpd.timeout = 1.0
        start = datetime.datetime.now()
        while (datetime.datetime.now() - start).total_seconds() < timeout_sec:
            httpd.handle_request()
            if CallbackHandler.captured_code:
                break

    if CallbackHandler.captured_code:
        return exchange_code_for_token(CallbackHandler.captured_code, target_email)
    return False, "Timeout: Tidak menerima respon callback dalam waktu batas."


import subprocess

def rotate_account():
    """Putar ke akun berikutnya di pool (Round Robin)."""
    accs, active_email = list_accounts()
    if not accs:
        return False, "Tidak ada akun di pool."
    if len(accs) == 1:
        return False, f"Hanya ada 1 akun ({accs[0]['email']}), tidak bisa rolling."

    curr_idx = -1
    for i, a in enumerate(accs):
        if a["active"]:
            curr_idx = i
            break

    next_idx = (curr_idx + 1) % len(accs)
    next_acc = accs[next_idx]
    old_email = active_email or "Unknown"
    new_email = next_acc["email"]

    ok, msg = switch_account(new_email)
    if ok:
        try:
            tele_script = "/root/telegram_remote_bot/send_telegram.py"
            if os.path.exists(tele_script):
                msg_tele = (
                    f"🔄 *[GMAIL AUTO-ROLLING]*\n"
                    f"• Dari Akun: `{old_email}`\n"
                    f"• Beralih ke: `{new_email}` ✅\n"
                    f"• Total Akun Pool: `{len(accs)}`\n"
                    f"Sesi CLI & Bot tetap aktif."
                )
                subprocess.Popen(["python3", tele_script, msg_tele], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        try:
            subprocess.run(["notify-send", "Gmail Rolling", f"Beralih: {old_email} -> {new_email}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

        return True, f"Sukses rolling akun: {old_email} ➡️ {new_email}"
    return False, msg


def main():
    sync_current_token()

    if len(sys.argv) < 2 or sys.argv[1] in ["list", "status", "ls"]:
        accs, active = list_accounts()
        if not accs:
            print("Belum ada akun tersimpan di pool accounts.")
            return

        print("=== DAFTAR AKUN GMAIL TERDAFTAR ===")
        for i, a in enumerate(accs, 1):
            mark = " [AKTIF ✅]" if a["active"] else ""
            print(f"{i}. {a['email']}{mark}")
        print("\nCara switch : gmail <email>")
        print("Cara rolling: gmail next")
        print("Cara tambah : gmail add <email>")
        print("Atau di Telegram bot: /gmail")
        return

    cmd = sys.argv[1].lower()

    # Perintah ROLLING / NEXT
    if cmd in ["next", "rotate", "roll"]:
        ok, msg = rotate_account()
        print(msg)
        sys.exit(0 if ok else 1)

    # Perintah ADD akun baru
    if cmd == "add":
        if len(sys.argv) < 3:
            print("Penggunaan: gmail add <email> [--code <auth_code>]")
            sys.exit(1)
        email = sys.argv[2].strip()

        # Jika kode diberikan langsung via CLI: gmail add email --code 4/0A...
        if len(sys.argv) >= 5 and sys.argv[3] == "--code":
            code = sys.argv[4].strip()
            ok, msg = exchange_code_for_token(code, email)
            print(msg)
            sys.exit(0 if ok else 1)

        url = generate_auth_url(email)
        print(f"\n🔗 Buka tautan berikut di browser untuk mengotorisasi '{email}':\n")
        print(url)
        print("\n⏳ Menunggu otorisasi callback (port 8085) selama 120 detik...")
        print("(Jika browser tidak otomatis redirect ke localhost, salin kode / URL hasil redirect dan jalankan:)")
        print(f"  gmail add {email} --code <KODE_DARI_URL>\n")

        ok, msg = run_auth_server(email)
        print(msg)
        sys.exit(0 if ok else 1)

    if cmd in ["switch", "set", "use"] and len(sys.argv) > 2:
        target = sys.argv[2]
    else:
        target = cmd

    ok, msg = switch_account(target)
    print(msg)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()


