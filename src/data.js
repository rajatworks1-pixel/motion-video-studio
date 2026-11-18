export const CONFIG = {
  project: "myproject",
  version: "1.0.0",
  aspect: "9:16",
  width: 1080,
  height: 1920,
  fps: 30,
  duration: 60,
  backgroundColor: "#0a0a0a",
  fontFamilies: {
    primary: "Satoshi",
    secondary: "Inter",
    accent: "Caveat Brush"
  },
  colors: {
    primary: "#ffffff",
    secondary: "#a0a0a0",
    accent: "#ff6a1a",
    accentGradient: ["#ff6a1a", "#ffaa00"],
    background: "#0a0a0a",
    surface: "#1a1a1a",
    text: "#ffffff",
    textMuted: "#888888"
  },
  safeZones: {
    top: 220,
    bottom: 420,
    right: 140,
    left: 140
  },
  intensity: 2,
  videoType: "saas_explainer"
};

export const BEATS = [
  { id: "hook", start: 0.0, end: 3.0, label: "Hook", voLine: 0 },
  { id: "problem", start: 3.0, end: 8.0, label: "Problem", voLine: 1 },
  { id: "solution", start: 8.0, end: 18.0, label: "Solution", voLine: 2 },
  { id: "proof", start: 18.0, end: 30.0, label: "Proof", voLine: 3 },
  { id: "cta", start: 30.0, end: 35.0, label: "CTA", voLine: 4 },
  { id: "outro", start: 35.0, end: 40.0, label: "Outro", voLine: 5 }
];

export const SCENES = [
  { id: "hook", component: "HookScene", beats: ["hook"] },
  { id: "problem", component: "ProblemScene", beats: ["problem"] },
  { id: "solution", component: "SolutionScene", beats: ["solution"] },
  { id: "proof", component: "ProofScene", beats: ["proof"] },
  { id: "cta", component: "CTAScene", beats: ["cta"] },
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

export function stagger(index, baseDelay, staggerAmount) {
  return baseDelay + index * staggerAmount;
}

export function seededRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}