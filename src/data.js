export const CONFIG = {
  project: "earth-stopped-spinning",
  version: "1.0.0",
  aspect: "16:9",
  width: 1920,
  height: 1080,
  fps: 30,
  duration: 60,
  backgroundColor: "#0a0a1a",
  fontFamilies: {
    primary: "Cinzel",
    secondary: "Libre Baskerville",
    mono: "Space Mono"
  },
  colors: {
    primary: "#ffffff",
    secondary: "#a0b8d0",
    accent: "#e8a838",
    accentGradient: ["#e8a838", "#ffcc00"],
    danger: "#c0392b",
    dangerGradient: ["#c0392b", "#e74c3c"],
    atmosphere: "#00b4d8",
    atmosphereGradient: ["#00b4d8", "#0077b6"],
    background: "#0a0a1a",
    surface: "#15152a",
    text: "#ffffff",
    textMuted: "#8899aa",
    gold: "#e8a838",
    teal: "#00b4d8",
    red: "#c0392b"
  },
  safeZones: {
    top: 80,
    bottom: 120,
    right: 100,
    left: 100
  },
  intensity: 4,
  videoType: "cinematic_documentary",
  grain: 0.08,
  vignette: 0.15
};

export const BEATS = [
  { id: "hook", start: 0.0, end: 5.0, label: "Hook — The Freeze", voLine: 0 },
  { id: "day_night", start: 5.0, end: 12.0, label: "Day/Night — Eternal Extremes", voLine: 1 },
  { id: "atmosphere", start: 12.0, end: 20.0, label: "Atmosphere — Supersonic Scour", voLine: 2 },
  { id: "oceans", start: 20.0, end: 28.0, label: "Oceans — Polar Surge", voLine: 3 },
  { id: "magnetic", start: 28.0, end: 36.0, label: "Magnetic — Field Collapse", voLine: 4 },
  { id: "temperature", start: 36.0, end: 44.0, label: "Temperature — Beyond Survival", voLine: 5 },
  { id: "life", start: 44.0, end: 52.0, label: "Life — Extremophiles Endure", voLine: 6 },
  { id: "outro", start: 52.0, end: 60.0, label: "Outro — What If Continues", voLine: 7 }
];

export const SCENES = [
  { id: "hook", component: "HookScene", beats: ["hook"] },
  { id: "day_night", component: "DayNightScene", beats: ["day_night"] },
  { id: "atmosphere", component: "AtmosphereScene", beats: ["atmosphere"] },
  { id: "oceans", component: "OceansScene", beats: ["oceans"] },
  { id: "magnetic", component: "MagneticScene", beats: ["magnetic"] },
  { id: "temperature", component: "TemperatureScene", beats: ["temperature"] },
  { id: "life", component: "LifeScene", beats: ["life"] },
  { id: "outro", component: "OutroScene", beats: ["outro"] }
];

export function getBeat(id) {
  return BEATS.find(b => b.id === id);
}

export function getScene(id) {
  return SCENES.find(s => s.id === id);
}

export function getBeatsForScene(sceneId) {
  const scene = getScene(sceneId);
  if (!scene) return [];
  return scene.beats.map(id => getBeat(id)).filter(Boolean);
}

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

export function easeInCubic(t) {
  return t * t * t;
}

export function easeOutExpo(t) {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
}

export function easeInExpo(t) {
  return t === 0 ? 0 : Math.pow(2, 10 * (t - 1));
}

export function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

export function stagger(index, baseDelay, staggerAmount) {
  return baseDelay + index * staggerAmount;
}

export function seededRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

export function perlinNoise(x, y, seed = 42) {
  const n = Math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453;
  return n - Math.floor(n);
}

export function smoothStep(t) {
  return t * t * (3 - 2 * t);
}

export function smootherStep(t) {
  return t * t * t * (t * (t * 6 - 15) + 10);
}