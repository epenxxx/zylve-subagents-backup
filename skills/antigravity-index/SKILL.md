---
name: antigravity-index
description: >-
  Indeks memori, skill, dan agent Antigravity yang sudah di-copy ke Cimoy.
  Use this when user asks about Antigravity skills, Hermes skills, brain memory,
  conversations, custom model proxy, or AGY CLI/IDE/SDK usage.
---

# Antigravity Index (Cimoy)

Copy penuh ada di `/root/projects/antigravity_copy/`.
Detail: baca `/root/projects/antigravity_copy/HASIL_PELAJARI.md`.

## Skill Bawaan (7)
Lokasi: `/root/projects/antigravity_copy/skills_builtin/`
- agy-customizations (Rules/Skills/Plugins/Hooks/MCP)
- antigravity_guide (CLI/IDE/App 2.0/SDK + docs https://antigravity.google/docs)
- generative_ui, i-have-adhd, migrate-workflows, no-ai-slop, permissioned-github

## Skill Hermes (64 SKILL.md, 18 kategori)
Lokasi: `/root/projects/antigravity_copy/skills_hermes/` (asli: `/root/.hermes/skills/`)
Kunci: autonomous-ai-agents, creative, karaoke-video-pipeline,
google-flow-generation, flow-batch-render, web-ai-visual-pipeline,
research, media, productivity, software-development.

## Skill Agen Cimoy (15)
Lokasi: `/root/.agents/skills/` (copy di `skills_agents/`)
Karaoke 7 agen + tiktok-affiliate + podcast-godmode + infografis + generate-image + graphify + g0dm0d3.

## Memori (185 brain + 185 conversations, 1.3GB)
Asli: `/root/.gemini/antigravity-cli/brain/`, `conversations/`
Indeks: `/root/projects/antigravity_copy/memori_index/` (daftar + annotations + implicit)
Akses langsung: `sqlite3 /root/.gemini/antigravity-cli/conversations/<id>.db .tables`

## Aturan Pemuatan (AGY)
- Rules: `AGENTS.md` + `GEMINI.md` (hierarkis) + `.agents/rules/*.md`
- Skills: on-demand via SKILL.md ini
- Hooks: `.agents/hooks.json`
- MCP: `.agents/mcp_config.json`
