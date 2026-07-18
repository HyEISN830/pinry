<template>
  <div
    v-if="visible"
    :key="animationKey"
    class="gallery-page-opening"
    aria-hidden="true"
    @touchmove.prevent
    @wheel.prevent>
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
    this.motionObserver = null;
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
    this.observeMotionPreference();
    if (this.visible) {
      this.startRenderer();
      this.scheduleHide();
    }
  },
  beforeDestroy() {
    this.playGeneration += 1;
    this.clearHideTimer();
    this.stopObservingMotionPreference();
    this.stopRenderer();
  },
  methods: {
    observeMotionPreference() {
      if (typeof window === 'undefined' || !window.MutationObserver) {
        return;
      }
      this.motionObserver = new window.MutationObserver(
        this.handleMotionPreferenceChange,
      );
      this.motionObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-motion'],
      });
    },
    stopObservingMotionPreference() {
      if (!this.motionObserver) {
        return;
      }
      this.motionObserver.disconnect();
      this.motionObserver = null;
    },
    handleMotionPreferenceChange() {
      if (!motionPreference.isReducedMotionEnabled()) {
        return;
      }
      this.playGeneration += 1;
      this.clearHideTimer();
      this.stopRenderer();
      this.visible = false;
    },
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
  position: fixed;
  z-index: var(--z-page-opening, 1000);
  inset: 0;
  contain: layout paint;
  isolation: isolate;
  overflow: hidden;
  pointer-events: auto;
  touch-action: none;
}

.gallery-page-opening__stage {
  position: absolute;
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

html[data-motion="reduce"] .gallery-page-opening {
  display: none;
}
</style>
