<template>
  <section ref="container" class="personal-comics">
    <div v-if="loading && comics.length === 0" class="personal-comics-state">
      <b-skeleton v-for="index in 4" :key="index" height="280px"></b-skeleton>
    </div>
    <div v-else-if="error" class="personal-comics-state has-text-centered">
      <p>{{ error }}</p>
      <b-button type="is-primary" @click="reload">{{ $t('retry') }}</b-button>
    </div>
    <div v-else-if="comics.length === 0" class="personal-comics-state has-text-centered">
      {{ $t('noComics') }}
    </div>
    <div
      v-else
      ref="grid"
      v-masonry=""
      v-layout-ready="{ itemSelector: '.personal-comic-tile' }"
      :key="masonryKey"
      :style="gridStyle"
      class="personal-comics-grid"
      item-selector=".personal-comic-tile"
      column-width=".personal-comic-sizer"
      gutter=".personal-comic-gutter"
      fit-width="true"
      transition-duration="0.12s">
      <div class="personal-comic-sizer"></div>
      <div class="personal-comic-gutter"></div>
      <ComicCard
        v-for="comic in comics"
        :key="comic.id"
        :comic="comic"
        :current-username="username"
        :like-busy="comic.likeBusy"
        class="personal-comic-tile"
        @delete="deleteComic"
        @toggle-like="toggleLike"
        @image-settled="redraw">
      </ComicCard>
    </div>
    <div v-if="hasMore" class="personal-comics-more">
      <b-button :loading="loading" @click="loadMore">加载更多</b-button>
    </div>
  </section>
</template>

<script>
import API from './api';
import ComicCard from './ComicCard.vue';

function metricsFor(width) {
  if (width <= 540) return { columns: 1, gutter: 0, item: Math.max(240, width) };
  const gutter = width >= 980 ? 16 : 14;
  const preferred = width >= 980 ? 220 : 216;
  const columns = Math.max(1, Math.min(4, Math.floor((width + gutter) / (preferred + gutter))));
  return {
    columns,
    gutter,
    item: Math.floor((width - ((columns - 1) * gutter)) / columns),
  };
}

export default {
  name: 'PersonalComics',
  components: { ComicCard },
  props: {
    username: { type: String, required: true },
  },
  data() {
    return {
      comics: [],
      loading: false,
      error: null,
      offset: 0,
      limit: 12,
      total: 0,
      metrics: metricsFor(240),
      masonryKey: 0,
      observer: null,
      retryTimer: null,
      retryCount: 0,
    };
  },
  computed: {
    hasMore() { return this.comics.length < this.total; },
    gridStyle() {
      return {
        '--personal-comic-width': `${this.metrics.item}px`,
        '--personal-comic-gutter': `${this.metrics.gutter}px`,
      };
    },
  },
  mounted() {
    this.measureWhenReady();
    if (window.ResizeObserver) {
      this.observer = new ResizeObserver(this.measure);
      this.observer.observe(this.$refs.container);
    }
    this.reload();
  },
  beforeDestroy() {
    if (this.observer) this.observer.disconnect();
    if (this.retryTimer) window.clearTimeout(this.retryTimer);
  },
  methods: {
    coverUrl(comic) {
      const image = comic.cover_image || comic.cover;
      return image && (image.thumbnail || image.image || image.url || image);
    },
    measureWhenReady() {
      this.$nextTick(() => window.requestAnimationFrame(() => {
        if (this.measure()) return;
        if (this.retryCount >= 8) return;
        this.retryCount += 1;
        this.retryTimer = window.setTimeout(this.measureWhenReady, Math.min(40 * this.retryCount, 240));
      }));
    },
    measure() {
      const width = this.$refs.container ? this.$refs.container.clientWidth : 0;
      if (!width) return false;
      const next = metricsFor(width);
      if (`${next.item}-${next.gutter}-${next.columns}` !== `${this.metrics.item}-${this.metrics.gutter}-${this.metrics.columns}`) {
        this.metrics = next;
        this.masonryKey += 1;
      }
      this.retryCount = 0;
      this.redraw();
      return true;
    },
    redraw() {
      this.$nextTick(() => {
        if (this.$redrawVueMasonry) this.$redrawVueMasonry();
      });
    },
    reload() {
      this.comics = [];
      this.offset = 0;
      this.total = 0;
      this.fetchNext();
    },
    loadMore() { this.fetchNext(); },
    deleteComic(comic) {
      this.$buefy.dialog.confirm({
        message: this.$t('deleteComicConfirm'),
        type: 'is-danger',
        onConfirm: () => API.Comic.delete(comic.id).then(() => {
          this.comics = this.comics.filter(item => item.id !== comic.id);
          this.total = Math.max(0, this.total - 1);
          this.$emit('meta', { count: this.total });
          this.redraw();
        }),
      });
    },
    toggleLike(comic) {
      if (comic.likeBusy) return;
      this.$set(comic, 'likeBusy', true);
      API.Comic.toggleLike(comic.id).then((response) => {
        this.$set(comic, 'viewer_liked', response.data.viewer_liked);
        this.$set(comic, 'likes_count', response.data.likes_count);
      }).finally(() => this.$set(comic, 'likeBusy', false));
    },
    fetchNext() {
      if (this.loading) return;
      this.loading = true;
      this.error = null;
      API.Comic.fetchList(this.offset, this.limit, null, this.username).then((response) => {
        const data = response.data || {};
        const results = data.results || [];
        this.comics = this.comics.concat(results);
        this.offset = this.comics.length;
        this.total = Number.isFinite(data.count) ? data.count : this.comics.length;
        this.$emit('meta', { count: this.total });
        this.measureWhenReady();
      }).catch(() => {
        this.error = '加载作品失败';
      }).finally(() => {
        this.loading = false;
      });
    },
  },
};
</script>

<style scoped lang="scss">
.personal-comics { width: 100%; background: transparent; }
.personal-comics-grid { margin-right: auto; margin-left: auto; }
.personal-comic-sizer, .personal-comic-tile { width: var(--personal-comic-width, 240px); }
.personal-comic-gutter { width: var(--personal-comic-gutter, 14px); height: 0; }
.personal-comic-tile { margin-bottom: var(--personal-comic-gutter, 14px); }
.personal-comic-card { display: block; overflow: hidden; color: inherit; background: var(--surface-1); border: 1px solid var(--line-soft); border-radius: 12px; box-shadow: var(--shadow-soft); transition: transform 220ms ease, box-shadow 220ms ease; }
html[data-motion='full'] .personal-comic-card:hover { transform: translateY(-6px) scale(1.025); box-shadow: 0 20px 44px rgba(16, 24, 40, .2); }
.personal-comic-card img { display: block; width: 100%; height: auto; object-fit: contain; }
.personal-comic-placeholder { min-height: 220px; background: var(--surface-2); }
.personal-comic-info { padding: 14px; }
.personal-comic-info h3 { margin: 0; font-weight: 700; }
.personal-comic-info p { margin: 8px 0 0; color: var(--text-secondary); }
.personal-comics-state, .personal-comics-more { width: 100%; padding: 20px 0; }
.personal-comics-more { text-align: center; }
@media screen and (max-width: 540px) { .personal-comic-sizer, .personal-comic-tile { width: 100%; } }
</style>
