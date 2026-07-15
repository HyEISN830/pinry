<template>
  <div
    class="home-collection-stat"
    :class="`is-${kind}`"
    :style="interactionStyle"
    role="status"
    aria-live="polite"
    tabindex="0"
    @pointermove="onPointerMove"
    @pointerleave="resetPointer"
    @blur="resetPointer">
    <span class="home-collection-stat__pattern" aria-hidden="true">
      <span class="home-collection-stat__panel is-one"></span>
      <span class="home-collection-stat__panel is-two"></span>
      <span class="home-collection-stat__panel is-three"></span>
    </span>
    <span class="home-collection-stat__art" aria-hidden="true">
      <span class="home-collection-stat__icon">
        <ComicIcon v-if="kind === 'comic'"></ComicIcon>
        <b-icon v-else icon="palette" custom-size="mdi-28px"></b-icon>
      </span>
      <span class="home-collection-stat__spark is-one"></span>
      <span class="home-collection-stat__spark is-two"></span>
      <span class="home-collection-stat__spark is-three"></span>
    </span>
    <span class="home-collection-stat__copy">
      <h1 class="home-collection-stat__title">{{ title }}</h1>
      <span class="home-collection-stat__metric">
        <strong>{{ displayCount }}</strong>
        <span>{{ label }}</span>
      </span>
    </span>
    <span class="home-collection-stat__orbit" aria-hidden="true"></span>
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
      default: null,
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
    title: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      pointerX: 50,
      pointerY: 50,
    };
  },
  computed: {
    displayCount() {
      return this.count === null ? '...' : this.count;
    },
    interactionStyle() {
      return {
        '--stat-pointer-x': `${this.pointerX}%`,
        '--stat-pointer-y': `${this.pointerY}%`,
      };
    },
  },
  methods: {
    onPointerMove(event) {
      if (event.pointerType === 'touch') {
        return;
      }
      const bounds = event.currentTarget.getBoundingClientRect();
      if (!bounds.width || !bounds.height) {
        return;
      }
      this.pointerX = Math.round(((event.clientX - bounds.left) / bounds.width) * 100);
      this.pointerY = Math.round(((event.clientY - bounds.top) / bounds.height) * 100);
    },
    resetPointer() {
      this.pointerX = 50;
      this.pointerY = 50;
    },
  },
};
</script>

<style lang="scss" scoped>
.home-collection-stat {
  position: relative;
  isolation: isolate;
  display: inline-flex;
  width: min(100%, 420px);
  min-height: 82px;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-xl) var(--space-sm) var(--space-sm);
  overflow: hidden;
  border: 1px solid var(--stat-border);
  border-radius: var(--radius-lg);
  color: var(--stat-ink);
  background: var(--stat-background);
  box-shadow: var(--stat-shadow);
  cursor: default;
  outline: none;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transform: translateZ(0);
  transition:
    transform 360ms var(--motion-ease-emphasized),
    border-color var(--motion-duration-standard) var(--motion-ease-standard),
    box-shadow 360ms var(--motion-ease-standard),
    filter 360ms var(--motion-ease-standard);
}

.home-collection-stat.is-comic {
  --stat-ink: color-mix(in srgb, var(--color-accent-strong) 76%, #682585);
  --stat-border: color-mix(in srgb, var(--color-accent-border) 72%, #ff8dcf);
  --stat-background:
    radial-gradient(circle at var(--stat-pointer-x) var(--stat-pointer-y), rgba(255, 255, 255, 0.34), transparent 34%),
    linear-gradient(135deg, rgba(255, 105, 180, 0.24), transparent 44%),
    linear-gradient(315deg, rgba(90, 174, 255, 0.22), transparent 54%),
    color-mix(in srgb, var(--color-surface-card) 82%, #fff0fa);
  --stat-art-background: linear-gradient(145deg, #ff72b8, #9a72ff 55%, #53c9ff);
  --stat-shadow: 0 14px 34px color-mix(in srgb, var(--color-theme-glow-strong) 78%, transparent);
}

.home-collection-stat.is-pin {
  --stat-ink: color-mix(in srgb, var(--color-accent-strong) 62%, #3f6d67);
  --stat-border: color-mix(in srgb, var(--color-accent-border) 62%, #8bbfa6);
  --stat-background:
    radial-gradient(circle at var(--stat-pointer-x) var(--stat-pointer-y), rgba(255, 255, 255, 0.3), transparent 36%),
    linear-gradient(118deg, rgba(243, 183, 104, 0.23), transparent 42%),
    linear-gradient(300deg, rgba(93, 173, 150, 0.2), transparent 58%),
    color-mix(in srgb, var(--color-surface-card) 88%, #f8f1df);
  --stat-art-background: linear-gradient(145deg, #efa65a, #d96f77 48%, #5ea98d);
  --stat-shadow: 0 14px 34px color-mix(in srgb, var(--color-theme-glow) 58%, rgba(77, 98, 78, 0.15));
}

.home-collection-stat::before {
  position: absolute;
  z-index: 0;
  inset: 0;
  background:
    repeating-linear-gradient(
      118deg,
      transparent 0 16px,
      color-mix(in srgb, var(--stat-border) 14%, transparent) 16px 17px
    );
  content: '';
  opacity: 0.42;
  pointer-events: none;
}

.home-collection-stat::after {
  position: absolute;
  z-index: 0;
  right: -44px;
  bottom: -68px;
  width: 170px;
  height: 170px;
  border: 18px solid color-mix(in srgb, var(--stat-border) 17%, transparent);
  border-radius: 50%;
  content: '';
  pointer-events: none;
  transition: transform 620ms var(--motion-ease-emphasized);
}

.home-collection-stat__pattern {
  position: absolute;
  z-index: 1;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.home-collection-stat__panel {
  position: absolute;
  border: 1px solid color-mix(in srgb, var(--stat-border) 38%, transparent);
  background: color-mix(in srgb, var(--color-surface-card) 28%, transparent);
  opacity: 0.72;
  transition: transform 520ms var(--motion-ease-emphasized);
}

.is-comic .home-collection-stat__panel.is-one {
  top: -18px;
  right: 82px;
  width: 72px;
  height: 54px;
  transform: rotate(13deg);
}

.is-comic .home-collection-stat__panel.is-two {
  right: 14px;
  bottom: -12px;
  width: 92px;
  height: 56px;
  transform: rotate(-8deg);
}

.is-comic .home-collection-stat__panel.is-three {
  top: 16px;
  right: 42px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background:
    radial-gradient(circle, color-mix(in srgb, var(--stat-border) 42%, transparent) 1px, transparent 1.5px);
  background-size: 6px 6px;
}

.is-pin .home-collection-stat__panel {
  border: 0;
  border-radius: 999px;
  background: color-mix(in srgb, var(--stat-border) 28%, transparent);
}

.is-pin .home-collection-stat__panel.is-one {
  top: 17px;
  right: 22px;
  width: 112px;
  height: 10px;
  transform: rotate(-8deg);
}

.is-pin .home-collection-stat__panel.is-two {
  right: 56px;
  bottom: 19px;
  width: 92px;
  height: 8px;
  transform: rotate(8deg);
}

.is-pin .home-collection-stat__panel.is-three {
  top: 14px;
  right: 102px;
  width: 36px;
  height: 36px;
  border-radius: 42% 58% 54% 46%;
  background: color-mix(in srgb, #f0b35d 28%, transparent);
}

.home-collection-stat__art {
  position: relative;
  z-index: 3;
  display: grid;
  width: 56px;
  height: 56px;
  flex: 0 0 56px;
  place-items: center;
  border: 2px solid rgba(255, 255, 255, 0.78);
  color: #fff;
  background: var(--stat-art-background);
  box-shadow:
    0 9px 20px color-mix(in srgb, var(--stat-border) 48%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
  transform: rotate(-3deg);
  transition: transform 420ms var(--motion-ease-spring);
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
  width: 28px;
  height: 28px;
  place-items: center;
  filter: drop-shadow(0 2px 4px rgba(48, 24, 56, 0.24));
}

.home-collection-stat__icon svg {
  width: 28px;
  height: 28px;
}

.home-collection-stat__copy {
  position: relative;
  z-index: 3;
  display: grid;
  min-width: 0;
  gap: 0.28rem;
}

.home-collection-stat__title {
  margin: 0;
  color: var(--color-text-strong);
  font-size: clamp(1.1rem, 1.5vw, 1.42rem);
  font-weight: 950;
  line-height: 1;
}

.home-collection-stat__metric {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs);
  min-width: 0;
}

.home-collection-stat__metric strong {
  color: var(--color-accent-foreground);
  font-size: 1.5rem;
  font-weight: 950;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.home-collection-stat__metric span {
  overflow: hidden;
  color: color-mix(in srgb, var(--color-text-muted) 76%, var(--stat-ink));
  font-size: 0.78rem;
  font-weight: 850;
  text-overflow: ellipsis;
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

.home-collection-stat__spark.is-one { top: -3px; right: 3px; }
.home-collection-stat__spark.is-two { right: -4px; bottom: 8px; width: 5px; height: 5px; }
.home-collection-stat__spark.is-three { bottom: -2px; left: 6px; width: 4px; height: 4px; }
.is-pin .home-collection-stat__spark { border-radius: 50%; }

.home-collection-stat__orbit {
  position: absolute;
  z-index: 2;
  top: 50%;
  right: 32px;
  width: 50px;
  height: 50px;
  border: 1px dashed color-mix(in srgb, var(--stat-border) 66%, transparent);
  border-radius: 50%;
  opacity: 0.62;
  pointer-events: none;
  transform: translateY(-50%);
}

.home-collection-stat__shine {
  position: absolute;
  z-index: 2;
  top: -70%;
  bottom: -70%;
  left: -28%;
  width: 18%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.74), transparent);
  opacity: 0.74;
  pointer-events: none;
  transform: skewX(-18deg);
}

html[data-motion='full'] .home-collection-stat__art {
  animation: home-stat-float 5.2s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .home-collection-stat.is-pin .home-collection-stat__art {
  animation-duration: 5.8s;
  animation-delay: -1.7s;
}

html[data-motion='full'] .home-collection-stat__shine {
  animation: home-stat-shine 4.8s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .home-collection-stat__orbit {
  animation: home-stat-orbit 9s linear infinite;
}

html[data-motion='full'] .home-collection-stat__spark {
  animation: home-stat-spark 2.1s ease-in-out infinite;
}

html[data-motion='full'] .home-collection-stat__spark.is-two { animation-delay: -0.7s; }
html[data-motion='full'] .home-collection-stat__spark.is-three { animation-delay: -1.35s; }

@media (hover: hover) and (pointer: fine) {
  .home-collection-stat:hover,
  .home-collection-stat:focus-visible {
    border-color: var(--stat-ink);
    box-shadow:
      var(--stat-shadow),
      0 0 0 3px color-mix(in srgb, var(--stat-border) 24%, transparent);
    filter: saturate(1.1);
    transform: translateY(-4px) scale(1.018);
  }

  .home-collection-stat:hover::after,
  .home-collection-stat:focus-visible::after {
    transform: translate(-12px, -8px) scale(1.08);
  }

  .home-collection-stat:hover .home-collection-stat__art,
  .home-collection-stat:focus-visible .home-collection-stat__art {
    animation: none;
    transform: rotate(4deg) scale(1.08);
  }

  .home-collection-stat:hover .home-collection-stat__panel.is-one,
  .home-collection-stat:focus-visible .home-collection-stat__panel.is-one {
    transform: translate(-5px, 3px) rotate(18deg);
  }

  .home-collection-stat:hover .home-collection-stat__panel.is-two,
  .home-collection-stat:focus-visible .home-collection-stat__panel.is-two {
    transform: translate(5px, -4px) rotate(-12deg);
  }
}

.home-collection-stat:active {
  box-shadow: var(--shadow-xs);
  transform: translateY(1px) scale(0.985);
  transition-duration: var(--motion-duration-instant);
}

@keyframes home-stat-float {
  0%, 100% { transform: translateY(0) rotate(-3deg); }
  50% { transform: translateY(-3px) rotate(-0.5deg); }
}

@keyframes home-stat-shine {
  0%, 55% { transform: translateX(0) skewX(-18deg); }
  84%, 100% { transform: translateX(820%) skewX(-18deg); }
}

@keyframes home-stat-orbit {
  from { transform: translateY(-50%) rotate(0); }
  to { transform: translateY(-50%) rotate(360deg); }
}

@keyframes home-stat-spark {
  0%, 100% { opacity: 0.42; transform: rotate(45deg) scale(0.62); }
  48% { opacity: 1; transform: rotate(45deg) scale(1.08); }
}

@media screen and (max-width: 540px) {
  .home-collection-stat {
    width: 100%;
    min-height: 74px;
    padding-right: var(--space-md);
  }

  .home-collection-stat__art {
    width: 50px;
    height: 50px;
    flex-basis: 50px;
  }

  .home-collection-stat__orbit {
    right: 18px;
  }
}

html[data-motion='reduce'] .home-collection-stat,
html[data-motion='reduce'] .home-collection-stat__art,
html[data-motion='reduce'] .home-collection-stat__shine,
html[data-motion='reduce'] .home-collection-stat__orbit,
html[data-motion='reduce'] .home-collection-stat__spark {
  animation: none;
}
</style>
