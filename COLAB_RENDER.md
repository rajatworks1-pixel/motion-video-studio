# 🎬 COLAB_RENDER.md — Beginner's Guide to Cloud Video Rendering

> **Motion Video Director** — Render professional motion graphics videos on Google Colab (free tier) with Google Drive storage. No local GPU needed.

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [One-Time Setup](#one-time-setup)
4. [Project Structure](#project-structure)
5. [Rendering Workflow](#rendering-workflow)
6. [Preview Mode](#preview-mode)
7. [Final Render](#final-render)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)
10. [FAQ](#faq)

---

## 🎯 Overview

This system lets you **create videos on your Android phone** (planning, scripting, storyboarding) and **render them in the cloud** (Google Colab free tier) with results saved to **Google Drive**.

```
┌─────────────────┐     GitHub      ┌─────────────────┐     Drive      ┌─────────────────┐
│  Android/PC     │ ─────────────▶ │  Google Colab   │ ────────────▶  │  Google Drive   │
│  (Plan/Dev)     │  Private Repo  │  (Render)       │  Auto-save     │  (Final MP4)    │
└─────────────────┘                └─────────────────┘                └─────────────────┘
```

**Key Benefits:**
- ✅ Free GPU rendering (T4, 15GB VRAM)
- ✅ No local dependencies (no Chromium, no ffmpeg on phone)
- ✅ Persistent output in Google Drive
- ✅ Resumable chunked rendering for long videos
- ✅ Secure secrets via Colab userdata (no keys in code)

---

## ✅ Prerequisites

| Requirement | Details |
|-------------|---------|
| **Google Account** | For Colab + Drive |
| **GitHub Account** | Private repository for project files |
| **Android TermFold + OpenCode** | For planning/authoring (this setup) |
| **NVIDIA NIM API Key** | For AI planning (Android only) |
| **Asset API Keys** (optional) | Pixabay, Freesound, Pexels, ElevenLabs |

**Time needed:** ~15 minutes first setup, ~3 minutes per render session.

---

## 🔧 One-Time Setup

### 1. Create GitHub Repository

```bash
# On your computer/Android
gh repo create myproject --private --clone
cd myproject
# Copy all project files here (this guide assumes you've done this)
git add . && git commit -m "Initial commit" && git push
```

### 2. Open Colab Notebook

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. **File → Upload notebook** → Select `render.ipynb` from your repo
3. Or: **File → Open notebook → GitHub** → Paste your repo URL

### 3. Enable GPU (Critical!)

```
Runtime → Change runtime type → Hardware accelerator: GPU (T4) → Save
```

**Verify:** Run Cell 1 in the notebook. Should show:
```
CUDA Available: True
GPU: Tesla T4
VRAM: 15.0 GB
```

### 4. Add API Secrets (Secure!)

Click the **🔑 key icon** in the left sidebar → **Add new secret** for each:

| Secret Name | Source | Required? |
|-------------|--------|-----------|
| `PIXABAY_API_KEY` | pixabay.com/api/docs | For stock images |
| `FREESOUND_API_KEY` | freesound.org/apiv2/apply | For SFX |
| `FREESOUND_CLIENT_ID` | freesound.org/apiv2/apply | For original SFX downloads |
| `PEXELS_API_KEY` | pexels.com/api | For stock photos/video |
| `UNSPLASH_ACCESS_KEY` | unsplash.com/developers | For photos |
| `ELEVENLABS_API_KEY` | elevenlabs.io/api | For SFX/music generation |
| `NIM_API_KEY` | build.nvidia.com | For Android planning only |

**Never paste keys in the notebook!** Colab userdata encrypts them.

### 5. Verify Drive Access

Run Cell 3. Should create:
```
/content/drive/MyDrive/myproject/
├── renders/
│   ├── previews/
│   └── final/
```

---

## 📁 Project Structure

Your GitHub repo should have this structure:

```
myproject/
├── render.ipynb              # ← Colab notebook (this file)
├── COLAB_RENDER.md           # ← This guide
├── src/
│   ├── render.py             # Python renderer (Colab)
│   ├── render.js             # Node renderer (local dev)
│   ├── data.js               # Shared config (beats, colors, easing)
│   ├── scenes/               # Scene modules
│   └── fx/                   # Reusable effects
├── assets/
│   ├── fonts/                # .woff2/.ttf + license.txt
│   ├── images/               # Downloaded via manifest
│   ├── lottie/               # .json animations
│   ├── sfx/                  # .wav sound effects
│   ├── music/                # Background tracks
│   └── vo/                   # Voiceover MP3 (user-provided)
├── scripts/
│   ├── colab_setup.py        # Installs deps, models
│   ├── colab_render.py       # Main render command
│   ├── fetch_assets.py       # Downloads from manifest
│   ├── colab_secrets.py      # Loads Colab secrets
│   ├── analyze_ref.py        # Reference video analysis
│   └── requirements.txt      # Python dependencies
├── manifest.json             # Asset registry (source of truth)
├── beats.json                # Master timeline (VO-driven)
├── .env.example              # Template for local .env
├── .gitignore
├── PROJECT.md                # Living brief
├── PROGRESS.md               # Phase tracker
└── LOG.md                    # Append-only log
```

---

## 🎬 Rendering Workflow

### Standard Workflow (Every Video)

```
1. PLAN (Android)          → Write script, storyboard, styleboard
2. VO GENERATION           → Generate MP3 on elevenlabs.io → assets/vo/vo_final.mp3
3. SYNC (GitHub)           → git add/commit/push all changes
4. COLAB: SETUP (Cells 1-5) → Mount Drive, clone repo, install deps
5. COLAB: ASSETS (Cell 6)  → Download fonts, images, SFX from manifest
6. COLAB: PREVIEW (Cell 7) → Fast render → check contact sheet + preview MP4
7. COLAB: FINAL (Cell 8)   → Full quality render → auto-saves to Drive
8. DOWNLOAD (Cell 9)       → Get MP4 from Drive or Colab
```

### Cell-by-Cell Execution

| Cell | Purpose | Time | Required? |
|------|---------|------|-----------|
| 1 | GPU/Environment check | 5s | ✅ Every session |
| 2 | Load secrets | 5s | ✅ Every session |
| 3 | Mount Google Drive | 10s | ✅ Every session |
| 4 | Clone/pull repo | 15s | ✅ Every session |
| 5 | Install deps + models | 2-5 min | 🔄 First time only |
| 6 | Download assets | 30s | 🔄 When manifest changes |
| 7 | Preview render | 15-30s | ✅ Every iteration |
| 8 | Final render | 2-10 min | ✅ After preview approval |
| 9 | Download results | 5s | ✅ After final render |

---

## 👀 Preview Mode

**Always run preview before final!** Catches 90% of issues.

### What Preview Generates

| Output | Location | Purpose |
|--------|----------|---------|
| Contact Sheet (JPG) | `renders/previews/sheet_0-40.jpg` | Grid of all frames with timestamps |
| Preview MP4 | `renders/previews/preview_0-40.mp4` | Low-res video with audio |

### Preview Settings (from manifest.json)

```json
"preview": {
  "fps": 8,
  "scale": 0.25,
  "crf": 28,
  "preset": "veryfast"
}
```

**Resolution:** 270×480 (9:16) at 8 fps — fast to render, easy to scrub.

### How to Inspect Preview

1. **Contact Sheet:** Single image showing every frame in sequence
   - Check: text legibility, safe zones, framing, overlaps, easing
   - Each frame labeled with timestamp (e.g., "3.2s")
2. **Preview MP4:** Play in browser or download
   - Check: timing, transitions, audio sync, pacing

### Iteration Loop

```
Edit scene code → Push to GitHub → Colab Cell 4 (pull) → Cell 7 (preview) → Review → Repeat
```

**Target:** < 30 seconds per iteration.

---

## 🎯 Final Render

### Final Settings (from manifest.json)

```json
"final": {
  "fps": 30,
  "scale": 1.0,
  "crf": 18,
  "preset": "slow",
  "pixFmt": "yuv420p",
  "audioCodec": "aac",
  "audioBitrate": "192k",
  "audioSampleRate": 48000,
  "loudnorm": { "I": -14, "TP": -1.5, "LRA": 11 }
}
```

**Quality:** 1080×1920 @ 30fps, H.264 High Profile, CRF 18 (visually lossless), -14 LUFS loudness.

### Chunked Rendering (Automatic for > 2 min)

For videos longer than 2 minutes, the renderer:
1. Splits into 2-minute chunks
2. Renders each chunk separately (parallelizable)
3. Concatenates video streams
4. Mixes audio separately with loudnorm
5. Muxes final output

**Benefits:**
- Survives Colab 90-min idle disconnect
- Resumable (re-run failed chunks only)
- Lower peak memory usage

### Output Location

```
Google Drive: /MyDrive/myproject/renders/final/myproject_v1.mp4
Colab Temp:   /content/project/renders/final/myproject_v1.mp4
```

**Versioning:** Auto-increments (v1, v2, v3...) — never overwrites.

---

## 🛠️ Troubleshooting

### "CUDA not available" / No GPU

```python
# In a cell:
import torch
print(torch.cuda.is_available())  # Should be True
```
**Fix:** Runtime → Change runtime type → GPU (T4) → **Restart runtime**

### "Out of Memory" (OOM)

| Symptom | Fix |
|---------|-----|
| Preview OOM | Reduce `--scale 0.15` in Cell 7 |
| Final OOM | Enable `--chunked --max-chunk-duration 60` |
| Model OOM | Use smaller whisper model (`tiny` instead of `small`) |

### Private Repo Clone Fails

```bash
# In Colab cell:
!git config --global credential.helper store
# Then run Cell 4 again — enter username + PAT (not password)
```

**Create PAT:** GitHub → Settings → Developer settings → Personal access tokens → `repo` scope.

### Fonts Not Loading

1. Run Cell 6 (`fetch_assets.py --category fonts`)
2. Check `manifest.json` has correct paths
3. Verify files exist: `ls /content/project/assets/fonts/`
4. Fonts must be `.woff2` or `.ttf` — no `.otf` (Pillow limitation)

### Audio Sync Issues

1. Verify VO file: `assets/vo/vo_final.mp3` exists
2. Check `beats.json` duration matches VO
3. Run analysis: `python scripts/analyze_ref.py assets/vo/vo_final.mp3`
4. Ensure `beats.json` has `voFile` and `voDuration` fields

### "ffmpeg not found"

```bash
# In Colab cell:
!apt-get update -qq && apt-get install -y -qq ffmpeg
```

### Runtime Disconnect During Render

1. Re-run Cells 1-4 (re-mount Drive, pull repo)
2. Run Cell 8 again — chunked rendering resumes from last completed chunk
3. Check `/content/project/cache/render_work/chunk_*/` for progress

### Drive Quota Exceeded

- Free Drive: 15 GB shared
- Delete old renders from `MyDrive/myproject/renders/final/`
- Or: compress before upload (handled by CRF 18)

---

## ⚡ Advanced Usage

### Render Specific Scene Only

```bash
# In Colab cell:
!python scripts/colab_render.py --mode preview --scene solution
```

### Custom Time Range

```bash
# Preview 5s-15s only:
!python scripts/colab_render.py --mode preview --from 5 --to 15

# Final render 10s-30s:
!python scripts/colab_render.py --mode final --from 10 --to 30
```

### Force Re-download Assets

```bash
!python scripts/fetch_assets.py --category all --force
```

### Verify Assets Without Downloading

```bash
!python scripts/fetch_assets.py --verify-only
```

### Analyze Reference Video

```bash
# On Android (TermFold) or Colab:
python scripts/analyze_ref.py path/to/ref.mp4 --output cache/my_ref
```

Outputs: `analysis_report.json`, frames, audio, stems, transcript.

### Custom Render Config

Edit `manifest.json` → `render` section:

```json
"render": {
  "final": {
    "crf": 16,           // Higher quality (larger file)
    "preset": "veryslow", // Better compression
    "loudnorm": { "I": -16 }  // For broadcast
  }
}
```

### Use Node Renderer Locally (Android/PC)

```bash
# Requires: Node 18+, npm install canvas
cd myproject
npm install
node src/render.js --from 0 --to 10 --fps 30 --scale 0.5 --out renders/test
```

---

## ❓ FAQ

### General

**Q: Can I use this without GitHub?**
A: Yes — upload project folder to Drive manually, skip Cell 4. But GitHub enables version control and easy sync.

**Q: Is Colab free tier enough?**
A: Yes for videos ≤ 2 min. Free tier: 12h/session, T4 GPU, 15GB RAM. For longer videos, use chunked rendering.

**Q: Can I render vertically (9:16) and horizontally (16:9)?**
A: Yes — change `aspect` in `manifest.json` and `data.js`. Re-layout scenes natively (don't crop).

**Q: Where do I put my ElevenLabs voiceover?**
A: `assets/vo/vo_final.mp3` — generate on elevenlabs.io, download, add to repo, push.

### Technical

**Q: How does deterministic rendering work?**
A: Every frame is a pure function of `t` (time). No `Date.now()`, no unseeded random, no state between frames. Same `t` = same pixels.

**Q: Can I use Three.js / WebGL in Colab?**
A: Yes — Playwright Chromium with `--use-angle=swiftshader` (software GL) or GPU acceleration. See `src/render.py` for headless Chrome setup.

**Q: How do I add custom scenes?**
A: 1. Add scene component to `src/scenes/` 2. Register in `src/data.js` `SCENES` array 3. Add beats to `beats.json` 4. Implement `drawScene` in `src/render.py` and `src/render.js`

**Q: What if I need a Python package not in requirements.txt?**
A: Add to `requirements.txt` and re-run Cell 5, or `!pip install package` in a notebook cell.

### Assets & Licensing

**Q: Do I need to credit assets?**
A: Check each asset's license in `manifest.json`. CC0 = no credit required. CC-BY = credit required. Log all in `manifest.json`.

**Q: Can I use Pinterest/Behance images?**
A: Only for **reference/moodboard** (mark `"use": "reference-only"` in manifest). For final video, use licensed sources (Pexels, Pixabay, Unsplash) or recreate in code.

**Q: How do I add a new font?**
A: 1. Download `.woff2` 2. Place in `assets/fonts/` 3. Add entry to `manifest.json` with license 4. Run `fetch_assets.py --category fonts` 5. Register in `data.js` `fontFamilies`

---

## 📞 Support & Resources

| Resource | Link |
|----------|------|
| Motion Video Director Skill | `.config/opencode/skills/motion-video-director/SKILL.md` |
| Project Issues | GitHub Issues in your repo |
| Colab Docs | https://colab.research.google.com/notebooks/intro.ipynb |
| ffmpeg Guide | https://ffmpeg.org/ffmpeg.html |
| Pillow Docs | https://pillow.readthedocs.io/ |

---

## ✅ Quick Checklist (Before Every Render Session)

- [ ] GPU enabled (T4) in Colab
- [ ] All secrets added in 🔑 panel
- [ ] Google Drive mounted
- [ ] Latest code pulled from GitHub
- [ ] Assets downloaded (Cell 6)
- [ ] Voiceover at `assets/vo/vo_final.mp3`
- [ ] Preview approved (Cell 7)
- [ ] Final render complete (Cell 8)
- [ ] MP4 downloaded from Drive (Cell 9)

---

*Happy rendering! 🎬 — Motion Video Director*