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
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';

const DESKTOP_OPENING_DURATION = 1580;
const MOBILE_OPENING_DURATION = 1100;
const PORTRAIT_QUERY = '(orientation: portrait)';

const SPARKS = [
  ['one', '49%', '47%', '-18vw', '-23vh', '0ms', '16px'],
  ['two', '51%', '50%', '19vw', '-19vh', '80ms', '12px'],
  ['three', '48%', '52%', '-27vw', '8vh', '130ms', '13px'],
  ['four', '52%', '48%', '29vw', '12vh', '40ms', '17px'],
  ['five', '50%', '49%', '-8vw', '-35vh', '170ms', '11px'],
  ['six', '50%', '51%', '10vw', '31vh', '110ms', '12px'],
  ['seven', '49%', '50%', '-36vw', '-7vh', '60ms', '11px'],
  ['eight', '51%', '49%', '38vw', '-3vh', '190ms', '13px'],
  ['nine', '50%', '52%', '-20vw', '27vh', '220ms', '11px'],
  ['ten', '50%', '48%', '24vw', '-30vh', '140ms', '12px'],
  ['eleven', '49%', '51%', '-5vw', '20vh', '260ms', '15px'],
  ['twelve', '51%', '50%', '7vw', '-14vh', '210ms', '11px'],
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
  --curtain-depth: color-mix(in srgb, var(--color-app-bg) 46%, var(--color-accent-strong));
  --curtain-highlight: color-mix(in srgb, #fff 42%, var(--color-accent));
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
    radial-gradient(circle at 50% 46%, rgba(255, 255, 255, 0.7), var(--color-theme-glow-strong) 18%, transparent 58%),
    color-mix(in srgb, var(--color-app-bg) 78%, var(--color-accent));
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

.gallery-opening__aurora {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(72vw, 980px);
  aspect-ratio: 1.65;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(255, 255, 255, 0.94) 0 2%, var(--color-theme-glow-strong) 13%, var(--color-theme-glow) 35%, transparent 69%);
  filter: blur(10px);
  transform: translate(-50%, -50%) scale(0.08);
  animation: stage-aurora-bloom 1340ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

.gallery-opening__ray {
  position: absolute;
  top: -14vh;
  left: 50%;
  width: clamp(180px, 24vw, 430px);
  height: 132vh;
  clip-path: polygon(43% 0, 57% 0, 100% 100%, 0 100%);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8), color-mix(in srgb, var(--color-accent) 48%, transparent) 45%, transparent 88%);
  filter: blur(10px);
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
  box-shadow: 0 0 18px var(--color-theme-glow-strong);
  opacity: 0;
  filter:
    drop-shadow(0 0 1px var(--color-accent-strong))
    drop-shadow(0 0 7px var(--color-theme-glow-strong));
  transform: translate(-50%, -50%) scale(0.1);
  animation: stage-spark-flight 1240ms cubic-bezier(0.16, 1, 0.3, 1) var(--spark-delay) both;
}

.gallery-opening__spark::before,
.gallery-opening__spark::after,
.gallery-opening__spark span {
  position: absolute;
  top: 50%;
  left: 50%;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 0 12px #fff, 0 0 25px var(--color-theme-glow-strong);
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
  filter: drop-shadow(0 0 24px var(--color-theme-glow-strong));
  will-change: transform;
}

.gallery-opening__curtain.is-left {
  left: 0;
  transform-origin: 0 18%;
  animation: stage-curtain-left 1580ms linear both;
}

.gallery-opening__curtain.is-right {
  right: 0;
  transform-origin: 100% 18%;
  animation: stage-curtain-right 1580ms linear both;
}

.gallery-opening__curtain-shape {
  position: absolute;
  z-index: 0;
  inset: 0;
  width: 100%;
  height: 100%;
  fill: var(--color-accent-strong);
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
  opacity: 0.94;
  background:
    radial-gradient(ellipse at 48% 6%, var(--curtain-highlight), transparent 32%),
    repeating-linear-gradient(92deg,
      var(--curtain-depth) 0 3%,
      color-mix(in srgb, var(--color-accent) 80%, #fff) 7%,
      var(--color-accent-strong) 12%,
      color-mix(in srgb, var(--color-accent-strong) 62%, #000) 16%,
      var(--curtain-highlight) 21%,
      var(--curtain-depth) 27%),
    var(--color-accent-gradient-diagonal);
  mix-blend-mode: multiply;
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
    linear-gradient(112deg, transparent 16%, rgba(255, 255, 255, 0.38) 28%, transparent 38%),
    repeating-linear-gradient(90deg, transparent 0 7%, rgba(255, 255, 255, 0.2) 9%, transparent 13%);
  opacity: 0.5;
  mix-blend-mode: screen;
}

.gallery-opening__seam {
  z-index: 3;
  box-shadow:
    inset 0 14px 22px rgba(255, 255, 255, 0.16),
    inset 0 -20px 34px rgba(0, 0, 0, 0.16);
}

.gallery-opening__tassel {
  position: absolute;
  z-index: 4;
  top: 42%;
  width: 16px;
  height: 84px;
  border-radius: 999px 999px 8px 8px;
  background:
    repeating-linear-gradient(90deg, #fff2b2 0 2px, #c79333 3px 5px),
    linear-gradient(#f9df88, #aa741c);
  box-shadow: 0 0 16px rgba(255, 225, 132, 0.62);
  animation: stage-tassel-sway 780ms ease-in-out 350ms both;
}

.gallery-opening__tassel::before {
  position: absolute;
  top: -10px;
  left: 50%;
  width: 31px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fff2b2, #bd8120);
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
  filter: drop-shadow(0 18px 22px rgba(0, 0, 0, 0.2));
  transform-origin: center top;
  animation: stage-valance-rise 1580ms linear both;
}

.gallery-opening__valance-fabric {
  position: absolute;
  z-index: 0;
  inset: 0;
  clip-path: polygon(0 0, 100% 0, 100% 56%, 94% 68%, 88% 59%, 82% 75%, 75% 63%, 68% 81%, 60% 67%, 52% 88%, 44% 67%, 36% 81%, 29% 63%, 22% 75%, 15% 59%, 8% 68%, 0 56%);
  background:
    repeating-linear-gradient(96deg,
      var(--curtain-depth) 0 5%,
      var(--curtain-highlight) 10%,
      var(--color-accent-strong) 16%,
      color-mix(in srgb, var(--color-accent-strong) 55%, #000) 22%),
    var(--color-accent-gradient-horizontal);
  box-shadow: inset 0 -26px 34px rgba(0, 0, 0, 0.16);
}

.gallery-opening__valance-swag {
  position: absolute;
  z-index: 1;
  top: 4%;
  width: 29%;
  height: 72%;
  border-radius: 0 0 50% 50%;
  border-bottom: 2px solid rgba(255, 255, 255, 0.24);
  background: radial-gradient(ellipse at 50% 0, rgba(255, 255, 255, 0.32), transparent 63%);
  box-shadow: inset 0 -16px 22px rgba(0, 0, 0, 0.12);
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
  background: repeating-linear-gradient(90deg, #fff0ae 0 10px, #be8425 10px 19px, #ffe6a0 19px 29px);
  box-shadow: 0 2px 7px rgba(255, 231, 151, 0.58);
}

.gallery-opening__lace {
  position: absolute;
  z-index: 3;
  right: 0;
  bottom: 4%;
  left: 0;
  height: 18%;
  background:
    linear-gradient(135deg, transparent 50%, rgba(255, 241, 190, 0.96) 51%) 0 0 / 32px 100% repeat-x,
    linear-gradient(225deg, transparent 50%, rgba(198, 139, 45, 0.96) 51%) 16px 0 / 32px 100% repeat-x;
  filter: drop-shadow(0 5px 5px rgba(0, 0, 0, 0.2));
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
  0%, 12% { transform: translate3d(0, 0, 0) scaleX(1); }
  52% { transform: translate3d(-81%, 0, 0) scaleX(0.92) skewY(-1.6deg); }
  64% { transform: translate3d(-75%, 0, 0) scaleX(0.97) skewY(1deg); }
  75% { transform: translate3d(-86%, 0, 0) scaleX(0.9) skewY(-0.6deg); }
  84%, 100% { transform: translate3d(-108%, 0, 0) scaleX(0.86); }
}

@keyframes stage-curtain-right {
  0%, 12% { transform: translate3d(0, 0, 0) scaleX(1); }
  52% { transform: translate3d(81%, 0, 0) scaleX(0.92) skewY(1.6deg); }
  64% { transform: translate3d(75%, 0, 0) scaleX(0.97) skewY(-1deg); }
  75% { transform: translate3d(86%, 0, 0) scaleX(0.9) skewY(0.6deg); }
  84%, 100% { transform: translate3d(108%, 0, 0) scaleX(0.86); }
}

@keyframes stage-valance-rise {
  0%, 22% { transform: translate3d(0, 0, 0) scaleY(1); }
  64% { transform: translate3d(0, -72%, 0) scaleY(0.93); }
  73% { transform: translate3d(0, -66%, 0) scaleY(0.97); }
  86%, 100% { transform: translate3d(0, -112%, 0) scaleY(0.9); }
}

@keyframes stage-aurora-bloom {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) scale(0.08); }
  38% { opacity: 1; transform: translate(-50%, -50%) scale(0.7); }
  72% { opacity: 0.72; transform: translate(-50%, -50%) scale(1.14); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
}

@keyframes stage-ray-reveal {
  0%, 18% { opacity: 0; filter: blur(18px); }
  42% { opacity: 0.68; filter: blur(8px); }
  78% { opacity: 0.38; }
  100% { opacity: 0; filter: blur(14px); }
}

@keyframes stage-spark-flight {
  0%, 18% { opacity: 0; transform: translate(-50%, -50%) scale(0.1) rotate(0deg); }
  34% { opacity: 1; transform: translate(-50%, -50%) scale(1.15) rotate(45deg); }
  78%, 100% {
    opacity: 0;
    transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(0.6) rotate(135deg);
  }
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

  .gallery-opening__aurora {
    top: 38%;
    width: 110vw;
    animation-duration: 980ms;
  }

  .gallery-opening__ray {
    top: -22vh;
    width: 58vw;
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
    background: var(--color-accent-gradient-vertical);
    box-shadow:
      inset 0 -38px 58px rgba(0, 0, 0, 0.2),
      0 18px 50px rgba(0, 0, 0, 0.26),
      0 0 40px var(--color-theme-glow-strong);
    transform-origin: 50% 0;
    animation: mobile-stage-lid-rise 1100ms linear both;
  }

  .gallery-opening__mobile-fabric {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse at 50% 8%, rgba(255, 255, 255, 0.42), transparent 32%),
      repeating-linear-gradient(90deg,
        var(--curtain-depth) 0 8%,
        var(--curtain-highlight) 13%,
        var(--color-accent-strong) 20%,
        color-mix(in srgb, var(--color-accent-strong) 58%, #000) 27%,
        var(--curtain-highlight) 34%);
    opacity: 0.88;
    mix-blend-mode: multiply;
  }

  .gallery-opening__mobile-scallops {
    position: absolute;
    right: 0;
    bottom: 5.5%;
    left: 0;
    height: 62px;
    background:
      radial-gradient(circle at 25px 0, transparent 24px, rgba(255, 239, 181, 0.94) 25px 29px, transparent 30px) 0 0 / 50px 100% repeat-x;
    opacity: 0.85;
  }

  .gallery-opening__mobile-rim {
    position: absolute;
    right: 0;
    bottom: 5.2%;
    left: 0;
    height: 16px;
    background: linear-gradient(180deg, #fff8cf, #e2ad49 42%, #a66e18 76%, rgba(255, 244, 195, 0.88));
    box-shadow:
      0 3px 8px rgba(0, 0, 0, 0.3),
      0 0 18px rgba(255, 235, 170, 0.84),
      0 0 38px var(--color-theme-glow-strong);
  }

  .gallery-opening__mobile-handle {
    position: absolute;
    bottom: 2.5%;
    left: 50%;
    width: 84px;
    height: 28px;
    border: 5px solid #f9dc85;
    border-bottom: 0;
    border-radius: 999px 999px 0 0;
    background: color-mix(in srgb, var(--color-accent) 72%, #fff);
    box-shadow: 0 0 16px rgba(255, 229, 143, 0.7);
    transform: translateX(-50%);
  }
}

@keyframes mobile-stage-lid-rise {
  0%, 16% { transform: translate3d(0, 0, 0) scaleY(1); }
  56% { transform: translate3d(0, -72%, 0) scaleY(0.96); }
  68% { transform: translate3d(0, -66%, 0) scaleY(0.99); }
  82%, 100% { transform: translate3d(0, -112%, 0) scaleY(0.92); }
}

@keyframes mobile-stage-backdrop-release {
  0%, 16% { opacity: 1; }
  78%, 100% { opacity: 0; }
}

html[data-motion="reduce"] .gallery-opening {
  display: none;
}
</style>
