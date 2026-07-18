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
  --opening-curtain-base: color-mix(in srgb, var(--color-surface-card) 72%, var(--color-accent));
  --opening-curtain-mid: color-mix(in srgb, var(--color-surface-card) 66%, var(--color-accent-strong));
  --opening-curtain-shade: color-mix(in srgb, var(--color-surface-card) 84%, var(--color-accent));
  --opening-curtain-star: color-mix(in srgb, #fff 62%, var(--color-accent));
  --opening-curtain-meteor: color-mix(in srgb, #fff 42%, var(--color-accent-strong));
  --opening-pattern: color-mix(in srgb, var(--color-surface-card) 22%, var(--color-accent));
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
    radial-gradient(circle at 48% 34%, rgba(255, 255, 255, 0.28), transparent 52%),
    radial-gradient(circle at 82% 72%, var(--color-theme-glow), transparent 46%),
    linear-gradient(145deg, color-mix(in srgb, var(--opening-curtain-base) 92%, transparent), color-mix(in srgb, var(--opening-curtain-mid) 84%, transparent)),
    var(--color-accent-soft-gradient);
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
  will-change: clip-path, transform;
}

.gallery-page-opening__curtain.is-upper {
  clip-path: polygon(0 0, 100% 0, 100% 60%, 87.5% 55%, 75% 50%, 62.5% 45%, 50% 40%, 37.5% 35%, 25% 30%, 12.5% 25%, 0 20%);
  transform: translate3d(0, 0, 0);
  animation: diagonal-curtain-upper 1520ms linear 80ms both;
}

.gallery-page-opening__curtain.is-lower {
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
  opacity: 0.22;
  background:
    repeating-linear-gradient(96deg, transparent 0 29px, rgba(255, 255, 255, 0.24) 30px, transparent 34px),
    repeating-linear-gradient(-7deg, transparent 0 14px, color-mix(in srgb, var(--opening-curtain-shade) 13%, transparent) 15px, transparent 20px),
    var(--color-accent-gradient-diagonal);
  filter: blur(0.45px) saturate(0.72);
  mix-blend-mode: soft-light;
}

.gallery-page-opening__motif {
  inset: 3%;
  background:
    radial-gradient(circle at 9% 18%, var(--opening-curtain-star) 0 1.2px, transparent 2.5px),
    radial-gradient(circle at 27% 66%, color-mix(in srgb, var(--opening-curtain-star) 72%, transparent) 0 1px, transparent 2.2px),
    radial-gradient(circle at 43% 31%, color-mix(in srgb, #fff 54%, var(--color-accent)) 0 1.4px, transparent 2.7px),
    radial-gradient(circle at 61% 76%, color-mix(in srgb, var(--opening-curtain-star) 68%, transparent) 0 0.9px, transparent 2px),
    radial-gradient(circle at 78% 24%, color-mix(in srgb, #fff 42%, var(--color-accent-strong)) 0 1.3px, transparent 2.6px),
    radial-gradient(circle at 91% 58%, color-mix(in srgb, var(--opening-curtain-star) 64%, transparent) 0 1px, transparent 2.2px),
    linear-gradient(31deg, transparent 49.55%, color-mix(in srgb, var(--opening-pattern) 17%, transparent) 49.8% 50.2%, transparent 50.45%) 8% 16% / 46% 42% no-repeat,
    linear-gradient(-37deg, transparent 49.58%, color-mix(in srgb, #fff 12%, transparent) 49.84% 50.16%, transparent 50.42%) 68% 58% / 38% 36% no-repeat;
  opacity: 0.22;
  filter: blur(0.35px);
  -webkit-mask-image: radial-gradient(ellipse at center, #000 12%, rgba(0, 0, 0, 0.82) 58%, transparent 94%);
  mask-image: radial-gradient(ellipse at center, #000 12%, rgba(0, 0, 0, 0.82) 58%, transparent 94%);
  animation: diagonal-curtain-motif-drift 1900ms ease-out both;
}

.gallery-page-opening__curtain-sky {
  inset: -8%;
  overflow: hidden;
  background:
    radial-gradient(circle, var(--opening-curtain-star) 0 0.8px, transparent 1.8px) 0 0 / 92px 86px,
    radial-gradient(circle, color-mix(in srgb, var(--opening-curtain-star) 72%, transparent) 0 1px, transparent 2px) 19px 31px / 137px 121px,
    radial-gradient(circle, color-mix(in srgb, var(--color-accent) 58%, transparent) 0 1.2px, transparent 2.5px) 47px 12px / 181px 156px;
  filter: blur(0.2px) drop-shadow(0 0 7px var(--color-theme-glow));
  opacity: 0.18;
  mix-blend-mode: screen;
  -webkit-mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0, 0, 0, 0.82) 64%, transparent 98%);
  mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0, 0, 0, 0.82) 64%, transparent 98%);
  animation: diagonal-curtain-sky-drift 1900ms ease-out both;
}

.gallery-page-opening__curtain-sky::before,
.gallery-page-opening__curtain-sky::after {
  position: absolute;
  left: -32vw;
  width: clamp(90px, 14vw, 220px);
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--color-theme-glow-strong) 58%, var(--opening-curtain-meteor));
  box-shadow:
    0 0 8px var(--color-theme-glow),
    0 0 18px color-mix(in srgb, var(--color-theme-glow-strong) 68%, transparent);
  content: "";
  opacity: 0;
  transform: rotate(var(--opening-angle)) translateX(-12vw) scaleX(0.48);
  transform-origin: right center;
  animation: diagonal-curtain-meteor 1460ms ease-out 140ms both;
}

.gallery-page-opening__curtain-sky::before {
  top: 26%;
}

.gallery-page-opening__curtain-sky::after {
  top: 68%;
  width: clamp(68px, 10vw, 160px);
  animation-delay: 330ms;
  animation-duration: 1320ms;
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__curtain-sky::before {
  top: 18%;
  animation-delay: 250ms;
}

.gallery-page-opening__curtain.is-lower .gallery-page-opening__curtain-sky::after {
  top: 62%;
  animation-delay: 430ms;
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
  0% { opacity: 0.16; transform: translate3d(-1.2%, -0.4%, 0) scale(1); }
  48% { opacity: 0.3; transform: translate3d(0.7%, 0.4%, 0) scale(1.015); }
  100% { opacity: 0.08; transform: translate3d(1.8%, 1%, 0) scale(1.03); }
}

@keyframes diagonal-curtain-meteor {
  0%, 10% { opacity: 0; transform: rotate(var(--opening-angle)) translateX(-12vw) scaleX(0.48); }
  28% { opacity: 0.18; }
  72% { opacity: 0.1; }
  100% { opacity: 0; transform: rotate(var(--opening-angle)) translateX(152vw) scaleX(1); }
}

@keyframes diagonal-curtain-motif-drift {
  0% { opacity: 0.12; transform: translate3d(-0.6%, -0.3%, 0) scale(1); }
  48% { opacity: 0.22; transform: translate3d(0.35%, 0.2%, 0) scale(1.008); }
  100% { opacity: 0.08; transform: translate3d(0.9%, 0.55%, 0) scale(1.016); }
}

@keyframes diagonal-curtain-sheen {
  0%, 10% { opacity: 0.22; transform: translate3d(-3%, 0, 0) scale(0.96); }
  48% { opacity: 0.48; transform: translate3d(2%, 0, 0) scale(1.02); }
  100% { opacity: 0.12; transform: translate3d(6%, 0, 0) scale(1.08); }
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
  }

  .gallery-page-opening__curtain.is-upper {
    animation-name: diagonal-curtain-upper-portrait;
  }

  .gallery-page-opening__curtain.is-lower {
    animation-name: diagonal-curtain-lower-portrait;
  }

  .gallery-page-opening__motif {
    opacity: 0.18;
  }

}

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
