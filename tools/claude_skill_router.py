#!/usr/bin/env python3
"""
claude_skill_router.py
Router & Auto-Activator Cerdas untuk 438 Skill Claude / Gemini CLI.

Fungsi:
1. Menerima deskripsi tugas / proyek pengguna.
2. Mencari kecocokan semantik & kata kunci di skills-index.json (438 skills).
3. Mengembalikan rekomendasi skill terbaik beserta path SKILL.md dan panduan eksekusi.
4. Mode auto-aktif: menampilkan ringkasan SOP skill untuk langsung diadopsi oleh Cimoy.
"""

import os
import sys
import json
import re

INDEX_FILE = "/root/projects/claude_skills/repo/.gemini/skills-index.json"
SKILLS_DIR = "/root/projects/claude_skills/repo/.gemini/skills"

def load_skills():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("skills", [])

def match_skills(query: str, top_k: int = 5):
    skills = load_skills()
    if not skills:
        return []

    tokens = [t.lower() for t in re.split(r'[\s\-_,.]+', query) if len(t) > 2]
    scored = []

    for s in skills:
        name = s.get("name", "").lower()
        desc = s.get("description", "").lower()
        cat = s.get("category", "").lower()

        score = 0
        for t in tokens:
            if t in name:
                score += 10
            if t in cat:
                score += 5
            if t in desc:
                score += 2

        if score > 0:
            skill_folder = os.path.join(SKILLS_DIR, s.get("name", ""))
            skill_md = os.path.join(skill_folder, "SKILL.md")
            if not os.path.exists(skill_md):
                # Fallback to name without cs- prefix
                raw_name = s.get("name", "").replace("cs-", "")
                skill_md = os.path.join(SKILLS_DIR, raw_name, "SKILL.md")

            scored.append({
                "score": score,
                "name": s.get("name"),
                "category": s.get("category"),
                "description": s.get("description"),
                "path": skill_md if os.path.exists(skill_md) else skill_folder
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def activate_skill(skill_name_or_query: str):
    matches = match_skills(skill_name_or_query, top_k=3)
    if not matches:
        return {"status": "not_found", "message": f"Tidak ditemukan skill cocok untuk '{skill_name_or_query}'"}

    top = matches[0]
    skill_path = top["path"]
    content_snippet = ""
    if os.path.exists(skill_path) and os.path.isfile(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content_snippet = "".join(lines[:30])

    return {
        "status": "activated",
        "active_skill": top["name"],
        "category": top["category"],
        "path": skill_path,
        "description": top["description"],
        "top_matches": matches,
        "snippet": content_snippet
    }

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "seo optimasi web"
    print(f"[*] Mencari & Mengaktifkan Skill untuk: '{q}'...")
    res = activate_skill(q)
    print(json.dumps(res, indent=2, ensure_ascii=False))
