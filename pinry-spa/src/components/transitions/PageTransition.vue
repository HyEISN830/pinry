<template>
  <div class="page-transition-shell">
    <transition name="page-reveal" mode="out-in" appear>
      <div :key="routeKey" class="page-transition-content">
        <slot></slot>
      </div>
    </transition>
    <transition name="route-curtain">
      <div v-if="curtainVisible" class="route-curtain" aria-hidden="true">
        <span></span>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'PageTransition',
  props: {
    routeKey: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      curtainTimer: null,
      curtainVisible: false,
    };
  },
  watch: {
    routeKey(next, previous) {
      if (!previous || next === previous) {
        return;
      }
      this.showCurtain();
    },
  },
  mounted() {
    this.showCurtain();
  },
  beforeDestroy() {
    if (this.curtainTimer) {
      window.clearTimeout(this.curtainTimer);
    }
  },
  methods: {
    showCurtain() {
      if (window.matchMedia
        && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
      }
      this.curtainVisible = false;
      this.$nextTick(() => {
        this.curtainVisible = true;
        if (this.curtainTimer) {
          window.clearTimeout(this.curtainTimer);
        }
        this.curtainTimer = window.setTimeout(() => {
          this.curtainVisible = false;
          this.curtainTimer = null;
        }, 360);
      });
    },
  },
};
</script>

<style scoped lang="scss">
.page-transition-shell,
.page-transition-content {
  min-height: calc(100vh - var(--nav-height));
}

.route-curtain {
  position: fixed;
  z-index: calc(var(--z-nav, 80) - 1);
  top: var(--nav-height);
  right: 0;
  bottom: 0;
  left: 0;
  overflow: hidden;
  pointer-events: none;
  background:
    radial-gradient(circle at 16% 12%, var(--color-theme-glow-strong), transparent 34%),
    linear-gradient(110deg, var(--color-accent-soft), transparent 58%);
}

.route-curtain span {
  position: absolute;
  top: 0;
  bottom: 0;
  left: -24%;
  width: 44%;
  background: linear-gradient(100deg, transparent, var(--color-accent), transparent);
  filter: blur(18px);
  opacity: 0.42;
  transform: skewX(-14deg);
}

.route-curtain-enter-active,
.route-curtain-leave-active {
  transition: opacity 180ms var(--motion-ease-standard);
}

.route-curtain-enter-active .route-curtain span {
  animation: route-curtain-sweep 340ms var(--motion-ease-emphasized) both;
}

.route-curtain-enter,
.route-curtain-leave-to {
  opacity: 0;
}

@keyframes route-curtain-sweep {
  from { transform: translate3d(-30%, 0, 0) skewX(-14deg); }
  to { transform: translate3d(330%, 0, 0) skewX(-14deg); }
}

@media (prefers-reduced-motion: reduce) {
  .route-curtain {
    display: none;
  }
}
</style>
