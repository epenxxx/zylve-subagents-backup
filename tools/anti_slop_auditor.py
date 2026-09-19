#!/usr/bin/env python3
"""
Tool Auditor Humanis & Filter Anti-AI-Slop Ketat
Memeriksa judul, deskripsi, tag, dan berkas sebelum upload.
"""
import sys
import re
import json

FORBIDDEN_PHRASES = [
    r"\bmari kita selami\b",
    r"\bdalam era digital\b",
    r"\bsebuah mahakarya\b",
    r"\btak lekang oleh waktu\b",
    r"\bdive into\b",
    r"\bunleash your\b",
    r"\btapestry of\b",
    r"\bdelve into\b",
    r"\btestament to\b"
]

def audit_text(text):
    issues = []
    for pattern in FORBIDDEN_PHRASES:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"Terdeteksi frasa AI slop klise: '{pattern}'")
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 anti_slop_auditor.py <text_file_or_string>")
        sys.exit(0)
    target = sys.argv[1]
    content = target
    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        pass
    issues = audit_text(content)
    if issues:
        print("[GAGAL AUDIT AI-SLOP]:")
        for iss in issues:
            print(f"- {iss}")
        sys.exit(1)
    print("[✓] Lolos Audit Humanis. Bebas AI Slop.")
    sys.exit(0)
