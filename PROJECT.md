# PROJECT — myproject

## Brief

**Goal:** Create a 40-second SaaS product explainer video for "Flow" — an automated workflow tool.

**Audience:** Technical decision-makers, developers, startup founders (B2B SaaS)

**Platform:** Social media (9:16 vertical), website embed (16:9 horizontal)

**Format:** 9:16 primary (1080×1920), 16:9 secondary (1920×1080)

**Duration:** 40 seconds (VO: ~35s + 5s outro hold)

**Tone:** Professional, confident, clarity-first (intensity 2)

**CTA:** "Start Free Today" → flow.example.com

---

## Brand Assets

| Asset | Status | Details |
|-------|--------|---------|
| Logo | ⬜ Pending | SVG needed |
| Color Palette | ✅ Defined | Primary #0a0a0a, Accent #ff6a1a, Gradient #ff6a1a→#ffaa00 |
| Fonts | ✅ Selected | Satoshi (headlines), Inter (body), Caveat Brush (accent) |
| Voiceover | ⬜ Pending | ElevenLabs v3, deep calm male narrator |

---

## Video Structure (Hook → Problem → Solution → Proof → CTA)

| Beat | Time | VO Line | Visual Concept | Keywords |
|------|------|---------|----------------|----------|
| Hook | 0-3s | "Nobody drew this. Not one line... not one frame." | Bold centered text rise | NOBODY, DREW, THIS |
| Problem | 3-8s | "Most teams lose hours every week to manual work." | Two-line body text fade | HOURS, MANUAL WORK |
| Solution | 8-18s | "So where did it come from? ... Meet Flow." | Gradient "Meet Flow." scale up | FLOW |
| Proof | 18-30s | "Automated workflows. Real-time sync. Zero config." | 3 feature cards stagger pop | AUTOMATED, REAL-TIME, ZERO CONFIG |
| CTA | 30-35s | "Start yours today — link below." | Gradient button rise | START, TODAY |
| Outro | 35-40s | "Flow. flow.example.com" | Logo + URL fade in | FLOW |

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Render Engine | Python PIL + ffmpeg (Colab) | No GPU deps on Android, deterministic |
| Preview Mode | 8fps, 25% scale, contact sheet | Fast iteration (<30s) |
| Final Quality | 30fps, CRF 18, -14 LUFS | Professional delivery standard |
| Chunking | 2-min chunks, auto-concat | Survives Colab disconnects |
| Font Loading | Local .woff2 via Pillow | No web font dependency |
| Audio Mix | VO + music bed + SFX per beat | Sync to transcript timestamps |

---

## Open Questions

- [ ] Finalize logo SVG
- [ ] Choose ElevenLabs voice (test 3 options)
- [ ] Source background music (ElevenLabs vs Freesound)
- [ ] Decide on 16:9 version (native re-layout or skip)
- [ ] Confirm feature card copy with product team

---

## Approval Gates

| Gate | Status | Approver |
|------|--------|----------|
| Script/VO | ⬜ Pending | You |
| Storyboard | ⬜ Pending | You |
| Styleboard | ⬜ Pending | You |
| Preview | ⬜ Pending | You |
| Final v1 | ⬜ Pending | You |

---

## References

- Recipe C (SaaS launch, intensity 2-3) from skill §14
- Reference: Slack launch video (clarity-first, 2D→3D pop)
- Music: Minimal ambient bed, sub pulses ~0.33s
- SFX: UI ticks, whoosh, impact, card pops, button click

---

*Updated: 2026-11-18 | Next: Write VO script (§10)*