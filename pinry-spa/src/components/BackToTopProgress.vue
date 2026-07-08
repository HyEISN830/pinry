<template>
  <button
    v-show="visible"
    class="back-to-top"
    :class="{ 'is-complete': progress >= 0.995 }"
    type="button"
    :aria-label="$t('backToTopButton')"
    :title="$t('backToTopButton')"
    :style="buttonStyle"
    @click="scrollToTop">
    &uarr;
  </button>
</template>

<script>
export default {
  name: 'BackToTopProgress',
  data() {
    return {
      progress: 0,
      scrollAnimationFrame: null,
      ticking: false,
      visible: false,
    };
  },
  computed: {
    buttonStyle() {
      const progressDegrees = this.progress * 360;
      return {
        '--scroll-progress': `${progressDegrees}deg`,
        '--scroll-progress-mid': `${this.progress * 210}deg`,
      };
    },
  },
  mounted() {
    this.updateProgress();
    window.addEventListener('scroll', this.requestUpdate, { passive: true });
    window.addEventListener('resize', this.requestUpdate);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.requestUpdate);
    window.removeEventListener('resize', this.requestUpdate);
    if (this.scrollAnimationFrame) {
      window.cancelAnimationFrame(this.scrollAnimationFrame);
    }
  },
  methods: {
    requestUpdate() {
      if (this.ticking) {
        return;
      }
      this.ticking = true;
      window.requestAnimationFrame(
        () => {
          this.ticking = false;
          this.updateProgress();
        },
      );
    },
    scrollToTop() {
      const startTop = window.pageYOffset
        || document.documentElement.scrollTop
        || 0;
      const duration = window.innerWidth > 760 ? 520 : 360;
      const startedAt = Date.now();
      if (this.scrollAnimationFrame) {
        window.cancelAnimationFrame(this.scrollAnimationFrame);
      }
      const step = () => {
        const elapsed = Date.now() - startedAt;
        const percent = Math.min(1, elapsed / duration);
        window.scrollTo({
          top: Math.round(startTop * (1 - percent)),
          behavior: 'auto',
        });
        if (percent < 1) {
          this.scrollAnimationFrame = window.requestAnimationFrame(step);
          return;
        }
        window.scrollTo({
          top: 0,
          behavior: 'auto',
        });
        this.scrollAnimationFrame = null;
      };
      this.scrollAnimationFrame = window.requestAnimationFrame(step);
    },
    updateProgress() {
      const { body, documentElement: doc } = document;
      const scrollHeight = Math.max(
        doc.scrollHeight,
        body ? body.scrollHeight : 0,
      );
      const maxScroll = Math.max(0, scrollHeight - window.innerHeight);
      const scrollTop = window.pageYOffset || doc.scrollTop || 0;
      this.progress = maxScroll === 0
        ? 0
        : Math.min(1, Math.max(0, scrollTop / maxScroll));
      this.visible = scrollTop > 120 && maxScroll > 0;
    },
  },
};
</script>

<style lang="scss" scoped>
.back-to-top {
  position: fixed;
  z-index: 70;
  right: clamp(1rem, 3vw, 2rem);
  bottom: clamp(1rem, 3vw, 2rem);
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 0;
  border-radius: 50%;
  color: var(--text-strong, #22313f);
  background:
    linear-gradient(var(--surface-1, #fff), var(--surface-1, #fff)) padding-box,
    conic-gradient(
      from -90deg,
      var(--scroll-ring-start, #ff9fd0) 0deg,
      var(--scroll-ring-mid, #ef7cba) var(--scroll-progress-mid),
      var(--scroll-ring-end, #db4e9c) var(--scroll-progress),
      var(--scroll-ring-track, #e5eaf2) var(--scroll-progress) 360deg
    ) border-box;
  border: 3px solid transparent;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.2);
  cursor: pointer;
  font-size: 1.35rem;
  font-weight: 900;
  line-height: 1;
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}
.back-to-top.is-complete {
  background:
    linear-gradient(var(--surface-1, #fff), var(--surface-1, #fff)) padding-box,
    conic-gradient(
      from -90deg,
      var(--scroll-ring-start, #ff9fd0) 0deg,
      var(--scroll-ring-mid, #ef7cba) 38%,
      var(--scroll-ring-end, #db4e9c) 68%,
      var(--scroll-ring-start, #ff9fd0) 100%
    ) border-box;
}
/*
  Legacy build targets render conic gradients more consistently when the
  completed state avoids an immediate fallback track color at the seam.
*/
.back-to-top:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.26);
  filter: saturate(1.04);
}
@media screen and (max-width: 542px) {
  .back-to-top {
    width: 44px;
    height: 44px;
    right: 0.9rem;
    bottom: 0.9rem;
  }
}
</style>
