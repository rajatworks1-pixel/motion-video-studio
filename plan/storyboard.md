# Storyboard — Earth Stopped Spinning (60s, 16:9)

## Global Style

- **Aspect:** 16:9 (1920×1080)
- **Palette:** Deep space #0a0a1a, Earth blue #1e5f9e, Accent gold #e8a838, Atmosphere teal #00b4d8, Danger red #c0392b, White #ffffff
- **Fonts:** Cinzel (titles/keywords), Libre Baskerville (body), Space Mono (data/labels)
- **Intensity:** 3-4 (cinematic documentary)
- **Grain:** 8% film grain overlay
- **Vignette:** Subtle, 15% at edges

---

## Scene 1: Hook — "The Freeze" (0-5s)

| Property | Detail |
|----------|--------|
| **VO** | "[ominous, hushed] What if Earth suddenly stopped spinning?" |
| **Visual** | Earth rotating slowly in starfield. At 1.5s: rotation FREEZES with a subtle "lock" effect. Camera pushes in. |
| **Motion** | Slow orbit (0.5°/s) → sudden stop (ease-in-cubic, 0.3s) → slow dolly push-in (1.02x over 3.5s) |
| **Text** | "EARTH" (Cinzel, large, center) rises from bottom; "STOPPED SPINNING" (Libre Baskerville, smaller) fades in below |
| **SFX** | Low sub-drone base → sharp "magnetic lock" transient at freeze frame (1.5s) → rising tension riser |
| **Transition** | Match cut to split screen (Earth becomes the divider) |
| **Key Frame** | t=1.5s: freeze moment with subtle chromatic aberration flash |

---

## Scene 2: Day/Night — "Eternal Extremes" (5-12s)

| Property | Detail |
|----------|--------|
| **VO** | "[grave, deliberate] One side burns in eternal day. The other freezes in endless night." |
| **Visual** | Vertical split screen: LEFT = blinding white/day side with heat distortion shimmer; RIGHT = deep blue/black night side with frost crystals growing. Center divider glows gold. |
| **Motion** | Split line pushes from center outward (revealing more of each side). Heat shimmer (perlin noise displacement). Frost crystal growth (procedural, seeded). Camera very slow push-in. |
| **Text** | "BURNS" (Cinzel, gold, left) / "FREEZES" (Cinzel, teal, right) — kinetic type, letter-by-letter reveal synced to VO. "ETERNAL DAY" / "ENDLESS NIGHT" (Libre Baskerville, smaller, below) |
| **SFX** | Left: low solar hum + subtle crackle. Right: wind howl + ice crack. Gold divider: soft chime on each keyword |
| **Transition** | Whip pan left (following "winds" keyword) → atmosphere view |
| **Key Frame** | t=8.5s: keywords fully visible, split at max width |

---

## Scene 3: Atmosphere — "Supersonic Scour" (12-20s)

| Property | Detail |
|----------|--------|
| **VO** | "[building tension] The atmosphere keeps moving. Supersonic winds scour the surface at a thousand miles per hour." |
| **Visual** | Side view of Earth: thick atmosphere layer (teal gradient) rushing left-to-right as supersonic wind arrows. Surface particles (dust, debris) ripped up. Shockwave cones forming at mountains. |
| **Motion** | Wind flow lines (animated SVG paths) at high speed. Particle system: thousands of small rects lifted and streaked. Shockwave cones pulse. Camera tracks with wind flow (parallax). |
| **Text** | "SUPERSONIC" (Cinzel, large, teal, tracking with wind) — letters stretch/smear in motion direction. "1,000 MPH" (Space Mono, gold, counter rolling up) |
| **SFX** | Intense wind howl (layered: low roar + high whistle). Sharp "whoosh" per shockwave. Sub-bass impacts on "scour" |
| **Transition** | Match cut: wind arrows become water currents → oceans |
| **Key Frame** | t=16s: max particle density, "SUPERSONIC" fully stretched |

---

## Scene 4: Oceans — "Polar Surge" (20-28s)

| Property | Detail |
|----------|--------|
| **VO** | "[urgent] Oceans surge toward the poles. Entire continents rise from the drowning depths." |
| **Visual** | Top-down Earth view: blue water masses rushing from equator toward poles (red arrows). Land masses (brown/green) emerging at equator as water leaves. Bathymetry map style. |
| **Motion** | Water flow simulation (shader-based). Land rising (scale Y 0→1 with ease-out-expo). Arrow paths animated. Camera orbits slowly. |
| **Text** | "OCEANS SURGE" (Cinzel, teal, curved along flow path). "POLES" (Cinzel, white, at poles). "CONTINENTS RISE" (Libre Baskerville, gold, at equator) |
| **SFX** | Deep water rush (low-frequency). Subtle "land rising" rumble. Gold chime on "continents" |
| **Transition** | Camera pushes through Earth crust → magnetic field view |
| **Key Frame** | t=24s: max water at poles, new equatorial landmass visible |

---

## Scene 5: Magnetic — "Field Collapse" (28-36s)

| Property | Detail |
|----------|--------|
| **VO** | "[cold, clinical] The magnetic field collapses. Cosmic radiation strips the air away, molecule by molecule." |
| **Visual** | 3D-style magnetic field lines (gold loops) around Earth. Lines flicker, weaken, snap. Charged particles (tiny white dots) from solar wind penetrate and hit atmosphere (red sparks). |
| **Motion** | Field lines: amplitude decay (sin wave dampening). Particle penetration: increasing rate. Atmosphere glow fading (teal → transparent). Camera slow orbit. |
| **Text** | "MAGNETIC FIELD" (Cinzel, gold, fading with field). "COLLAPSES" (Cinzel, red, impact flash). "RADIATION" (Space Mono, red, counter: particles hitting/sec) |
| **SFX** | Low electromagnetic hum (descending pitch). Sharp "snap" per field line break. Geiger counter clicks (accelerating). High-frequency "strip" sizzle |
| **Transition** | Hard cut to temperature graphic (data visualization style) |
| **Key Frame** | t=32s: field lines gone, particle storm at max |

---

## Scene 6: Temperature — "Beyond Survival" (36-44s)

| Property | Detail |
|----------|--------|
| **VO** | "[stark] Extremes beyond survival. One hundred Celsius day. Minus one hundred Celsius night." |
| **Visual** | Split thermometers: LEFT (day) mercury shooting up past 100°C, glass cracking. RIGHT (night) mercury plummeting past -100°C, frost sealing bulb. Background: day side solar flare, night side starfield. |
| **Motion** | Mercury: rapid ease-out-expo to max/min. Glass crack propagation (procedural). Frost growth (cellular automaton). Numbers count up/down (Space Mono). |
| **Text** | "100°C" / "-100°C" (Cinzel, huge, gold/teal). "BEYOND SURVIVAL" (Libre Baskerville, white, center, fade in) |
| **SFX** | Mercury rise: rising pitch tone. Mercury fall: descending tone. Glass crack: sharp transient. Frost: crystalline chimes. Sub hit on "survival" |
| **Transition** | Crossfade to microscopic view (life finds a way) |
| **Key Frame** | t=40s: both thermometers at extreme, "BEYOND SURVIVAL" centered |

---

## Scene 7: Life — "Extremophiles Endure" (44-52s)

| Property | Detail |
|----------|--------|
| **VO** | "[quiet wonder] Only extremophiles endure. Deep underground. Deep ocean vents. Life... finds a way." |
| **Visual** | Microscopic view: thermophilic archaea (rod-shaped, glowing gold) near hydrothermal vent (black smoker, teal/gold plumes). Camera moves through vent chimney into dark rock fissures. |
| **Motion** | Microbes: subtle Brownian motion, gentle pulsing. Vent plume: turbulent fluid sim. Camera: slow descent into fissure. Bioluminescence pulses. |
| **Text** | "EXTREMOPHILES" (Cinzel, gold, floating with microbes). "ENDURE" (Libre Baskerville, white, fade in on "endure"). "LIFE FINDS A WAY" (Cinzel, gold, large, final hold) |
| **SFX** | Deep ocean ambience (low rumble). Vent: bubbling/hissing. Microbe pulses: soft organic clicks. "finds a way": warm major chord resolution |
| **Transition** | Slow pull out: fissure → vent → ocean → Earth from space |
| **Key Frame** | t=50s: "LIFE FINDS A WAY" centered, microbes visible |

---

## Scene 8: Outro — "What If Continues" (52-60s)

| Property | Detail |
|----------|--------|
| **VO** | "[warm, reflective] Earth stops. Life persists. What If... continues." |
| **Visual** | Earth in space (static, no rotation). Slow fade to starfield. Channel logo appears (center). Subscribe button (gold gradient) rises. URL fades in below. |
| **Motion** | Earth: slow scale down (1.0→0.8). Logo: scale 0→1.1→1 (overshoot). Button: rise + gradient shimmer sweep. Text: fade in. |
| **Text** | Channel logo (SVG). "SUBSCRIBE" (Cinzel, gold, on button). "What If... continues" (Libre Baskerville, white). Channel URL (Space Mono, teal) |
| **SFX** | Music bed resolves to major. Logo: soft "whoom" impact. Button: subtle click. Final chord hold. |
| **Transition** | Fade to black (1s) |
| **Key Frame** | t=56s: all elements visible, hold to 60s |

---

## Shot List Summary

| # | Scene | Duration | Visual Style | Text Style | SFX Intensity |
|---|-------|----------|--------------|------------|---------------|
| 1 | Hook | 5s | Space/planet | Cinzel rise | Low → spike |
| 2 | Day/Night | 7s | Split screen | Kinetic split | Medium (dual) |
| 3 | Atmosphere | 8s | Flow viz | Stretched kinetic | High |
| 4 | Oceans | 8s | Map/simulation | Curved path | Medium-high |
| 5 | Magnetic | 8s | Field lines | Fading + counter | High (geiger) |
| 6 | Temperature | 8s | Data viz | Giant numbers | Medium |
| 7 | Life | 8s | Micro/cinematic | Floating organic | Low → resolve |
| 8 | Outro | 8s | Space/logo | Clean UI | Resolve |

---

## Motion Principles Applied

- **Disney's 12:** Anticipation (freeze frame), Follow-through (particles), Slow in/out (all text), Arcs (camera orbits), Secondary action (plumes/microbes), Timing (VO sync), Exaggeration (stretched type), Appeal (gold/teal contrast)
- **Easing:** easeOutExpo (entrances), easeInCubic (exits), easeOutCubic (holds)
- **Stagger:** 60-80ms between related elements
- **Hierarchy:** One focal keyword per beat, body text supports
- **Continuity:** Gold = energy/life, Teal = atmosphere/water, Red = danger/heat, Blue = cold/space

---

## Asset Requirements

| Asset | Source | Status |
|-------|--------|--------|
| Fonts: Cinzel, Libre Baskerville, Space Mono | Google Fonts (OFL) | ⬜ Download |
| Music: Dark ambient bed (60s) | ElevenLabs / Freesound | ⬜ Generate |
| SFX: Wind, water, geiger, impacts, clicks | Freesound (CC0) | ⬜ Fetch |
| Channel logo SVG | Brand assets | ⬜ Provide |
| Starfield background | Procedural / Pixabay | ⬜ Generate |