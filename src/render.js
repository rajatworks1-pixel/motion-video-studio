#!/usr/bin/env node
import { program } from "commander";
import {
  CONFIG, BEATS, SCENES, getBeat, getScene, getBeatsForScene,
  lerp, clamp, easeOutCubic, easeInCubic, easeOutExpo, easeInExpo, easeOutBack,
  stagger, seededRandom, perlinNoise, smoothStep, smootherStep
} from "./data.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createCanvas } from "canvas";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

program
  .name("render")
  .description("Deterministic frame renderer for motion video")
  .option("--from <number>", "Start time in seconds", 0)
  .option("--to <number>", "End time in seconds", CONFIG.duration)
  .option("--fps <number>", "Frames per second", CONFIG.fps)
  .option("--scale <number>", "Resolution scale 0-1", 1.0)
  .option("--out <string>", "Output directory", "renders/final")
  .option("--jpg", "Output JPG instead of PNG", false)
  .option("--scene <string>", "Render specific scene only", null)
  .option("--seed <number>", "Random seed for deterministic noise", 42)
  .parse(process.argv);

const opts = program.opts();
const FROM = parseFloat(opts.from);
const TO = parseFloat(opts.to);
const FPS = parseInt(opts.fps, 10);
const SCALE = clamp(parseFloat(opts.scale), 0.01, 1.0);
const OUT_DIR = path.resolve(__dirname, "..", opts.out);
const USE_JPG = opts.jpg;
const TARGET_SCENE = opts.scene;
const SEED = parseInt(opts.seed, 10);

const WIDTH = Math.round(CONFIG.width * SCALE);
const HEIGHT = Math.round(CONFIG.height * SCALE);
const TOTAL_FRAMES = Math.round((TO - FROM) * FPS);

console.log(`[render] Project: ${CONFIG.project}`);
console.log(`[render] Range: ${FROM}s - ${TO}s (${TOTAL_FRAMES} frames)`);
console.log(`[render] Resolution: ${WIDTH}x${HEIGHT} @ ${FPS}fps (scale: ${SCALE})`);
console.log(`[render] Output: ${OUT_DIR}`);
console.log(`[render] Seed: ${SEED}`);

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const canvas = createCanvas(WIDTH, HEIGHT);
const ctx = canvas.getContext("2d");

const FONT_CACHE = new Map();

function loadFont(fontName, size, weight = "regular") {
  const key = `${fontName}-${weight}-${size}`;
  if (FONT_CACHE.has(key)) return FONT_CACHE.get(key);

  const fontDir = path.resolve(__dirname, "..", "assets", "fonts");
  const fontMap = {
    "Cinzel-bold": "Cinzel-Variable.ttf",
    "Cinzel-regular": "Cinzel-Variable.ttf",
    "Libre Baskerville-bold": "LibreBaskerville-Variable.ttf",
    "Libre Baskerville-regular": "LibreBaskerville-Variable.ttf",
    "Libre Baskerville-italic": "LibreBaskerville-Italic-Variable.ttf",
    "Space Mono-bold": "SpaceMono-Bold.ttf",
    "Space Mono-regular": "SpaceMono-Regular.ttf",
  };

  const fontFile = fontMap[`${fontName}-${weight}`];
  let fontStr;
  if (fontFile && fs.existsSync(path.join(fontDir, fontFile))) {
    fontStr = `${weight} ${size}px "${fontName}"`;
  } else {
    fontStr = `${weight === "bold" ? "bold" : "normal"} ${size}px sans-serif`;
  }
  FONT_CACHE.set(key, fontStr);
  return fontStr;
}

function hexToRgb(hex) {
  const h = hex.replace("#", "");
  return {
    r: parseInt(h.substr(0, 2), 16),
    g: parseInt(h.substr(2, 2), 16),
    b: parseInt(h.substr(4, 2), 16)
  };
}

function hexToRgba(hex, alpha) {
  const { r, g, b } = hexToRgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function drawStarfield(ctx, width, height, seed, density = 0.001) {
  const numStars = Math.floor(width * height * density);
  for (let i = 0; i < numStars; i++) {
    const x = Math.floor(seededRandom(seed + i) * width);
    const y = Math.floor(seededRandom(seed + i + 1000) * height);
    const brightness = Math.floor(128 + seededRandom(seed + i + 2000) * 127);
    const size = seededRandom(seed + i + 3000) > 0.7 ? 2 : 1;
    ctx.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness})`;
    ctx.fillRect(x, y, size, size);
  }
}

function drawRoundedRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function drawGrainOverlay(ctx, width, height, amount, seed) {
  if (amount <= 0) return;
  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const noise = seededRandom(seed + x * 0.01 + y * 0.01) - 0.5;
      const grain = noise * amount * 255;
      data[idx] = Math.min(255, Math.max(0, data[idx] + grain));
      data[idx + 1] = Math.min(255, Math.max(0, data[idx + 1] + grain));
      data[idx + 2] = Math.min(255, Math.max(0, data[idx + 2] + grain));
    }
  }
  ctx.putImageData(imageData, 0, 0);
}

function drawVignette(ctx, width, height, amount) {
  if (amount <= 0) return;
  const cx = width / 2, cy = height / 2;
  const maxR = Math.hypot(cx, cy);
  const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);
  gradient.addColorStop(0, "rgba(0,0,0,0)");
  gradient.addColorStop(1, `rgba(0,0,0,${amount})`);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
}

function drawDebugInfo(ctx, t, frameIndex) {
  ctx.save();
  ctx.font = "12px monospace";
  ctx.fillStyle = "rgba(255,255,255,0.5)";
  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.fillText(`t=${t.toFixed(3)}s frame=${frameIndex} seed=${SEED}`, 10, 10);
  ctx.fillText(`${WIDTH}x${HEIGHT} @ ${FPS}fps scale=${SCALE}`, 10, 30);

  for (const beat of BEATS) {
    if (beat.start <= t && t < beat.end) {
      ctx.fillStyle = "rgba(232,168,56,0.8)";
      ctx.fillText(`Beat: ${beat.id} (${beat.label})`, 10, 50);
      break;
    }
  }
  ctx.restore();
}

// ========== SCENE 1: HOOK ==========
function drawHookScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  drawStarfield(ctx, CONFIG.width, CONFIG.height, SEED, 0.0008);

  const earthR = Math.min(CONFIG.width, CONFIG.height) * 0.25;
  const earthProgress = clamp(progress / 0.3, 0, 1);
  const rotationAngle = lerp(0, -0.3, easeInCubic(earthProgress));

  // Earth circle with simple shading
  for (let r = earthR; r > 0; r -= 2) {
    const alpha = (1 - r / earthR) * 0.6;
    ctx.strokeStyle = `rgba(30, 80, 150, ${alpha})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(cx, cy, r, r, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Freeze flash
  if (progress > 0.25 && progress < 0.35) {
    const flashAlpha = 1 - Math.abs(progress - 0.3) / 0.05;
    ctx.strokeStyle = `rgba(255, 255, 200, ${flashAlpha})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(cx, cy, earthR, earthR, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Camera push-in
  const scale = lerp(1.0, 1.15, progress);
  const scaledR = earthR * scale;

  // Text: "EARTH" rises
  const textProgress = clamp((progress - 0.2) / 0.5, 0, 1);
  const easing = easeOutExpo(textProgress);
  const y = lerp(cy + 200, cy - 80, easing);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.font = "bold 96px Cinzel, serif";
  ctx.fillStyle = CONFIG.colors.primary;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("EARTH", cx, y);
  ctx.restore();

  // "STOPPED SPINNING"
  const subProgress = clamp((progress - 0.5) / 0.4, 0, 1);
  const subEasing = easeOutCubic(subProgress);
  const subY = lerp(cy + 100, cy + 40, subEasing);
  const subOpacity = subEasing;

  ctx.save();
  ctx.globalAlpha = subOpacity;
  ctx.font = "36px 'Libre Baskerville', serif";
  ctx.fillStyle = CONFIG.colors.secondary;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("STOPPED SPINNING", cx, subY);
  ctx.restore();
}

// ========== SCENE 2: DAY/NIGHT ==========
function drawDayNightScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const splitProgress = easeOutCubic(progress);
  const leftWidth = cx * splitProgress;
  const rightStart = CONFIG.width - leftWidth;

  // Day side (left) - heat shimmer
  for (let x = 0; x < leftWidth; x += 2) {
    for (let y = 0; y < CONFIG.height; y += 4) {
      const noiseVal = perlinNoise(x * 0.02, y * 0.01 + t * 2, SEED);
      const offset = noiseVal * 8;
      const shade = 200 + noiseVal * 55;
      ctx.fillStyle = `rgb(${shade}, ${shade / 2}, 0)`;
      ctx.fillRect(x + offset, y, 2, 3);
    }
  }

  // Sun glow
  const sunAlpha = 100 * splitProgress / 255;
  for (let r = 200; r > 0; r -= 10) {
    ctx.strokeStyle = `rgba(255, 200, 0, ${sunAlpha / (200 / r + 1)})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(cx - leftWidth, cy, r, r, 0, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Night side (right) - frost crystals
  for (let x = rightStart; x < CONFIG.width; x += 3) {
    for (let y = 0; y < CONFIG.height; y += 6) {
      const noiseVal = perlinNoise(x * 0.015, y * 0.02, SEED + 1000);
      if (noiseVal > 0.7) {
        const crystalH = noiseVal * 40;
        ctx.strokeStyle = `rgba(100, 180, 255, ${noiseVal * 0.8})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + noiseVal * 3, y - crystalH);
        ctx.stroke();
      }
    }
  }

  // Gold divider
  const dividerAlpha = splitProgress;
  ctx.strokeStyle = `rgba(232, 168, 56, ${dividerAlpha})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(cx, 0);
  ctx.lineTo(cx, CONFIG.height);
  ctx.stroke();

  // "BURNS" (left)
  const burnsProgress = clamp((progress - 0.1) / 0.4, 0, 1);
  const burnsEasing = easeOutExpo(burnsProgress);
  if (burnsProgress > 0) {
    ctx.save();
    ctx.globalAlpha = burnsEasing;
    ctx.font = "bold 72px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("BURNS", cx - leftWidth / 2, cy - 60);
    ctx.restore();
  }

  // "FREEZES" (right)
  const freezesProgress = clamp((progress - 0.2) / 0.4, 0, 1);
  const freezesEasing = easeOutExpo(freezesProgress);
  if (freezesProgress > 0) {
    ctx.save();
    ctx.globalAlpha = freezesEasing;
    ctx.font = "bold 72px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.teal;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("FREEZES", cx + (CONFIG.width - rightStart) / 2, cy - 60);
    ctx.restore();
  }

  // Sub text
  const subProgress = clamp((progress - 0.5) / 0.4, 0, 1);
  const subEasing = easeOutCubic(subProgress);
  if (subProgress > 0) {
    ctx.save();
    ctx.globalAlpha = subEasing;
    ctx.font = "italic 28px 'Libre Baskerville', serif";
    ctx.fillStyle = CONFIG.colors.textMuted;
    ctx.textAlign = "center";
    ctx.fillText("ETERNAL DAY", cx - leftWidth / 2, cy + 40);
    ctx.fillText("ENDLESS NIGHT", cx + (CONFIG.width - rightStart) / 2, cy + 40);
    ctx.restore();
  }
}

// ========== SCENE 3: ATMOSPHERE ==========
function drawAtmosphereScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const earthH = CONFIG.height * 0.3;
  ctx.fillStyle = "rgb(10, 10, 30)";
  ctx.fillRect(0, CONFIG.height - earthH, CONFIG.width, earthH);

  const atmoH = CONFIG.height * 0.15;
  const atmoY = CONFIG.height - earthH - atmoH;

  // Atmosphere gradient
  const atmoGrad = ctx.createLinearGradient(0, atmoY, 0, atmoY + atmoH);
  atmoGrad.addColorStop(0, "rgba(0, 180, 216, 0.7)");
  atmoGrad.addColorStop(1, "rgba(0, 119, 182, 0)");
  ctx.fillStyle = atmoGrad;
  ctx.fillRect(0, atmoY, CONFIG.width, atmoH);

  // Wind flow lines
  const flowSpeed = t * 500;
  const numLines = 20;
  for (let i = 0; i < numLines; i++) {
    const y = atmoY + (i / numLines) * atmoH;
    const lineProgress = (flowSpeed + i * 50) % CONFIG.width;
    const lineLen = 150;
    const alpha = 0.8 * (1 - Math.abs((lineProgress % CONFIG.width) - CONFIG.width/2) / (CONFIG.width/2));
    ctx.strokeStyle = `rgba(0, 200, 255, ${alpha})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(lineProgress, y);
    ctx.lineTo(lineProgress + lineLen, y);
    ctx.stroke();
  }

  // Particles
  for (let i = 0; i < 50; i++) {
    const pSeed = SEED + i * 100;
    const x = (seededRandom(pSeed) * CONFIG.width + t * 300) % CONFIG.width;
    const y = CONFIG.height - earthH - seededRandom(pSeed + 1) * earthH * 0.5;
    const size = 2 + seededRandom(pSeed + 2) * 4;
    const alpha = 0.6 + seededRandom(pSeed + 3) * 0.4;
    ctx.fillStyle = `rgba(200, 200, 100, ${alpha})`;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // Shockwave cones
  const mountainX = [CONFIG.width * 0.2, CONFIG.width * 0.5, CONFIG.width * 0.8];
  for (const mx of mountainX) {
    const swProgress = (t * 2) % 1.5 / 1.5;
    const swH = earthH * swProgress;
    const swAlpha = 0.8 * (1 - swProgress);
    for (let dy = 0; dy < swH; dy += 2) {
      const w = dy * 0.5;
      ctx.strokeStyle = `rgba(255, 150, 0, ${swAlpha})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(mx - w, CONFIG.height - earthH - dy);
      ctx.lineTo(mx + w, CONFIG.height - earthH - dy);
      ctx.stroke();
    }
  }

  // "SUPERSONIC" stretched
  const textProgress = clamp((progress - 0.1) / 0.3, 0, 1);
  if (textProgress > 0) {
    ctx.save();
    ctx.globalAlpha = textProgress;
    ctx.font = "bold 80px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.teal;
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    const text = "SUPERSONIC";
    let xStart = CONFIG.width * 0.1;
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      const metrics = ctx.measureText(char);
      const stretch = 1 + textProgress * 0.5;
      const y = atmoY - 60 + Math.sin(t * 5 + i) * 5;
      ctx.fillText(char, xStart, y);
      xStart += metrics.width * stretch;
    }
    ctx.restore();
  }

  // "1,000 MPH" counter
  const counterProgress = clamp((progress - 0.4) / 0.3, 0, 1);
  if (counterProgress > 0) {
    ctx.save();
    ctx.globalAlpha = counterProgress;
    ctx.font = "bold 48px 'Space Mono', monospace";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "right";
    const val = Math.floor(1000 * easeOutExpo(counterProgress));
    ctx.fillText(`${val.toLocaleString()} MPH`, CONFIG.width - 50, 80);
    ctx.restore();
  }
}

// ========== SCENE 4: OCEANS ==========
function drawOceansScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;
  const r = Math.min(CONFIG.width, CONFIG.height) * 0.35;

  // Ocean currents (arcs from equator to poles)
  for (let angle = 0; angle < 360; angle += 10) {
    const rad = angle * Math.PI / 180;
    const poleFactor = Math.abs(Math.sin(rad));
    const flowProgress = (progress + poleFactor * 0.5) % 1.0;
    const currentR = r * (0.3 + 0.7 * flowProgress);

    const x1 = cx + currentR * Math.cos(rad);
    const y1 = cy + currentR * Math.sin(rad);
    const x2 = cx + r * Math.cos(rad);
    const y2 = cy + r * Math.sin(rad);

    const alpha = 0.8 * poleFactor;
    ctx.strokeStyle = `rgba(0, 100, 200, ${alpha})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  // Land masses emerging
  const landAngles = [0, 45, 135, 180, 225, 315];
  const landProgress = easeOutExpo(progress);
  for (const angle of landAngles) {
    const rad = angle * Math.PI / 180;
    const landR = r * 0.3 * landProgress;
    const x = cx + (r * 0.4 + landR) * Math.cos(rad);
    const y = cy + (r * 0.4 + landR) * Math.sin(rad);
    const size = 30 * landProgress;
    ctx.fillStyle = `rgba(100, 150, 50, ${landProgress})`;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // Arrow indicators
  for (const angle of [30, 150, 210, 330]) {
    const rad = angle * Math.PI / 180;
    const arrowR = r * 0.6;
    const x = cx + arrowR * Math.cos(rad);
    const y = cy + arrowR * Math.sin(rad);
    const poleY = y < cy ? -1 : 1;
    ctx.fillStyle = "rgba(255, 50, 50, 0.8)";
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 10, y + 20 * poleY);
    ctx.lineTo(x + 10, y + 20 * poleY);
    ctx.closePath();
    ctx.fill();
  }

  // "OCEANS SURGE" curved
  const textProgress = clamp((progress - 0.1) / 0.3, 0, 1);
  if (textProgress > 0) {
    ctx.save();
    ctx.globalAlpha = textProgress;
    ctx.font = "bold 56px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.teal;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const text = "OCEANS SURGE";
    for (let i = 0; i < text.length; i++) {
      const angle = -90 + i * 180 / text.length;
      const rad = angle * Math.PI / 180;
      const x = cx + r * 1.2 * Math.cos(rad);
      const y = cy + r * 1.2 * Math.sin(rad);
      ctx.fillText(text[i], x, y);
    }
    ctx.restore();
  }

  // "POLES"
  const polesProgress = clamp((progress - 0.4) / 0.3, 0, 1);
  if (polesProgress > 0) {
    ctx.save();
    ctx.globalAlpha = polesProgress;
    ctx.font = "bold 40px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.primary;
    ctx.textAlign = "center";
    ctx.fillText("POLES", cx, cy - r - 50);
    ctx.fillText("POLES", cx, cy + r + 70);
    ctx.restore();
  }

  // "CONTINENTS RISE"
  const continentsProgress = clamp((progress - 0.6) / 0.3, 0, 1);
  if (continentsProgress > 0) {
    ctx.save();
    ctx.globalAlpha = continentsProgress;
    ctx.font = "italic 28px 'Libre Baskerville', serif";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.fillText("CONTINENTS RISE", cx, cy + r + 120);
    ctx.restore();
  }
}

// ========== SCENE 5: MAGNETIC ==========
function drawMagneticScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;
  const earthR = Math.min(CONFIG.width, CONFIG.height) * 0.2;

  ctx.fillStyle = "rgb(20, 20, 40)";
  ctx.beginPath();
  ctx.arc(cx, cy, earthR, 0, Math.PI * 2);
  ctx.fill();

  // Magnetic field lines (decaying)
  const fieldStrength = 1 - easeInCubic(progress);
  const numLoops = 12;
  for (let i = 0; i < numLoops; i++) {
    const angle = i * 2 * Math.PI / numLoops;
    const loopR = earthR * 1.5 * fieldStrength;
    if (loopR < earthR) continue;

    const alpha = 0.8 * fieldStrength;
    ctx.strokeStyle = `rgba(232, 168, 56, ${alpha})`;
    ctx.lineWidth = 2;

    for (let a = 0; a < 180; a += 5) {
      const rad = a * Math.PI / 180;
      const x1 = cx + loopR * Math.cos(rad) * Math.cos(angle);
      const y1 = cy + loopR * Math.sin(rad) * 0.5;
      const x2 = cx + loopR * Math.cos(rad + 0.087) * Math.cos(angle);
      const y2 = cy + loopR * Math.sin(rad + 0.087) * 0.5;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
  }

  // Solar particles (increasing)
  const particleRate = progress * 200;
  for (let i = 0; i < particleRate; i++) {
    const pSeed = SEED + i * 10 + Math.floor(t * 1000);
    const angle = seededRandom(pSeed) * 2 * Math.PI;
    const dist = earthR + seededRandom(pSeed + 1) * 300;
    let x = cx + dist * Math.cos(angle);
    let y = cy + dist * Math.sin(angle) * 0.5;

    x += (cx - x) * progress * 0.1;
    y += (cy - y) * progress * 0.1;

    const alpha = seededRandom(pSeed + 2);
    ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
    ctx.beginPath();
    ctx.arc(x, y, 2, 0, Math.PI * 2);
    ctx.fill();

    if (dist < earthR + 50) {
      const sparkAlpha = 1 - progress;
      ctx.fillStyle = `rgba(255, 50, 0, ${sparkAlpha})`;
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Atmosphere fading
  const atmoAlpha = 0.6 * fieldStrength;
  for (let r = earthR; r < earthR + 40; r += 2) {
    const a = atmoAlpha * (1 - (r - earthR) / 40);
    ctx.strokeStyle = `rgba(0, 180, 216, ${a})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // "MAGNETIC FIELD" fading
  if (fieldStrength > 0) {
    ctx.save();
    ctx.globalAlpha = fieldStrength;
    ctx.font = "bold 48px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.fillText("MAGNETIC FIELD", cx, cy - earthR - 70);
    ctx.restore();
  }

  // "COLLAPSES" impact
  const collapseProgress = clamp((progress - 0.3) / 0.2, 0, 1);
  if (collapseProgress > 0) {
    ctx.save();
    ctx.globalAlpha = collapseProgress;
    ctx.font = "bold 72px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.red;
    ctx.textAlign = "center";
    ctx.fillText("COLLAPSES", cx, cy - earthR - 70);
    ctx.restore();

    if (collapseProgress < 0.3) {
      const flashAlpha = 0.8 * (1 - collapseProgress / 0.3);
      ctx.fillStyle = `rgba(255, 50, 0, ${flashAlpha})`;
      ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);
    }
  }

  // Radiation counter
  const radProgress = clamp((progress - 0.5) / 0.3, 0, 1);
  if (radProgress > 0) {
    ctx.save();
    ctx.globalAlpha = radProgress;
    ctx.font = "bold 36px 'Space Mono', monospace";
    ctx.fillStyle = CONFIG.colors.red;
    ctx.textAlign = "left";
    const val = Math.floor(10000 * progress);
    ctx.fillText(`RADIATION: ${val.toLocaleString()}/s`, 50, 80);
    ctx.restore();
  }
}

// ========== SCENE 6: TEMPERATURE ==========
function drawTemperatureScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  // Left background (red gradient)
  for (let x = 0; x < cx; x++) {
    const p = x / cx;
    const r = lerp(50, 100, p);
    const g = lerp(10, 0, p);
    ctx.strokeStyle = `rgb(${r}, ${g}, 10)`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, CONFIG.height);
    ctx.stroke();
  }

  // Right background (blue gradient)
  for (let x = cx; x < CONFIG.width; x++) {
    const p = (x - cx) / (CONFIG.width - cx);
    const g = lerp(10, 30, p);
    const b = lerp(50, 100, p);
    ctx.strokeStyle = `rgb(10, ${g}, ${b})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, CONFIG.height);
    ctx.stroke();
  }

  // Thermometers
  const thermW = 80;
  const thermH = 500;
  const thermY = cy - thermH / 2;
  const leftX = cx - 300;
  const rightX = cx + 220;

  // Day mercury (rising)
  const dayProgress = easeOutExpo(progress);
  const mercuryHDay = thermH * 0.9 * dayProgress;
  const mercuryYDay = thermY + thermH - mercuryHDay;

  ctx.fillStyle = "rgba(255, 50, 0, 1)";
  drawRoundedRect(ctx, leftX, mercuryYDay, thermW, thermH - (mercuryYDay - thermY), thermW / 2);
  ctx.fill();

  // Glass crack (day)
  if (dayProgress > 0.8) {
    const crackProgress = (dayProgress - 0.8) / 0.2;
    for (let i = 0; i < 5 * crackProgress; i++) {
      const crackX = leftX + thermW / 2 + (seededRandom(SEED + i) - 0.5) * 20;
      const crackY = thermY + seededRandom(SEED + i + 10) * thermH * 0.3;
      ctx.strokeStyle = "rgba(255, 255, 255, 0.8)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(crackX, crackY);
      ctx.lineTo(crackX + (seededRandom(SEED + i + 20) - 0.5) * 60, crackY - 20);
      ctx.stroke();
    }
  }

  // Night mercury (falling)
  const nightProgress = easeOutExpo(progress);
  const mercuryHNight = thermH * 0.9 * (1 - nightProgress);
  const mercuryYNight = thermY + thermH - mercuryHNight;

  ctx.fillStyle = "rgba(0, 100, 255, 1)";
  drawRoundedRect(ctx, rightX, mercuryYNight, thermW, thermH - (mercuryYNight - thermY), thermW / 2);
  ctx.fill();

  // Frost (night)
  if (nightProgress > 0.7) {
    const frostProgress = (nightProgress - 0.7) / 0.3;
    for (let i = 0; i < 20 * frostProgress; i++) {
      const fx = rightX + seededRandom(SEED + i + 100) * thermW;
      const fy = thermY + thermH - seededRandom(SEED + i + 200) * thermH * 0.5;
      const fh = seededRandom(SEED + i + 300) * 30;
      ctx.strokeStyle = "rgba(150, 200, 255, 0.8)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(fx, fy);
      ctx.lineTo(fx + (seededRandom(SEED + i + 400) - 0.5) * 10, fy - fh);
      ctx.stroke();
    }
  }

  // Temperature numbers
  const dayTemp = Math.floor(100 * dayProgress);
  const nightTemp = Math.floor(-100 * nightProgress);

  ctx.font = "bold 64px 'Space Mono', monospace";
  ctx.fillStyle = "rgba(255, 200, 0, 1)";
  ctx.textAlign = "center";
  ctx.fillText(`+${dayTemp}°C`, leftX + thermW / 2, thermY - 80);

  ctx.fillStyle = "rgba(0, 200, 255, 1)";
  ctx.fillText(`${nightTemp}°C`, rightX + thermW / 2, thermY - 80);

  // "BEYOND SURVIVAL"
  const survivalProgress = clamp((progress - 0.5) / 0.3, 0, 1);
  if (survivalProgress > 0) {
    ctx.save();
    ctx.globalAlpha = survivalProgress;
    ctx.font = "italic 48px 'Libre Baskerville', serif";
    ctx.fillStyle = CONFIG.colors.primary;
    ctx.textAlign = "center";
    ctx.fillText("BEYOND SURVIVAL", cx, cy + 150);
    ctx.restore();
  }

  // Labels
  ctx.font = "24px 'Libre Baskerville', serif";
  ctx.fillStyle = "rgba(200, 200, 200, 1)";
  ctx.textAlign = "center";
  ctx.fillText("ETERNAL DAY", leftX + thermW / 2, thermY + thermH + 50);
  ctx.fillText("ETERNAL NIGHT", rightX + thermW / 2, thermY + thermH + 50);
}

// ========== SCENE 7: LIFE ==========
function drawLifeScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  ctx.fillStyle = "rgb(5, 10, 20)";
  ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);

  const ventX = cx;
  const ventY = cy + 100;
  const ventW = 60;
  const ventH = 200;

  // Vent chimney
  ctx.fillStyle = "rgb(40, 30, 20)";
  drawRoundedRect(ctx, ventX - ventW/2, ventY - ventH, ventW, ventH, ventW/2);
  ctx.fill();

  // Vent plume
  for (let y = 0; y < ventH; y++) {
    const p = y / ventH;
    const plumeW = ventW * (1 + p * 2);
    const alpha = 0.6 * (1 - p) * progress;
    const r = lerp(0, 232, p);
    const g = lerp(180, 168, p);
    const b = lerp(216, 56, p);
    ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
    ctx.beginPath();
    ctx.ellipse(ventX, ventY - y, plumeW/2, 10, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  // Microbes
  for (let i = 0; i < 30; i++) {
    const mSeed = SEED + i * 50;
    const angle = seededRandom(mSeed) * 2 * Math.PI;
    const dist = 50 + seededRandom(mSeed + 1) * 150;
    let mx = ventX + dist * Math.cos(angle);
    let my = ventY - dist * Math.sin(angle) * 0.5;

    mx += Math.sin(t * 3 + i) * 5;
    my += Math.cos(t * 2 + i) * 3;

    const alpha = 0.8 + 0.2 * Math.sin(t * 2 + i);
    ctx.fillStyle = `rgba(232, 168, 56, ${alpha})`;
    ctx.beginPath();
    ctx.ellipse(mx, my, 6, 1.5, seededRandom(mSeed + 2) * 2 * Math.PI, 0, Math.PI * 2);
    ctx.fill();
  }

  // Bioluminescence
  for (let i = 0; i < 10; i++) {
    const pulse = (Math.sin(t * 1.5 + i) + 1) / 2;
    const px = ventX + (seededRandom(SEED + i * 100) - 0.5) * 200;
    const py = ventY - seededRandom(SEED + i * 100 + 1) * 150;
    const size = 5 + pulse * 15;
    ctx.fillStyle = `rgba(232, 168, 56, ${pulse * 0.4})`;
    ctx.beginPath();
    ctx.arc(px, py, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // "EXTREMOPHILES" floating
  const extremProgress = clamp((progress - 0.1) / 0.3, 0, 1);
  if (extremProgress > 0) {
    ctx.save();
    ctx.globalAlpha = extremProgress;
    ctx.font = "bold 56px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const fx = cx + Math.sin(t * 0.5) * 50;
    const fy = cy - 100 + Math.cos(t * 0.3) * 30;
    ctx.fillText("EXTREMOPHILES", fx, fy);
    ctx.restore();
  }

  // "ENDURE"
  const endureProgress = clamp((progress - 0.4) / 0.3, 0, 1);
  if (endureProgress > 0) {
    ctx.save();
    ctx.globalAlpha = endureProgress;
    ctx.font = "italic 40px 'Libre Baskerville', serif";
    ctx.fillStyle = CONFIG.colors.primary;
    ctx.textAlign = "center";
    ctx.fillText("ENDURE", cx, cy + 50);
    ctx.restore();
  }

  // "LIFE FINDS A WAY"
  const wayProgress = clamp((progress - 0.7) / 0.3, 0, 1);
  if (wayProgress > 0) {
    ctx.save();
    ctx.globalAlpha = wayProgress;
    ctx.font = "bold 64px Cinzel, serif";
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.fillText("LIFE FINDS A WAY", cx, cy + 150);
    ctx.restore();
  }
}

// ========== SCENE 8: OUTRO ==========
function drawOutroScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  drawStarfield(ctx, CONFIG.width, CONFIG.height, SEED, 0.001);

  const earthR = Math.min(CONFIG.width, CONFIG.height) * 0.25;
  const scale = lerp(1.0, 0.7, progress);
  const scaledR = earthR * scale;

  // Earth
  for (let r = scaledR; r > 0; r -= 2) {
    const p = r / scaledR;
    const alpha = 0.8 * (1 - p * 0.5);
    ctx.strokeStyle = `rgba(${30 * p}, ${80 * p}, ${150 * p}, ${alpha})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Fade to starfield
  const fadeAlpha = progress;
  ctx.fillStyle = `rgba(10, 10, 26, ${fadeAlpha})`;
  ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);

  // Channel logo
  const logoProgress = clamp((progress - 0.1) / 0.4, 0, 1);
  const logoEasing = easeOutBack(logoProgress);
  if (logoProgress > 0) {
    const logoR = 80 * logoEasing;
    ctx.fillStyle = `rgba(20, 20, 40, ${logoEasing})`;
    ctx.strokeStyle = `rgba(232, 168, 56, ${logoEasing})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(cx, cy - 50, logoR, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.save();
    ctx.globalAlpha = logoEasing;
    ctx.font = `bold ${36 * logoEasing}px Cinzel, serif`;
    ctx.fillStyle = CONFIG.colors.gold;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("WHAT IF", cx, cy - 50);
    ctx.restore();
  }

  // Subscribe button
  const btnProgress = clamp((progress - 0.4) / 0.3, 0, 1);
  const btnEasing = easeOutCubic(btnProgress);
  if (btnProgress > 0) {
    const btnW = 300;
    const btnH = 60;
    const btnX = cx - btnW / 2;
    const btnY = cy + 100;

    // Gradient
    const grad = ctx.createLinearGradient(btnX, btnY, btnX + btnW, btnY + btnH);
    grad.addColorStop(0, "rgba(232, 168, 56, 1)");
    grad.addColorStop(1, "rgba(255, 204, 0, 1)");
    ctx.globalAlpha = btnEasing;
    ctx.fillStyle = grad;
    drawRoundedRect(ctx, btnX, btnY, btnW, btnH, 30);
    ctx.fill();

    // Shimmer
    const shimmerX = btnX + ((btnW + 100) * ((t * 0.5) % 1)) - 50;
    if (shimmerX > btnX && shimmerX < btnX + btnW) {
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.fillRect(shimmerX, btnY, 20, btnH);
    }

    // Button text
    ctx.font = "bold 28px Cinzel, serif";
    ctx.fillStyle = "rgba(0, 0, 0, 1)";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("SUBSCRIBE", cx, btnY + btnH / 2);
  }

  // "What If... continues"
  const continuesProgress = clamp((progress - 0.6) / 0.3, 0, 1);
  if (continuesProgress > 0) {
    ctx.save();
    ctx.globalAlpha = continuesProgress;
    ctx.font = "italic 32px 'Libre Baskerville', serif";
    ctx.fillStyle = CONFIG.colors.primary;
    ctx.textAlign = "center";
    ctx.fillText("What If... continues", cx, cy + 200);
    ctx.restore();
  }

  // Channel URL
  const urlProgress = clamp((progress - 0.7) / 0.3, 0, 1);
  if (urlProgress > 0) {
    ctx.save();
    ctx.globalAlpha = urlProgress;
    ctx.font = "20px 'Space Mono', monospace";
    ctx.fillStyle = CONFIG.colors.teal;
    ctx.textAlign = "center";
    ctx.fillText("youtube.com/@whatif", cx, cy + 250);
    ctx.restore();
  }
}

function drawScene(ctx, sceneId, beat, progress, t) {
  switch (sceneId) {
    case "hook":
      drawHookScene(ctx, beat, progress, t);
      break;
    case "day_night":
      drawDayNightScene(ctx, beat, progress, t);
      break;
    case "atmosphere":
      drawAtmosphereScene(ctx, beat, progress, t);
      break;
    case "oceans":
      drawOceansScene(ctx, beat, progress, t);
      break;
    case "magnetic":
      drawMagneticScene(ctx, beat, progress, t);
      break;
    case "temperature":
      drawTemperatureScene(ctx, beat, progress, t);
      break;
    case "life":
      drawLifeScene(ctx, beat, progress, t);
      break;
    case "outro":
      drawOutroScene(ctx, beat, progress, t);
      break;
  }
}

function drawFrame(t, frameIndex) {
  ctx.fillStyle = CONFIG.backgroundColor;
  ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);

  ctx.save();
  ctx.scale(SCALE, SCALE);

  const activeScenes = SCENES.filter(scene => {
    if (TARGET_SCENE && scene.id !== TARGET_SCENE) return false;
    const beats = getBeatsForScene(scene.id);
    return beats.some(b => t >= b.start && t < b.end);
  });

  for (const scene of activeScenes) {
    const beats = getBeatsForScene(scene.id);
    for (const beat of beats) {
      const progress = clamp((t - beat.start) / (beat.end - beat.start), 0, 1);
      drawScene(ctx, scene.id, beat, progress, t);
    }
  }

  drawDebugInfo(ctx, t, frameIndex);

  // Grain and vignette (applied after scaling back)
  ctx.restore();
  drawGrainOverlay(ctx, WIDTH, HEIGHT, CONFIG.grain, SEED);
  drawVignette(ctx, WIDTH, HEIGHT, CONFIG.vignette);
}

async function main() {
  const startTime = Date.now();

  for (let frame = 0; frame < TOTAL_FRAMES; frame++) {
    const t = FROM + frame / FPS;
    drawFrame(t, frame);

    const ext = USE_JPG ? "jpg" : "png";
    const filename = `frame_${String(frame).padStart(6, "0")}.${ext}`;
    const filepath = path.join(OUT_DIR, filename);

    const buffer = USE_JPG
      ? canvas.toBuffer("image/jpeg", { quality: 0.9 })
      : canvas.toBuffer("image/png");

    fs.writeFileSync(filepath, buffer);

    if (frame % 30 === 0 || frame === TOTAL_FRAMES - 1) {
      const pct = ((frame + 1) / TOTAL_FRAMES * 100).toFixed(1);
      console.log(`[render] ${pct}% (${frame + 1}/${TOTAL_FRAMES})`);
    }
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`[render] Done in ${elapsed}s. Frames saved to ${OUT_DIR}`);
}

main().catch(err => {
  console.error("[render] Error:", err);
  process.exit(1);
});