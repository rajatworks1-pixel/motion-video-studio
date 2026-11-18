# PROGRESS — myproject (updated 2026-11-18 00:00)

**Phase:** setup
**Current version:** none
**Next step:** Write VO script for ElevenLabs (§10)

---

## Done

- [x] Project structure created
- [x] Core render entry points (render.js, render.py, data.js)
- [x] Configuration files (beats.json, manifest.json, .env.example, .gitignore)
- [x] Colab scripts (setup, render, fetch_assets, secrets, analyze_ref)
- [x] Google Colab notebook (render.ipynb)
- [x] COLAB_RENDER.md beginner guide
- [x] PROJECT.md brief
- [x] Asset directories with .gitkeep

---

## In Progress

- [ ] Write VO script (paste-ready ElevenLabs block)
- [ ] Generate VO MP3 on elevenlabs.io
- [ ] Add VO to assets/vo/vo_final.mp3
- [ ] Commit and push to GitHub

---

## Next Steps

1. **Write VO script** using §10 format (target: 40s, ~100 words)
2. **Generate MP3** on elevenlabs.io (v3, deep calm male, stability 45%, similarity 75%)
3. **Place in assets/vo/vo_final.mp3**
4. **Update beats.json** with actual VO timings (after faster-whisper analysis)
5. **Run Colab preview** to verify timing

---

## Open Issues / Feedback Not Yet Fixed

- None yet

---

## Key Decisions & Preferences

- **Rendering:** Cloud-only (Colab), no local heavy deps
- **Aspect:** 9:16 primary, 16:9 secondary (native re-layout)
- **Intensity:** 2 (clarity-first SaaS explainer)
- **Fonts:** Satoshi/Inter/Caveat Brush (all ITF Free/OFL)
- **Colors:** Dark bg #0a0a0a, orange accent #ff6a1a, gradient #ff6a1a→#ffaa00
- **Audio:** -14 LUFS, VO 10-15dB above music, SFX synced ±1 frame
- **Chunking:** Enabled for >2min videos, 120s max chunk

---

## Key Files

| File | Purpose |
|------|---------|
| `src/render.py` | Colab render entry (Python) |
| `src/render.js` | Local dev render entry (Node) |
| `src/data.js` | Shared config, beats, easing |
| `beats.json` | Master timeline (VO-driven) |
| `manifest.json` | Asset registry + render config |
| `scripts/colab_render.py` | Main Colab render command |
| `scripts/colab_setup.py` | Colab environment setup |
| `scripts/fetch_assets.py` | Asset downloader |
| `render.ipynb` | Colab notebook (run cells 1-9) |
| `COLAB_RENDER.md` | Beginner guide |

---

*Read this file first when resuming. Update after every session.*