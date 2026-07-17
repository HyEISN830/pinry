<template>
  <div
    v-if="visible"
    :key="animationKey"
    class="gallery-page-opening"
    aria-hidden="true"
    @touchmove.prevent
    @wheel.prevent>
    <div class="gallery-page-opening__curtain is-start">
      <span class="gallery-page-opening__weave"></span>
      <span class="gallery-page-opening__motif"></span>
      <span class="gallery-page-opening__sheen"></span>
      <span class="gallery-page-opening__edge"></span>
    </div>
    <div class="gallery-page-opening__curtain is-end">
      <span class="gallery-page-opening__weave"></span>
      <span class="gallery-page-opening__motif"></span>
      <span class="gallery-page-opening__sheen"></span>
      <span class="gallery-page-opening__edge"></span>
    </div>
    <div class="gallery-page-opening__stage">
      <span class="gallery-page-opening__halo"></span>
      <span class="gallery-page-opening__prism"></span>
      <span class="gallery-page-opening__beam is-primary"></span>
      <span class="gallery-page-opening__beam is-secondary"></span>
      <span class="gallery-page-opening__spark is-one"></span>
      <span class="gallery-page-opening__spark is-two"></span>
      <span class="gallery-page-opening__spark is-three"></span>
      <span class="gallery-page-opening__spark is-four"></span>
      <span class="gallery-page-opening__spark is-five"></span>
      <span class="gallery-page-opening__spark is-six"></span>
      <span class="gallery-page-opening__spark is-seven"></span>
      <span class="gallery-page-opening__spark is-eight"></span>
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';

const DESKTOP_OPENING_DURATION = 1040;
const MOBILE_OPENING_DURATION = 1500;
const PORTRAIT_QUERY = '(orientation: portrait)';

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
    openingDuration() {
      if (window.matchMedia && window.matchMedia(PORTRAIT_QUERY).matches) {
        return MOBILE_OPENING_DURATION;
      }
      return DESKTOP_OPENING_DURATION;
    },
    scheduleHide() {
      this.hideTimer = window.setTimeout(() => {
        this.visible = false;
        this.hideTimer = null;
      }, this.openingDuration());
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
  animation: gallery-opening-visibility 1040ms linear both;
}

.gallery-page-opening::before,
.gallery-page-opening::after {
  position: absolute;
  inset: -5%;
  content: "";
  opacity: 0;
  pointer-events: none;
}

.gallery-page-opening::before {
  z-index: 3;
  background:
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.46) 0 3%, var(--color-theme-glow-strong) 18%, var(--color-theme-glow) 38%, transparent 66%);
  filter: blur(28px) saturate(0.84);
  mix-blend-mode: screen;
  animation: gallery-post-bloom 1040ms cubic-bezier(0.22, 0.72, 0.26, 1) both;
}

.gallery-page-opening::after {
  z-index: 4;
  background: radial-gradient(circle at center, color-mix(in srgb, var(--color-theme-glow) 18%, transparent), transparent 62%);
  -webkit-backdrop-filter: blur(1.6px) saturate(0.84) brightness(1.06);
  backdrop-filter: blur(1.6px) saturate(0.84) brightness(1.06);
  mix-blend-mode: screen;
  animation: gallery-soft-focus 1040ms ease-out both;
}

.gallery-page-opening__curtain {
  position: absolute;
  z-index: 1;
  top: 0;
  bottom: 0;
  width: calc(50% + 2px);
  overflow: visible;
  background: transparent;
  filter:
    saturate(0.82)
    brightness(1.06)
    drop-shadow(0 0 30px var(--color-theme-glow));
  will-change: transform;
}

.gallery-page-opening__curtain::before {
  position: absolute;
  z-index: 0;
  inset: 0;
  background:
    radial-gradient(circle at 48% 34%, rgba(255, 255, 255, 0.42), transparent 52%),
    linear-gradient(145deg, var(--opening-curtain-base), color-mix(in srgb, var(--opening-curtain-mid) 72%, transparent)),
    color-mix(in srgb, var(--color-surface-card) 58%, transparent);
  box-shadow:
    inset 0 0 110px color-mix(in srgb, var(--color-theme-glow) 30%, transparent),
    inset 0 0 0 1px rgba(255, 255, 255, 0.34);
  -webkit-backdrop-filter: blur(12px) saturate(0.86) brightness(1.08);
  backdrop-filter: blur(12px) saturate(0.86) brightness(1.08);
  content: "";
}

.gallery-page-opening__curtain.is-start {
  left: 0;
  transform-origin: left center;
  animation: gallery-curtain-start 1040ms linear both;
}

.gallery-page-opening__curtain.is-start::before {
  -webkit-mask-image: linear-gradient(90deg, #000 0, #000 calc(100% - 54px), transparent 100%);
  mask-image: linear-gradient(90deg, #000 0, #000 calc(100% - 54px), transparent 100%);
}

.gallery-page-opening__curtain.is-end {
  right: 0;
  transform-origin: right center;
  animation: gallery-curtain-end 1040ms linear both;
}

.gallery-page-opening__curtain.is-end::before {
  -webkit-mask-image: linear-gradient(270deg, #000 0, #000 calc(100% - 54px), transparent 100%);
  mask-image: linear-gradient(270deg, #000 0, #000 calc(100% - 54px), transparent 100%);
}

.gallery-page-opening__weave {
  position: absolute;
  z-index: 1;
  inset: 0;
  opacity: 0.32;
  background:
    repeating-linear-gradient(92deg, transparent 0 17px, rgba(255, 255, 255, 0.32) 18px, transparent 21px),
    repeating-linear-gradient(0deg, transparent 0 6px, color-mix(in srgb, var(--opening-curtain-shade) 16%, transparent) 7px, transparent 10px),
    var(--color-accent-gradient-diagonal);
  filter: blur(0.35px) saturate(0.72);
  mix-blend-mode: soft-light;
}

.gallery-page-opening__motif {
  position: absolute;
  z-index: 1;
  inset: 5% 7%;
  border: 1px solid color-mix(in srgb, var(--opening-pattern) 38%, transparent);
  border-radius: 42% 58% 44% 56% / 54% 46% 58% 42%;
  background:
    radial-gradient(circle at 50% 50%, transparent 0 31px, color-mix(in srgb, #fff 48%, transparent) 32px 33px, transparent 34px) 0 0 / 112px 112px,
    linear-gradient(45deg, transparent 46%, color-mix(in srgb, var(--opening-pattern) 32%, transparent) 48% 52%, transparent 54%) 0 0 / 86px 86px,
    linear-gradient(-45deg, transparent 46%, color-mix(in srgb, #fff 28%, transparent) 48% 52%, transparent 54%) 0 0 / 86px 86px;
  box-shadow:
    inset 0 0 44px rgba(255, 255, 255, 0.18),
    0 0 34px color-mix(in srgb, var(--color-theme-glow) 26%, transparent);
  opacity: 0.52;
  filter: blur(0.55px);
  -webkit-mask-image: radial-gradient(ellipse at center, #000 14%, rgba(0, 0, 0, 0.84) 54%, transparent 92%);
  mask-image: radial-gradient(ellipse at center, #000 14%, rgba(0, 0, 0, 0.84) 54%, transparent 92%);
}

.is-end .gallery-page-opening__motif {
  transform: scaleX(-1);
}

.gallery-page-opening__sheen {
  position: absolute;
  z-index: 1;
  inset: -12%;
  background:
    radial-gradient(ellipse at 50% 18%, rgba(255, 255, 255, 0.4), transparent 52%),
    linear-gradient(112deg, transparent 18%, rgba(255, 255, 255, 0.3) 42%, transparent 66%);
  filter: blur(18px);
  opacity: 0.5;
  mix-blend-mode: screen;
  animation: gallery-curtain-sheen 820ms ease-out both;
}

.gallery-page-opening__edge {
  position: absolute;
  z-index: 2;
  top: 0;
  bottom: 0;
  width: 42px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.72), color-mix(in srgb, #fff 54%, var(--color-accent)), transparent);
  filter: blur(11px) saturate(0.82);
  box-shadow:
    0 0 28px rgba(255, 255, 255, 0.72),
    0 0 58px var(--color-theme-glow-strong),
    0 0 92px var(--color-theme-glow);
  opacity: 0.86;
  mix-blend-mode: screen;
}

.is-start .gallery-page-opening__edge {
  right: -19px;
}

.is-end .gallery-page-opening__edge {
  left: -19px;
  transform: scaleX(-1);
}

.gallery-page-opening__stage {
  position: absolute;
  z-index: 2;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  filter: saturate(0.86) brightness(1.04);
}

.gallery-page-opening__stage::before,
.gallery-page-opening__stage::after {
  position: absolute;
  z-index: 0;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  content: "";
  opacity: 0;
  mix-blend-mode: screen;
  transform: translate(-50%, -50%) scale(0.08);
}

.gallery-page-opening__stage::before {
  width: min(84vw, 1040px);
  aspect-ratio: 1.5;
  background: radial-gradient(ellipse, rgba(255, 255, 255, 0.52), var(--color-theme-glow-strong) 20%, var(--color-theme-glow) 42%, transparent 72%);
  filter: blur(34px);
  animation: gallery-stage-bloom 980ms cubic-bezier(0.2, 0.72, 0.26, 1) both;
}

.gallery-page-opening__stage::after {
  width: min(58vw, 760px);
  aspect-ratio: 1;
  border: 4px solid color-mix(in srgb, #fff 32%, var(--color-accent));
  box-shadow:
    0 0 34px rgba(255, 255, 255, 0.68),
    0 0 88px var(--color-theme-glow-strong),
    inset 0 0 62px var(--color-theme-glow);
  filter: blur(12px);
  animation: gallery-stage-ring 940ms cubic-bezier(0.2, 0.7, 0.28, 1) 30ms both;
}

.gallery-page-opening__halo,
.gallery-page-opening__prism,
.gallery-page-opening__beam,
.gallery-page-opening__spark {
  position: absolute;
  z-index: 1;
  top: 50%;
  left: 50%;
}

.gallery-page-opening__halo {
  width: min(64vw, 820px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.68) 0 3%, color-mix(in srgb, #fff 42%, var(--color-accent)) 14%, var(--color-theme-glow-strong) 30%, var(--color-theme-glow) 46%, transparent 72%);
  box-shadow: 0 0 78px var(--color-theme-glow);
  filter: blur(18px) saturate(0.82);
  mix-blend-mode: screen;
  transform: translate(-50%, -50%);
  animation: gallery-halo-bloom 960ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__prism {
  width: 70px;
  aspect-ratio: 1;
  border: 3px solid rgba(255, 255, 255, 0.56);
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.74), transparent 52%),
    var(--color-accent-soft-gradient),
    color-mix(in srgb, #fff 70%, var(--color-accent));
  box-shadow:
    0 0 28px rgba(255, 255, 255, 0.72),
    0 0 72px var(--color-theme-glow-strong),
    0 0 118px var(--color-theme-glow);
  filter: blur(1.8px) saturate(0.8) brightness(1.08);
  mix-blend-mode: screen;
  transform: translate(-50%, -50%) rotate(45deg);
  animation: gallery-prism-release 960ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__beam {
  width: max(145vw, 145vh);
  height: 14px;
  background: linear-gradient(90deg, transparent 7%, color-mix(in srgb, var(--color-accent) 46%, transparent) 32%, rgba(255, 255, 255, 0.9) 50%, color-mix(in srgb, var(--color-accent) 42%, transparent) 68%, transparent 93%);
  box-shadow:
    0 0 22px rgba(255, 255, 255, 0.74),
    0 0 54px var(--color-theme-glow-strong),
    0 0 96px var(--color-theme-glow);
  filter: blur(8px) saturate(0.76);
  mix-blend-mode: screen;
  transform-origin: center;
}

.gallery-page-opening__beam.is-primary {
  transform: translate(-50%, -50%);
  animation: gallery-beam-primary 920ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__beam.is-secondary {
  height: 8px;
  opacity: 0.66;
  transform: translate(-50%, -50%) rotate(90deg);
  animation: gallery-beam-secondary 920ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__spark {
  width: var(--spark-size, 9px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0 16%, color-mix(in srgb, #fff 58%, var(--color-accent)) 28%, var(--color-theme-glow-strong) 48%, transparent 76%);
  box-shadow:
    0 0 16px rgba(255, 255, 255, 0.74),
    0 0 38px var(--color-theme-glow-strong),
    0 0 68px var(--color-theme-glow);
  filter: blur(0.8px) saturate(0.8);
  mix-blend-mode: screen;
  animation: gallery-spark-flight 940ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__spark::before,
.gallery-page-opening__spark::after {
  position: absolute;
  top: 50%;
  left: 50%;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 0 20px var(--color-theme-glow-strong);
  content: "";
  transform: translate(-50%, -50%);
}

.gallery-page-opening__spark::before {
  width: 220%;
  height: 1px;
}

.gallery-page-opening__spark::after {
  width: 1px;
  height: 220%;
}

.gallery-page-opening__spark.is-one { --spark-x: -31vw; --spark-y: -22vh; --spark-size: 10px; animation-delay: 30ms; }
.gallery-page-opening__spark.is-two { --spark-x: 35vw; --spark-y: -17vh; --spark-size: 8px; animation-delay: 80ms; }
.gallery-page-opening__spark.is-three { --spark-x: -38vw; --spark-y: 24vh; --spark-size: 11px; animation-delay: 110ms; }
.gallery-page-opening__spark.is-four { --spark-x: 29vw; --spark-y: 28vh; --spark-size: 9px; animation-delay: 60ms; }
.gallery-page-opening__spark.is-five { --spark-x: -12vw; --spark-y: -34vh; --spark-size: 7px; animation-delay: 140ms; }
.gallery-page-opening__spark.is-six { --spark-x: 14vw; --spark-y: 35vh; --spark-size: 8px; animation-delay: 20ms; }
.gallery-page-opening__spark.is-seven { --spark-x: -43vw; --spark-y: 3vh; --spark-size: 6px; animation-delay: 170ms; }
.gallery-page-opening__spark.is-eight { --spark-x: 42vw; --spark-y: 6vh; --spark-size: 7px; animation-delay: 100ms; }

@keyframes gallery-opening-visibility {
  0%, 94% { visibility: visible; }
  100% { visibility: hidden; }
}

@keyframes gallery-curtain-start {
  0%, 11% {
    transform: translate3d(0, 0, 0) scaleX(1);
    animation-timing-function: cubic-bezier(0.3, 0.04, 0.2, 1);
  }
  88%, 100% { transform: translate3d(-106%, 0, 0) scaleX(0.92); }
}

@keyframes gallery-curtain-end {
  0%, 11% {
    transform: translate3d(0, 0, 0) scaleX(1);
    animation-timing-function: cubic-bezier(0.3, 0.04, 0.2, 1);
  }
  88%, 100% { transform: translate3d(106%, 0, 0) scaleX(0.92); }
}

@keyframes gallery-halo-bloom {
  0%, 10% { opacity: 0; transform: translate(-50%, -50%) scale(0.06); }
  36% { opacity: 0.88; transform: translate(-50%, -50%) scale(0.62); }
  76% { opacity: 0.38; transform: translate(-50%, -50%) scale(1.28); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.7); }
}

@keyframes gallery-prism-release {
  0%, 10% { opacity: 0; transform: translate(-50%, -50%) rotate(45deg) scale(0.24); }
  34% { opacity: 0.78; transform: translate(-50%, -50%) rotate(128deg) scale(0.92); }
  72% { opacity: 0.28; transform: translate(-50%, -50%) rotate(208deg) scale(1.46); }
  100% { opacity: 0; transform: translate(-50%, -50%) rotate(236deg) scale(1.76); }
}

@keyframes gallery-beam-primary {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) scaleX(0.02); }
  40% { opacity: 0.76; transform: translate(-50%, -50%) scaleX(0.7); }
  76% { opacity: 0.22; transform: translate(-50%, -50%) scaleX(0.96); }
  100% { opacity: 0; transform: translate(-50%, -50%) scaleX(1.08); }
}

@keyframes gallery-beam-secondary {
  0%, 18% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.02); }
  43% { opacity: 0.58; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.5); }
  74% { opacity: 0.18; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.84); }
  100% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.96); }
}

@keyframes gallery-spark-flight {
  0%, 16% { opacity: 0; transform: translate(-50%, -50%) scale(0.12) rotate(0deg); }
  38% { opacity: 0.82; transform: translate(-50%, -50%) scale(1.06) rotate(38deg); }
  76% {
    opacity: 0.3;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.72) rotate(112deg);
  }
  100% {
    opacity: 0;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.28) rotate(148deg);
  }
}

@keyframes gallery-curtain-sheen {
  0%, 10% { opacity: 0.24; transform: translate3d(-4%, 0, 0) scale(0.96); }
  48% { opacity: 0.5; transform: translate3d(2%, 0, 0) scale(1.02); }
  100% { opacity: 0.18; transform: translate3d(6%, 0, 0) scale(1.06); }
}

@keyframes gallery-stage-bloom {
  0%, 10% { opacity: 0; transform: translate(-50%, -50%) scale(0.08); }
  34% { opacity: 0.58; transform: translate(-50%, -50%) scale(0.56); }
  72% { opacity: 0.28; transform: translate(-50%, -50%) scale(1.1); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
}

@keyframes gallery-stage-ring {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) scale(0.06); }
  40% { opacity: 0.58; transform: translate(-50%, -50%) scale(0.46); }
  78% { opacity: 0.18; transform: translate(-50%, -50%) scale(1.04); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.28); }
}

@keyframes gallery-post-bloom {
  0%, 8% { opacity: 0; transform: scale(0.84); }
  38% { opacity: 0.48; transform: scale(1); }
  76% { opacity: 0.18; transform: scale(1.08); }
  100% { opacity: 0; transform: scale(1.16); }
}

@keyframes gallery-soft-focus {
  0%, 14% { opacity: 0.36; }
  68% { opacity: 0.2; }
  100% { opacity: 0; }
}

@media screen and (orientation: portrait) {
  .gallery-page-opening {
    animation-duration: 1500ms;
  }

  .gallery-page-opening::before,
  .gallery-page-opening::after,
  .gallery-page-opening__curtain {
    animation-duration: 1500ms;
  }

  .gallery-page-opening__curtain.is-start,
  .gallery-page-opening__curtain.is-end {
    animation-duration: 1500ms;
  }

  .gallery-page-opening__sheen {
    animation-duration: 1320ms;
  }

  .gallery-page-opening__stage::before {
    animation-duration: 1450ms;
  }

  .gallery-page-opening__stage::after,
  .gallery-page-opening__halo,
  .gallery-page-opening__prism,
  .gallery-page-opening__beam,
  .gallery-page-opening__spark {
    animation-duration: 1400ms;
  }

  .gallery-page-opening__beam.is-primary,
  .gallery-page-opening__beam.is-secondary {
    animation-duration: 1400ms;
  }

  .gallery-page-opening__curtain {
    right: 0;
    left: 0;
    width: auto;
    height: calc(50% + 2px);
  }

  .gallery-page-opening__curtain.is-start {
    top: 0;
    bottom: auto;
    transform-origin: center top;
    animation-name: gallery-lid-start;
  }

  .gallery-page-opening__curtain.is-start::before {
    -webkit-mask-image: linear-gradient(180deg, #000 0, #000 calc(100% - 54px), transparent 100%);
    mask-image: linear-gradient(180deg, #000 0, #000 calc(100% - 54px), transparent 100%);
  }

  .gallery-page-opening__curtain.is-end {
    top: auto;
    bottom: 0;
    transform-origin: center bottom;
    animation-name: gallery-lid-end;
  }

  .gallery-page-opening__curtain.is-end::before {
    -webkit-mask-image: linear-gradient(0deg, #000 0, #000 calc(100% - 54px), transparent 100%);
    mask-image: linear-gradient(0deg, #000 0, #000 calc(100% - 54px), transparent 100%);
  }

  .gallery-page-opening__edge {
    right: 0;
    left: 0;
    width: auto;
    height: 42px;
    background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.72), color-mix(in srgb, #fff 54%, var(--color-accent)), transparent);
  }

  .is-start .gallery-page-opening__edge {
    top: auto;
    right: 0;
    bottom: -19px;
  }

  .is-end .gallery-page-opening__edge {
    top: -19px;
    left: 0;
    transform: scaleY(-1);
  }

  .gallery-page-opening__beam.is-primary {
    transform: translate(-50%, -50%) rotate(90deg);
    animation-name: gallery-beam-portrait;
  }

  .gallery-page-opening__beam.is-secondary {
    transform: translate(-50%, -50%);
    animation-name: gallery-beam-primary;
  }

  .gallery-page-opening__halo {
    width: min(96vw, 620px);
  }

  .gallery-page-opening__prism {
    width: 58px;
  }

  .gallery-page-opening__motif {
    inset: 7% 5%;
    opacity: 0.34;
  }
}

@keyframes gallery-lid-start {
  0%, 10% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.3, 0.04, 0.2, 1);
  }
  90%, 100% { transform: translate3d(0, -106%, 0) scaleY(0.92); }
}

@keyframes gallery-lid-end {
  0%, 10% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.3, 0.04, 0.2, 1);
  }
  90%, 100% { transform: translate3d(0, 106%, 0) scaleY(0.92); }
}

@keyframes gallery-beam-portrait {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.02); }
  40% { opacity: 0.76; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.7); }
  76% { opacity: 0.22; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.96); }
  100% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(1.08); }
}

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
