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
      <span class="gallery-page-opening__curtain-sky"></span>
      <span class="gallery-page-opening__sheen"></span>
    </div>
    <div class="gallery-page-opening__curtain is-lower">
      <span class="gallery-page-opening__weave"></span>
      <span class="gallery-page-opening__motif"></span>
      <span class="gallery-page-opening__curtain-sky"></span>
      <span class="gallery-page-opening__sheen"></span>
    </div>

    <div class="gallery-page-opening__stage">
      <canvas
        ref="effectsCanvas"
        class="gallery-page-opening__effects"></canvas>
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';
import GalleryOpeningRenderer from './galleryOpeningRenderer';

const OPENING_DURATION = 1900;

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
      visible: !motionPreference.isReducedMotionEnabled(),
    };
  },
  created() {
    this.openingRenderer = null;
    this.playGeneration = 0;
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
      this.startRenderer();
      this.scheduleHide();
    }
  },
  beforeDestroy() {
    this.playGeneration += 1;
    this.clearHideTimer();
    this.stopRenderer();
  },
  methods: {
    clearHideTimer() {
      if (this.hideTimer === null) {
        return;
      }
      window.clearTimeout(this.hideTimer);
      this.hideTimer = null;
    },
    scheduleHide(generation = this.playGeneration) {
      this.clearHideTimer();
      this.hideTimer = window.setTimeout(() => {
        if (generation !== this.playGeneration) {
          return;
        }
        this.stopRenderer();
        this.visible = false;
        this.hideTimer = null;
      }, OPENING_DURATION);
    },
    startRenderer() {
      this.stopRenderer();
      const { effectsCanvas } = this.$refs;
      if (!effectsCanvas) {
        return;
      }
      this.openingRenderer = new GalleryOpeningRenderer(
        effectsCanvas,
        { duration: OPENING_DURATION },
      );
      this.openingRenderer.start();
    },
    stopRenderer() {
      if (!this.openingRenderer) {
        return;
      }
      this.openingRenderer.stop();
      this.openingRenderer = null;
    },
    play() {
      const generation = this.playGeneration + 1;
      this.playGeneration = generation;
      this.clearHideTimer();
      this.stopRenderer();
      if (motionPreference.isReducedMotionEnabled()) {
        this.visible = false;
        return;
      }
      this.animationKey += 1;
      this.visible = true;
      this.$nextTick(() => {
        if (generation !== this.playGeneration || !this.visible) {
          return;
        }
        this.startRenderer();
        this.scheduleHide(generation);
      });
    },
  },
};
</script>

<style scoped lang="scss">
.gallery-page-opening {
  --opening-angle: 14deg;
  --opening-curtain-shade: color-mix(in srgb, var(--color-surface-card) 84%, var(--color-accent));
  --opening-curtain-meteor: color-mix(in srgb, #fff 42%, var(--color-accent-strong));
  --opening-constellation-line: color-mix(in srgb, #fff 16%, var(--color-accent));
  --opening-sheen-peak: 0.28;
  --opening-sky-y-from: -0.35%;
  --opening-sky-y-to: -1.1%;
  --opening-motif-y-from: -0.25%;
  --opening-motif-y-to: -0.9%;
  --opening-space-deep: color-mix(in srgb, #070d1b 76%, var(--color-accent));
  --opening-space-mid: color-mix(in srgb, #14213b 70%, var(--color-accent-strong));
  --opening-star-cool: color-mix(in srgb, #f5fbff 82%, var(--color-accent));
  --opening-star-warm: color-mix(in srgb, #ffe7b0 66%, var(--color-accent-strong));
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
  z-index: 2;
  inset: -8%;
  content: "";
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
}

.gallery-page-opening::before {
  background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.26), var(--color-theme-glow-strong) 18%, var(--color-theme-glow) 42%, transparent 72%);
  filter: blur(36px) saturate(0.78);
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
    radial-gradient(ellipse at 16% 12%, color-mix(in srgb, var(--color-theme-glow-start) 78%, transparent), transparent 42%),
    radial-gradient(ellipse at 84% 78%, color-mix(in srgb, var(--color-theme-glow-end) 72%, transparent), transparent 44%),
    radial-gradient(ellipse at 52% 46%, color-mix(in srgb, var(--color-accent) 16%, transparent), transparent 54%),
    linear-gradient(145deg, var(--opening-space-deep), var(--opening-space-mid) 52%, color-mix(in srgb, var(--opening-space-deep) 88%, #02050d));
  box-shadow:
    inset 0 0 180px rgba(1, 4, 14, 0.42),
    inset 0 0 92px color-mix(in srgb, var(--color-theme-glow) 18%, transparent),
    inset 0 0 0 1px rgba(255, 255, 255, 0.12);
  filter:
    saturate(0.96)
    brightness(0.98)
    drop-shadow(0 0 36px var(--color-theme-glow));
  transform-origin: center;
  will-change: clip-path, transform;
}

.gallery-page-opening__curtain.is-upper {
  --opening-motif-y-from: -0.25%;
  --opening-motif-y-to: -0.9%;
  --opening-sky-y-from: -0.35%;
  --opening-sky-y-to: -1.1%;
  clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 20%);
  transform: translate3d(0, 0, 0);
  animation: diagonal-curtain-upper 1520ms linear 80ms both;
}

.gallery-page-opening__curtain.is-lower {
  --opening-motif-y-from: 0.3%;
  --opening-motif-y-to: 1%;
  --opening-sky-y-from: 0.4%;
  --opening-sky-y-to: 1.2%;
  clip-path: polygon(0 20%, 12.5% 25%, 25% 30%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%);
  transform: translate3d(0, 0, 0);
  animation: diagonal-curtain-lower 1520ms linear 80ms both;
}

.gallery-page-opening__weave,
.gallery-page-opening__motif,
.gallery-page-opening__curtain-sky,
.gallery-page-opening__sheen {
  position: absolute;
  inset: 0;
}

.gallery-page-opening__weave {
  opacity: 0.12;
  background:
    repeating-linear-gradient(97deg, transparent 0 36px, rgba(255, 255, 255, 0.08) 37px, transparent 40px),
    repeating-linear-gradient(-8deg, transparent 0 22px, color-mix(in srgb, var(--opening-curtain-shade) 10%, transparent) 23px, transparent 27px),
    linear-gradient(145deg, color-mix(in srgb, var(--opening-space-mid) 18%, transparent), transparent 46%, color-mix(in srgb, var(--opening-space-deep) 24%, transparent));
  filter: blur(0.3px) saturate(0.78);
  mix-blend-mode: soft-light;
}

.gallery-page-opening__motif {
  inset: 1%;
  background:
    radial-gradient(circle at 8% 72%, color-mix(in srgb, var(--opening-star-cool) 62%, transparent) 0 0.8px, transparent 2px),
    radial-gradient(circle at 29% 48%, color-mix(in srgb, var(--opening-star-warm) 52%, transparent) 0 0.7px, transparent 1.9px),
    radial-gradient(circle at 48% 14%, color-mix(in srgb, var(--opening-star-cool) 72%, transparent) 0 1px, transparent 2.3px),
    radial-gradient(circle at 59% 86%, color-mix(in srgb, var(--opening-star-cool) 48%, transparent) 0 0.7px, transparent 1.8px),
    radial-gradient(circle at 78% 36%, color-mix(in srgb, var(--opening-star-warm) 58%, transparent) 0 0.9px, transparent 2.1px),
    radial-gradient(circle at 94% 18%, color-mix(in srgb, var(--opening-star-cool) 56%, transparent) 0 0.8px, transparent 2px);
  opacity: 0.24;
  filter: drop-shadow(0 0 5px color-mix(in srgb, var(--color-theme-glow) 64%, transparent));
  mix-blend-mode: screen;
  -webkit-mask-image: radial-gradient(ellipse at center, #000 10%, rgba(0, 0, 0, 0.9) 68%, transparent 100%);
  mask-image: radial-gradient(ellipse at center, #000 10%, rgba(0, 0, 0, 0.9) 68%, transparent 100%);
  animation: diagonal-curtain-motif-drift 1900ms ease-out both;
}

.gallery-page-opening__motif::before,
.gallery-page-opening__motif::after {
  position: absolute;
  width: 34%;
  height: 31%;
  background:
    radial-gradient(circle at 5% 58%, var(--opening-star-cool) 0 1.1px, transparent 2.4px),
    radial-gradient(circle at 21% 28%, var(--opening-star-warm) 0 0.8px, transparent 2px),
    radial-gradient(circle at 40% 52%, var(--opening-star-cool) 0 1.35px, transparent 2.7px),
    radial-gradient(circle at 57% 18%, color-mix(in srgb, var(--opening-star-cool) 76%, transparent) 0 0.9px, transparent 2.1px),
    radial-gradient(circle at 73% 44%, var(--opening-star-warm) 0 1.1px, transparent 2.4px),
    radial-gradient(circle at 93% 26%, var(--opening-star-cool) 0 0.85px, transparent 2.1px),
    linear-gradient(30deg, transparent 49.3%, var(--opening-constellation-line) 49.72% 50.28%, transparent 50.7%) 4% 25% / 21% 42% no-repeat,
    linear-gradient(128deg, transparent 49.3%, var(--opening-constellation-line) 49.72% 50.28%, transparent 50.7%) 19% 26% / 25% 30% no-repeat,
    linear-gradient(35deg, transparent 49.3%, var(--opening-constellation-line) 49.72% 50.28%, transparent 50.7%) 38% 15% / 23% 40% no-repeat,
    linear-gradient(126deg, transparent 49.3%, var(--opening-constellation-line) 49.72% 50.28%, transparent 50.7%) 55% 17% / 22% 30% no-repeat,
    linear-gradient(74deg, transparent 49.3%, var(--opening-constellation-line) 49.72% 50.28%, transparent 50.7%) 71% 22% / 24% 26% no-repeat;
  content: "";
}

.gallery-page-opening__motif::before {
  top: 8%;
  left: 6%;
}

.gallery-page-opening__motif::after {
  right: 4%;
  bottom: 9%;
  opacity: 0.74;
  transform: rotate(168deg) scale(0.88);
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__motif::before {
  transform: translate3d(4%, 8%, 0) rotate(-8deg);
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__motif::after {
  transform: rotate(154deg) scale(0.82);
}

.gallery-page-opening__curtain-sky {
  inset: -8%;
  overflow: hidden;
  background:
    radial-gradient(circle, color-mix(in srgb, var(--opening-star-cool) 54%, transparent) 0 0.55px, transparent 1.45px) 7px 11px / 113px 97px,
    radial-gradient(circle, color-mix(in srgb, var(--opening-star-warm) 58%, transparent) 0 0.78px, transparent 1.8px) 31px 43px / 181px 157px,
    radial-gradient(circle, color-mix(in srgb, var(--opening-star-cool) 72%, transparent) 0 1.05px, transparent 2.25px) 79px 19px / 263px 223px,
    radial-gradient(circle, #fff 0 1.25px, color-mix(in srgb, var(--opening-star-cool) 56%, transparent) 1.5px 3.6px, transparent 6.4px) 151px 73px / 397px 331px;
  opacity: 0.3;
  mix-blend-mode: screen;
  -webkit-mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0, 0, 0, 0.9) 68%, transparent 100%);
  mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0, 0, 0, 0.9) 68%, transparent 100%);
  animation: diagonal-curtain-sky-drift 1900ms ease-out both;
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__curtain-sky {
  background-position: 41px 23px, 13px 61px, 107px 37px, 229px 111px;
}

.gallery-page-opening__curtain-sky::before,
.gallery-page-opening__curtain-sky::after {
  position: absolute;
  left: -26vw;
  width: clamp(92px, 12vw, 190px);
  height: 1px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--color-theme-glow-strong) 58%, var(--opening-curtain-meteor));
  box-shadow:
    0 0 7px var(--color-theme-glow),
    0 0 14px color-mix(in srgb, var(--color-theme-glow-strong) 54%, transparent);
  content: "";
  opacity: 0;
  transform: rotate(var(--opening-angle)) translateX(-12vw) scaleX(0.48);
  transform-origin: right center;
  animation: diagonal-curtain-meteor 1380ms ease-out 180ms both;
}

.gallery-page-opening__curtain-sky::before {
  top: 22%;
}

.gallery-page-opening__curtain-sky::after {
  display: none;
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__curtain-sky::before {
  top: 68%;
  animation-delay: 360ms;
}

.gallery-page-opening__sheen {
  inset: -10%;
  background:
    radial-gradient(ellipse at 48% 18%, rgba(255, 255, 255, 0.18), transparent 54%),
    linear-gradient(112deg, transparent 18%, rgba(255, 255, 255, 0.11) 42%, transparent 66%);
  filter: blur(16px);
  opacity: 0.26;
  mix-blend-mode: screen;
  animation: diagonal-curtain-sheen 1520ms ease-out both;
}

.gallery-page-opening__stage {
  position: absolute;
  z-index: 3;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  isolation: isolate;
}

.gallery-page-opening__effects {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  mix-blend-mode: screen;
}

@keyframes diagonal-opening-lifetime {
  0%, 97% { visibility: visible; }
  100% { visibility: hidden; }
}

@keyframes diagonal-curtain-upper {
  0%, 16% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 20%); transform: translate3d(0, 0, 0); }
  24% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 17%); transform: translate3d(0, 0, 0); }
  32% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 28%, 12.5% 18%, 0 6%); transform: translate3d(0, 0, 0); }
  40% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 32%, 25% 21%, 12.5% 7%, 0 -7%); transform: translate3d(0, 0, 0); }
  48% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 44%, 50% 35%, 37.5% 23%, 25% 9%, 12.5% -6%, 0 -14%); transform: translate3d(0, 0, 0); }
  56% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 48%, 62.5% 38%, 50% 25%, 37.5% 11%, 25% -3%, 12.5% -9%, 0 -14%); transform: translate3d(0, 0, 0); }
  64% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 52%, 75% 41%, 62.5% 28%, 50% 14%, 37.5% 2%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, 0, 0); }
  72% { clip-path: polygon(0 0, 100% 0, 100% 56%, 87.5% 44%, 75% 29%, 62.5% 15%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, 0, 0); }
  82% { clip-path: polygon(0 0, 100% 0, 100% 26%, 87.5% 21%, 75% 16%, 62.5% 11%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, -28%, 0); }
  100% { clip-path: polygon(0 0, 100% 0, 100% 26%, 87.5% 21%, 75% 16%, 62.5% 11%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, -108%, 0); }
}

@keyframes diagonal-curtain-lower {
  0%, 16% { clip-path: polygon(0 20%, 12.5% 25%, 25% 30%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  24% { clip-path: polygon(0 23%, 12.5% 25%, 25% 30%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  32% { clip-path: polygon(0 34%, 12.5% 32%, 25% 32%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  40% { clip-path: polygon(0 47%, 12.5% 43%, 25% 39%, 37.5% 38%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  48% { clip-path: polygon(0 54%, 12.5% 56%, 25% 51%, 37.5% 47%, 50% 45%, 62.5% 46%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  56% { clip-path: polygon(0 54%, 12.5% 59%, 25% 63%, 37.5% 59%, 50% 55%, 62.5% 52%, 75% 52%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  64% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 68%, 50% 66%, 62.5% 62%, 75% 59%, 87.5% 58%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  72% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 75%, 75% 71%, 87.5% 66%, 100% 64%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  82% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 79%, 75% 84%, 87.5% 89%, 100% 94%, 100% 100%, 0 100%); transform: translate3d(0, 28%, 0); }
  100% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 79%, 75% 84%, 87.5% 89%, 100% 94%, 100% 100%, 0 100%); transform: translate3d(0, 108%, 0); }
}

@keyframes diagonal-curtain-upper-portrait {
  0%, 26% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 20%); transform: translate3d(0, 0, 0); }
  32% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 17%); transform: translate3d(0, 0, 0); }
  38% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 28%, 12.5% 18%, 0 6%); transform: translate3d(0, 0, 0); }
  44% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 32%, 25% 21%, 12.5% 7%, 0 -7%); transform: translate3d(0, 0, 0); }
  50% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 44%, 50% 35%, 37.5% 23%, 25% 9%, 12.5% -6%, 0 -14%); transform: translate3d(0, 0, 0); }
  56% { clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 48%, 62.5% 38%, 50% 25%, 37.5% 11%, 25% -3%, 12.5% -9%, 0 -14%); transform: translate3d(0, 0, 0); }
  62% { clip-path: polygon(0 0, 100% 0, 100% 56%, 87.5% 44%, 75% 29%, 62.5% 15%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, 0, 0); }
  72% { clip-path: polygon(0 0, 100% 0, 100% 26%, 87.5% 21%, 75% 16%, 62.5% 11%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, -28%, 0); }
  86%, 100% { clip-path: polygon(0 0, 100% 0, 100% 26%, 87.5% 21%, 75% 16%, 62.5% 11%, 50% 6%, 37.5% 1%, 25% -4%, 12.5% -9%, 0 -14%); transform: translate3d(0, -108%, 0); }
}

@keyframes diagonal-curtain-lower-portrait {
  0%, 26% { clip-path: polygon(0 20%, 12.5% 25%, 25% 30%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  32% { clip-path: polygon(0 23%, 12.5% 25%, 25% 30%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  38% { clip-path: polygon(0 34%, 12.5% 32%, 25% 32%, 37.5% 35%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  44% { clip-path: polygon(0 47%, 12.5% 43%, 25% 39%, 37.5% 38%, 50% 40%, 62.5% 45%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  50% { clip-path: polygon(0 54%, 12.5% 56%, 25% 51%, 37.5% 47%, 50% 45%, 62.5% 46%, 75% 50%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  56% { clip-path: polygon(0 54%, 12.5% 59%, 25% 63%, 37.5% 59%, 50% 55%, 62.5% 52%, 75% 52%, 87.5% 55%, 100% 60%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  62% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 75%, 75% 71%, 87.5% 66%, 100% 64%, 100% 100%, 0 100%); transform: translate3d(0, 0, 0); }
  72% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 79%, 75% 84%, 87.5% 89%, 100% 94%, 100% 100%, 0 100%); transform: translate3d(0, 28%, 0); }
  86%, 100% { clip-path: polygon(0 54%, 12.5% 59%, 25% 64%, 37.5% 69%, 50% 74%, 62.5% 79%, 75% 84%, 87.5% 89%, 100% 94%, 100% 100%, 0 100%); transform: translate3d(0, 108%, 0); }
}

@keyframes diagonal-curtain-sky-drift {
  0% { opacity: 0.3; transform: translate3d(-0.6%, var(--opening-sky-y-from), 0) scale(1); }
  42% { opacity: 0.44; transform: translate3d(0.1%, 0, 0) scale(1.008); }
  74% { opacity: 0.3; transform: translate3d(0.7%, var(--opening-sky-y-to), 0) scale(1.014); }
  100% { opacity: 0.12; transform: translate3d(1.2%, var(--opening-sky-y-to), 0) scale(1.018); }
}

@keyframes diagonal-curtain-meteor {
  0%, 10% { opacity: 0; transform: rotate(var(--opening-angle)) translateX(-12vw) scaleX(0.48); }
  30% { opacity: 0.34; }
  72% { opacity: 0.16; }
  100% { opacity: 0; transform: rotate(var(--opening-angle)) translateX(152vw) scaleX(1); }
}

@keyframes diagonal-curtain-motif-drift {
  0% { opacity: 0.18; transform: translate3d(-0.4%, var(--opening-motif-y-from), 0) scale(1); }
  36% { opacity: 0.3; transform: translate3d(0.2%, 0, 0) scale(1.005); }
  58% { opacity: 0.34; transform: translate3d(0.7%, var(--opening-motif-y-to), 0) scale(1.01); }
  100% { opacity: 0.1; transform: translate3d(1.4%, var(--opening-motif-y-to), 0) scale(1.016); }
}

@keyframes diagonal-curtain-sheen {
  0%, 10% { opacity: 0.1; transform: translate3d(-3%, 0, 0) scale(0.96); }
  48% { opacity: var(--opening-sheen-peak); transform: translate3d(2%, 0, 0) scale(1.02); }
  100% { opacity: 0.06; transform: translate3d(6%, 0, 0) scale(1.08); }
}

@keyframes diagonal-opening-bloom {
  0%, 10% { opacity: 0; transform: scale(0.82); }
  34% { opacity: 0.28; transform: scale(0.96); }
  68% { opacity: 0.12; transform: scale(1.08); }
  100% { opacity: 0; transform: scale(1.2); }
}

@keyframes diagonal-opening-soft-focus {
  0%, 14% { opacity: 0.2; }
  72% { opacity: 0.08; }
  100% { opacity: 0; }
}

@media screen and (orientation: portrait) {
  .gallery-page-opening {
    --opening-angle: 41deg;
    --opening-sheen-peak: 0.22;
  }

  .gallery-page-opening__curtain.is-upper {
    animation-name: diagonal-curtain-upper-portrait;
  }

  .gallery-page-opening__curtain.is-lower {
    animation-name: diagonal-curtain-lower-portrait;
  }

}

@media screen and (max-width: 760px) {
  .gallery-page-opening__curtain {
    filter:
      saturate(0.94)
      brightness(0.97)
      drop-shadow(0 0 28px var(--color-theme-glow));
  }

  .gallery-page-opening__motif::after {
    display: none;
  }

  .gallery-page-opening__sheen {
    filter: blur(12px);
  }
}

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
