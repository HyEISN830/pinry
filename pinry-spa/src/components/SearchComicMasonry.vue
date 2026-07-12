<template>
  <div ref="container" class="search-comics-container">
    <div
      ref="grid"
      v-masonry=""
      v-layout-ready="{ itemSelector: '.search-comic-tile' }"
      :key="masonryKey"
      :style="gridStyle"
      class="search-comics-masonry"
      transition-duration="0.12s"
      item-selector=".search-comic-tile"
      column-width=".search-comic-sizer"
      gutter=".search-comic-gutter"
      fit-width="true">
      <div class="search-comic-sizer"></div>
      <div class="search-comic-gutter"></div>
      <ComicCard
        v-for="comic in comics"
        :key="comic.id"
        v-masonry-tile
        class="search-comic-tile"
        :comic="comic"
        :like-busy="comic.likeBusy"
        @read="$emit('read', $event)"
        @delete="$emit('delete', $event)"
        @toggle-like="$emit('toggle-like', $event)"
        @image-settled="queueLayout">
      </ComicCard>
    </div>
  </div>
</template>

<script>
import ComicCard from './ComicCard.vue';

const SAFE_WIDTH = 240;
const MAX_MEASURE_ATTEMPTS = 8;

function metricsFor(widthValue) {
  const width = Math.max(0, widthValue || 0);
  if (width <= 540) return { columns: 1, gutter: 0, itemWidth: width || SAFE_WIDTH };
  const gutter = width >= 980 ? 18 : 14;
  const preferredWidth = width >= 980 ? 246 : 236;
  const columns = Math.max(1, Math.floor((width + gutter) / (preferredWidth + gutter)));
  return {
    columns,
    gutter,
    itemWidth: Math.floor((width - ((columns - 1) * gutter)) / columns),
  };
}

export default {
  name: 'SearchComicMasonry',
  components: { ComicCard },
  props: {
    comics: { type: Array, default: () => [] },
  },
  data() {
    return {
      metrics: metricsFor(SAFE_WIDTH),
      metricsSignature: '240-0-1',
      masonryKey: 0,
      measureAttempts: 0,
      measureTimer: null,
      resizeObserver: null,
      measureFrame: null,
      layoutFrame: null,
      layoutTimers: [],
    };
  },
  computed: {
    gridStyle() {
      return {
        '--search-comic-width': `${this.metrics.itemWidth}px`,
        '--search-comic-gutter': `${this.metrics.gutter}px`,
      };
    },
  },
  watch: {
    comics() { this.$nextTick(this.measureWhenReady); },
  },
  mounted() {
    this.observeContainer();
    this.measureWhenReady();
  },
  beforeDestroy() {
    this.clearLayoutTimers();
    if (this.resizeObserver) this.resizeObserver.disconnect();
    if (this.measureTimer) window.clearTimeout(this.measureTimer);
    if (this.measureFrame) {
      const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
      cancelFrame(this.measureFrame);
      this.measureFrame = null;
    }
  },
  methods: {
    updateMetrics() {
      const width = this.$refs.container ? this.$refs.container.clientWidth : 0;
      if (!width) return false;
      const metrics = metricsFor(width);
      const signature = `${metrics.itemWidth}-${metrics.gutter}-${metrics.columns}`;
      if (signature === this.metricsSignature) return false;
      this.metrics = metrics;
      this.metricsSignature = signature;
      return true;
    },
    measureWhenReady() {
      if (this.measureTimer) {
        window.clearTimeout(this.measureTimer);
        this.measureTimer = null;
      }
      this.$nextTick(() => {
        if (this.measureFrame) {
          const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
          cancelFrame(this.measureFrame);
        }
        const requestFrame = window.requestAnimationFrame || (callback => window.setTimeout(callback, 16));
        this.measureFrame = requestFrame(() => {
          this.measureFrame = null;
          if (this.updateMetrics()) {
            this.measureAttempts = 0;
            this.masonryKey += 1;
            this.$nextTick(this.redraw);
            return;
          }
          const width = this.$refs.container ? this.$refs.container.clientWidth : 0;
          if (width || this.measureAttempts >= MAX_MEASURE_ATTEMPTS) {
            this.measureAttempts = 0;
            this.redraw();
            return;
          }
          this.measureAttempts += 1;
          this.measureTimer = window.setTimeout(this.measureWhenReady, Math.min(40 * this.measureAttempts, 240));
        });
      });
    },
    observeContainer() {
      if (typeof window.ResizeObserver !== 'function' || !this.$refs.container) return;
      this.resizeObserver = new window.ResizeObserver(() => {
        if (this.updateMetrics()) {
          this.masonryKey += 1;
          this.$nextTick(this.redraw);
        }
      });
      this.resizeObserver.observe(this.$refs.container);
    },
    redraw() {
      if (typeof this.$redrawVueMasonry === 'function') this.$redrawVueMasonry();
    },
    queueLayout() {
      this.clearLayoutTimers();
      const requestFrame = window.requestAnimationFrame || (callback => window.setTimeout(callback, 16));
      this.layoutFrame = requestFrame(() => { this.layoutFrame = null; this.redraw(); });
      [80, 180, 360].forEach(delay => this.layoutTimers.push(window.setTimeout(this.redraw, delay)));
    },
    clearLayoutTimers() {
      if (this.layoutFrame) {
        const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
        cancelFrame(this.layoutFrame);
        this.layoutFrame = null;
      }
      this.layoutTimers.forEach(timer => window.clearTimeout(timer));
      this.layoutTimers = [];
    },
  },
};
</script>

<style lang="scss" scoped>
.search-comics-container { width: 100%; min-width: 0; background: transparent; }
.search-comics-masonry { margin-right: auto; margin-left: auto; background: transparent; }
.search-comic-sizer, .search-comic-tile { width: var(--search-comic-width, 240px); }
.search-comic-tile { margin-bottom: var(--search-comic-gutter, 16px); }
.search-comic-gutter { width: var(--search-comic-gutter, 16px); }
@media (max-width: 540px) {
  .search-comic-sizer, .search-comic-tile { width: 100%; }
  .search-comic-gutter { width: 0; }
}
</style>
