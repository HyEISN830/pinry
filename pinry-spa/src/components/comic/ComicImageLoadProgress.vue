<template>
  <div
    class="comic-image-load-progress"
    :class="{ 'is-indeterminate': normalizedProgress === null }"
    :style="progressStyle"
    role="status"
    aria-live="polite">
    <div class="comic-image-load-progress__visual" aria-hidden="true"></div>
    <div class="comic-image-load-progress__body">
      <div class="comic-image-load-progress__headline">
        <p>{{ $t("imageLoadingText") }}</p>
        <strong>{{ normalizedProgress === null ? '...' : `${normalizedProgress}%` }}</strong>
      </div>
      <div
        class="comic-image-load-progress__track"
        role="progressbar"
        :aria-valuenow="normalizedProgress"
        aria-valuemin="0"
        aria-valuemax="100">
        <span class="comic-image-load-progress__fill"></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComicImageLoadProgress',
  props: {
    progress: {
      type: Number,
      default: null,
    },
  },
  computed: {
    normalizedProgress() {
      if (!Number.isFinite(this.progress)) {
        return null;
      }
      return Math.min(100, Math.max(0, Math.round(this.progress)));
    },
    progressStyle() {
      const progress = this.normalizedProgress === null ? 32 : this.normalizedProgress;
      return {
        '--comic-image-load-progress': `${progress}%`,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.comic-image-load-progress {
  --comic-image-load-progress: 0%;
  position: absolute;
  z-index: 3;
  right: 12px;
  bottom: 12px;
  left: 12px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 0.76rem;
  align-items: center;
  max-width: 390px;
  margin: 0 auto;
  padding: 0.72rem 0.82rem;
  overflow: hidden;
  color: var(--color-text-strong);
  text-align: left;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  background:
    radial-gradient(circle at 8% 5%, var(--color-theme-glow-strong), transparent 68%),
    color-mix(in srgb, var(--color-surface-card) 84%, transparent);
  backdrop-filter: blur(14px) saturate(1.12);
  box-shadow:
    0 14px 34px color-mix(in srgb, var(--color-theme-glow) 48%, transparent),
    var(--shadow-sm);
}
.comic-image-load-progress::before {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(112deg, transparent 22%, color-mix(in srgb, var(--color-surface-card) 68%, transparent) 47%, transparent 72%);
  content: '';
  opacity: 0.76;
  pointer-events: none;
  transform: translateX(-115%);
  animation: comic-image-loading-sheen 2.8s var(--motion-ease-standard) infinite;
}
.comic-image-load-progress__visual {
  position: relative;
  z-index: 1;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: conic-gradient(
    from -90deg,
    var(--color-accent-strong) 0 var(--comic-image-load-progress),
    var(--color-accent-soft) var(--comic-image-load-progress) 100%
  );
  box-shadow:
    0 0 0 1px var(--color-accent-border),
    0 0 22px var(--color-theme-glow);
}
.comic-image-load-progress__visual::before,
.comic-image-load-progress__visual::after {
  position: absolute;
  border-radius: inherit;
  content: '';
}
.comic-image-load-progress__visual::before {
  inset: 4px;
  background: color-mix(in srgb, var(--color-surface-card) 84%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--color-accent-border) 54%, transparent);
}
.comic-image-load-progress__visual::after {
  inset: 13px;
  background: var(--color-accent-strong);
  box-shadow: 0 0 15px var(--color-theme-glow-strong);
  animation: comic-image-loading-core 1.5s var(--motion-ease-standard) infinite;
}
.comic-image-load-progress__body {
  position: relative;
  z-index: 1;
  min-width: 0;
}
.comic-image-load-progress__headline {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-xs);
}
.comic-image-load-progress__headline p,
.comic-image-load-progress__headline strong {
  margin: 0;
}
.comic-image-load-progress__headline p {
  overflow: hidden;
  color: var(--color-text-strong);
  font-size: 0.82rem;
  font-weight: 780;
  letter-spacing: 0;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comic-image-load-progress__headline strong {
  flex: 0 0 auto;
  color: var(--color-accent-strong);
  font-size: 0.84rem;
  font-variant-numeric: tabular-nums;
}
.comic-image-load-progress__track {
  position: relative;
  height: 6px;
  margin-top: 0.48rem;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--color-accent-border) 74%, transparent);
  border-radius: var(--radius-pill);
  background: color-mix(in srgb, var(--color-accent-soft) 60%, transparent);
  box-shadow: inset 0 1px 3px color-mix(in srgb, var(--color-text-strong) 12%, transparent);
}
.comic-image-load-progress__fill {
  position: relative;
  display: block;
  width: var(--comic-image-load-progress);
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-strong), var(--color-accent));
  box-shadow: 0 0 14px var(--color-theme-glow-strong);
  transition: width 360ms var(--motion-ease-emphasized);
}
.comic-image-load-progress__fill::after {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 42%;
  background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--color-accent-text) 76%, transparent), transparent);
  content: '';
  transform: translateX(-180%);
  animation: comic-image-loading-shimmer 1.35s ease-in-out infinite;
}
.comic-image-load-progress.is-indeterminate .comic-image-load-progress__visual {
  animation: comic-image-loading-orbit 1.35s linear infinite;
}
.comic-image-load-progress.is-indeterminate .comic-image-load-progress__fill {
  width: 42%;
  animation: comic-image-loading-sweep 1.65s var(--motion-ease-emphasized) infinite;
}
@keyframes comic-image-loading-sheen {
  0%,
  28% {
    transform: translateX(-115%);
  }
  62%,
  100% {
    transform: translateX(125%);
  }
}
@keyframes comic-image-loading-core {
  0%,
  100% {
    opacity: 0.65;
    transform: scale(0.82);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes comic-image-loading-shimmer {
  from {
    transform: translateX(-180%);
  }
  to {
    transform: translateX(340%);
  }
}
@keyframes comic-image-loading-orbit {
  to {
    transform: rotate(360deg);
  }
}
@keyframes comic-image-loading-sweep {
  0% {
    transform: translateX(-125%);
  }
  52% {
    transform: translateX(145%);
  }
  100% {
    transform: translateX(245%);
  }
}
@media screen and (max-width: 542px) {
  .comic-image-load-progress {
    right: 8px;
    bottom: 8px;
    left: 8px;
    grid-template-columns: 38px minmax(0, 1fr);
    gap: 0.62rem;
    padding: 0.62rem 0.68rem;
  }
  .comic-image-load-progress__visual {
    width: 38px;
    height: 38px;
  }
  .comic-image-load-progress__visual::after {
    inset: 11px;
  }
}
html[data-motion='reduce'] .comic-image-load-progress::before,
html[data-motion='reduce'] .comic-image-load-progress__visual,
html[data-motion='reduce'] .comic-image-load-progress__visual::after,
html[data-motion='reduce'] .comic-image-load-progress__fill,
html[data-motion='reduce'] .comic-image-load-progress__fill::after {
  animation: none !important;
  transition: none;
}
</style>
