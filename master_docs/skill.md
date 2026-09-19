# Katalog & Panduan Skill (Cimoy)

## 1. Aturan Pembuatan Skill
- **Kapan Buat Skill**: Alur kerja berulang, prosedur teknis rumit, atau multi-langkah baku untuk proyek tertentu.
- **Kapan Cukup Memori**: Catatan status proyek, preferensi ringan, to-do list, atau fakta sederhana ➔ masukkan ke [memori.md](file:///root/memori.md).

## 2. Format & Lokasi Skill
- Skill proyek dibuat di `.agents/skills/<nama_skill>/SKILL.md` atau didaftarkan di berkas ini.
- Format ringkas: Tujuan, Prasyarat, Perintah/SOP Terstruktur.

## 3. Daftar Skill Aktif
- [model](file:///root/.agents/skills/model/SKILL.md) (Perintah CLI `/model`: Switch & Cek Model AI Aktif / Custom)
- [quota](file:///root/.agents/skills/quota/SKILL.md) (Perintah CLI `/quota`: Cek Batas Rate Limit & Kuota API)
- [effort](file:///root/.agents/skills/effort/SKILL.md) (Perintah CLI `/effort`: Pengaturan Reasoning Effort Low/Medium/High)
- [status](file:///root/.agents/skills/status/SKILL.md) (Perintah CLI `/status`: Cek Kesehatan Sistem, CPU/RAM, Bot, & Service)
- [switch](file:///root/.agents/skills/switch/SKILL.md) (Perintah CLI `/switch`: Alih Workspace & Fokus Proyek)
- [new](file:///root/.agents/skills/new/SKILL.md) (Perintah CLI `/new`: Reset Fokus Konteks Sesi Baru)
- [stop](file:///root/.agents/skills/stop/SKILL.md) (Perintah CLI `/stop`: Hentikan Background Tasks, Subagen & Proses Aktif)
- [settings](file:///root/.agents/skills/settings/SKILL.md) (Perintah CLI `/settings`: Konfigurasi Sistem Antigravity CLI)
- [agy-customizations](file:///root/.gemini/antigravity-cli/builtin/skills/agy-customizations/SKILL.md) (Bawaan Sistem)
- [antigravity-custom-model](file:///root/.hermes/skills/antigravity-custom-model/SKILL.md) (Custom provider OpenAI-compatible + proxy lokal + registrasi `/model`).
- [antigravity_guide](file:///root/.gemini/antigravity-cli/builtin/skills/antigravity_guide/SKILL.md) (Bawaan Sistem)
- [antigravity-index](file:///root/.agents/skills/antigravity-index/SKILL.md) (Indeks copy Antigravity: 7 builtin + 64 Hermes + 15 agen + memori 185 brain/conv).
- [generate-image](file:///root/.agents/skills/generate-image/SKILL.md) (SOP Generate & Display Gambar)
- [infographic-storyboard](file:///root/.agents/skills/infographic-storyboard/SKILL.md) (Storyboard Infografis 3D Pixar 1 Slide Poster Tunggal ZYLVEmedia: Rasio 3:4, Master Template 6 Poin Baku, Watermark ZYLVEmedia, Lencana [🛡️ FAKTA VALID]).
- [gmail](file:///root/.agents/skills/gmail/SKILL.md) (Perintah CLI / Telegram `/gmail`: Multi-Account Switcher & Auto-Fallback Rolling Akun Google OAuth saat kuota habis).
- [agency-agents](file:///root/projects/agency_agents/README.md) (279 Persona Agen AI Spesialis The Agency terpasang di ~/.gemini/config/skills/ lintas 18 divisi).
- [karaoke-marketing-promoter](file:///root/.agents/skills/karaoke-marketing-promoter/SKILL.md) (SOP Promosi & Distribusi Omnichannel Konten Lagu Karaoke ZYLVEmedia ke TikTok, Reels, Shorts, & FB Groups).
- [comment-engager](file:///root/.agents/skills/comment-engager/SKILL.md) (Subagen Pembalas Komentar Netizen Otomatis Ramah & Cepat via Groq LPU).
- [cross-format-repurposer](file:///root/.agents/skills/cross-format-repurposer/SKILL.md) (Subagen Pengubah 1 Materi Berita/Lagu Menjadi 5 Format Omnichannel Lengkap).
- [agent-short](file:///root/.agents/skills/agent-short/SKILL.md) (Agent Short: Produksi Full-Stack & Akselerator YouTube Shorts ZYLVEmedia02 Menuju 10 Juta Views + Otomasi Upload 3x Harian 22:00-06:00 WIB).
- [claude-skills](file:///root/projects/claude_skills/repo/README.md) (Perpustakaan 438 Skill Claude/Gemini CLI: Engineering, DevOps, AEO/Marketing, C-Level Advisory, Research Ops. Router otomatis: [/root/tools/claude_skill_router.py](file:///root/tools/claude_skill_router.py)).
- [remove-ai-marks](file:///root/.agents/skills/remove-ai-marks/SKILL.md) (Standar Produksi Pembersih AI Watermarks, Metadata C2PA/EXIF/XMP, dan Unicode Tersembunyi via HTTP Service lokal port 8765 & CLI `clean-ai-watermark`).


## 4. Tim Subagen Khusus (Telah Diselaraskan 100% dengan Skill Relevan)
- **`agent_short`**: Subagen Produksi & Akselerasi YouTube Shorts Akun 2 (@zylvemedia02). Skill: `agent-short`, `cs-video-content-strategist`, `agency-short-video-editing-coach`, `agency-video-optimization-specialist`, `cs-youtube-full`.
- **`tiktok_news_scout`**: Subagen Riset & Verifikasi Berita TikTok (Agent 0). Skill: `tiktok-news-scout`, `agency-trend-researcher`, `cs-deep-research`.
- **`radar_berita`**: Riset berita viral 24 jam media arus utama kredibel. Skill: `agency-research-synthesist`, `g0dm0d3-engine`, `deep-research`.
- **`art_director`**: Master visual infografis 3:4 fotorealistis. Skill: `infographic-storyboard`, `agency-visual-storyteller`, `agency-brand-guardian`, `no-ai-slop`.
- **`copywriter_humanizer`**: Hook emosional & percakapan luwes anti-klise. Skill: `content-humanizer`, `agency-content-creator`, `cs-content-creator`.
- **`tiktok_operator`**: Otomasi upload TikTok Studio (+ Add sound). Skill: `agency-tiktok-strategist`, `browser-automation`.
- **`competitor_spy`**: Intelijen topik viral akun kompetitor besar. Skill: `agency-trend-researcher`, `cs-competitive-matrix`.
- **`community_analyst`**: Analisis sentimen komentar netizen untuk Part 2. Skill: `agency-feedback-synthesizer`, `community-analyst`.
- **`audio_scout`**: Kurasi sound musik tren & emosi berita. Skill: `agency-game-audio-engineer`.
- **`omnichannel_distributor`**: Distribusi video 9:16 (FB Reels, YT Shorts, Bilibili, Web). Skill: `cross-format-repurposer`, `agency-multi-platform-publisher`, `agency-video-streaming-engineer`.
- **`session_watchdog`**: Pemantau kesehatan sesi cookies & disk. Skill: `agency-sre-site-reliability-engineer`, `status`.
- **`community_replier`**: Balas komentar netizen humanis cepat (<0.3s). Skill: `comment-engager`.
- **`visual_qc_auditor`**: Quality Control visual rasio 3:4 bebas glitch. Skill: `agency-ui-finish-gate-reviewer`, `agency-evidence-collector`, `no-ai-slop`.
- **`seo_web_publisher`**: Optimasi artikel web zylvemedia.web.id disitasi AI search. Skill: `cs-aeo`, `agency-seo-specialist`, `agency-agentic-search-optimizer`.
- **`post_verification_growth`**: Verifikasi status tayang & engagement. Skill: `performance-auditor`, `agency-analytics-reporter`.
- **`fb_group_marketer`**: Pemasaran video ke grup FB santun anti-spam. Skill: `fb-group-marketing`, `agency-social-media-strategist`.
- **`humanizer_anti_slop`**: Kurator konten anti-AI-slop & anti frasa robotik. Skill: `humanizer-anti-slop`, `no-ai-slop`.
- **`karaoke_growth_analyst`**: Analis views & trending lagu YouTube 1. Skill: `karaoke-growth-analyst`, `agency-analytics-reporter`.
- **`karaoke_song_researcher`**: Agent 1 riset lagu viral & lirik resmi terpercaya. Skill: `karaoke-song-researcher`, `cs-youtube-full`.
- **`karaoke_audio_processor`**: Agent 2 pemisah vokal HuggingFace + mastering sutra -14 LUFS zero hiss. Skill: `karaoke-audio-processor`, `agency-game-audio-engineer`.
- **`karaoke_video_creator`**: Agent 3 video 16:9 alam Pexels, ASS sync, render VAAPI. Skill: `karaoke-video-creator`, `agency-video-streaming-engineer`.
- **`karaoke_thumbnail_designer`**: Agent 4 thumbnail 3D emas megah Google Flow acuan foto asli. Skill: `karaoke-thumbnail-designer`, `agency-brand-guardian`.
- **`karaoke_youtube_seo`**: Agent 5 SEO YouTube ramah penonton & kredit resmi musisi. Skill: `karaoke-youtube-seo`, `cs-youtube-full`, `agency-video-optimization-specialist`.
- **`karaoke_youtube_uploader`**: Agent 6 eksekutor upload Data API v3 resmi. Skill: `agency-devops-automator`.
- **`karaoke_storage_cleaner`**: Agent 7 janitor pembersih file media mentah >24 jam. Skill: `karaoke-storage-cleaner`, `agency-devops-automator`.
- [karaoke-song-researcher](file:///root/.agents/skills/karaoke-song-researcher/SKILL.md) (SOP Agent 1: Riset Lagu & Ekstraksi Lirik Resmi Terpercaya).
- [karaoke-audio-processor](file:///root/.agents/skills/karaoke-audio-processor/SKILL.md) (SOP Agent 2: Pembuat Lagu Karaoke di Hugging Face + Studio HD Mastering).
- [karaoke-thumbnail-designer](file:///root/.agents/skills/karaoke-thumbnail-designer/SKILL.md) (SOP Agent 4: Modif Thumbnail di Google Flow).
- [karaoke-video-creator](file:///root/.agents/skills/karaoke-video-creator/SKILL.md) (SOP Trio Agent Pembuat Video Karaoke 16:9 Subtitle ASS Berjalan Berbasis Lirik Resmi).
- [karaoke-youtube-seo](file:///root/.agents/skills/karaoke-youtube-seo/SKILL.md) (SOP Subagen 5: YouTube Karaoke SEO & Metadata Specialist).
- [karaoke-youtube-uploader](file:///root/.agents/skills/karaoke-youtube-uploader/SKILL.md) (SOP Subagen 6: YouTube Karaoke Uploader & Publisher).
- [karaoke-storage-cleaner](file:///root/.agents/skills/karaoke-storage-cleaner/SKILL.md) (SOP Subagen 7: Karaoke Storage Cleaner 24 Jam).
- [karaoke-growth-analyst](file:///root/.agents/skills/karaoke-growth-analyst/SKILL.md) (SOP Subagen Analis Pertumbuhan & Monetisasi YouTube 1).
- [humanizer-anti-slop](file:///root/.agents/skills/humanizer-anti-slop/SKILL.md) (SOP Subagen Humanizer & Strict Anti-AI-Slop Auditor).
- [fb-group-marketing](file:///root/.agents/skills/fb-group-marketing/SKILL.md) (SOP Subagen Pemasaran & Distribusi Iklan Grup Facebook).
- [gmail](file:///root/.agents/skills/gmail/SKILL.md) (SOP Perintah /gmail Multi-Account Switcher Bebas Logout Saat Kuota Habis).
- **`karaoke_marketer`**: Subagen Spesialis Pemasaran & Distribusi Konten Lagu Karaoke. Bertugas memotong klip viral 9:16 (8-15s) reff lagu, meracik copywriting nostalgia/challenge menyanyi, blasting terjadwal ke grup komunitas musik, dan mengalirkan penonton ke video full YouTube ZYLVEmedia. Skill: [.agents/skills/karaoke-marketing-promoter](file:///root/.agents/skills/karaoke-marketing-promoter/SKILL.md).
- **`comment_engager`**: Subagen Pembalas Komentar Netizen Otomatis. Merespons interaksi audiens di TikTok & YouTube secara santun, cerdas, humanis, dan kilat via Groq LPU (<0.3 detik) untuk mendongkrak skor algoritma engagement. Skrip: `/root/tools/comment_engager.py`.
- **`cross_format_repurposer`**: Subagen Omnichannel Multi-Format. Mengubah 1 materi berita atau lagu menjadi 5 format media sekaligus (Reels/Shorts 8s script, thread X, Telegram broadcast, caption IG/FB, meta desc SEO) dalam hitungan detik. Skrip: `/root/tools/cross_format_repurposer.py`.
- **`performance_auditor`**: Subagen Audit Kinerja & Analisis Jam Tayang. Menganalisis log penayangan TikTok & YouTube serta merumuskan rekomendasi jam posting emas dan topik berpotensi viral tinggi. Skrip: `/root/tools/performance_auditor.py`.
- **`agent_orchestrator`**: Super Manager Seluruh Subagen ZYLVEmedia. Memimpin dan mengorkestrasi 5 divisi subagen (Berita, Shorts, Bilibili, Karaoke, Utility), mengendalikan antrean hardware VAAPI (`/tmp/vaapi.lock`), mengawasi kesehatan proses anti-deadlock, dan menyusun Executive Report harian via Groq LPU & Gemini API (Zero Token Cimoy). Skill: [.agents/skills/agent-orchestrator](file:///root/.agents/skills/agent-orchestrator/SKILL.md). Skrip: [`/root/tools/agent_manager_orchestrator.py`](file:///root/tools/agent_manager_orchestrator.py).
- **`tim_bilibili`**: Tim Bilibili (Pengelola Akun & Produksi Konten Cuan Full-Stack Bilibili). Bertugas akselerasi syarat monetisasi (Creator Incentive Level 4 / 1k followers / 100k views), riset niche RPM tinggi (Sains/Luar Angkasa/AI), optimasi koin Sanlian, integrasi cuan afiliasi (Daihuo), jadwal otomatis 3x sehari jam ramai China (11:30, 17:30, 20:30 WIB), dan eksekusi hardware VAAPI Radeon Vega 11. Skill: [.agents/skills/agent-bilibili](file:///root/.agents/skills/agent-bilibili/SKILL.md). Runner: [`/root/tools/run_tim_bilibili_pipeline.py`](file:///root/tools/run_tim_bilibili_pipeline.py).
- **`tim_audit_sop`**: Tim Audit SOP, Kepatuhan & Quality Control (Di bawah Manajer `agent_orchestrator`). Bertugas menginspeksi kepatuhan protokol AGENTS.md, memvalidasi Zero Cimoy Token Policy, menjaga isolasi Single-Gate Reporting, memeriksa mutu media pra-rilis, dan mendeteksi deviasi alur kerja subagen. Skill: [.agents/skills/tim-audit-sop](file:///root/.agents/skills/tim-audit-sop/SKILL.md). Inspector: [`/root/tools/sop_audit_inspector.py`](file:///root/tools/sop_audit_inspector.py).
- **`agent_engineer`**: Subagen Rekayasa Sistem & Backend (Di bawah Manajer `agent_orchestrator`). Bertugas optimasi kode, arsitektur sistem, stabilitas driver hardware VAAPI, refactoring, dan debugging teknis. Skill: [.agents/skills/agent-engineer](file:///root/.agents/skills/agent-engineer/SKILL.md).
- **`agent_builder`**: Subagen Pembangun Fitur & Otomasi (Di bawah Manajer `agent_orchestrator`). Bertugas membangun skrip otomasi baru, pipeline video/multimedia, scaffolding fitur, integrasi API, dan rapid prototyping. Skill: [.agents/skills/agent-builder](file:///root/.agents/skills/agent-builder/SKILL.md).
- **`agent_content_auditor`**: Subagen Auditor Konten Pra-Posting (Di bawah Manajer `agent_orchestrator`). Bertugas mengaudit kualitas pacing, hook, kejernihan audio/subtitle, dan memberikan vonis LAYAK atau masukan perbaikan PERLU_REVISI sebelum konten diizinkan terbit. Skill: [.agents/skills/agent-content-auditor](file:///root/.agents/skills/agent-content-auditor/SKILL.md). Tool: [`/root/tools/prepost_audit_and_capcut_editor.py`](file:///root/tools/prepost_audit_and_capcut_editor.py).
- **`agent_capcut_editor`**: Subagen Editor CapCut Web (Di bawah Manajer `agent_orchestrator`). Bertugas menyunting dan memoles video yang dinilai belum layak oleh auditor menggunakan CapCut Web (`capcut_cookies.json`) dan penyempurnaan FFmpeg kilat. Skill: [.agents/skills/agent-capcut-editor](file:///root/.agents/skills/agent-capcut-editor/SKILL.md). Tool: [`/root/tools/prepost_audit_and_capcut_editor.py`](file:///root/tools/prepost_audit_and_capcut_editor.py).

## 5. Matriks Integrasi Keahlian The Agency ke Agen & Subagen Eksisting
- **Copywriting & Humanizer** (`copywriter_humanizer`, `claude_copywriter`): Diperkuat oleh `agency-content-creator`, `agency-brand-guardian`, `agency-whimsy-injector` (tone emosional, hook viral, bebas klise).
- **Riset & Verifikasi Fakta** (`tiktok_news_scout`, `radar_berita`, `kimi_researcher`): Diperkuat oleh `agency-trend-researcher`, `agency-research-synthesist`, `agency-statistician` (ekstraksi angka valid, triangulasi sumber).
- **Visual & Infografis** (`art_director`, `gemini_web_artist`): Diperkuat oleh `agency-ui-designer`, `agency-visual-storyteller`, `agency-inclusive-visuals-specialist` (komposisi fotorealistis murni, hierarki visual).
- **Logika Kritis & Sensorik** (`deepseek_thinker`): Diperkuat oleh `agency-strategy-duel-agent`, `agency-threat-intelligence-analyst`, `agency-legal-compliance-checker` (penetrasi sensor, mitigasi risiko).
- **Rekayasa Kode & Otomasi** (`qwen_architect`, `Cimoy`): Diperkuat oleh `agency-software-architect`, `agency-backend-architect`, `agency-devops-automator`, `agency-code-reviewer` (kestabilan sistem Linux, refactoring bersih).
- **Distribusi & Pertumbuhan** (`seo_web_publisher`, `omnichannel_distributor`, `tiktok_operator`, `fb_group_marketer`, `karaoke_growth_analyst`, `karaoke_marketer`): Diperkuat oleh `agency-seo-specialist`, `agency-tiktok-strategist`, `agency-social-media-strategist`, `agency-growth-hacker`, `agency-video-optimization-specialist`.
- **Produksi Media & Audio** (Agent Karaoke 1-7, `audio_scout`): Diperkuat oleh `agency-game-audio-engineer`, `agency-video-streaming-engineer`, `agency-video-optimization-specialist` (mastering super smooth, VAAPI tuning).
- **Audit Mutu & Anti-Slop** (`visual_qc_auditor`, `humanizer_anti_slop`): Diperkuat oleh `agency-reality-checker`, `agency-evidence-collector`, `agency-ui-finish-gate-reviewer` (zero toleransi AI slop).
