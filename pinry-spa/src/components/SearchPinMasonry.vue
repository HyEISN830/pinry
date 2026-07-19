<template>
  <div ref="container" class="search-pins-container">
    <div
      ref="grid"
      v-masonry=""
      v-layout-ready="{ itemSelector: '.search-pin-tile' }"
      :key="masonryKey"
      :style="gridStyle"
      class="search-pins-masonry"
      transition-duration="0.12s"
      item-selector=".search-pin-tile"
      column-width=".search-pin-sizer"
      gutter=".search-pin-gutter"
      fit-width="true">
      <div class="search-pin-sizer" aria-hidden="true"></div>
      <div class="search-pin-gutter" aria-hidden="true"></div>
      <SearchPinCard
        v-for="pin in pins"
        :key="pin.id"
        v-masonry-tile
        class="search-pin-tile"
        :pin="pin"
        :like-busy="pin.likeBusy"
        @preview="$emit('preview', $event)"
        @toggle-like="$emit('toggle-like', $event)">
      </SearchPinCard>
    </div>
  </div>
</template>

<script>
import SearchPinCard from './SearchPinCard.vue';

const SAFE_WIDTH = 240;
const MAX_MEASURE_ATTEMPTS = 8;

function metricsFor(widthValue) {
  const width = Math.max(0, widthValue || 0);
  if (width <= 540) {
    return { columns: 1, gutter: 0, itemWidth: width || SAFE_WIDTH };
  }
  const gutter = width >= 980 ? 18 : 14;
  const preferredWidth = width >= 980 ? 236 : 224;
  const columns = Math.max(
    1,
    Math.floor((width + gutter) / (preferredWidth + gutter)),
  );
  return {
    columns,
    gutter,
    itemWidth: Math.floor((width - ((columns - 1) * gutter)) / columns),
  };
}

export default {
  name: 'SearchPinMasonry',
  components: { SearchPinCard },
  props: {
    pins: { type: Array, default: () => [] },
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
      imageLoadHandler: null,
    };
  },
  computed: {
    gridStyle() {
      return {
        '--search-pin-width': `${this.metrics.itemWidth}px`,
        '--search-pin-gutter': `${this.metrics.gutter}px`,
      };
    },
  },
  watch: {
    pins() {
      this.$nextTick(() => {
        this.bindImageLoad();
        this.measureWhenReady();
      });
    },
  },
  mounted() {
    this.bindImageLoad();
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
    if (this.$refs.container && this.imageLoadHandler) {
      this.$refs.container.removeEventListener('load', this.imageLoadHandler, true);
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
        const requestFrame = window.requestAnimationFrame
          || (callback => window.setTimeout(callback, 16));
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
          this.measureTimer = window.setTimeout(
            () => this.measureWhenReady(),
            Math.min(40 * this.measureAttempts, 240),
          );
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
    bindImageLoad() {
      const { container } = this.$refs;
      if (!container) return;
      if (this.imageLoadHandler) {
        container.removeEventListener('load', this.imageLoadHandler, true);
      }
      this.imageLoadHandler = () => this.queueLayout();
      // Image load does not bubble, so listen during capture to catch card images.
      container.addEventListener('load', this.imageLoadHandler, true);
    },
    redraw() {
      if (typeof this.$redrawVueMasonry === 'function') this.$redrawVueMasonry();
    },
    queueLayout() {
      this.clearLayoutTimers();
      const requestFrame = window.requestAnimationFrame
        || (callback => window.setTimeout(callback, 16));
      this.layoutFrame = requestFrame(() => {
        this.layoutFrame = null;
        this.redraw();
      });
      [80, 180, 360].forEach((delay) => {
        this.layoutTimers.push(window.setTimeout(() => this.redraw(), delay));
      });
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
.search-pins-container { width: 100%; min-width: 0; background: transparent; }
.search-pins-masonry { margin-right: auto; margin-left: auto; background: transparent; }
.search-pin-sizer, .search-pin-tile { width: var(--search-pin-width, 240px); }
.search-pin-tile { margin-bottom: var(--search-pin-gutter, 16px); }
.search-pin-gutter { width: var(--search-pin-gutter, 16px); }
@media (max-width: 540px) {
  .search-pin-sizer, .search-pin-tile { width: 100%; }
  .search-pin-gutter { width: 0; }
}
</style>
