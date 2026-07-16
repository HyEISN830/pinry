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
      <span class="gallery-page-opening__edge"></span>
    </div>
    <div class="gallery-page-opening__curtain is-end">
      <span class="gallery-page-opening__weave"></span>
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
    </div>
  </div>
</template>

<script>
import motionPreference from '../utils/motionPreference';

const OPENING_DURATION = 1080;

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
  position: fixed;
  z-index: var(--z-page-opening, 1000);
  inset: 0;
  isolation: isolate;
  overflow: hidden;
  pointer-events: auto;
  touch-action: none;
  animation: gallery-opening-visibility 1080ms linear both;
}

.gallery-page-opening__curtain {
  position: absolute;
  z-index: 1;
  top: 0;
  bottom: 0;
  width: calc(50% + 2px);
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 32%, var(--color-theme-glow-strong), transparent 56%),
    var(--color-accent-gradient-diagonal),
    var(--color-app-bg);
  box-shadow: inset 0 0 90px color-mix(in srgb, var(--color-app-bg) 52%, transparent);
  will-change: transform;
}

.gallery-page-opening__curtain.is-start {
  left: 0;
  transform-origin: left center;
  animation: gallery-curtain-start 1080ms linear both;
}

.gallery-page-opening__curtain.is-end {
  right: 0;
  transform-origin: right center;
  animation: gallery-curtain-end 1080ms linear both;
}

.gallery-page-opening__weave {
  position: absolute;
  inset: 0;
  opacity: 0.28;
  background:
    repeating-linear-gradient(92deg, transparent 0 14px, rgba(255, 255, 255, 0.16) 15px, transparent 17px),
    repeating-linear-gradient(0deg, transparent 0 4px, color-mix(in srgb, var(--color-app-bg) 24%, transparent) 5px, transparent 7px);
  mix-blend-mode: soft-light;
}

.gallery-page-opening__edge {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 16px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.92), var(--color-accent), transparent);
  filter: blur(2px);
  box-shadow:
    0 0 20px rgba(255, 255, 255, 0.84),
    0 0 42px var(--color-theme-glow-strong);
}

.is-start .gallery-page-opening__edge {
  right: -7px;
}

.is-end .gallery-page-opening__edge {
  left: -7px;
  transform: scaleX(-1);
}

.gallery-page-opening__stage {
  position: absolute;
  z-index: 2;
  inset: 0;
  pointer-events: none;
}

.gallery-page-opening__halo,
.gallery-page-opening__prism,
.gallery-page-opening__beam,
.gallery-page-opening__spark {
  position: absolute;
  top: 50%;
  left: 50%;
}

.gallery-page-opening__halo {
  width: min(52vw, 680px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.96) 0 3%, var(--color-theme-glow-strong) 13%, var(--color-theme-glow) 34%, transparent 68%);
  filter: blur(5px);
  transform: translate(-50%, -50%);
  animation: gallery-halo-bloom 920ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__prism {
  width: 70px;
  aspect-ratio: 1;
  border: 1px solid rgba(255, 255, 255, 0.88);
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), transparent 42%),
    var(--color-accent-gradient-diagonal);
  box-shadow:
    0 0 22px rgba(255, 255, 255, 0.86),
    0 0 64px var(--color-theme-glow-strong);
  transform: translate(-50%, -50%) rotate(45deg);
  animation: gallery-prism-release 940ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__beam {
  width: max(145vw, 145vh);
  height: 3px;
  background: linear-gradient(90deg, transparent 8%, var(--color-accent) 36%, #fff 50%, var(--color-accent-strong) 64%, transparent 92%);
  box-shadow:
    0 0 14px rgba(255, 255, 255, 0.9),
    0 0 28px var(--color-theme-glow-strong);
  transform-origin: center;
}

.gallery-page-opening__beam.is-primary {
  transform: translate(-50%, -50%);
  animation: gallery-beam-primary 900ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__beam.is-secondary {
  height: 1px;
  opacity: 0.72;
  transform: translate(-50%, -50%) rotate(90deg);
  animation: gallery-beam-secondary 900ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__spark {
  width: 7px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #fff;
  box-shadow:
    0 0 12px rgba(255, 255, 255, 0.94),
    0 0 24px var(--color-theme-glow-strong);
  animation: gallery-spark-flight 920ms var(--motion-ease-emphasized) both;
}

.gallery-page-opening__spark.is-one { --spark-x: -31vw; --spark-y: -22vh; animation-delay: 40ms; }
.gallery-page-opening__spark.is-two { --spark-x: 35vw; --spark-y: -17vh; animation-delay: 90ms; }
.gallery-page-opening__spark.is-three { --spark-x: -38vw; --spark-y: 24vh; animation-delay: 120ms; }
.gallery-page-opening__spark.is-four { --spark-x: 29vw; --spark-y: 28vh; animation-delay: 70ms; }

@keyframes gallery-opening-visibility {
  0%, 90% { visibility: visible; }
  100% { visibility: hidden; }
}

@keyframes gallery-curtain-start {
  0%, 14% {
    transform: translate3d(0, 0, 0) scaleX(1);
    animation-timing-function: cubic-bezier(0.45, 0, 0.55, 1);
  }
  78%, 100% { transform: translate3d(-104%, 0, 0) scaleX(0.88); }
}

@keyframes gallery-curtain-end {
  0%, 14% {
    transform: translate3d(0, 0, 0) scaleX(1);
    animation-timing-function: cubic-bezier(0.45, 0, 0.55, 1);
  }
  78%, 100% { transform: translate3d(104%, 0, 0) scaleX(0.88); }
}

@keyframes gallery-halo-bloom {
  0%, 14% { opacity: 0; transform: translate(-50%, -50%) scale(0.06); }
  34% { opacity: 1; transform: translate(-50%, -50%) scale(0.58); }
  78%, 100% { opacity: 0; transform: translate(-50%, -50%) scale(1.65); }
}

@keyframes gallery-prism-release {
  0%, 12% { opacity: 0; transform: translate(-50%, -50%) rotate(45deg) scale(0.28); }
  32% { opacity: 1; transform: translate(-50%, -50%) rotate(135deg) scale(1); }
  68%, 100% { opacity: 0; transform: translate(-50%, -50%) rotate(225deg) scale(1.72); }
}

@keyframes gallery-beam-primary {
  0%, 18% { opacity: 0; transform: translate(-50%, -50%) scaleX(0.02); }
  38% { opacity: 1; transform: translate(-50%, -50%) scaleX(0.72); }
  76%, 100% { opacity: 0; transform: translate(-50%, -50%) scaleX(1); }
}

@keyframes gallery-beam-secondary {
  0%, 22% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.02); }
  42% { opacity: 0.72; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.48); }
  74%, 100% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.86); }
}

@keyframes gallery-spark-flight {
  0%, 20% { opacity: 0; transform: translate(-50%, -50%) scale(0.2); }
  38% { opacity: 1; }
  78%, 100% { opacity: 0; transform: translate(calc(-50% + var(--spark-x)), calc(-50% + var(--spark-y))) scale(1.25); }
}

@media screen and (orientation: portrait) {
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

  .gallery-page-opening__curtain.is-end {
    top: auto;
    bottom: 0;
    transform-origin: center bottom;
    animation-name: gallery-lid-end;
  }

  .gallery-page-opening__edge {
    right: 0;
    left: 0;
    width: auto;
    height: 16px;
    background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.92), var(--color-accent), transparent);
  }

  .is-start .gallery-page-opening__edge {
    top: auto;
    right: 0;
    bottom: -7px;
  }

  .is-end .gallery-page-opening__edge {
    top: -7px;
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
    width: min(86vw, 560px);
  }

  .gallery-page-opening__prism {
    width: 58px;
  }
}

@keyframes gallery-lid-start {
  0%, 14% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.45, 0, 0.55, 1);
  }
  78%, 100% { transform: translate3d(0, -104%, 0) scaleY(0.88); }
}

@keyframes gallery-lid-end {
  0%, 14% {
    transform: translate3d(0, 0, 0) scaleY(1);
    animation-timing-function: cubic-bezier(0.45, 0, 0.55, 1);
  }
  78%, 100% { transform: translate3d(0, 104%, 0) scaleY(0.88); }
}

@keyframes gallery-beam-portrait {
  0%, 18% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.02); }
  38% { opacity: 1; transform: translate(-50%, -50%) rotate(90deg) scaleX(0.72); }
  76%, 100% { opacity: 0; transform: translate(-50%, -50%) rotate(90deg) scaleX(1); }
}

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
