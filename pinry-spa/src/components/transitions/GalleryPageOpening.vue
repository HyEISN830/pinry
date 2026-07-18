<template>
  <div
    v-if="visible"
    :key="animationKey"
    class="gallery-page-opening"
    aria-hidden="true"
    @touchmove.prevent
    @wheel.prevent>
    <div class="gallery-page-opening__curtain is-upper">
      <span class="gallery-page-opening__weave"></span>
      <span class="gallery-page-opening__motif"></span>
      <span class="gallery-page-opening__sheen"></span>
    </div>
    <div class="gallery-page-opening__curtain is-lower">
      <span class="gallery-page-opening__weave"></span>
      <span class="gallery-page-opening__motif"></span>
      <span class="gallery-page-opening__sheen"></span>
    </div>

    <div class="gallery-page-opening__stage">
      <span class="gallery-page-opening__afterglow is-wide"></span>
      <span class="gallery-page-opening__afterglow is-core"></span>
      <span class="gallery-page-opening__comet">
        <span class="gallery-page-opening__comet-tail is-soft"></span>
        <span class="gallery-page-opening__comet-tail is-bright"></span>
        <span class="gallery-page-opening__comet-head"></span>
      </span>
      <span
        v-for="particle in particles"
        :key="particle.id"
        class="gallery-page-opening__particle"
        :style="particle.style"></span>
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';

const OPENING_DURATION = 1900;

const PARTICLES = [
  ['one', '15%', '26%', '-18px', '-5vw', '-8vh', '120ms', '7px'],
  ['two', '24%', '29.6%', '14px', '4vw', '7vh', '190ms', '10px'],
  ['three', '33%', '33.2%', '-24px', '-7vw', '-10vh', '250ms', '6px'],
  ['four', '42%', '36.8%', '20px', '6vw', '9vh', '310ms', '9px'],
  ['five', '51%', '40.4%', '-12px', '-4vw', '-12vh', '370ms', '8px'],
  ['six', '59%', '43.6%', '24px', '8vw', '11vh', '420ms', '11px'],
  ['seven', '68%', '47.2%', '-20px', '-6vw', '-9vh', '470ms', '7px'],
  ['eight', '77%', '50.8%', '16px', '5vw', '8vh', '520ms', '9px'],
  ['nine', '86%', '54.4%', '-14px', '-5vw', '-7vh', '570ms', '6px'],
  ['ten', '92%', '56.8%', '22px', '7vw', '9vh', '610ms', '8px'],
  ['eleven', '37%', '34.8%', '4px', '-2vw', '12vh', '280ms', '5px'],
  ['twelve', '63%', '45.2%', '-4px', '3vw', '-13vh', '450ms', '6px'],
].map(([id, path, top, offset, driftX, driftY, delay, size]) => ({
  id,
  style: {
    '--particle-delay': delay,
    '--particle-drift-x': driftX,
    '--particle-drift-y': driftY,
    '--particle-offset': offset,
    '--particle-path': path,
    '--particle-size': size,
    '--particle-top': top,
  },
}));

export default {
  name: 'GalleryPageOpening',
  props: {
    routeKey: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      animationKey: 0,
      hideTimer: null,
      particles: PARTICLES,
      visible: !motionPreference.isReducedMotionEnabled(),
    };
  },
  watch: {
    routeKey(next, previous) {
      if (!previous || next === previous) {
        return;
      }
      this.play();
    },
  },
  mounted() {
    if (this.visible) {
      this.scheduleHide();
    }
  },
  beforeDestroy() {
    this.clearHideTimer();
  },
  methods: {
    clearHideTimer() {
      if (this.hideTimer === null) {
        return;
      }
      window.clearTimeout(this.hideTimer);
      this.hideTimer = null;
    },
    scheduleHide() {
      this.hideTimer = window.setTimeout(() => {
        this.visible = false;
        this.hideTimer = null;
      }, OPENING_DURATION);
    },
    play() {
      this.clearHideTimer();
      if (motionPreference.isReducedMotionEnabled()) {
        this.visible = false;
        return;
      }
      this.animationKey += 1;
      this.visible = true;
      this.scheduleHide();
    },
  },
};
</script>

<style scoped lang="scss">
.gallery-page-opening {
  --opening-angle: 14deg;
  --opening-curtain-base: color-mix(in srgb, #fff 68%, var(--color-accent));
  --opening-curtain-mid: color-mix(in srgb, #fff 58%, var(--color-accent));
  --opening-curtain-shade: color-mix(in srgb, #fff 45%, var(--color-accent-strong));
  --opening-pattern: color-mix(in srgb, #fff 18%, var(--color-accent));
  position: fixed;
  z-index: var(--z-page-opening, 1000);
  inset: 0;
  isolation: isolate;
  overflow: hidden;
  pointer-events: auto;
  touch-action: none;
  animation: diagonal-opening-lifetime 1900ms linear both;
}

.gallery-page-opening::before,
.gallery-page-opening::after {
  position: absolute;
  z-index: 5;
  inset: -8%;
  content: "";
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
}

.gallery-page-opening::before {
  background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.46), var(--color-theme-glow-strong) 20%, var(--color-theme-glow) 44%, transparent 72%);
  filter: blur(30px) saturate(0.82);
  animation: diagonal-opening-bloom 1780ms cubic-bezier(0.2, 0.7, 0.26, 1) both;
}

.gallery-page-opening::after {
  background: radial-gradient(ellipse at center, color-mix(in srgb, var(--color-theme-glow) 20%, transparent), transparent 66%);
  -webkit-backdrop-filter: blur(1.8px) saturate(0.86) brightness(1.05);
  backdrop-filter: blur(1.8px) saturate(0.86) brightness(1.05);
  animation: diagonal-opening-soft-focus 1900ms ease-out both;
}

.gallery-page-opening__curtain {
  position: absolute;
  z-index: 1;
  inset: -12%;
  width: auto;
  height: auto;
  overflow: hidden;
  background:
    radial-gradient(circle at 48% 34%, rgba(255, 255, 255, 0.42), transparent 52%),
    linear-gradient(145deg, var(--opening-curtain-base), color-mix(in srgb, var(--opening-curtain-mid) 72%, transparent)),
    color-mix(in srgb, var(--color-surface-card) 58%, transparent);
  box-shadow:
    inset 0 0 140px color-mix(in srgb, var(--color-theme-glow) 30%, transparent),
    inset 0 0 0 1px rgba(255, 255, 255, 0.32);
  -webkit-backdrop-filter: blur(12px) saturate(0.86) brightness(1.08);
  backdrop-filter: blur(12px) saturate(0.86) brightness(1.08);
  filter:
    saturate(0.82)
    brightness(1.06)
    drop-shadow(0 0 42px var(--color-theme-glow));
  transform-origin: center;
  will-change: transform;
}

.gallery-page-opening__curtain.is-upper {
  clip-path: polygon(0 0, 100% 0, 100% 60%, 100% 60%, 0 20%);
  transform: translate3d(0, 0, 0);
  animation: diagonal-curtain-upper 1900ms linear both;
}

.gallery-page-opening__curtain.is-lower {
  clip-path: polygon(0 20%, 0 20%, 100% 60%, 100% 100%, 0 100%);
  transform: translate3d(0, 0, 0);
  animation: diagonal-curtain-lower 1900ms linear both;
}

.gallery-page-opening__weave,
.gallery-page-opening__motif,
.gallery-page-opening__sheen {
  position: absolute;
  inset: 0;
}

.gallery-page-opening__weave {
  opacity: 0.3;
  background:
    repeating-linear-gradient(92deg, transparent 0 17px, rgba(255, 255, 255, 0.3) 18px, transparent 21px),
    repeating-linear-gradient(0deg, transparent 0 6px, color-mix(in srgb, var(--opening-curtain-shade) 16%, transparent) 7px, transparent 10px),
    var(--color-accent-gradient-diagonal);
  filter: blur(0.45px) saturate(0.72);
  mix-blend-mode: soft-light;
}

.gallery-page-opening__motif {
  inset: 4%;
  background:
    radial-gradient(circle at 50% 50%, transparent 0 31px, color-mix(in srgb, #fff 44%, transparent) 32px 33px, transparent 34px) 0 0 / 112px 112px,
    linear-gradient(45deg, transparent 46%, color-mix(in srgb, var(--opening-pattern) 30%, transparent) 48% 52%, transparent 54%) 0 0 / 86px 86px,
    linear-gradient(-45deg, transparent 46%, color-mix(in srgb, #fff 24%, transparent) 48% 52%, transparent 54%) 0 0 / 86px 86px;
  opacity: 0.48;
  filter: blur(0.6px);
  -webkit-mask-image: radial-gradient(ellipse at center, #000 12%, rgba(0, 0, 0, 0.82) 58%, transparent 94%);
  mask-image: radial-gradient(ellipse at center, #000 12%, rgba(0, 0, 0, 0.82) 58%, transparent 94%);
}

.gallery-page-opening__sheen {
  inset: -10%;
  background:
    radial-gradient(ellipse at 48% 18%, rgba(255, 255, 255, 0.38), transparent 54%),
    linear-gradient(112deg, transparent 18%, rgba(255, 255, 255, 0.28) 42%, transparent 66%);
  filter: blur(20px);
  opacity: 0.48;
  mix-blend-mode: screen;
  animation: diagonal-curtain-sheen 1520ms ease-out both;
}

.gallery-page-opening__stage {
  position: absolute;
  z-index: 3;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  filter: saturate(0.86) brightness(1.04);
}

.gallery-page-opening__afterglow {
  position: absolute;
  z-index: 0;
  top: 40%;
  left: 50%;
  height: clamp(54px, 6vw, 100px);
  border-radius: 50%;
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
  transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(0.08);
}

.gallery-page-opening__afterglow.is-wide {
  width: 180vmax;
  height: clamp(54px, 6vw, 100px);
  background: linear-gradient(90deg, transparent, var(--color-theme-glow) 30%, rgba(255, 255, 255, 0.5) 50%, var(--color-theme-glow) 70%, transparent);
  filter: blur(26px);
  animation: diagonal-afterglow-wide 1840ms ease-out both;
}

.gallery-page-opening__afterglow.is-core {
  width: 180vmax;
  height: clamp(12px, 1.3vw, 22px);
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.78), color-mix(in srgb, #fff 44%, var(--color-accent)), rgba(255, 255, 255, 0.78), transparent);
  box-shadow:
    0 0 32px rgba(255, 255, 255, 0.68),
    0 0 74px var(--color-theme-glow-strong),
    0 0 120px var(--color-theme-glow);
  filter: blur(9px);
  animation: diagonal-afterglow-core 1720ms ease-out 80ms both;
}

.gallery-page-opening__comet {
  position: absolute;
  z-index: 3;
  top: 40%;
  left: 50%;
  width: 0;
  height: 0;
  transform: rotate(var(--opening-angle)) translateX(-72vmax);
  transform-origin: center;
  will-change: transform;
  animation: diagonal-comet-flight 1520ms linear 80ms both;
}

.gallery-page-opening__comet-tail {
  position: absolute;
  top: 50%;
  right: 0;
  border-radius: 999px;
  opacity: 0;
  transform: translateY(-50%);
  transform-origin: right center;
  mix-blend-mode: screen;
}

.gallery-page-opening__comet-tail.is-soft {
  width: clamp(220px, 36vw, 620px);
  height: clamp(40px, 4.8vw, 78px);
  background: linear-gradient(90deg, transparent, var(--color-theme-glow) 44%, rgba(255, 255, 255, 0.52));
  box-shadow: 0 0 46px var(--color-theme-glow-strong);
  filter: blur(18px);
  animation: diagonal-comet-tail-soft 1660ms ease-out 100ms both;
}

.gallery-page-opening__comet-tail.is-bright {
  width: clamp(145px, 24vw, 410px);
  height: clamp(9px, 1.2vw, 19px);
  background: linear-gradient(90deg, transparent, color-mix(in srgb, #fff 34%, var(--color-accent)) 50%, #fff);
  box-shadow:
    0 0 20px rgba(255, 255, 255, 0.74),
    0 0 52px var(--color-theme-glow-strong);
  filter: blur(4px);
  animation: diagonal-comet-tail-bright 1540ms ease-out 100ms both;
}

.gallery-page-opening__comet-head {
  position: absolute;
  top: 50%;
  left: 0;
  width: clamp(30px, 3.6vw, 56px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0 16%, color-mix(in srgb, #fff 56%, var(--color-accent)) 30%, var(--color-theme-glow-strong) 54%, transparent 76%);
  box-shadow:
    0 0 28px rgba(255, 255, 255, 0.94),
    0 0 72px var(--color-theme-glow-strong),
    0 0 132px var(--color-theme-glow);
  filter: blur(1.5px) saturate(0.84);
  opacity: 0;
  transform: translate(-50%, -50%);
  mix-blend-mode: screen;
  animation: diagonal-comet-head 1560ms ease-out 60ms both;
}

.gallery-page-opening__comet-head::before,
.gallery-page-opening__comet-head::after {
  position: absolute;
  top: 50%;
  left: 50%;
  content: "";
  pointer-events: none;
  transform: translate(-50%, -50%);
}

.gallery-page-opening__comet-head::before {
  width: 28%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #fff;
  box-shadow:
    0 0 12px #fff,
    0 0 28px color-mix(in srgb, #fff 48%, var(--color-accent));
}

.gallery-page-opening__comet-head::after {
  width: 190%;
  height: 190%;
  background:
    linear-gradient(90deg, transparent 47%, rgba(255, 255, 255, 0.72) 49% 51%, transparent 53%),
    linear-gradient(0deg, transparent 47%, rgba(255, 255, 255, 0.72) 49% 51%, transparent 53%);
  filter: blur(1px);
  opacity: 0.72;
}

.gallery-page-opening__particle {
  position: absolute;
  z-index: 2;
  top: calc(var(--particle-top) - var(--particle-offset));
  left: var(--particle-path);
  width: var(--particle-size);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0 18%, color-mix(in srgb, #fff 50%, var(--color-accent)) 30%, var(--color-theme-glow-strong) 52%, transparent 76%);
  box-shadow:
    0 0 14px rgba(255, 255, 255, 0.76),
    0 0 36px var(--color-theme-glow-strong),
    0 0 66px var(--color-theme-glow);
  filter: blur(0.8px) saturate(0.82);
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
  transform: translate(-50%, -50%) rotate(var(--opening-angle)) scale(0.12);
  animation: diagonal-particle-drift 1160ms cubic-bezier(0.18, 0.66, 0.3, 1) var(--particle-delay) both;
}

.gallery-page-opening__particle::before,
.gallery-page-opening__particle::after {
  position: absolute;
  top: 50%;
  left: 50%;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 0 16px var(--color-theme-glow-strong);
  content: "";
  transform: translate(-50%, -50%);
}

.gallery-page-opening__particle::before {
  width: 190%;
  height: 1px;
}

.gallery-page-opening__particle::after {
  width: 1px;
  height: 190%;
}

@keyframes diagonal-opening-lifetime {
  0%, 97% { visibility: visible; }
  100% { visibility: hidden; }
}

@keyframes diagonal-curtain-upper {
  0%, 8% {
    clip-path: polygon(0 0, 100% 0, 100% 60%, 100% 60%, 0 20%);
    transform: translate3d(0, 0, 0);
    animation-timing-function: cubic-bezier(0.32, 0.04, 0.22, 1);
  }
  24% { clip-path: polygon(0 0, 100% 0, 100% 60%, 100% 60%, 0 20%); transform: translate3d(0, 0, 0); }
  42% { clip-path: polygon(0 0, 100% 0, 100% 60%, 56% 38%, 0 12%); transform: translate3d(0, -5%, 0); }
  58% { clip-path: polygon(0 0, 100% 0, 100% 52%, 82% 48%, 0 3%); transform: translate3d(0, -22%, 0); }
  78%, 100% { clip-path: polygon(0 0, 100% 0, 100% 40%, 100% 40%, 0 0); transform: translate3d(0, -104%, 0); }
}

@keyframes diagonal-curtain-lower {
  0%, 8% {
    clip-path: polygon(0 20%, 0 20%, 100% 60%, 100% 100%, 0 100%);
    transform: translate3d(0, 0, 0);
    animation-timing-function: cubic-bezier(0.32, 0.04, 0.22, 1);
  }
  24% { clip-path: polygon(0 20%, 0 20%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  42% { clip-path: polygon(0 28%, 56% 44%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 5%, 0); }
  58% { clip-path: polygon(0 37%, 82% 55%, 100% 68%, 100% 100%, 0 100%); transform: translate3d(0, 22%, 0); }
  78%, 100% { clip-path: polygon(0 52%, 100% 76%, 100% 76%, 100% 100%, 0 100%); transform: translate3d(0, 104%, 0); }
}

@keyframes diagonal-curtain-sheen {
  0%, 10% { opacity: 0.22; transform: translate3d(-3%, 0, 0) scale(0.96); }
  48% { opacity: 0.48; transform: translate3d(2%, 0, 0) scale(1.02); }
  100% { opacity: 0.12; transform: translate3d(6%, 0, 0) scale(1.08); }
}

@keyframes diagonal-comet-flight {
  0%, 8% { transform: rotate(var(--opening-angle)) translateX(-72vmax); }
  82%, 100% { transform: rotate(var(--opening-angle)) translateX(72vmax); }
}

@keyframes diagonal-comet-head {
  0%, 6% { opacity: 0; transform: translate(-50%, -50%) scale(0.4); }
  18% { opacity: 0.94; transform: translate(-50%, -50%) scale(1); }
  72% { opacity: 0.84; transform: translate(-50%, -50%) scale(0.92); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(0.56); }
}

@keyframes diagonal-comet-tail-soft {
  0%, 8% { opacity: 0; transform: translateY(-50%) scaleX(0.12); }
  24% { opacity: 0.7; transform: translateY(-50%) scaleX(0.8); }
  68% { opacity: 0.48; transform: translateY(-50%) scaleX(1); }
  100% { opacity: 0; transform: translateY(-50%) scaleX(1.08); }
}

@keyframes diagonal-comet-tail-bright {
  0%, 10% { opacity: 0; transform: translateY(-50%) scaleX(0.08); }
  25% { opacity: 0.9; transform: translateY(-50%) scaleX(0.78); }
  65% { opacity: 0.62; transform: translateY(-50%) scaleX(1); }
  100% { opacity: 0; transform: translateY(-50%) scaleX(1.04); }
}

@keyframes diagonal-afterglow-wide {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(0.06); }
  42% { opacity: 0.42; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(0.72); }
  72% { opacity: 0.2; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(1.12); }
}

@keyframes diagonal-afterglow-core {
  0%, 16% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(0.04); }
  40% { opacity: 0.62; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(0.7); }
  72% { opacity: 0.26; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scaleX(1.06); }
}

@keyframes diagonal-particle-drift {
  0%, 8% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--opening-angle)) scale(0.12); }
  24% { opacity: 0.86; transform: translate(-50%, -50%) rotate(calc(var(--opening-angle) + 38deg)) scale(1.08); }
  70% {
    opacity: 0.48;
    transform: translate(calc(-50% + var(--particle-drift-x)), calc(-50% + var(--particle-drift-y))) rotate(calc(var(--opening-angle) + 102deg)) scale(0.72);
  }
  100% {
    opacity: 0;
    transform: translate(calc(-50% + var(--particle-drift-x)), calc(-50% + var(--particle-drift-y))) rotate(calc(var(--opening-angle) + 154deg)) scale(0.24);
  }
}

@keyframes diagonal-opening-bloom {
  0%, 10% { opacity: 0; transform: scale(0.82); }
  34% { opacity: 0.5; transform: scale(0.96); }
  68% { opacity: 0.24; transform: scale(1.08); }
  100% { opacity: 0; transform: scale(1.2); }
}

@keyframes diagonal-opening-soft-focus {
  0%, 14% { opacity: 0.34; }
  72% { opacity: 0.16; }
  100% { opacity: 0; }
}

@media screen and (orientation: portrait) {
  .gallery-page-opening {
    --opening-angle: 41deg;
  }

  .gallery-page-opening__comet-tail.is-soft {
    width: 72vw;
  }

  .gallery-page-opening__comet-tail.is-bright {
    width: 52vw;
  }

  .gallery-page-opening__afterglow.is-wide {
    width: 180vmax;
    height: 24vw;
  }

  .gallery-page-opening__afterglow.is-core {
    width: 180vmax;
    height: 7vw;
  }

  .gallery-page-opening__motif {
    opacity: 0.42;
  }

}

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
