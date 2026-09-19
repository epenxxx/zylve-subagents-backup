#!/usr/bin/env python3
"""
zernio_client.py
Klien Python resmi ZYLVEmedia untuk Zernio API (Social Media Scheduler & Publisher).
Mendukung upload media langsung, TikTok (@zylve70), dan platform lainnya.
"""

import os
import sys
import json
import mimetypes
import urllib.request
import urllib.error

API_KEY_FILE = "/root/.config/zernio/api_key"
BASE_URL = "https://zernio.com/api/v1"

def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return os.getenv("ZERNIO_API_KEY", "")

class ZernioClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError("ZERNIO_API_KEY tidak ditemukan.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, payload=None, extra_headers=None):
        url = f"{BASE_URL}{endpoint}"
        headers = dict(self.headers)
        if extra_headers:
            headers.update(extra_headers)
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body) if res_body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"[Zernio Error] HTTP {e.code}: {err_body}")
            return {"error": True, "status": e.code, "message": err_body}
        except Exception as e:
            print(f"[Zernio Error] Exception: {e}")
            return {"error": True, "message": str(e)}

    def get_analytics(self, account_id="6aae7e918d284ffb211b417d"):
        """Ambil data analitik akun (views, likes, followers)."""
        return self._request("GET", f"/analytics?accountId={account_id}")

    def get_profiles(self):
        """Ambil daftar profile Zernio."""
        return self._request("GET", "/profiles")

    def get_accounts(self, profile_id=None):
        """Ambil daftar connected accounts."""
        endpoint = f"/accounts?profileId={profile_id}" if profile_id else "/accounts"
        return self._request("GET", endpoint)

    def get_connect_url(self, platform, profile_id, redirect_url=None):
        """Dapatkan link OAuth untuk menghubungkan akun platform baru."""
        endpoint = f"/connect/{platform}?profileId={profile_id}"
        if redirect_url:
            endpoint += f"&redirect_url={urllib.parse.quote(redirect_url)}"
        return self._request("GET", endpoint)

    def upload_media(self, file_path):
        """
        Upload file lokal ke storage Zernio via Presigned URL:
        1. POST /v1/media/presign
        2. PUT file binary ke uploadUrl (tanpa Auth header)
        3. Kembalikan publicUrl
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File media tidak ditemukan: {file_path}")

        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            if file_path.endswith(".mp4"):
                content_type = "video/mp4"
            elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            else:
                content_type = "application/octet-stream"

        # 1. Presign
        presign_resp = self._request("POST", "/media/presign", {
            "filename": filename,
            "contentType": content_type
        })
        if "uploadUrl" not in presign_resp:
            raise RuntimeError(f"Gagal mendapatkan presigned URL dari Zernio: {presign_resp}")

        upload_url = presign_resp["uploadUrl"]
        public_url = presign_resp.get("publicUrl")

        # 2. Upload biner via PUT
        file_size = os.path.getsize(file_path)
        print(f"[*] Mengunggah media {filename} ({file_size / (1024*1024):.2f} MB) ke Zernio...")
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        put_req = urllib.request.Request(
            upload_url,
            data=file_bytes,
            headers={"Content-Type": content_type},
            method="PUT"
        )
        with urllib.request.urlopen(put_req, timeout=120) as put_resp:
            if put_resp.status in (200, 201, 204):
                print(f"[✓] Berhasil upload media ke Zernio! Public URL: {public_url}")
                return public_url
            else:
                raise RuntimeError(f"Gagal PUT file: HTTP {put_resp.status}")

    def create_post(self, payload):
        """Kirim atau jadwalkan post lewat endpoint POST /v1/posts."""
        return self._request("POST", "/posts", payload)

    def get_post(self, post_id):
        """Cek status post via GET /v1/posts/{postId}."""
        return self._request("GET", f"/posts/{post_id}")

    def list_posts(self, page=1, limit=10):
        """Lihat riwayat posting."""
        return self._request("GET", f"/posts?page={page}&limit={limit}")

    def post_tiktok_media(self, media_paths, caption, title=None, account_id="6aae7e918d284ffb211b417d", publish_now=True, scheduled_for=None, timezone="Asia/Jakarta"):
        """
        Upload media (video MP4 atau list gambar/slide foto) dan publikasikan ke TikTok ZYLVEmedia (@zylve70).
        """
        if isinstance(media_paths, str):
            media_paths = [media_paths]

        public_urls = []
        for p in media_paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Media tidak ditemukan: {p}")
            u = self.upload_media(p)
            public_urls.append(u)

        platform_entry = {
            "platform": "tiktok",
            "accountId": account_id
        }
        if title:
            platform_entry["title"] = title[:100]

        full_content = caption
        if title and title not in full_content:
            full_content = f"{title}\n\n{caption}"

        payload = {
            "content": full_content,
            "mediaUrls": public_urls,
            "platforms": [platform_entry]
        }

        if publish_now or not scheduled_for:
            payload["publishNow"] = True
        else:
            payload["scheduledFor"] = scheduled_for
            payload["timezone"] = timezone

        print(f"[*] Mengirim post TikTok ke Zernio API ({len(public_urls)} media)...")
        res = self.create_post(payload)
        print(f"[✓] Respon Zernio API: {res}")
        return res

    def post_tiktok_video(self, video_path, caption, account_id="6aae7e918d284ffb211b417d", publish_now=True, scheduled_for=None, timezone="Asia/Jakarta"):
        return self.post_tiktok_media([video_path], caption, account_id=account_id, publish_now=publish_now, scheduled_for=scheduled_for, timezone=timezone)

if __name__ == "__main__":
    client = ZernioClient()
    accounts = client.get_accounts().get("accounts", [])
    print("=== Akun Terhubung ===")
    for acc in accounts:
        print(f"ID: {acc['_id']} | Platform: {acc['platform']} | Akun: {acc.get('displayName')} (@{acc.get('username')})")
