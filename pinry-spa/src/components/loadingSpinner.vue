<template>
  <transition name="app-loader-fade">
    <div
      v-if="show"
      class="app-loader"
      :class="`is-${size}`"
      role="status"
      aria-live="polite"
      :aria-label="label">
      <span class="app-loader__orbit" aria-hidden="true">
        <span class="app-loader__ring is-outer"></span>
        <span class="app-loader__ring is-inner"></span>
        <span class="app-loader__core"></span>
      </span>
      <span class="app-loader__screen-reader">{{ label }}</span>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'loadingSpinner',
  props: {
    label: {
      type: String,
      default: 'Loading',
    },
    show: {
      type: Boolean,
      default: false,
    },
    size: {
      type: String,
      default: 'regular',
      validator: value => ['compact', 'regular', 'large'].indexOf(value) >= 0,
    },
  },
};
</script>

<style lang="scss" scoped>
.app-loader {
  --app-loader-size: 68px;
  display: grid;
  min-height: 132px;
  padding: var(--space-md);
  place-items: center;
}
.app-loader.is-compact {
  --app-loader-size: 42px;
  min-height: 70px;
  padding: var(--space-xs);
}
.app-loader.is-large {
  --app-loader-size: 82px;
  min-height: 172px;
  padding: var(--space-xl);
}
.app-loader__orbit {
  position: relative;
  display: block;
  width: var(--app-loader-size);
  height: var(--app-loader-size);
  border-radius: 50%;
  filter: drop-shadow(0 10px 18px var(--color-theme-glow));
}
.app-loader__ring,
.app-loader__core {
  position: absolute;
  display: block;
  border-radius: 50%;
}
.app-loader__ring.is-outer {
  inset: 0;
  border: max(2px, calc(var(--app-loader-size) * 0.04)) solid var(--color-accent-soft);
  border-top-color: var(--color-accent);
  border-right-color: var(--color-accent-strong);
  animation: app-loader-orbit 1.2s linear infinite;
}
.app-loader__ring.is-inner {
  inset: 19%;
  border: max(1px, calc(var(--app-loader-size) * 0.026)) solid var(--color-accent-border);
  border-bottom-color: var(--color-accent-strong);
  border-left-color: var(--color-accent);
  opacity: 0.92;
  animation: app-loader-orbit-reverse 1.7s linear infinite;
}
.app-loader__core {
  inset: 40%;
  background: var(--color-accent-fill);
  box-shadow:
    0 0 0 calc(var(--app-loader-size) * 0.045) var(--color-accent-soft),
    0 0 calc(var(--app-loader-size) * 0.31) var(--color-theme-glow-strong);
  animation: app-loader-core 1.35s var(--motion-ease-standard) infinite;
}
.app-loader__screen-reader {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.app-loader-fade-enter-active,
.app-loader-fade-leave-active {
  transition:
    opacity var(--motion-duration-standard) var(--motion-ease-standard),
    transform var(--motion-duration-standard) var(--motion-ease-emphasized);
}
.app-loader-fade-enter,
.app-loader-fade-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.94);
}
@keyframes app-loader-orbit {
  to {
    transform: rotate(360deg);
  }
}
@keyframes app-loader-orbit-reverse {
  to {
    transform: rotate(-360deg);
  }
}
@keyframes app-loader-core {
  0%,
  100% {
    opacity: 0.6;
    transform: scale(0.76);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
html[data-motion='reduce'] .app-loader__ring,
html[data-motion='reduce'] .app-loader__core {
  animation: none;
}
html[data-motion='reduce'] .app-loader-fade-enter-active,
html[data-motion='reduce'] .app-loader-fade-leave-active {
  transition: none;
}
</style>
