# PROGRESS — earth-stopped-spinning (updated 2026-11-18 00:00)

**Phase:** assets
**Current version:** none
**Next step:** Generate VO MP3 on elevenlabs.io (from plan/vo_script.md)

---

## Done

- [x] Project structure created
- [x] Core render entry points (render.js, render.py, data.js)
- [x] Configuration files (beats.json, manifest.json, .env.example, .gitignore)
- [x] Colab scripts (setup, render, fetch_assets, secrets, analyze_ref)
- [x] Google Colab notebook (render.ipynb) - updated for 16:9, 60s
- [x] COLAB_RENDER.md beginner guide - updated for new project
- [x] PROJECT.md brief - updated for "What If Earth Stopped Spinning?"
- [x] Asset directories with .gitkeep
- [x] **VO script written** (plan/vo_script.md) - ElevenLabs paste-ready
- [x] **Storyboard created** (plan/storyboard.md) - 8 detailed scenes
- [x] **beats.json updated** - 8 beats for 60s timeline
- [x] **manifest.json updated** - 16:9, new fonts, colors, SFX, music
- [x] **src/data.js updated** - 16:9 config, 8 scenes, cinematic palette
- [x] **src/render.py updated** - 8 scene drawing functions
- [x] **src/render.js updated** - 8 scene drawing functions
- [x] **Scene modules created** (src/scenes/) - 8 modular scene files
- [x] **Fonts downloaded** - Cinzel, Libre Baskerville, Space Mono (OFL)

---

## In Progress

- [ ] Generate VO MP3 on elevenlabs.io (using plan/vo_script.md)
- [ ] Place VO in assets/vo/vo_final.mp3
- [ ] Update beats.json with actual VO timings (after faster-whisper)
- [ ] Download/fetch SFX from Freesound (manifest.json)
- [ ] Generate/fetch music bed (ElevenLabs or Freesound)
- [ ] Provide channel logo SVG

---

## Next Steps

1. **Generate VO MP3** on elevenlabs.io using plan/vo_script.md (v3, deep documentary male, stability 35%, similarity 80%)
2. **Place VO** at assets/vo/vo_final.mp3
3. **Commit and push** all changes to GitHub
4. **Open Colab notebook** (render.ipynb)
5. **Run Cells 1-6** (setup, mount Drive, clone repo, install deps, download assets)
6. **Run Cell 7** (preview render) - check contact sheet + preview MP4
7. **Iterate** on scene code if needed
8. **Run Cell 8** (final render) after preview approval
9. **Download final MP4** from Google Drive (Cell 9)

---

## Open Issues / Feedback Not Yet Fixed

- None yet

---

## Key Decisions & Preferences

- **Rendering:** Cloud-only (Colab), no local heavy deps
- **Aspect:** 16:9 primary (1920×1080)
- **Intensity:** 4 (cinematic documentary)
- **Fonts:** Cinzel (titles), Libre Baskerville (body), Space Mono (data)
- **Colors:** Deep space #0a0a1a, Earth blue #1e5f9e, Gold #e8a838, Teal #00b4d8, Red #c0392b
- **Audio:** -14 LUFS, VO 10-15dB above music, SFX synced ±1 frame
- **Chunking:** Enabled for >2min videos, 120s max chunk

---

## Key Files

| File | Purpose |
|------|---------|
| `src/render.py` | Colab render entry (Python) |
| `src/render.js` | Local dev render entry (Node) |
| `src/data.js` | Shared config, beats, easing |
| `src/scenes/` | Modular scene drawing functions |
| `beats.json` | Master timeline (VO-driven) |
| `manifest.json` | Asset registry + render config |
| `scripts/colab_render.py` | Main Colab render command |
| `scripts/colab_setup.py` | Colab environment setup |
| `scripts/fetch_assets.py` | Asset downloader |
| `render.ipynb` | Colab notebook (run cells 1-9) |
| `COLAB_RENDER.md` | Beginner guide |
| `plan/vo_script.md` | VO script for ElevenLabs |
| `plan/storyboard.md` | 8-scene storyboard |

---

*Read this file first when resuming. Update after every session.*