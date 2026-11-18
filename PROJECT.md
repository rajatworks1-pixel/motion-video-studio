# PROJECT — Earth Stopped Spinning

## Brief

**Goal:** Create a 60-second cinematic 2D animation exploring "What If Earth Suddenly Stopped Spinning?"

**Audience:** Science-curious viewers, documentary fans, educational content consumers

**Platform:** YouTube (16:9 horizontal), social media clips

**Format:** 16:9 primary (1920×1080), cinematic 2D animation

**Duration:** 60 seconds (VO: ~55s + 5s outro hold)

**Tone:** Dramatic, atmospheric, scientific wonder (intensity 3-4)

**CTA:** "Subscribe for more What If scenarios" → channel link

---

## Brand Assets

| Asset | Status | Details |
|-------|--------|---------|
| Logo | ⬜ Pending | Channel logo SVG needed |
| Color Palette | ✅ Defined | Deep space #0a0a1a, Earth blue #1e5f9e, Accent gold #e8a838, Atmosphere teal #00b4d8, Danger red #c0392b |
| Fonts | ⬜ Pending | Cinzel (titles), Libre Baskerville (body), Space Mono (data/labels) |
| Voiceover | ⬜ Pending | ElevenLabs v3, deep dramatic male narrator (documentary style) |

---

## Video Structure (8 Scenes - Hook → Catastrophe → Atmosphere → Oceans → Temperature → Life → Aftermath → Outro)

| Beat | Time | VO Line | Visual Concept | Keywords |
|------|------|---------|----------------|----------|
| 1. Hook | 0-5s | "What if Earth suddenly stopped spinning?" | Earth in space, slow rotation, then FREEZE frame | EARTH, STOPPED, SPINNING |
| 2. Day/Night | 5-12s | "One side burns in eternal day. The other freezes in endless night." | Split screen: scorching day / frozen night | BURNS, FREEZES, ETERNAL |
| 3. Atmosphere | 12-20s | "The atmosphere keeps moving. Supersonic winds scour the surface." | Wind arrows, shockwaves, debris flying | ATMOSPHERE, SUPERSONIC, SCOUR |
| 4. Oceans | 20-28s | "Oceans surge toward the poles. Equatorial lands rise from the depths." | Water rushing poleward, land emerging | OCEANS, SURGE, POLES |
| 5. Magnetic | 28-36s | "The magnetic field collapses. Radiation strips the air away." | Magnetic field lines fading, particles hitting atmosphere | MAGNETIC, COLLAPSES, RADIATION |
| 6. Temperature | 36-44s | "Extremes beyond survival. 100°C day. -100°C night." | Thermometer graphics, extreme values | EXTREMES, SURVIVAL |
| 7. Life | 44-52s | "Only extremophiles endure. Deep underground. Deep ocean vents." | Microscopic life, hydrothermal vents | EXTREMOPHILES, ENDURE |
| 8. Outro | 52-60s | "Earth stops. Life finds a way. What If... continues." | Earth slowly fading, channel logo, subscribe | EARTH, LIFE, SUBSCRIBE |

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
| Aspect Ratio | 16:9 (1920×1080) | Cinematic horizontal format |

---

## Open Questions

- [ ] Finalize channel logo SVG
- [ ] Choose ElevenLabs voice (test 3 documentary voices)
- [ ] Source background music (cinematic ambient, Freesound/ElevenLabs)
- [ ] Decide on vertical 9:16 cut (native re-layout or skip)
- [ ] Verify scientific accuracy with sources

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

- Recipe B (Cinematic storyteller, intensity 5) from skill §14
- Reference: Kurzgesagt / What If / PBS Space Time style
- Music: Dark ambient, low drones, tension-building
- SFX: Wind howls, magnetic hum, water rush, Geiger counter, deep impacts

---

*Updated: 2026-11-18 | Next: Write VO script (§10)*