<template>
  <div
    v-if="visible"
    :key="animationKey"
    class="gallery-opening"
    aria-hidden="true"
    @touchmove.prevent
    @wheel.prevent>
    <div class="gallery-opening__backdrop"></div>

    <div class="gallery-opening__light-show">
      <span class="gallery-opening__aurora"></span>
      <span class="gallery-opening__ray is-left"></span>
      <span class="gallery-opening__ray is-center"></span>
      <span class="gallery-opening__ray is-right"></span>
      <span
        v-for="spark in sparks"
        :key="spark.id"
        class="gallery-opening__spark"
        :style="spark.style">
        <span></span>
      </span>
    </div>

    <div class="gallery-opening__desktop-stage">
      <div class="gallery-opening__curtain is-left">
        <span class="gallery-opening__fabric"></span>
        <span class="gallery-opening__seam"></span>
        <svg
          class="gallery-opening__curtain-shape"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true">
          <path d="M0 0H100C100 5 92 8 92 14S100 23 100 29S92 39 92 45S100 55 100 61S92 71 92 77S100 88 92 100H0Z"></path>
        </svg>
        <span class="gallery-opening__curtain-gloss"></span>
        <span class="gallery-opening__tassel"></span>
        <span
          v-for="mote in curtainMotes"
          :key="`left-${mote.id}`"
          class="gallery-opening__curtain-mote"
          :style="mote.style"></span>
      </div>
      <div class="gallery-opening__curtain is-right">
        <span class="gallery-opening__fabric"></span>
        <span class="gallery-opening__seam"></span>
        <svg
          class="gallery-opening__curtain-shape"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true">
          <path d="M0 0C0 5 8 8 8 14S0 23 0 29S8 39 8 45S0 55 0 61S8 71 8 77S0 88 8 100H100V0Z"></path>
        </svg>
        <span class="gallery-opening__curtain-gloss"></span>
        <span class="gallery-opening__tassel"></span>
        <span
          v-for="mote in curtainMotes"
          :key="`right-${mote.id}`"
          class="gallery-opening__curtain-mote"
          :style="mote.style"></span>
      </div>

      <div class="gallery-opening__valance">
        <span class="gallery-opening__valance-fabric"></span>
        <span class="gallery-opening__valance-swag is-one"></span>
        <span class="gallery-opening__valance-swag is-two"></span>
        <span class="gallery-opening__valance-swag is-three"></span>
        <span class="gallery-opening__valance-swag is-four"></span>
        <span class="gallery-opening__valance-trim"></span>
        <span class="gallery-opening__lace"></span>
      </div>
    </div>

    <div class="gallery-opening__mobile-lid">
      <span class="gallery-opening__mobile-fabric"></span>
      <span class="gallery-opening__mobile-scallops"></span>
      <span class="gallery-opening__mobile-rim"></span>
      <span class="gallery-opening__mobile-handle"></span>
      <span
        v-for="mote in mobileMotes"
        :key="mote.id"
        class="gallery-opening__mobile-mote"
        :style="mote.style"></span>
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';

const DESKTOP_OPENING_DURATION = 1580;
const MOBILE_OPENING_DURATION = 1100;
const PORTRAIT_QUERY = '(orientation: portrait)';

const SPARKS = [
  ['one', '49%', '47%', '-18vw', '-23vh', '0ms', '18px'],
  ['two', '51%', '50%', '19vw', '-19vh', '70ms', '14px'],
  ['three', '48%', '52%', '-27vw', '8vh', '120ms', '15px'],
  ['four', '52%', '48%', '29vw', '12vh', '35ms', '20px'],
  ['five', '50%', '49%', '-8vw', '-35vh', '160ms', '13px'],
  ['six', '50%', '51%', '10vw', '31vh', '100ms', '14px'],
  ['seven', '49%', '50%', '-39vw', '-7vh', '55ms', '12px'],
  ['eight', '51%', '49%', '40vw', '-3vh', '180ms', '15px'],
  ['nine', '50%', '52%', '-20vw', '29vh', '210ms', '13px'],
  ['ten', '50%', '48%', '24vw', '-32vh', '130ms', '14px'],
  ['eleven', '49%', '51%', '-5vw', '20vh', '245ms', '17px'],
  ['twelve', '51%', '50%', '7vw', '-14vh', '195ms', '13px'],
  ['thirteen', '48%', '49%', '-31vw', '-27vh', '90ms', '10px'],
  ['fourteen', '52%', '51%', '34vw', '25vh', '230ms', '11px'],
  ['fifteen', '49%', '48%', '-44vw', '18vh', '155ms', '9px'],
  ['sixteen', '51%', '52%', '45vw', '-21vh', '20ms', '10px'],
  ['seventeen', '50%', '50%', '-2vw', '-42vh', '280ms', '12px'],
  ['eighteen', '50%', '51%', '3vw', '39vh', '75ms', '11px'],
  ['nineteen', '49%', '49%', '-14vw', '4vh', '300ms', '8px'],
  ['twenty', '51%', '50%', '15vw', '-5vh', '260ms', '9px'],
].map(([id, left, top, x, y, delay, size]) => ({
  id,
  style: {
    '--spark-delay': delay,
    '--spark-left': left,
    '--spark-size': size,
    '--spark-top': top,
    '--spark-x': x,
    '--spark-y': y,
  },
}));

const CURTAIN_MOTES = [
  ['one', '9%', '0ms', '10px', '-8px'],
  ['two', '19%', '120ms', '7px', '6px'],
  ['three', '31%', '240ms', '12px', '-5px'],
  ['four', '44%', '80ms', '8px', '9px'],
  ['five', '57%', '310ms', '11px', '-7px'],
  ['six', '69%', '170ms', '7px', '5px'],
  ['seven', '81%', '390ms', '10px', '-9px'],
  ['eight', '91%', '220ms', '6px', '7px'],
].map(([id, top, delay, size, drift]) => ({
  id,
  style: {
    '--mote-delay': delay,
    '--mote-drift': drift,
    '--mote-size': size,
    '--mote-top': top,
  },
}));

const MOBILE_MOTES = [
  ['mobile-one', '8%', '0ms', '8px'],
  ['mobile-two', '19%', '150ms', '11px'],
  ['mobile-three', '32%', '70ms', '7px'],
  ['mobile-four', '46%', '260ms', '12px'],
  ['mobile-five', '59%', '110ms', '8px'],
  ['mobile-six', '72%', '330ms', '10px'],
  ['mobile-seven', '84%', '190ms', '7px'],
  ['mobile-eight', '94%', '40ms', '9px'],
].map(([id, left, delay, size]) => ({
  id,
  style: {
    '--mobile-mote-delay': delay,
    '--mobile-mote-left': left,
    '--mobile-mote-size': size,
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
      curtainMotes: CURTAIN_MOTES,
      hideTimer: null,
      mobileMotes: MOBILE_MOTES,
      sparks: SPARKS,
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
.gallery-opening {
  --curtain-base: color-mix(in srgb, #fff 58%, var(--color-accent));
  --curtain-depth: color-mix(in srgb, #fff 30%, var(--color-accent-strong));
  --curtain-highlight: color-mix(in srgb, #fff 82%, var(--color-accent));
  --curtain-sheer: color-mix(in srgb, var(--color-accent-soft) 72%, transparent);
  --ornament-bright: color-mix(in srgb, #fff 82%, var(--color-accent));
  --ornament-shadow: color-mix(in srgb, #e5b85a 62%, var(--color-accent));
  position: fixed;
  z-index: var(--z-page-opening, 2147483647);
  inset: 0;
  isolation: isolate;
  overflow: hidden;
  pointer-events: auto;
  touch-action: none;
  animation: stage-opening-lifetime 1580ms linear both;
}

.gallery-opening__backdrop {
  position: absolute;
  z-index: 0;
  inset: 0;
  background:
    radial-gradient(circle at 50% 46%, rgba(255, 255, 255, 0.86) 0 5%, var(--color-theme-glow-strong) 24%, transparent 62%),
    radial-gradient(circle at 18% 52%, var(--color-theme-glow) 0, transparent 46%),
    radial-gradient(circle at 82% 48%, var(--color-theme-glow) 0, transparent 46%),
    color-mix(in srgb, var(--color-surface-card) 78%, transparent);
  -webkit-backdrop-filter: blur(7px) saturate(1.16);
  backdrop-filter: blur(7px) saturate(1.16);
  animation: stage-backdrop-release 1580ms ease-out both;
}

.gallery-opening__desktop-stage,
.gallery-opening__light-show {
  position: absolute;
  inset: 0;
}

.gallery-opening__desktop-stage {
  z-index: 3;
}

.gallery-opening__light-show {
  z-index: 2;
  overflow: hidden;
  pointer-events: none;
}

.gallery-opening__light-show::before,
.gallery-opening__light-show::after {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  content: "";
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
  transform: translate(-50%, -50%) scale(0.1);
}

.gallery-opening__light-show::before {
  width: min(92vw, 1280px);
  aspect-ratio: 1.8;
  background:
    radial-gradient(ellipse, rgba(255, 255, 255, 0.92) 0 3%, var(--color-theme-glow-strong) 15%, var(--color-theme-glow) 38%, transparent 72%);
  filter: blur(18px) saturate(1.28);
  animation: stage-halo-bloom 1420ms cubic-bezier(0.2, 0.74, 0.26, 1) both;
}

.gallery-opening__light-show::after {
  width: min(64vw, 840px);
  aspect-ratio: 1;
  border: 2px solid color-mix(in srgb, #fff 52%, var(--color-accent));
  box-shadow:
    0 0 18px rgba(255, 255, 255, 0.86),
    0 0 56px var(--color-theme-glow-strong),
    inset 0 0 42px var(--color-theme-glow);
  filter: blur(2px);
  animation: stage-halo-ring 1280ms cubic-bezier(0.16, 1, 0.3, 1) 90ms both;
}

.gallery-opening__aurora {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(82vw, 1120px);
  aspect-ratio: 1.65;
  border-radius: 50%;
  background:
    radial-gradient(ellipse, rgba(255, 255, 255, 0.98) 0 3%, color-mix(in srgb, #fff 48%, var(--color-accent)) 12%, var(--color-theme-glow-strong) 27%, var(--color-theme-glow) 46%, transparent 72%);
  box-shadow: 0 0 72px var(--color-theme-glow-strong);
  filter: blur(14px) saturate(1.24);
  transform: translate(-50%, -50%) scale(0.08);
  animation: stage-aurora-bloom 1340ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

.gallery-opening__ray {
  position: absolute;
  top: -14vh;
  left: 50%;
  width: clamp(220px, 29vw, 520px);
  height: 132vh;
  clip-path: polygon(43% 0, 57% 0, 100% 100%, 0 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 30%, #000 70%, transparent 100%);
  mask-image: linear-gradient(90deg, transparent 0, #000 30%, #000 70%, transparent 100%);
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.96),
    color-mix(in srgb, #fff 42%, var(--color-accent)) 22%,
    color-mix(in srgb, var(--color-accent) 54%, transparent) 56%,
    transparent 90%
  );
  box-shadow: 0 0 46px var(--color-theme-glow-strong);
  filter: blur(13px) saturate(1.22);
  mix-blend-mode: screen;
  opacity: 0;
  transform-origin: 50% 0;
  animation: stage-ray-reveal 1250ms ease-out both;
}

.gallery-opening__ray.is-left {
  transform: translateX(-76%) rotate(16deg) scaleX(0.55);
  animation-delay: 140ms;
}

.gallery-opening__ray.is-center {
  transform: translateX(-50%) scaleX(0.45);
  animation-delay: 70ms;
}

.gallery-opening__ray.is-right {
  transform: translateX(-24%) rotate(-16deg) scaleX(0.55);
  animation-delay: 200ms;
}

.gallery-opening__spark {
  position: absolute;
  top: var(--spark-top);
  left: var(--spark-left);
  width: var(--spark-size);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle,
    #fff 0 12%,
    color-mix(in srgb, #fff 58%, var(--color-accent)) 14% 24%,
    var(--color-theme-glow-strong) 34%,
    transparent 68%);
  box-shadow:
    0 0 8px rgba(255, 255, 255, 0.96),
    0 0 24px var(--color-theme-glow-strong),
    0 0 46px var(--color-theme-glow);
  opacity: 0;
  filter:
    drop-shadow(0 0 2px #fff)
    drop-shadow(0 0 10px var(--color-theme-glow-strong))
    saturate(1.25);
  transform: translate(-50%, -50%) scale(0.1);
  animation: stage-spark-flight 1360ms cubic-bezier(0.18, 0.76, 0.22, 1) var(--spark-delay) both;
}

.gallery-opening__spark::before,
.gallery-opening__spark::after,
.gallery-opening__spark span {
  position: absolute;
  top: 50%;
  left: 50%;
  background: rgba(255, 255, 255, 0.98);
  box-shadow:
    0 0 12px #fff,
    0 0 28px var(--color-theme-glow-strong),
    0 0 50px var(--color-theme-glow);
  content: "";
  transform: translate(-50%, -50%);
}

.gallery-opening__spark::before {
  width: 130%;
  height: 2px;
}

.gallery-opening__spark::after {
  width: 2px;
  height: 130%;
}

.gallery-opening__spark span {
  width: 42%;
  aspect-ratio: 1;
  border-radius: 50%;
}

.gallery-opening__curtain {
  position: absolute;
  z-index: 1;
  top: 0;
  bottom: 0;
  width: 55%;
  filter:
    drop-shadow(0 0 18px rgba(255, 255, 255, 0.48))
    drop-shadow(0 0 38px var(--color-theme-glow-strong))
    drop-shadow(0 12px 42px color-mix(in srgb, var(--color-theme-glow) 74%, transparent));
  will-change: transform;
}

.gallery-opening__curtain::after {
  position: absolute;
  z-index: 4;
  top: -4%;
  bottom: -4%;
  width: 54px;
  border-radius: 50%;
  background: linear-gradient(
    180deg,
    transparent,
    rgba(255, 255, 255, 0.78) 18%,
    var(--color-theme-glow-strong) 52%,
    rgba(255, 255, 255, 0.56) 78%,
    transparent
  );
  content: "";
  filter: blur(16px);
  opacity: 0.76;
  pointer-events: none;
  mix-blend-mode: screen;
  animation: stage-edge-glow 940ms ease-in-out 120ms both;
}

.gallery-opening__curtain.is-left {
  left: 0;
  transform-origin: 0 18%;
  animation: stage-curtain-left 1580ms both;
}

.gallery-opening__curtain.is-left::after {
  right: -20px;
}

.gallery-opening__curtain.is-right {
  right: 0;
  transform-origin: 100% 18%;
  animation: stage-curtain-right 1580ms both;
}

.gallery-opening__curtain.is-right::after {
  left: -20px;
}

.gallery-opening__curtain-shape {
  position: absolute;
  z-index: 0;
  inset: 0;
  width: 100%;
  height: 100%;
  fill: var(--curtain-base);
  opacity: 0.88;
}

.gallery-opening__fabric,
.gallery-opening__curtain-gloss,
.gallery-opening__seam {
  position: absolute;
  z-index: 1;
  inset: 0;
  -webkit-mask-position: center;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-size: 100% 100%;
  mask-position: center;
  mask-repeat: no-repeat;
  mask-size: 100% 100%;
}

.gallery-opening__fabric {
  opacity: 0.9;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.46), var(--curtain-sheer) 48%, rgba(255, 255, 255, 0.28)),
    radial-gradient(ellipse at 48% 6%, rgba(255, 255, 255, 0.82), transparent 35%),
    repeating-linear-gradient(92deg,
      color-mix(in srgb, var(--curtain-depth) 66%, transparent) 0 3%,
      color-mix(in srgb, #fff 72%, var(--color-accent)) 7%,
      color-mix(in srgb, var(--curtain-base) 78%, transparent) 12%,
      color-mix(in srgb, var(--color-accent-strong) 38%, transparent) 16%,
      color-mix(in srgb, var(--curtain-highlight) 84%, transparent) 21%,
      color-mix(in srgb, var(--curtain-depth) 58%, transparent) 27%),
    var(--color-accent-gradient-diagonal);
  background-blend-mode: screen, screen, soft-light, normal;
}

.gallery-opening__curtain.is-left .gallery-opening__fabric,
.gallery-opening__curtain.is-left .gallery-opening__curtain-gloss,
.gallery-opening__curtain.is-left .gallery-opening__seam {
  -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cpath fill='white' d='M0 0H100C100 5 92 8 92 14S100 23 100 29S92 39 92 45S100 55 100 61S92 71 92 77S100 88 92 100H0Z'/%3E%3C/svg%3E");
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cpath fill='white' d='M0 0H100C100 5 92 8 92 14S100 23 100 29S92 39 92 45S100 55 100 61S92 71 92 77S100 88 92 100H0Z'/%3E%3C/svg%3E");
}

.gallery-opening__curtain.is-right .gallery-opening__fabric,
.gallery-opening__curtain.is-right .gallery-opening__curtain-gloss,
.gallery-opening__curtain.is-right .gallery-opening__seam {
  -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cpath fill='white' d='M0 0C0 5 8 8 8 14S0 23 0 29S8 39 8 45S0 55 0 61S8 71 8 77S0 88 8 100H100V0Z'/%3E%3C/svg%3E");
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cpath fill='white' d='M0 0C0 5 8 8 8 14S0 23 0 29S8 39 8 45S0 55 0 61S8 71 8 77S0 88 8 100H100V0Z'/%3E%3C/svg%3E");
}

.gallery-opening__curtain-gloss {
  z-index: 2;
  background:
    linear-gradient(112deg, transparent 12%, rgba(255, 255, 255, 0.68) 28%, transparent 42%),
    repeating-linear-gradient(90deg, transparent 0 7%, rgba(255, 255, 255, 0.3) 9%, transparent 14%);
  opacity: 0.7;
  mix-blend-mode: screen;
}

.gallery-opening__seam {
  z-index: 3;
  box-shadow:
    inset 0 14px 24px rgba(255, 255, 255, 0.36),
    inset 0 -20px 36px color-mix(in srgb, var(--color-accent-strong) 16%, transparent);
}

.gallery-opening__curtain-mote {
  position: absolute;
  z-index: 6;
  top: var(--mote-top);
  width: var(--mote-size);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0 18%, var(--curtain-highlight) 28%, var(--color-theme-glow-strong) 48%, transparent 72%);
  box-shadow:
    0 0 10px #fff,
    0 0 24px var(--color-theme-glow-strong),
    0 0 42px var(--color-theme-glow);
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: screen;
  animation: stage-curtain-mote 820ms ease-in-out var(--mote-delay) both;
}

.gallery-opening__curtain-mote::before,
.gallery-opening__curtain-mote::after {
  position: absolute;
  top: 50%;
  left: 50%;
  background: rgba(255, 255, 255, 0.92);
  content: "";
  transform: translate(-50%, -50%);
}

.gallery-opening__curtain-mote::before {
  width: 170%;
  height: 1px;
}

.gallery-opening__curtain-mote::after {
  width: 1px;
  height: 170%;
}

.gallery-opening__curtain.is-left .gallery-opening__curtain-mote {
  right: -8px;
}

.gallery-opening__curtain.is-right .gallery-opening__curtain-mote {
  left: -8px;
}

.gallery-opening__tassel {
  position: absolute;
  z-index: 4;
  top: 42%;
  width: 16px;
  height: 84px;
  border-radius: 999px 999px 8px 8px;
  background:
    repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.92) 0 2px, var(--ornament-shadow) 3px 5px),
    linear-gradient(var(--ornament-bright), var(--ornament-shadow));
  box-shadow:
    0 0 12px rgba(255, 255, 255, 0.72),
    0 0 24px var(--color-theme-glow-strong);
  animation: stage-tassel-sway 780ms ease-in-out 350ms both;
}

.gallery-opening__tassel::before {
  position: absolute;
  top: -10px;
  left: 50%;
  width: 31px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--ornament-bright), var(--ornament-shadow));
  content: "";
  transform: translateX(-50%);
}

.gallery-opening__curtain.is-left .gallery-opening__tassel {
  right: 3.5%;
}

.gallery-opening__curtain.is-right .gallery-opening__tassel {
  left: 3.5%;
}

.gallery-opening__valance {
  position: absolute;
  z-index: 4;
  top: 0;
  left: -2%;
  width: 104%;
  height: clamp(150px, 23vh, 250px);
  filter:
    drop-shadow(0 12px 18px rgba(255, 255, 255, 0.22))
    drop-shadow(0 18px 30px var(--color-theme-glow-strong));
  transform-origin: center top;
  animation: stage-valance-rise 1580ms both;
}

.gallery-opening__valance-fabric {
  position: absolute;
  z-index: 0;
  inset: 0;
  clip-path: polygon(0 0, 100% 0, 100% 56%, 94% 68%, 88% 59%, 82% 75%, 75% 63%, 68% 81%, 60% 67%, 52% 88%, 44% 67%, 36% 81%, 29% 63%, 22% 75%, 15% 59%, 8% 68%, 0 56%);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.52), var(--curtain-sheer)),
    repeating-linear-gradient(96deg,
      color-mix(in srgb, var(--curtain-depth) 58%, transparent) 0 5%,
      var(--curtain-highlight) 10%,
      var(--curtain-base) 16%,
      color-mix(in srgb, var(--color-accent-strong) 34%, transparent) 22%),
    var(--color-accent-gradient-horizontal);
  background-blend-mode: screen, soft-light, normal;
  box-shadow:
    inset 0 12px 24px rgba(255, 255, 255, 0.34),
    inset 0 -24px 34px color-mix(in srgb, var(--color-accent-strong) 14%, transparent);
  opacity: 0.94;
}

.gallery-opening__valance-swag {
  position: absolute;
  z-index: 1;
  top: 4%;
  width: 29%;
  height: 72%;
  border-radius: 0 0 50% 50%;
  border-bottom: 2px solid rgba(255, 255, 255, 0.52);
  background: radial-gradient(ellipse at 50% 0, rgba(255, 255, 255, 0.54), transparent 66%);
  box-shadow: inset 0 -16px 24px color-mix(in srgb, var(--color-accent-strong) 12%, transparent);
}

.gallery-opening__valance-swag.is-one { left: -1%; }
.gallery-opening__valance-swag.is-two { left: 24%; }
.gallery-opening__valance-swag.is-three { right: 24%; }
.gallery-opening__valance-swag.is-four { right: -1%; }

.gallery-opening__valance-trim {
  position: absolute;
  z-index: 2;
  right: 0;
  bottom: 21%;
  left: 0;
  height: 9px;
  background: repeating-linear-gradient(90deg, var(--ornament-bright) 0 10px, var(--ornament-shadow) 10px 19px, rgba(255, 255, 255, 0.88) 19px 29px);
  box-shadow:
    0 2px 7px rgba(255, 255, 255, 0.58),
    0 0 18px var(--color-theme-glow-strong);
}

.gallery-opening__lace {
  position: absolute;
  z-index: 3;
  right: 0;
  bottom: 4%;
  left: 0;
  height: 18%;
  background:
    linear-gradient(135deg, transparent 50%, var(--ornament-bright) 51%) 0 0 / 32px 100% repeat-x,
    linear-gradient(225deg, transparent 50%, var(--ornament-shadow) 51%) 16px 0 / 32px 100% repeat-x;
  filter:
    drop-shadow(0 4px 4px rgba(255, 255, 255, 0.34))
    drop-shadow(0 7px 12px var(--color-theme-glow));
}

.gallery-opening__mobile-lid {
  display: none;
}

@keyframes stage-opening-lifetime {
  0%, 96% { visibility: visible; }
  100% { visibility: hidden; }
}

@keyframes stage-backdrop-release {
  0%, 16% { opacity: 1; }
  76%, 100% { opacity: 0; }
}

@keyframes stage-curtain-left {
  0%, 12% {
    transform: translate3d(0, 0, 0) scaleX(1) skewY(0deg);
    animation-timing-function: cubic-bezier(0.18, 0.76, 0.24, 1);
  }
  50% {
    transform: translate3d(-68%, 0, 0) scaleX(0.95) skewY(-1.4deg);
    animation-timing-function: cubic-bezier(0.24, 0.62, 0.22, 1);
  }
  72% {
    transform: translate3d(-91%, 0, 0) scaleX(0.9) skewY(0.45deg);
    animation-timing-function: cubic-bezier(0.3, 0.58, 0.32, 1);
  }
  88%, 100% { transform: translate3d(-112%, 0, 0) scaleX(0.87) skewY(0deg); }
}

@keyframes stage-curtain-right {
  0%, 12% {
    transform: translate3d(0, 0, 0) scaleX(1) skewY(0deg);
    animation-timing-function: cubic-bezier(0.18, 0.76, 0.24, 1);
  }
  50% {
    transform: translate3d(68%, 0, 0) scaleX(0.95) skewY(1.4deg);
    animation-timing-function: cubic-bezier(0.24, 0.62, 0.22, 1);
  }
  72% {
    transform: translate3d(91%, 0, 0) scaleX(0.9) skewY(-0.45deg);
    animation-timing-function: cubic-bezier(0.3, 0.58, 0.32, 1);
  }
  88%, 100% { transform: translate3d(112%, 0, 0) scaleX(0.87) skewY(0deg); }
}

@keyframes stage-valance-rise {
  0%, 20% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.2, 0.72, 0.24, 1);
  }
  58% {
    transform: translate3d(0, -67%, 0) scaleY(0.96);
    animation-timing-function: cubic-bezier(0.24, 0.62, 0.26, 1);
  }
  76% {
    transform: translate3d(0, -92%, 0) scaleY(0.93);
    animation-timing-function: cubic-bezier(0.32, 0.58, 0.34, 1);
  }
  88%, 100% { transform: translate3d(0, -116%, 0) scaleY(0.91); }
}

@keyframes stage-aurora-bloom {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) scale(0.08); }
  36% { opacity: 1; transform: translate(-50%, -50%) scale(0.76); }
  70% { opacity: 0.88; transform: translate(-50%, -50%) scale(1.2); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.58); }
}

@keyframes stage-ray-reveal {
  0%, 14% { opacity: 0; filter: blur(22px); }
  38% { opacity: 0.88; filter: blur(11px); }
  72% { opacity: 0.62; filter: blur(13px); }
  100% { opacity: 0; filter: blur(20px); }
}

@keyframes stage-spark-flight {
  0%, 12% { opacity: 0; transform: translate(-50%, -50%) scale(0.08) rotate(0deg); }
  29% { opacity: 1; transform: translate(-50%, -50%) scale(1.32) rotate(38deg); }
  62% {
    opacity: 0.92;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.86) rotate(104deg);
  }
  88% {
    opacity: 0.28;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.48) rotate(148deg);
  }
  100% {
    opacity: 0;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.2) rotate(170deg);
  }
}

@keyframes stage-halo-bloom {
  0%, 12% { opacity: 0; transform: translate(-50%, -50%) scale(0.08); }
  34% { opacity: 0.94; transform: translate(-50%, -50%) scale(0.68); }
  70% { opacity: 0.68; transform: translate(-50%, -50%) scale(1.12); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
}

@keyframes stage-halo-ring {
  0%, 16% { opacity: 0; transform: translate(-50%, -50%) scale(0.08); }
  38% { opacity: 0.78; transform: translate(-50%, -50%) scale(0.48); }
  76% { opacity: 0.28; transform: translate(-50%, -50%) scale(1.08); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.34); }
}

@keyframes stage-edge-glow {
  0%, 12% { opacity: 0.28; transform: scaleY(0.72); }
  42% { opacity: 0.94; transform: scaleY(1.02); }
  82% { opacity: 0.66; transform: scaleY(1.08); }
  100% { opacity: 0; transform: scaleY(1.14); }
}

@keyframes stage-curtain-mote {
  0%, 12% { opacity: 0; transform: translate3d(0, 8px, 0) scale(0.22) rotate(0deg); }
  38% { opacity: 1; transform: translate3d(var(--mote-drift), 0, 0) scale(1.18) rotate(45deg); }
  76% { opacity: 0.72; transform: translate3d(var(--mote-drift), -8px, 0) scale(0.76) rotate(92deg); }
  100% { opacity: 0; transform: translate3d(var(--mote-drift), -15px, 0) scale(0.3) rotate(135deg); }
}

@keyframes stage-tassel-sway {
  0% { transform: rotate(0deg); }
  38% { transform: rotate(10deg); }
  68% { transform: rotate(-5deg); }
  100% { transform: rotate(2deg); }
}

@media screen and (orientation: portrait) {
  .gallery-opening {
    animation-duration: 1100ms;
  }

  .gallery-opening__desktop-stage {
    display: none;
  }

  .gallery-opening__backdrop {
    animation: mobile-stage-backdrop-release 1100ms ease-out both;
  }

  .gallery-opening__light-show {
    z-index: 1;
  }

  .gallery-opening__light-show::before {
    width: 128vw;
    aspect-ratio: 0.92;
    filter: blur(16px) saturate(1.24);
    animation-duration: 1020ms;
  }

  .gallery-opening__light-show::after {
    width: 94vw;
    animation-duration: 940ms;
  }

  .gallery-opening__aurora {
    top: 38%;
    width: 124vw;
    animation-duration: 980ms;
  }

  .gallery-opening__ray {
    top: -22vh;
    width: 66vw;
    height: 130vh;
    opacity: 0;
    animation-duration: 950ms;
  }

  .gallery-opening__ray.is-left {
    transform: translateX(-80%) rotate(12deg) scaleX(0.52);
  }

  .gallery-opening__ray.is-right {
    transform: translateX(-20%) rotate(-12deg) scaleX(0.52);
  }

  .gallery-opening__spark {
    animation-duration: 900ms;
  }

  .gallery-opening__mobile-lid {
    position: absolute;
    z-index: 3;
    inset: -5vh -8vw -8vh;
    display: block;
    overflow: hidden;
    border-radius: 0 0 50% 50% / 0 0 12% 12%;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.48), var(--curtain-sheer)),
      var(--color-accent-gradient-vertical);
    background-blend-mode: screen, normal;
    box-shadow:
      inset 0 22px 44px rgba(255, 255, 255, 0.34),
      inset 0 -38px 58px color-mix(in srgb, var(--color-accent-strong) 15%, transparent),
      0 18px 50px color-mix(in srgb, var(--color-theme-glow) 64%, transparent),
      0 0 54px var(--color-theme-glow-strong);
    transform-origin: 50% 0;
    animation: mobile-stage-lid-rise 1100ms both;
  }

  .gallery-opening__mobile-lid::after {
    position: absolute;
    z-index: 4;
    right: -4%;
    bottom: 2.8%;
    left: -4%;
    height: 72px;
    border-radius: 50%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.82), var(--color-theme-glow-strong), rgba(255, 255, 255, 0.82), transparent);
    content: "";
    filter: blur(18px);
    opacity: 0.78;
    pointer-events: none;
    mix-blend-mode: screen;
    animation: stage-edge-glow 860ms ease-in-out 80ms both;
  }

  .gallery-opening__mobile-fabric {
    position: absolute;
    inset: 0;
    background:
      linear-gradient(145deg, rgba(255, 255, 255, 0.4), var(--curtain-sheer) 52%, rgba(255, 255, 255, 0.28)),
      radial-gradient(ellipse at 50% 8%, rgba(255, 255, 255, 0.72), transparent 36%),
      repeating-linear-gradient(90deg,
        color-mix(in srgb, var(--curtain-depth) 52%, transparent) 0 8%,
        var(--curtain-highlight) 13%,
        var(--curtain-base) 20%,
        color-mix(in srgb, var(--color-accent-strong) 32%, transparent) 27%,
        var(--curtain-highlight) 34%);
    opacity: 0.9;
    background-blend-mode: screen, screen, soft-light;
  }

  .gallery-opening__mobile-scallops {
    position: absolute;
    right: 0;
    bottom: 5.5%;
    left: 0;
    height: 62px;
    background:
      radial-gradient(circle at 25px 0, transparent 24px, var(--ornament-bright) 25px 29px, transparent 30px) 0 0 / 50px 100% repeat-x;
    filter: drop-shadow(0 0 10px var(--color-theme-glow-strong));
    opacity: 0.9;
  }

  .gallery-opening__mobile-rim {
    position: absolute;
    right: 0;
    bottom: 5.2%;
    left: 0;
    height: 16px;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), var(--ornament-bright) 42%, var(--ornament-shadow) 76%, rgba(255, 255, 255, 0.82));
    box-shadow:
      0 3px 8px color-mix(in srgb, var(--color-accent-strong) 20%, transparent),
      0 0 20px rgba(255, 255, 255, 0.84),
      0 0 44px var(--color-theme-glow-strong);
  }

  .gallery-opening__mobile-handle {
    position: absolute;
    bottom: 2.5%;
    left: 50%;
    width: 84px;
    height: 28px;
    border: 5px solid var(--ornament-bright);
    border-bottom: 0;
    border-radius: 999px 999px 0 0;
    background: var(--curtain-base);
    box-shadow:
      0 0 14px rgba(255, 255, 255, 0.78),
      0 0 26px var(--color-theme-glow-strong);
    transform: translateX(-50%);
  }

  .gallery-opening__mobile-mote {
    position: absolute;
    z-index: 6;
    bottom: 5.8%;
    left: var(--mobile-mote-left);
    width: var(--mobile-mote-size);
    aspect-ratio: 1;
    border-radius: 50%;
    background: radial-gradient(circle, #fff 0 20%, var(--curtain-highlight) 32%, var(--color-theme-glow-strong) 50%, transparent 74%);
    box-shadow:
      0 0 9px #fff,
      0 0 22px var(--color-theme-glow-strong),
      0 0 38px var(--color-theme-glow);
    opacity: 0;
    pointer-events: none;
    mix-blend-mode: screen;
    animation: mobile-stage-mote 760ms ease-in-out var(--mobile-mote-delay) both;
  }
}

@keyframes mobile-stage-lid-rise {
  0%, 14% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.2, 0.74, 0.24, 1);
  }
  54% {
    transform: translate3d(0, -72%, 0) scaleY(0.97);
    animation-timing-function: cubic-bezier(0.24, 0.64, 0.28, 1);
  }
  76% {
    transform: translate3d(0, -96%, 0) scaleY(0.94);
    animation-timing-function: cubic-bezier(0.32, 0.58, 0.34, 1);
  }
  88%, 100% { transform: translate3d(0, -116%, 0) scaleY(0.92); }
}

@keyframes mobile-stage-mote {
  0%, 14% { opacity: 0; transform: translate3d(0, 8px, 0) scale(0.2); }
  42% { opacity: 1; transform: translate3d(0, -4px, 0) scale(1.16); }
  78% { opacity: 0.68; transform: translate3d(0, -16px, 0) scale(0.72); }
  100% { opacity: 0; transform: translate3d(0, -28px, 0) scale(0.3); }
}

@keyframes mobile-stage-backdrop-release {
  0%, 16% { opacity: 1; }
  78%, 100% { opacity: 0; }
}

html[data-motion="reduce"] .gallery-opening {
  display: none;
}
</style>
