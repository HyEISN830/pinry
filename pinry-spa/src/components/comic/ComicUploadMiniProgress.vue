<template>
  <div class="comic-upload-mini" :class="statusClass">
    <div class="comic-upload-mini__meta">
      <span>{{ statusText }}</span>
      <strong v-if="showPercent">{{ normalizedProgress }}%</strong>
    </div>
    <div
      class="comic-upload-mini__track"
      :class="{ 'is-indeterminate': status === 'uploading' && progress === null }"
      role="progressbar"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="showPercent ? normalizedProgress : null"
      :aria-label="statusText">
      <span
        class="comic-upload-mini__fill"
        :style="progressStyle">
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComicUploadMiniProgress',
  props: {
    progress: {
      type: Number,
      default: null,
    },
    status: {
      type: String,
      default: 'queued',
    },
  },
  computed: {
    normalizedProgress() {
      if (this.status === 'complete') {
        return 100;
      }
      return Math.min(100, Math.max(0, Math.round(this.progress || 0)));
    },
    showPercent() {
      return this.status === 'complete'
        || (this.status === 'uploading' && this.progress !== null);
    },
    progressStyle() {
      return { width: `${this.normalizedProgress}%` };
    },
    statusClass() {
      return `is-${this.status}`;
    },
    statusText() {
      if (this.status === 'complete') {
        return this.$t('imageUploadComplete');
      }
      if (this.status === 'failed') {
        return this.$t('imageUploadFailed');
      }
      if (this.status === 'uploading') {
        return this.$t('imageUploadInProgress');
      }
      return this.$t('imageUploadQueued');
    },
  },
};
</script>

<style lang="scss" scoped>
.comic-upload-mini {
  --comic-upload-progress: 0%;
  --comic-upload-danger: #c43f62;
  display: grid;
  min-width: 0;
  gap: var(--space-2xs);
}
.comic-upload-mini__meta {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs);
  color: var(--color-text-muted);
  font-size: 0.68rem;
  font-weight: 800;
}
.comic-upload-mini__meta span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comic-upload-mini__meta strong {
  color: var(--color-accent-strong);
  font-size: 0.7rem;
}
.comic-upload-mini__track {
  position: relative;
  height: 6px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--color-line-soft) 72%, transparent);
  border-radius: var(--radius-pill);
  background: color-mix(in srgb, var(--color-surface-1) 66%, transparent);
  box-shadow: inset 0 1px 3px color-mix(in srgb, var(--color-text-strong) 8%, transparent);
}
.comic-upload-mini__fill {
  position: absolute;
  inset: 0 auto 0 0;
  min-width: 0;
  overflow: hidden;
  border-radius: inherit;
  background: var(--color-accent-progress);
  box-shadow: 0 0 12px var(--color-theme-glow-strong);
  transition: width 320ms var(--motion-ease-emphasized);
}
.comic-upload-mini__fill::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    color-mix(in srgb, var(--color-accent-text) 82%, transparent),
    transparent
  );
  content: '';
  transform: translateX(-120%);
  animation: comic-upload-mini-shimmer 1.15s ease-in-out infinite;
}
.comic-upload-mini__track.is-indeterminate .comic-upload-mini__fill {
  width: 38% !important;
  animation: comic-upload-mini-sweep 1.35s var(--motion-ease-emphasized) infinite;
}
.comic-upload-mini.is-complete .comic-upload-mini__track {
  border-color: var(--color-accent-border);
}
.comic-upload-mini.is-failed .comic-upload-mini__meta {
  color: var(--comic-upload-danger);
}
.comic-upload-mini.is-failed .comic-upload-mini__fill {
  width: 100% !important;
  background: var(--comic-upload-danger);
  box-shadow: 0 0 10px color-mix(in srgb, var(--comic-upload-danger) 38%, transparent);
}
@keyframes comic-upload-mini-shimmer {
  to { transform: translateX(120%); }
}
@keyframes comic-upload-mini-sweep {
  from { left: -42%; }
  to { left: 104%; }
}
html[data-motion='reduce'] .comic-upload-mini__fill,
html[data-motion='reduce'] .comic-upload-mini__fill::after {
  animation: none;
  transition: none;
}
</style>
