<template>
  <section class="personal-comics-list" aria-live="polite">
    <div ref="container" class="personal-comics-container">
      <div
        v-if="comics.length"
        ref="masonryGrid"
        v-masonry=""
        v-layout-ready="{ itemSelector: '.personal-comic-tile' }"
        :key="masonryKey"
        :style="gridStyle"
        class="personal-comics-masonry"
        transition-duration="0.12s"
        item-selector=".personal-comic-tile"
        column-width=".personal-comic-sizer"
        gutter=".personal-comic-gutter"
        fit-width="true">
        <div class="personal-comic-sizer"></div>
        <div class="personal-comic-gutter"></div>
        <ComicCard
          v-for="comic in comics"
          :key="comic.id"
          v-masonry-tile
          class="personal-comic-tile"
          :comic="comic"
          :current-username="currentUsername"
          :like-busy="comic.likeBusy"
          @read="readComic"
          @delete="deleteComic"
          @toggle-like="toggleLike"
          @image-settled="queueLayout"
          @layout-settled="queueLayout">
        </ComicCard>
      </div>
    </div>

    <loadingSpinner :show="status.loading" size="compact"></loadingSpinner>
    <div v-if="status.error" class="personal-comics-state">
      <p>{{ $t('cardLoadError') }}</p>
      <button type="button" @click="fetchNext">{{ $t('loadMoreResults') }}</button>
    </div>
    <div v-else-if="showEmpty" class="personal-comics-state">
      <p>{{ $t('comicsEmptyState') }}</p>
    </div>
    <div v-if="status.hasNext && comics.length" class="personal-comics-more">
      <button type="button" :disabled="status.loading" @click="fetchNext">
        {{ $t('loadMoreResults') }}
      </button>
    </div>
  </section>
</template>

<script>
import API from './api';
import ComicCard from './ComicCard.vue';
import loadingSpinner from './loadingSpinner.vue';
import modals from './modals';
import { responsiveBatchSize } from './utils/responsiveMedia';

const PAGE_SIZE = 18;
const SAFE_WIDTH = 240;
const MAX_MEASURE_ATTEMPTS = 8;

function getGridMetrics(containerWidth) {
  const width = Math.max(0, containerWidth || 0);
  if (width <= 540) {
    return { columns: 1, gutter: 0, itemWidth: width || SAFE_WIDTH };
  }
  const gutter = width >= 980 ? 18 : 14;
  const preferredWidth = width >= 980 ? 246 : 236;
  const columns = Math.max(1, Math.floor((width + gutter) / (preferredWidth + gutter)));
  const itemWidth = Math.floor((width - ((columns - 1) * gutter)) / columns);
  return { columns, gutter, itemWidth };
}

export default {
  name: 'PersonalComics',
  components: { ComicCard, loadingSpinner },
  props: {
    username: { type: String, required: true },
  },
  data() {
    return {
      comics: [],
      currentUsername: null,
      metrics: getGridMetrics(SAFE_WIDTH),
      metricsSignature: '240-0-1',
      masonryKey: 0,
      requestEpoch: 0,
      measureAttempts: 0,
      measureTimer: null,
      resizeObserver: null,
      layoutFrame: null,
      layoutTimers: [],
      status: {
        count: 0,
        error: false,
        hasNext: true,
        loading: false,
        offset: 0,
      },
    };
  },
  computed: {
    gridStyle() {
      return {
        '--personal-comic-width': `${this.metrics.itemWidth}px`,
        '--personal-comic-gutter': `${this.metrics.gutter}px`,
      };
    },
    showEmpty() {
      return !this.status.loading && !this.status.error && !this.comics.length;
    },
  },
  watch: {
    username() { this.reset(); },
  },
  created() {
    API.User.fetchUserInfo().then((user) => {
      this.currentUsername = user ? user.username : null;
    });
    this.fetchNext();
  },
  mounted() {
    this.observeContainer();
    this.measureWhenReady();
  },
  beforeDestroy() {
    this.clearLayoutTimers();
    if (this.resizeObserver) this.resizeObserver.disconnect();
    if (this.measureTimer) window.clearTimeout(this.measureTimer);
  },
  methods: {
    readComic(comic) {
      this.$router.push({ name: 'comic', params: { comicId: comic.id } });
    },
    fetchNext() {
      if (this.status.loading || !this.status.hasNext) return;
      const epoch = this.requestEpoch;
      const { username } = this;
      this.status.loading = true;
      API.Comic.fetchList(
        this.status.offset,
        responsiveBatchSize(PAGE_SIZE),
        null,
        username,
      ).then((response) => {
        if (epoch !== this.requestEpoch || username !== this.username) return;
        const { data } = response;
        const incoming = (data.results || []).map(comic => Object.assign({}, comic, { likeBusy: false }));
        this.comics = this.comics.concat(incoming);
        this.status.count = data.count || 0;
        this.status.offset = this.comics.length;
        this.status.hasNext = data.next !== null;
        this.status.error = false;
        this.status.loading = false;
        this.$emit('meta', { count: this.status.count });
        this.$nextTick(() => {
          this.measureWhenReady();
          this.queueLayout();
        });
      }, () => {
        if (epoch !== this.requestEpoch || username !== this.username) return;
        this.status.error = true;
        this.status.loading = false;
      });
    },
    reset() {
      this.requestEpoch += 1;
      this.comics = [];
      this.status = {
        count: 0, error: false, hasNext: true, loading: false, offset: 0,
      };
      this.$emit('meta', { count: 0 });
      this.fetchNext();
    },
    toggleLike(comic) {
      if (comic.likeBusy) return;
      this.$set(comic, 'likeBusy', true);
      API.Comic.toggleLike(comic.id).then((response) => {
        this.$set(comic, 'viewer_liked', response.data.viewer_liked);
        this.$set(comic, 'likes_count', response.data.likes_count);
        this.$set(comic, 'likeBusy', false);
      }, () => this.$set(comic, 'likeBusy', false));
    },
    deleteComic(comic) {
      modals.openActionConfirm(
        this,
        {
          title: this.$t('comicDeleteTitle'),
          message: this.$t('deleteComicConfirm'),
          confirmLabel: this.$t('deleteButton'),
          cancelLabel: this.$t('cancelButton'),
          icon: 'delete-outline',
        },
        () => API.Comic.delete(comic.id).then(() => {
          this.comics = this.comics.filter(item => item.id !== comic.id);
          this.status.count = Math.max(0, this.status.count - 1);
          this.$emit('meta', { count: this.status.count });
          this.queueLayout();
        }),
      );
    },
    updateMetrics() {
      const width = this.$refs.container ? this.$refs.container.clientWidth : 0;
      if (!width) return false;
      const metrics = getGridMetrics(width);
      const signature = `${metrics.itemWidth}-${metrics.gutter}-${metrics.columns}`;
      if (signature === this.metricsSignature) return false;
      this.metrics = metrics;
      this.metricsSignature = signature;
      return true;
    },
    measureWhenReady() {
      this.$nextTick(() => {
        const requestFrame = window.requestAnimationFrame || (callback => window.setTimeout(callback, 16));
        requestFrame(() => {
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
            this.measureWhenReady,
            Math.min(40 * this.measureAttempts, 240),
          );
        });
      });
    },
    observeContainer() {
      if (!window.ResizeObserver || !this.$refs.container) return;
      this.resizeObserver = new ResizeObserver(() => {
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
      this.layoutFrame = requestFrame(() => {
        this.layoutFrame = null;
        this.redraw();
      });
      [80, 180, 360].forEach((delay) => {
        this.layoutTimers.push(window.setTimeout(this.redraw, delay));
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
.personal-comics-list,
.personal-comics-container {
  width: 100%;
  min-width: 0;
  background: transparent;
}
.personal-comics-masonry { margin-right: auto; margin-left: auto; background: transparent; }
.personal-comic-sizer,
.personal-comic-tile { width: var(--personal-comic-width, 240px); }
.personal-comic-tile { margin-bottom: var(--personal-comic-gutter, 16px); }
.personal-comic-gutter { width: var(--personal-comic-gutter, 16px); }
.personal-comics-state { padding: 24px 0; color: var(--color-text-muted, var(--text-muted, #64748b)); text-align: center; }
.personal-comics-state button,
.personal-comics-more button { padding: 8px 14px; border: 1px solid var(--color-border-soft, var(--line-soft, #dfe5ec)); border-radius: 8px; color: var(--color-text-primary, var(--text-strong, #243447)); background: var(--color-surface-card, #fff); cursor: pointer; font-weight: 700; }
.personal-comics-more { display:flex; justify-content:center; padding:8px 0 24px; }
@media (max-width: 540px) {
  .personal-comic-sizer,
  .personal-comic-tile { width: 100%; }
  .personal-comic-gutter { width: 0; }
}
</style>
