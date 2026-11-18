#!/usr/bin/env node
import { program } from "commander";
import { CONFIG, BEATS, SCENES, getBeat, getScene, lerp, clamp, easeOutCubic, easeInCubic, easeOutExpo, stagger, seededRandom } from "./data.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

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

function createCanvas(w, h) {
  const { createCanvas } = await import("canvas");
  return createCanvas(w, h);
}

function drawFrame(t, frameIndex) {
  ctx.fillStyle = CONFIG.backgroundColor;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

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

  ctx.restore();
}

function drawScene(ctx, sceneId, beat, progress, globalTime) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  switch (sceneId) {
    case "hook":
      drawHookScene(ctx, beat, progress, globalTime);
      break;
    case "problem":
      drawProblemScene(ctx, beat, progress, globalTime);
      break;
    case "solution":
      drawSolutionScene(ctx, beat, progress, globalTime);
      break;
    case "proof":
      drawProofScene(ctx, beat, progress, globalTime);
      break;
    case "cta":
      drawCTAScene(ctx, beat, progress, globalTime);
      break;
    case "outro":
      drawOutroScene(ctx, beat, progress, globalTime);
      break;
  }
}

function drawHookScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const easing = easeOutExpo(progress);
  const y = lerp(cy + 200, cy, easing);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.font = "bold 96px Satoshi, sans-serif";
  ctx.fillStyle = CONFIG.colors.primary;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const text = "Nobody drew this.";
  ctx.fillText(text, cx, y);

  ctx.restore();
}

function drawProblemScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const easing = easeOutCubic(progress);
  const y = lerp(cy + 150, cy, easing);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.font = "400 48px Inter, sans-serif";
  ctx.fillStyle = CONFIG.colors.secondary;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const lines = [
    "Most teams lose hours",
    "every week to manual work."
  ];

  lines.forEach((line, i) => {
    ctx.fillText(line, cx, y + i * 70);
  });

  ctx.restore();
}

function drawSolutionScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const easing = easeOutCubic(progress);
  const scale = lerp(0.5, 1.0, easing);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.translate(cx, cy);
  ctx.scale(scale, scale);

  ctx.font = "bold 72px Satoshi, sans-serif";
  ctx.fillStyle = CONFIG.colors.accent;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const gradient = ctx.createLinearGradient(-200, 0, 200, 0);
  gradient.addColorStop(0, CONFIG.colors.accentGradient[0]);
  gradient.addColorStop(1, CONFIG.colors.accentGradient[1]);
  ctx.fillStyle = gradient;

  ctx.fillText("Meet Flow.", 0, 0);

  ctx.restore();
}

function drawProofScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const cardCount = 3;
  const cardWidth = 300;
  const cardHeight = 400;
  const spacing = 40;
  const totalWidth = cardCount * cardWidth + (cardCount - 1) * spacing;
  const startX = cx - totalWidth / 2;

  for (let i = 0; i < cardCount; i++) {
    const cardProgress = clamp((progress - i * 0.1) / 0.8, 0, 1);
    const easing = easeOutExpo(cardProgress);
    const x = startX + i * (cardWidth + spacing);
    const y = cy - cardHeight / 2;
    const scale = lerp(0.8, 1.0, easing);
    const opacity = easing;

    ctx.save();
    ctx.globalAlpha = opacity;
    ctx.translate(x + cardWidth / 2, y + cardHeight / 2);
    ctx.scale(scale, scale);
    ctx.translate(-cardWidth / 2, -cardHeight / 2);

    ctx.fillStyle = CONFIG.colors.surface;
    roundRect(ctx, 0, 0, cardWidth, cardHeight, 16);
    ctx.fill();

    ctx.fillStyle = CONFIG.colors.primary;
    ctx.font = "bold 24px Satoshi, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`Feature ${i + 1}`, cardWidth / 2, 60);

    ctx.font = "300 20px Inter, sans-serif";
    ctx.fillStyle = CONFIG.colors.textMuted;
    ctx.fillText("Automated workflow", cardWidth / 2, 100);
    ctx.fillText("Real-time sync", cardWidth / 2, 140);
    ctx.fillText("Zero config", cardWidth / 2, 180);

    ctx.restore();
  }
}

function drawCTAScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const easing = easeOutCubic(progress);
  const y = lerp(cy + 100, cy, easing);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;

  const btnWidth = 320;
  const btnHeight = 72;
  const btnX = cx - btnWidth / 2;
  const btnY = y - btnHeight / 2;

  const gradient = ctx.createLinearGradient(btnX, btnY, btnX + btnWidth, btnY + btnHeight);
  gradient.addColorStop(0, CONFIG.colors.accentGradient[0]);
  gradient.addColorStop(1, CONFIG.colors.accentGradient[1]);

  ctx.fillStyle = gradient;
  roundRect(ctx, btnX, btnY, btnWidth, btnHeight, 36);
  ctx.fill();

  ctx.font = "bold 28px Satoshi, sans-serif";
  ctx.fillStyle = "#000000";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("Start Free Today", cx, y);

  ctx.restore();
}

function drawOutroScene(ctx, beat, progress, t) {
  const cx = CONFIG.width / 2;
  const cy = CONFIG.height / 2;

  const easing = easeOutCubic(progress);
  const opacity = easing;

  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.font = "bold 48px Satoshi, sans-serif";
  ctx.fillStyle = CONFIG.colors.primary;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  ctx.fillText("Flow", cx, cy - 40);

  ctx.font = "300 24px Inter, sans-serif";
  ctx.fillStyle = CONFIG.colors.textMuted;
  ctx.fillText("flow.example.com", cx, cy + 30);

  ctx.restore();
}

function drawDebugInfo(ctx, t, frameIndex) {
  ctx.save();
  ctx.font = "12px monospace";
  ctx.fillStyle = "rgba(255,255,255,0.5)";
  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.fillText(`t=${t.toFixed(3)}s frame=${frameIndex} seed=${SEED}`, 10, 10);
  ctx.fillText(`${WIDTH}x${HEIGHT} @ ${FPS}fps scale=${SCALE}`, 10, 30);
  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
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

async function main() {
  const { createCanvas } = await import("canvas");
  global.createCanvas = createCanvas;

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