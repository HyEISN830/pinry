<template>
  <div
    class="home-collection-stat"
    :class="`is-${kind}`"
    role="status"
    aria-live="polite"
    tabindex="0">
    <span class="home-collection-stat__art" aria-hidden="true">
      <span class="home-collection-stat__icon">
        <ComicIcon v-if="kind === 'comic'"></ComicIcon>
        <b-icon v-else icon="palette" custom-size="mdi-24px"></b-icon>
      </span>
      <span class="home-collection-stat__spark is-one"></span>
      <span class="home-collection-stat__spark is-two"></span>
      <span class="home-collection-stat__spark is-three"></span>
    </span>
    <span class="home-collection-stat__copy">
      <strong>{{ count }}</strong>
      <span>{{ label }}</span>
    </span>
    <span class="home-collection-stat__shine" aria-hidden="true"></span>
  </div>
</template>

<script>
import ComicIcon from './icons/ComicIcon.vue';

export default {
  name: 'HomeCollectionStat',
  components: {
    ComicIcon,
  },
  props: {
    count: {
      type: Number,
      required: true,
    },
    kind: {
      type: String,
      required: true,
      validator(value) {
        return ['comic', 'pin'].indexOf(value) !== -1;
      },
    },
    label: {
      type: String,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.home-collection-stat {
  position: relative;
  isolation: isolate;
  display: inline-flex;
  min-width: 176px;
  min-height: 64px;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-md) var(--space-xs) var(--space-xs);
  overflow: hidden;
  border: 1px solid var(--stat-border);
  border-radius: var(--radius-md);
  color: var(--stat-ink);
  background: var(--stat-background);
  box-shadow: var(--stat-shadow);
  cursor: default;
  outline: none;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transform: translateZ(0);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-spring),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard),
    filter var(--motion-duration-standard) var(--motion-ease-standard);
}

.home-collection-stat.is-comic {
  --stat-ink: color-mix(in srgb, var(--color-accent-strong) 78%, #682585);
  --stat-border: color-mix(in srgb, var(--color-accent-border) 72%, #ff8dcf);
  --stat-background:
    linear-gradient(135deg, rgba(255, 105, 180, 0.2), transparent 46%),
    linear-gradient(315deg, rgba(90, 174, 255, 0.2), transparent 52%),
    color-mix(in srgb, var(--color-surface-card) 84%, #fff0fa);
  --stat-art-background: linear-gradient(145deg, #ff72b8, #9a72ff 55%, #53c9ff);
  --stat-shadow: 0 12px 28px color-mix(in srgb, var(--color-theme-glow-strong) 78%, transparent);
}

.home-collection-stat.is-pin {
  --stat-ink: color-mix(in srgb, var(--color-accent-strong) 64%, #3f6d67);
  --stat-border: color-mix(in srgb, var(--color-accent-border) 62%, #8bbfa6);
  --stat-background:
    linear-gradient(118deg, rgba(243, 183, 104, 0.2), transparent 42%),
    linear-gradient(300deg, rgba(93, 173, 150, 0.18), transparent 56%),
    color-mix(in srgb, var(--color-surface-card) 90%, #f8f1df);
  --stat-art-background: linear-gradient(145deg, #efa65a, #d96f77 48%, #5ea98d);
  --stat-shadow: 0 12px 28px color-mix(in srgb, var(--color-theme-glow) 58%, rgba(77, 98, 78, 0.15));
}

.home-collection-stat::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  background:
    repeating-linear-gradient(
      118deg,
      transparent 0 14px,
      color-mix(in srgb, var(--stat-border) 14%, transparent) 14px 15px
    );
  content: '';
  opacity: 0.5;
  pointer-events: none;
}

.home-collection-stat__art {
  position: relative;
  display: grid;
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  place-items: center;
  border: 2px solid rgba(255, 255, 255, 0.78);
  border-radius: var(--radius-sm);
  color: #fff;
  background: var(--stat-art-background);
  box-shadow:
    0 7px 16px color-mix(in srgb, var(--stat-border) 46%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transform: rotate(-3deg);
  transition: transform var(--motion-duration-standard) var(--motion-ease-spring);
}

.is-comic .home-collection-stat__art {
  border-radius: 46% 54% 42% 58% / 52% 43% 57% 48%;
}

.is-pin .home-collection-stat__art {
  border-radius: 38% 62% 56% 44% / 52% 42% 58% 48%;
}

.home-collection-stat__icon {
  position: relative;
  z-index: 2;
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  filter: drop-shadow(0 2px 4px rgba(48, 24, 56, 0.24));
}

.home-collection-stat__icon svg {
  width: 24px;
  height: 24px;
}

.home-collection-stat__copy {
  position: relative;
  z-index: 2;
  display: grid;
  min-width: 0;
  line-height: 1.05;
}

.home-collection-stat__copy strong {
  color: inherit;
  font-size: 1.45rem;
  font-weight: 950;
  font-variant-numeric: tabular-nums;
}

.home-collection-stat__copy span {
  margin-top: 0.22rem;
  color: color-mix(in srgb, var(--color-text-muted) 76%, var(--stat-ink));
  font-size: 0.75rem;
  font-weight: 850;
  white-space: nowrap;
}

.home-collection-stat__spark {
  position: absolute;
  z-index: 3;
  width: 7px;
  height: 7px;
  border-radius: 2px;
  background: #fff;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.92);
  transform: rotate(45deg) scale(0.72);
}

.home-collection-stat__spark.is-one {
  top: -3px;
  right: 3px;
}

.home-collection-stat__spark.is-two {
  right: -4px;
  bottom: 8px;
  width: 5px;
  height: 5px;
}

.home-collection-stat__spark.is-three {
  bottom: -2px;
  left: 6px;
  width: 4px;
  height: 4px;
}

.is-pin .home-collection-stat__spark {
  border-radius: 50%;
}

.home-collection-stat__shine {
  position: absolute;
  z-index: 1;
  top: -70%;
  bottom: -70%;
  left: -38%;
  width: 22%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.72), transparent);
  opacity: 0.76;
  pointer-events: none;
  transform: skewX(-18deg);
}

html[data-motion='full'] .home-collection-stat {
  animation: home-stat-float 4.8s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .home-collection-stat.is-pin {
  animation-duration: 5.6s;
  animation-delay: -1.7s;
}

html[data-motion='full'] .home-collection-stat__shine {
  animation: home-stat-shine 4.6s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .home-collection-stat__spark {
  animation: home-stat-spark 2.1s ease-in-out infinite;
}

html[data-motion='full'] .home-collection-stat__spark.is-two {
  animation-delay: -0.7s;
}

html[data-motion='full'] .home-collection-stat__spark.is-three {
  animation-delay: -1.35s;
}

@media (hover: hover) and (pointer: fine) {
  .home-collection-stat:hover,
  .home-collection-stat:focus-visible {
    border-color: var(--stat-ink);
    box-shadow:
      var(--stat-shadow),
      0 0 0 3px color-mix(in srgb, var(--stat-border) 24%, transparent);
    filter: saturate(1.1);
    transform: translateY(-4px) rotate(-0.35deg) scale(1.025);
  }

  .home-collection-stat:hover .home-collection-stat__art,
  .home-collection-stat:focus-visible .home-collection-stat__art {
    transform: rotate(4deg) scale(1.08);
  }
}

.home-collection-stat:active {
  box-shadow: var(--shadow-xs);
  transform: translateY(1px) scale(0.975);
  transition-duration: var(--motion-duration-instant);
}

@keyframes home-stat-float {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-2px) rotate(0.25deg); }
}

@keyframes home-stat-shine {
  0%, 54% { transform: translateX(0) skewX(-18deg); }
  82%, 100% { transform: translateX(690%) skewX(-18deg); }
}

@keyframes home-stat-spark {
  0%, 100% { opacity: 0.42; transform: rotate(45deg) scale(0.62); }
  48% { opacity: 1; transform: rotate(45deg) scale(1.08); }
}

@media screen and (max-width: 540px) {
  .home-collection-stat {
    min-width: 154px;
    min-height: 58px;
    padding-right: var(--space-sm);
  }

  .home-collection-stat__art {
    width: 42px;
    height: 42px;
    flex-basis: 42px;
  }
}

html[data-motion='reduce'] .home-collection-stat,
html[data-motion='reduce'] .home-collection-stat__shine,
html[data-motion='reduce'] .home-collection-stat__spark {
  animation: none;
}
</style>
