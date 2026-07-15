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
      scrollBehaviorSnapshot: null,
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
    this.restoreScrollBehavior();
  },
  methods: {
    disableSmoothScroll() {
      if (this.scrollBehaviorSnapshot !== null) {
        return;
      }
      const { body, documentElement: doc } = document;
      this.scrollBehaviorSnapshot = {
        body: body ? body.style.scrollBehavior : null,
        doc: doc.style.scrollBehavior,
      };
      doc.style.scrollBehavior = 'auto';
      if (body) {
        body.style.scrollBehavior = 'auto';
      }
    },
    restoreScrollBehavior() {
      if (this.scrollBehaviorSnapshot === null) {
        return;
      }
      const { body, documentElement: doc } = document;
      doc.style.scrollBehavior = this.scrollBehaviorSnapshot.doc;
      if (body && this.scrollBehaviorSnapshot.body !== null) {
        body.style.scrollBehavior = this.scrollBehaviorSnapshot.body;
      }
      this.scrollBehaviorSnapshot = null;
    },
    setScrollTop(top) {
      const { body, documentElement: doc } = document;
      doc.scrollTop = top;
      if (body) {
        body.scrollTop = top;
      }
      window.scrollTo(0, top);
    },
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
      if (startTop <= 0) {
        return;
      }
      const duration = Math.min(
        900,
        Math.max(320, startTop / 3.2),
      );
      const startedAt = window.performance.now();
      if (this.scrollAnimationFrame) {
        window.cancelAnimationFrame(this.scrollAnimationFrame);
      }
      this.disableSmoothScroll();
      const step = (now) => {
        const elapsed = now - startedAt;
        const percent = Math.min(1, elapsed / duration);
        this.setScrollTop(Math.round(startTop * (1 - percent)));
        if (percent < 1) {
          this.scrollAnimationFrame = window.requestAnimationFrame(step);
          return;
        }
        this.setScrollTop(0);
        this.scrollAnimationFrame = null;
        this.restoreScrollBehavior();
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
      from 0deg,
      var(--accent, #ef7cba) 0deg,
      var(--accent-strong, #d94691) var(--scroll-progress),
      var(--line-soft, #e5eaf2) var(--scroll-progress),
      var(--line-soft, #e5eaf2) 360deg
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
      from 0deg,
      var(--accent, #ef7cba) 0deg,
      var(--accent-strong, #d94691) 360deg
    ) border-box;
}
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
