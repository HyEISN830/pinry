<template>
  <div
    class="comics-page"
    :class="{
      'is-embedded': embedded,
      'is-home-showcase': homeShowcase,
      'is-infinite-masonry': usesInfiniteMasonry
    }">
    <PHeader v-if="!embedded"></PHeader>
    <section class="section comics-section">
      <div class="container comics-container">
        <div class="comics-toolbar">
          <div class="comics-toolbar__identity">
            <h1 v-if="!homeShowcase">{{ displayTitle }}</h1>
            <HomeCollectionStat
              v-if="homeShowcase"
              :count="status.count"
              kind="comic"
              :label="$t('collectionArtworksLabel')"
              :title="displayTitle">
            </HomeCollectionStat>
            <p v-else-if="status.count !== null">
              {{ status.count }} {{ $t("collectionArtworksLabel") }}
            </p>
          </div>
          <div class="toolbar-actions">
            <button
              v-if="user.loggedIn && !embedded && showCreate"
              class="comic-create-action"
              type="button"
              @click="createComic">
              <span class="comic-create-action__shine" aria-hidden="true"></span>
              <b-icon icon="plus" custom-size="mdi-19px"></b-icon>
              <span>{{ $t("NewComicTitle") }}</span>
            </button>
          </div>
        </div>
        <div v-if="embedded && status.count !== null" class="comic-page-summary">
          {{ currentPage + 1 }}/{{ totalPages }} · {{ status.count }}
        </div>
        <div
          v-if="embedded"
          class="comic-row-shell"
          :class="{
            'can-page-left': currentPage > 0,
            'can-page-right': status.hasNext
          }">
          <button
            v-if="currentPage > 0"
            class="comic-page-button is-left"
            type="button"
            :disabled="status.loading"
            :aria-label="$t('previousPageButton')"
            :title="$t('previousPageButton')"
            @click="previousPage">
            <span class="comic-page-button__halo" aria-hidden="true"></span>
            <span class="comic-page-button__surface" aria-hidden="true">
              <span class="comic-page-button__shine"></span>
            </span>
            <b-icon icon="chevron-left" custom-size="mdi-27px"></b-icon>
          </button>
          <div
            v-if="comics.length > 0"
            class="comic-grid motion-stagger"
            v-layout-ready="{ itemSelector: '.comic-card-shell' }"
            :style="gridStyle">
            <ComicCard
              v-for="comic in comics"
              :key="comic.id"
              :comic="comic"
              :current-username="user.loggedIn ? user.meta.username : null"
              :like-busy="comic.likeBusy"
              @read="openComic"
              @delete="deleteComic"
              @toggle-like="toggleComicLike">
            </ComicCard>
          </div>
          <button
            v-if="status.hasNext"
            class="comic-page-button is-right"
            type="button"
            :disabled="status.loading"
            :aria-label="$t('nextPageButton')"
            :title="$t('nextPageButton')"
            @click="nextPage">
            <span class="comic-page-button__halo" aria-hidden="true"></span>
            <span class="comic-page-button__surface" aria-hidden="true">
              <span class="comic-page-button__shine"></span>
            </span>
            <b-icon icon="chevron-right" custom-size="mdi-27px"></b-icon>
          </button>
        </div>
        <div
          v-else
          ref="masonryContainer"
          class="comic-masonry-container">
          <div
            v-if="comics.length > 0"
            ref="masonryGrid"
            v-masonry=""
            v-layout-ready="{ itemSelector: '.comic-masonry-item' }"
            :key="masonryKey"
            :style="gridStyle"
            class="comic-masonry motion-stagger"
            transition-duration="0.16s"
            item-selector=".comic-masonry-item"
            column-width=".comic-masonry-sizer"
            gutter=".comic-masonry-gutter"
            fit-width="true">
            <div class="comic-masonry-sizer" aria-hidden="true"></div>
            <div class="comic-masonry-gutter" aria-hidden="true"></div>
            <ComicCard
              v-for="comic in comics"
              :key="comic.id"
              v-masonry-tile
              class="comic-masonry-item"
              :comic="comic"
              :current-username="user.loggedIn ? user.meta.username : null"
              :like-busy="comic.likeBusy"
              @read="openComic"
              @delete="deleteComic"
              @toggle-like="toggleComicLike"
              @image-settled="queueMasonryLayout"
              @layout-settled="queueMasonryLayout">
            </ComicCard>
          </div>
        </div>
        <div
          v-if="showInitialSkeleton"
          class="comic-skeleton-grid"
          :style="gridStyle"
          aria-hidden="true">
          <div v-for="index in skeletonCount" :key="index" class="comic-skeleton-card">
            <div class="comic-skeleton-cover"></div>
            <div class="comic-skeleton-line is-wide"></div>
            <div class="comic-skeleton-line"></div>
          </div>
        </div>
        <div v-if="status.error" class="comic-state is-error">
          <p>{{ $t("cardLoadError") }}</p>
          <button class="button is-light" type="button" @click="retryLoad">
            {{ $t("loadMoreResults") }}
          </button>
        </div>
        <div v-else-if="showEmptyState" class="comic-state is-empty">
          <p>{{ $t("comicsEmptyState") }}</p>
        </div>
        <loadingSpinner :show="status.loading && comics.length > 0" size="compact"></loadingSpinner>
        <div
          v-if="usesInfiniteMasonry && status.hasNext"
          ref="loadSentinel"
          class="comic-load-sentinel"
          aria-hidden="true">
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import API from '../components/api';
import ComicCard from '../components/ComicCard.vue';
import HomeCollectionStat from '../components/HomeCollectionStat.vue';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import modals from '../components/modals';

const FULL_PAGE_BATCH_SIZE = 12;
const FULL_PAGE_MAX_COLUMNS = 4;
const MASONRY_GUTTER = 16;
const MAX_MEASURE_ATTEMPTS = 8;

function comicGridCapacity(viewportWidth) {
  if (viewportWidth < 543) {
    return 1;
  }
  if (viewportWidth < 798) {
    return 2;
  }
  if (viewportWidth < 1053) {
    return 3;
  }
  if (viewportWidth < 1308) {
    return 4;
  }
  if (viewportWidth < 1818) {
    return 5;
  }
  if (viewportWidth < 2583) {
    return 6;
  }
  if (viewportWidth < 2838) {
    return 7;
  }
  return 8;
}

function comicPageLimit(largeCards = false, maxColumns = null) {
  if (typeof window === 'undefined') {
    const fallback = largeCards ? 3 : 4;
    return maxColumns ? Math.min(fallback, maxColumns) : fallback;
  }
  const viewportWidth = window.innerWidth
    || document.documentElement.clientWidth
    || 0;
  const capacity = comicGridCapacity(viewportWidth);
  const cardCapacity = largeCards ? Math.max(1, capacity - 1) : capacity;
  return maxColumns ? Math.min(cardCapacity, maxColumns) : cardCapacity;
}

function masonryMetrics(containerWidth, columns) {
  const safeWidth = Math.max(0, containerWidth || 0);
  const safeColumns = Math.max(1, columns || 1);
  const gutter = safeColumns === 1 ? 0 : MASONRY_GUTTER;
  const availableWidth = Math.max(1, safeWidth - ((safeColumns - 1) * gutter));
  const itemWidth = Math.round((availableWidth / safeColumns) * 1000) / 1000;
  return { columns: safeColumns, gutter, itemWidth };
}

export default {
  name: 'Comics',
  components: {
    ComicCard,
    HomeCollectionStat,
    PHeader,
    loadingSpinner,
  },
  props: {
    embedded: {
      type: Boolean,
      default: false,
    },
    showCreate: {
      type: Boolean,
      default: true,
    },
    largeCards: {
      type: Boolean,
      default: false,
    },
    homeShowcase: {
      type: Boolean,
      default: false,
    },
    maxColumns: {
      type: Number,
      default: null,
      validator(value) {
        return value === null || (Number.isInteger(value) && value > 0);
      },
    },
    tagFilter: {
      type: String,
      default: null,
    },
    title: {
      type: String,
      default: null,
    },
    userFilter: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      comics: [],
      currentPage: 0,
      pageLimit: comicPageLimit(
        this.largeCards,
        this.embedded ? this.maxColumns : FULL_PAGE_MAX_COLUMNS,
      ),
      resizeTimer: null,
      requestEpoch: 0,
      masonryKey: 0,
      masonryMetrics: masonryMetrics(240, 1),
      masonryMetricsSignature: '240-0-1',
      masonryMeasureAttempts: 0,
      masonryMeasureTimer: null,
      masonryMeasureFrame: null,
      masonryLayoutFrame: null,
      masonryLayoutTimers: [],
      masonryResizeObserver: null,
      loadObserver: null,
      fillViewportTimer: null,
      scrollFallbackBound: false,
      status: {
        count: null,
        error: false,
        hasNext: false,
        loading: false,
        offset: 0,
      },
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    showInitialSkeleton() {
      return this.status.loading && this.comics.length === 0;
    },
    showEmptyState() {
      return !this.status.loading
        && !this.status.error
        && this.comics.length === 0;
    },
    displayTitle() {
      return this.title || this.$t('comicsLink');
    },
    usesInfiniteMasonry() {
      return !this.embedded;
    },
    skeletonCount() {
      return this.usesInfiniteMasonry ? this.pageLimit * 2 : this.pageLimit;
    },
    totalPages() {
      if (this.status.count === null || this.status.count === 0) return 1;
      return Math.max(1, Math.ceil(this.status.count / this.pageLimit));
    },
    gridStyle() {
      return {
        '--comic-page-limit': this.pageLimit,
        '--comic-masonry-width': `${this.masonryMetrics.itemWidth}px`,
        '--comic-masonry-gutter': `${this.masonryMetrics.gutter}px`,
      };
    },
  },
  watch: {
    largeCards() {
      this.pageLimit = comicPageLimit(
        this.largeCards,
        this.embedded ? this.maxColumns : FULL_PAGE_MAX_COLUMNS,
      );
      this.resetPages();
    },
    maxColumns() {
      if (this.usesInfiniteMasonry) {
        return;
      }
      this.pageLimit = comicPageLimit(this.largeCards, this.maxColumns);
      this.resetPages();
    },
    tagFilter() {
      this.resetPages();
    },
    userFilter() {
      this.resetPages();
    },
  },
  created() {
    this.fetchUser();
    this.resetPages();
    window.addEventListener('resize', this.handleResize);
  },
  mounted() {
    if (this.usesInfiniteMasonry) {
      this.observeMasonryContainer();
      this.measureMasonryWhenReady();
      this.setupInfiniteLoading();
    }
  },
  beforeDestroy() {
    if (this.resizeTimer) {
      window.clearTimeout(this.resizeTimer);
    }
    if (this.masonryMeasureTimer) {
      window.clearTimeout(this.masonryMeasureTimer);
    }
    if (this.masonryMeasureFrame) {
      const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
      cancelFrame(this.masonryMeasureFrame);
    }
    if (this.masonryResizeObserver) {
      this.masonryResizeObserver.disconnect();
    }
    if (this.loadObserver) {
      this.loadObserver.disconnect();
    }
    if (this.fillViewportTimer) {
      window.clearTimeout(this.fillViewportTimer);
    }
    if (this.scrollFallbackBound) {
      window.removeEventListener('scroll', this.handleInfiniteScroll);
    }
    this.clearMasonryLayoutTimers();
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    openComic(comic) {
      this.$router.push({ name: 'comic', params: { comicId: comic.id } });
    },
    fetchUser() {
      API.User.fetchUserInfo().then(
        (user) => {
          if (user === null) {
            this.user.loggedIn = false;
            this.user.meta = {};
            return;
          }
          this.user.loggedIn = true;
          this.user.meta = user;
        },
      );
    },
    fetchPage(page) {
      if (this.status.loading || page < 0 || this.usesInfiniteMasonry) {
        return;
      }
      const epoch = this.requestEpoch;
      this.status.loading = true;
      this.status.error = false;
      API.Comic.fetchList(
        page * this.pageLimit,
        this.pageLimit,
        this.tagFilter,
        this.userFilter,
      ).then(
        (resp) => {
          if (epoch !== this.requestEpoch) {
            return;
          }
          const { count, results, next } = resp.data;
          this.comics = (results || []).map(item => Object.assign({ likeBusy: false }, item));
          this.currentPage = page;
          this.status.count = count;
          this.status.hasNext = next !== null;
          this.status.offset = this.comics.length;
          this.status.loading = false;
          this.$emit('comics-meta-loaded', { count });
        },
        () => {
          if (epoch !== this.requestEpoch) {
            return;
          }
          this.status.loading = false;
          this.status.error = true;
        },
      );
    },
    fetchNext() {
      if (!this.usesInfiniteMasonry || this.status.loading || !this.status.hasNext) {
        return;
      }
      const epoch = this.requestEpoch;
      const { offset } = this.status;
      this.status.loading = true;
      this.status.error = false;
      API.Comic.fetchList(
        offset,
        FULL_PAGE_BATCH_SIZE,
        this.tagFilter,
        this.userFilter,
      ).then(
        (resp) => {
          if (epoch !== this.requestEpoch) {
            return;
          }
          const { count, results, next } = resp.data;
          const incoming = (results || []).map(
            item => Object.assign({ likeBusy: false }, item),
          );
          const knownIds = new Set(this.comics.map(item => item.id));
          const additions = incoming.filter(item => !knownIds.has(item.id));
          this.comics = this.comics.concat(additions);
          this.status.count = count;
          this.status.offset = offset + incoming.length;
          this.status.hasNext = next !== null && incoming.length > 0;
          this.status.loading = false;
          this.$emit('comics-meta-loaded', { count });
          this.$nextTick(() => {
            this.measureMasonryWhenReady();
            this.queueMasonryLayout();
            this.observeLoadSentinel();
            this.scheduleViewportFill();
          });
        },
        () => {
          if (epoch !== this.requestEpoch) {
            return;
          }
          this.status.loading = false;
          this.status.error = true;
        },
      );
    },
    resetPages() {
      this.requestEpoch += 1;
      this.comics = [];
      this.currentPage = 0;
      this.status.count = null;
      this.status.error = false;
      this.status.hasNext = this.usesInfiniteMasonry;
      this.status.loading = false;
      this.status.offset = 0;
      if (this.usesInfiniteMasonry) {
        this.masonryKey += 1;
        this.fetchNext();
        this.$nextTick(this.observeLoadSentinel);
        return;
      }
      this.fetchPage(0);
    },
    handleResize() {
      if (this.resizeTimer) {
        window.clearTimeout(this.resizeTimer);
      }
      this.resizeTimer = window.setTimeout(() => {
        const nextLimit = comicPageLimit(
          this.largeCards,
          this.embedded ? this.maxColumns : FULL_PAGE_MAX_COLUMNS,
        );
        if (nextLimit === this.pageLimit && this.embedded) {
          return;
        }
        const limitChanged = nextLimit !== this.pageLimit;
        this.pageLimit = nextLimit;
        if (this.usesInfiniteMasonry) {
          this.measureMasonryWhenReady();
          if (limitChanged) {
            this.scheduleViewportFill();
          }
          return;
        }
        this.resetPages();
      }, 120);
    },
    nextPage() {
      if (this.status.hasNext) {
        this.fetchPage(this.currentPage + 1);
      }
    },
    previousPage() {
      if (this.currentPage > 0) {
        this.fetchPage(this.currentPage - 1);
      }
    },
    retryLoad() {
      if (this.usesInfiniteMasonry) {
        this.fetchNext();
        return;
      }
      this.fetchPage(this.currentPage);
    },
    createComic() {
      modals.openComicCreate(
        this,
        this.user.meta.username,
        () => {
          this.resetPages();
        },
      );
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
        () => {
          API.Comic.delete(comic.id).then(
            () => {
              this.comics = this.comics.filter(item => item.id !== comic.id);
              if (this.status.count !== null) {
                this.status.count = Math.max(0, this.status.count - 1);
              }
              this.$emit('comics-meta-loaded', { count: this.status.count });
              if (this.usesInfiniteMasonry) {
                this.status.offset = Math.max(0, this.status.offset - 1);
                this.$nextTick(() => {
                  this.queueMasonryLayout();
                  this.scheduleViewportFill();
                });
              } else if (this.comics.length === 0 && this.currentPage > 0) {
                this.fetchPage(this.currentPage - 1);
              }
            },
          );
        },
      );
    },
    updateMasonryMetrics() {
      const container = this.$refs.masonryContainer;
      const width = container ? container.clientWidth : 0;
      if (!width) {
        return false;
      }
      const metrics = masonryMetrics(width, this.pageLimit);
      const signature = `${metrics.itemWidth}-${metrics.gutter}-${metrics.columns}`;
      if (signature === this.masonryMetricsSignature) {
        return false;
      }
      this.masonryMetrics = metrics;
      this.masonryMetricsSignature = signature;
      return true;
    },
    measureMasonryWhenReady() {
      if (!this.usesInfiniteMasonry) {
        return;
      }
      if (this.masonryMeasureTimer) {
        window.clearTimeout(this.masonryMeasureTimer);
        this.masonryMeasureTimer = null;
      }
      this.$nextTick(() => {
        if (this.masonryMeasureFrame) {
          const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
          cancelFrame(this.masonryMeasureFrame);
        }
        const requestFrame = window.requestAnimationFrame
          || (callback => window.setTimeout(callback, 16));
        this.masonryMeasureFrame = requestFrame(() => {
          this.masonryMeasureFrame = null;
          if (this.updateMasonryMetrics()) {
            this.masonryMeasureAttempts = 0;
            this.masonryKey += 1;
            this.$nextTick(this.redrawMasonry);
            return;
          }
          const container = this.$refs.masonryContainer;
          const width = container ? container.clientWidth : 0;
          if (width || this.masonryMeasureAttempts >= MAX_MEASURE_ATTEMPTS) {
            this.masonryMeasureAttempts = 0;
            this.redrawMasonry();
            return;
          }
          this.masonryMeasureAttempts += 1;
          this.masonryMeasureTimer = window.setTimeout(
            this.measureMasonryWhenReady,
            Math.min(40 * this.masonryMeasureAttempts, 240),
          );
        });
      });
    },
    observeMasonryContainer() {
      if (!window.ResizeObserver || !this.$refs.masonryContainer) {
        return;
      }
      this.masonryResizeObserver = new window.ResizeObserver(() => {
        if (this.updateMasonryMetrics()) {
          this.masonryKey += 1;
          this.$nextTick(this.redrawMasonry);
        }
      });
      this.masonryResizeObserver.observe(this.$refs.masonryContainer);
    },
    redrawMasonry() {
      if (typeof this.$redrawVueMasonry === 'function') {
        this.$redrawVueMasonry();
      }
    },
    queueMasonryLayout() {
      if (!this.usesInfiniteMasonry) {
        return;
      }
      this.clearMasonryLayoutTimers();
      this.$nextTick(() => {
        const requestFrame = window.requestAnimationFrame
          || (callback => window.setTimeout(callback, 16));
        this.masonryLayoutFrame = requestFrame(() => {
          this.masonryLayoutFrame = null;
          this.redrawMasonry();
        });
        [100, 220, 420].forEach((delay) => {
          this.masonryLayoutTimers.push(
            window.setTimeout(this.redrawMasonry, delay),
          );
        });
      });
    },
    clearMasonryLayoutTimers() {
      if (this.masonryLayoutFrame) {
        const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
        cancelFrame(this.masonryLayoutFrame);
        this.masonryLayoutFrame = null;
      }
      this.masonryLayoutTimers.forEach(timer => window.clearTimeout(timer));
      this.masonryLayoutTimers = [];
    },
    setupInfiniteLoading() {
      if (window.IntersectionObserver) {
        this.loadObserver = new window.IntersectionObserver(
          (entries) => {
            if (entries.some(entry => entry.isIntersecting)) {
              this.fetchNext();
            }
          },
          { rootMargin: '520px 0px' },
        );
        this.observeLoadSentinel();
      } else {
        window.addEventListener('scroll', this.handleInfiniteScroll, { passive: true });
        this.scrollFallbackBound = true;
      }
      this.scheduleViewportFill();
    },
    observeLoadSentinel() {
      if (!this.loadObserver) {
        return;
      }
      this.loadObserver.disconnect();
      if (this.$refs.loadSentinel) {
        this.loadObserver.observe(this.$refs.loadSentinel);
      }
    },
    handleInfiniteScroll() {
      const { body, documentElement } = document;
      const scrollHeight = Math.max(
        documentElement.scrollHeight,
        body ? body.scrollHeight : 0,
      );
      const currentBottom = window.pageYOffset + window.innerHeight;
      if (currentBottom >= scrollHeight - 520) {
        this.fetchNext();
      }
    },
    scheduleViewportFill() {
      if (!this.usesInfiniteMasonry) {
        return;
      }
      if (this.fillViewportTimer) {
        window.clearTimeout(this.fillViewportTimer);
      }
      this.fillViewportTimer = window.setTimeout(() => {
        this.fillViewportTimer = null;
        if (this.status.loading || !this.status.hasNext) {
          return;
        }
        const { body, documentElement } = document;
        const scrollHeight = Math.max(
          documentElement.scrollHeight,
          body ? body.scrollHeight : 0,
        );
        if (scrollHeight <= window.innerHeight + 280) {
          this.fetchNext();
        }
      }, 240);
    },
    toggleComicLike(comic) {
      if (comic.likeBusy) {
        return;
      }
      this.$set(comic, 'likeBusy', true);
      API.Comic.toggleLike(comic.id).then(
        (resp) => {
          this.$set(comic, 'viewer_liked', resp.data.viewer_liked);
          this.$set(comic, 'likes_count', resp.data.likes_count);
          this.$set(comic, 'likeBusy', false);
        },
        () => {
          this.$set(comic, 'likeBusy', false);
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../components/utils/motion-mixins';
@import '../components/utils/grid-layout';

.comics-page {
  min-height: 100vh;
  background: transparent;
}

.comics-page.is-embedded {
  min-height: 0;
  background: transparent;
}

.comics-page.is-embedded .comics-section {
  padding-top: var(--space-md, 16px);
}

.comics-page.is-infinite-masonry .comics-section {
  padding-right: 0;
  padding-left: 0;
}

.comics-container {
  margin: 0 auto;
}

.comics-page.is-infinite-masonry .comics-container {
  box-sizing: border-box;
  width: min(1260px, calc(100vw - 32px));
  max-width: min(1260px, calc(100vw - 32px));
}

.comics-section {
  padding-bottom: var(--space-xl, 32px);
}

.comics-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md, 16px);
  margin-bottom: var(--space-lg, 24px);
  padding: var(--space-md, 16px);
  border: 1px solid var(--color-border-soft, var(--line-soft, #e7ebf2));
  border-radius: var(--radius-card, 22px);
  background: var(--color-surface-card, var(--surface-card, #fff));
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}

.comics-toolbar__identity {
  min-width: 0;
}

.comics-page.is-home-showcase .comics-toolbar__identity {
  width: min(100%, 420px);
  flex: 0 1 420px;
}

.comics-toolbar h1 {
  margin: 0;
  color: var(--color-text-primary, var(--text-strong, #22313f));
  font-size: clamp(1.35rem, 2vw, 1.8rem);
  font-weight: 900;
}

.comics-toolbar p {
  margin: var(--space-2xs, 4px) 0 0;
  color: var(--color-text-muted, var(--text-muted, #64748b));
  font-size: 0.95rem;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 12px);
}

.comic-create-action {
  position: relative;
  isolation: isolate;
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: 0.62rem 1.08rem;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--color-accent-border) 82%, #fff);
  border-radius: var(--radius-pill);
  color: var(--color-accent-text);
  background:
    radial-gradient(circle at 24% 16%, color-mix(in srgb, #fff 42%, transparent), transparent 38%),
    linear-gradient(135deg, var(--color-accent), var(--color-accent-strong));
  box-shadow:
    0 12px 26px var(--color-theme-glow),
    inset 0 1px 0 color-mix(in srgb, #fff 46%, transparent);
  cursor: pointer;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 900;
  letter-spacing: 0;
  appearance: none;
  -webkit-tap-highlight-color: transparent;
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    filter var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
}

.comic-create-action::after {
  content: '';
  position: absolute;
  z-index: 0;
  inset: 3px;
  border: 1px solid color-mix(in srgb, var(--color-accent-text) 30%, transparent);
  border-radius: inherit;
  pointer-events: none;
}

.comic-create-action__shine {
  position: absolute;
  z-index: 0;
  top: -55%;
  bottom: -55%;
  left: -45%;
  width: 26%;
  background: linear-gradient(
    105deg,
    transparent,
    color-mix(in srgb, var(--color-accent-text) 72%, transparent),
    transparent
  );
  opacity: 0.68;
  pointer-events: none;
  transform: skewX(-18deg);
}

.comic-create-action .icon,
.comic-create-action > span:last-child {
  position: relative;
  z-index: 1;
}

.comic-create-action .icon {
  transition: transform var(--motion-duration-standard) var(--motion-ease-spring);
}

.comic-create-action:focus-visible {
  outline: none;
  box-shadow:
    var(--focus-ring),
    0 15px 32px var(--color-theme-glow-strong),
    inset 0 1px 0 color-mix(in srgb, #fff 52%, transparent);
}

.comic-create-action:active {
  filter: saturate(0.92);
  transform: translateY(0) scale(0.97);
  transition-duration: var(--motion-duration-instant);
}

html[data-motion='full'] .comic-create-action__shine {
  animation: comic-create-action-shine 3.8s var(--motion-ease-standard) infinite;
}

@media (hover: hover) and (pointer: fine) {
  .comic-create-action:hover {
    border-color: color-mix(in srgb, var(--color-accent) 72%, #fff);
    filter: saturate(1.12) brightness(1.04);
    transform: translateY(-2px) scale(1.025);
    box-shadow:
      0 17px 34px var(--color-theme-glow-strong),
      0 0 0 4px color-mix(in srgb, var(--color-accent-soft) 72%, transparent),
      inset 0 1px 0 color-mix(in srgb, #fff 56%, transparent);
  }

  .comic-create-action:hover .icon {
    transform: rotate(90deg) scale(1.08);
  }
}

.comic-row-shell {
  position: relative;
}

.comic-page-summary {
  margin: 0 0 var(--space-xs, 8px);
  color: var(--color-text-muted, var(--text-muted, #64748b));
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
}

.comic-row-shell::before,
.comic-row-shell::after {
  content: "";
  position: absolute;
  z-index: 5;
  top: 0;
  bottom: calc(-1 * var(--space-md, 16px));
  width: 76px;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease);
}

.comics-page.is-embedded .comic-row-shell::before {
  background: linear-gradient(
    to right,
    color-mix(in srgb, var(--app-bg, #f6f7fb) 72%, transparent),
    transparent
  );
}

.comics-page.is-embedded .comic-row-shell::after {
  background: linear-gradient(
    to left,
    color-mix(in srgb, var(--app-bg, #f6f7fb) 72%, transparent),
    transparent
  );
}

.comic-row-shell::before {
  left: 0;
  background: linear-gradient(
    to right,
    color-mix(in srgb, var(--app-bg, #f6f7fb) 72%, transparent),
    transparent
  );
}

.comic-row-shell::after {
  right: 0;
  background: linear-gradient(
    to left,
    color-mix(in srgb, var(--app-bg, #f6f7fb) 72%, transparent),
    transparent
  );
}

.comic-row-shell.can-page-left::before,
.comic-row-shell.can-page-right::after {
  opacity: 1;
}

.comics-page.is-home-showcase .comic-row-shell::before,
.comics-page.is-home-showcase .comic-row-shell::after {
  content: none;
}

.comic-page-button {
  position: absolute;
  z-index: 6;
  top: 50%;
  isolation: isolate;
  display: grid;
  width: 3.2rem;
  min-width: 3.2rem;
  height: 3.2rem;
  place-items: center;
  padding: 0;
  overflow: visible;
  border: 0;
  border-radius: 50%;
  color: var(--color-accent-text);
  background: transparent;
  cursor: pointer;
  transform: translateY(-50%);
  box-shadow: none;
  -webkit-tap-highlight-color: transparent;
  transition:
    transform 340ms var(--motion-ease-emphasized),
    filter 340ms var(--motion-ease-standard),
    opacity var(--motion-duration-fast) var(--motion-ease-standard);
}

.comic-page-button__surface {
  position: absolute;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--color-accent-border) 82%, #fff);
  border-radius: 50%;
  background:
    radial-gradient(circle at 32% 24%, rgba(255, 255, 255, 0.48), transparent 34%),
    linear-gradient(145deg, var(--color-accent), var(--color-accent-strong));
  box-shadow:
    0 16px 34px color-mix(in srgb, var(--color-theme-glow-strong) 84%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.62);
  pointer-events: none;
  transform: translateZ(0) scale(1);
  transition:
    border-color 300ms var(--motion-ease-standard),
    box-shadow 360ms var(--motion-ease-standard),
    transform 360ms var(--motion-ease-emphasized);
}

.comic-page-button__surface::before {
  position: absolute;
  z-index: 1;
  inset: 3px;
  border: 1px solid rgba(255, 255, 255, 0.42);
  border-radius: inherit;
  content: '';
  pointer-events: none;
}

.comic-page-button__shine {
  position: absolute;
  z-index: 2;
  top: -45%;
  bottom: -45%;
  left: -72%;
  width: 34%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.78), transparent);
  opacity: 0.72;
  pointer-events: none;
  transform: skewX(-18deg);
}

.comic-page-button .icon {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 3px 5px rgba(34, 18, 62, 0.3));
  transition: transform var(--motion-duration-standard) var(--motion-ease-spring);
}

.comic-page-button__halo {
  position: absolute;
  z-index: -1;
  inset: -8px;
  border: 2px solid var(--color-accent-border);
  border-radius: 50%;
  opacity: 0;
  pointer-events: none;
  transform: scale(0.78);
}

.comic-page-button.is-left {
  left: calc(var(--space-md) * -1);
}

.comic-page-button.is-right {
  right: calc(var(--space-md) * -1);
}

.comic-page-button:focus-visible {
  outline: none;
}

.comic-page-button:focus-visible .comic-page-button__surface {
  box-shadow:
    var(--focus-ring),
    0 18px 38px var(--color-theme-glow-strong),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.comic-page-button:active {
  filter: saturate(0.92);
  transform: translateY(-50%) scale(0.95);
  transition-duration: 120ms;
}

.comic-page-button:active .comic-page-button__surface {
  animation: none;
  transform: scale(0.96);
  transition-duration: 120ms;
}

.comic-page-button:disabled {
  opacity: 0.58;
  cursor: wait;
  filter: saturate(0.62);
}

.comic-page-button:disabled .comic-page-button__surface,
.comic-page-button:disabled .comic-page-button__shine,
.comic-page-button:disabled .comic-page-button__halo {
  animation-play-state: paused;
}

html[data-motion='full'] .comic-page-button__shine {
  animation: comic-page-button-shine 3.2s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .comic-page-button__halo {
  animation: comic-page-button-halo 2.8s var(--motion-ease-standard) infinite;
}

html[data-motion='full'] .comic-page-button__surface {
  animation: comic-page-button-breathe 4.2s var(--motion-ease-standard) infinite;
}

@media (hover: hover) and (pointer: fine) {
  .comic-page-button:hover:not(:disabled) {
    filter: saturate(1.18) brightness(1.04);
    transform: translateY(-50%) scale(1.065);
  }

  .comic-page-button:hover:not(:disabled) .comic-page-button__surface {
    animation: none;
    border-color: color-mix(in srgb, var(--color-accent) 68%, #fff);
    transform: scale(1.025);
    box-shadow:
      0 20px 44px var(--color-theme-glow-strong),
      0 0 0 5px color-mix(in srgb, var(--color-accent-soft) 72%, transparent),
      inset 0 1px 0 rgba(255, 255, 255, 0.72);
  }

  .comic-page-button.is-left:hover:not(:disabled) .icon {
    transform: translateX(-3px) scale(1.08);
  }

  .comic-page-button.is-right:hover:not(:disabled) .icon {
    transform: translateX(3px) scale(1.08);
  }
}

.comic-grid {
  display: grid;
  grid-template-columns: repeat(
    var(--comic-page-limit),
    minmax(0, var(--comic-card-width, var(--pin-card-width, 240px)))
  );
  gap: var(--space-md, var(--pin-grid-gutter, 15px));
  justify-content: start;
  perspective: 1200px;
}

.comic-masonry-container {
  width: 100%;
  min-width: 0;
}

.comic-masonry {
  margin-right: auto;
  margin-left: auto;
  background: transparent;
  perspective: 1200px;
}

.comic-masonry-sizer,
.comic-masonry-item {
  width: var(--comic-masonry-width, 240px);
}

.comic-masonry-gutter {
  width: var(--comic-masonry-gutter, 16px);
}

.comic-masonry-item {
  margin-bottom: calc(var(--comic-masonry-gutter, 16px) + 14px);
  transform: none;
  will-change: top, left;
}

.comic-load-sentinel {
  width: 100%;
  height: 2px;
  pointer-events: none;
}

.comic-card-shell {
  position: relative;
  min-width: 0;
  z-index: 1;
}

.comic-card-shell.is-tilting {
  z-index: 3;
}

.comic-card {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-width: 0;
  color: inherit;
  cursor: pointer;
  border: 1px solid var(--color-border-accent, var(--accent-border, rgba(126, 87, 194, 0.42)));
  border-radius: var(--radius-card, 22px);
  background:
    radial-gradient(circle at top left, var(--theme-glow), transparent 240px),
    var(--color-surface-card, var(--surface-card, #fff));
  box-shadow:
    0 0 0 2px var(--accent-soft, rgba(126, 87, 194, 0.08)),
    var(--shadow-card, 0 18px 50px rgba(15, 23, 42, 0.16));
  transform-style: preserve-3d;
  will-change: transform;
}

.comic-card::before,
.comic-card::after {
  content: "";
  position: absolute;
  left: var(--space-sm, 12px);
  right: var(--space-sm, 12px);
  height: 12px;
  border: 1px solid var(--accent-border, rgba(126, 87, 194, 0.22));
  border-radius: 0 0 var(--radius-sm, 8px) var(--radius-sm, 8px);
  background: var(--accent-soft, #faf7ff);
  pointer-events: none;
}

.comic-card::before {
  bottom: -7px;
  z-index: -1;
}

.comic-card::after {
  bottom: -13px;
  left: var(--space-lg, 24px);
  right: var(--space-lg, 24px);
  background: var(--surface-accent, #f0ebff);
  z-index: -2;
}

.comic-card-shell.is-tilting {
  z-index: 3;
}

.comic-glare {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: var(--tilt-glare-opacity, 0);
  background: radial-gradient(
    circle at var(--tilt-glare-x, 50%) var(--tilt-glare-y, 50%),
    rgba(255, 255, 255, 0.52),
    rgba(255, 255, 255, 0.08) 34%,
    transparent 62%
  );
  mix-blend-mode: screen;
  transition: opacity var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease);
  z-index: 2;
}

.comic-ribbon {
  position: absolute;
  z-index: 4;
  top: var(--space-sm, 12px);
  left: var(--space-sm, 12px);
  padding: 0.25rem 0.45rem;
  border-radius: var(--radius-sm, 8px);
  color: var(--accent-text, #fff);
  background: var(--accent-strong, #7e57c2);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.02em;
}

.comic-card-menu {
  position: absolute;
  z-index: 8;
  top: var(--space-xs, 8px);
  right: var(--space-xs, 8px);
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--radius-sm, 8px);
  background: rgba(15, 23, 42, 0.58);
  backdrop-filter: blur(8px);
  box-shadow: var(--shadow-card, 0 10px 24px rgba(15, 23, 42, 0.24));
}

.comic-menu-enter-active,
.comic-menu-leave-active {
  transition: opacity var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease), transform var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease);
}

.comic-menu-enter,
.comic-menu-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}

.comic-cover {
  position: relative;
  isolation: isolate;
  aspect-ratio: 2 / 3;
  min-height: 220px;
  overflow: hidden;
  border-radius: var(--radius-card, 22px) var(--radius-card, 22px) 0 0;
  background: var(--color-surface-muted, var(--surface-accent, #f7f3ff));
}

.comic-cover::before {
  content: "";
  position: absolute;
  z-index: 0;
  inset: -18px;
  background-image: var(--comic-cover-image);
  background-position: center;
  background-size: cover;
  filter: blur(18px) saturate(1.18);
  opacity: 0.42;
  transform: scale(1.06);
}

.comic-cover::after {
  content: "";
  position: absolute;
  z-index: 0;
  inset: 0;
  background: var(--theme-glow, rgba(255, 255, 255, 0.18));
}

.comic-cover img,
.comic-cover-placeholder {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
}

.comic-cover img {
  display: block;
  object-fit: cover;
}

.comic-cover-placeholder,
.comic-skeleton-cover {
  display: grid;
  min-height: 220px;
  place-items: center;
  padding: var(--space-md, 16px);
  color: var(--color-text-muted, var(--text-muted, #64748b));
  background: linear-gradient(135deg, var(--color-surface-muted, #f1f5f9), var(--color-surface-card, #fff));
  text-align: center;
}

.comic-info {
  padding: var(--space-md, 16px);
  border-top: 1px solid var(--color-border-soft, var(--line-soft, #efe9ff));
}

.comic-info h2 {
  overflow: hidden;
  margin: 0;
  color: var(--color-text-primary, var(--text-strong, #22313f));
  font-size: 16px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
  max-height: 3.25rem;
  margin-top: var(--space-xs, 8px);
  overflow: hidden;
}

.comic-tags a,
.comic-tag-more {
  max-width: 100%;
  padding: 0.15rem 0.42rem;
  border: 0;
  border-radius: 999px;
  color: var(--accent-strong, #6d4bc1);
  background: var(--accent-soft, #f2edff);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.comic-tag-more {
  color: var(--color-text-muted, var(--text-muted, #64748b));
  background: var(--color-surface-muted, var(--surface-2, #eef1f5));
  cursor: pointer;
}

.comic-author {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  min-width: 0;
  margin-top: var(--space-xs, 8px);
  color: var(--color-text-muted, var(--text-muted, #64748b));
  font-size: 13px;
}

.comic-author img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.comic-author a {
  overflow: hidden;
  min-width: 0;
  color: var(--color-text-primary, var(--text-strong, #334155));
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comic-author span {
  flex: 0 0 auto;
}

.comic-source {
  overflow: hidden;
  margin: var(--space-xs, 8px) 0 0;
  color: var(--color-text-muted, var(--text-muted, #64748b));
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comic-source a,
.comic-source span {
  color: var(--accent-strong, #7e57c2);
  font-weight: 700;
}

.comic-source.is-warning {
  color: #8a6d1d;
}

.comic-like {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  min-height: 30px;
  margin-top: var(--space-xs, 8px);
  padding: 0 0.58rem;
  border: 1px solid var(--color-border-soft, var(--line-soft, #e0e6ef));
  border-radius: 999px;
  color: var(--color-text-muted, var(--text-muted, #64748b));
  background: var(--color-surface-muted, var(--surface-2, #f8fafc));
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
  transition: transform var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease), color var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease), background var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease), border-color var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease);
}

.comic-like:hover,
.comic-like.is-liked {
  color: var(--accent-strong, #7e57c2);
  border-color: var(--accent, #7e57c2);
  background: var(--accent-soft, rgba(126, 87, 194, 0.14));
}

.comic-like:hover {
  transform: translateY(-1px);
}

.comic-like:disabled {
  opacity: 0.72;
  cursor: wait;
}

.comic-skeleton-grid {
  display: grid;
  grid-template-columns: repeat(var(--comic-page-limit), minmax(0, 1fr));
  gap: var(--space-md, 16px);
}

.comic-skeleton-card,
.comic-state {
  border: 1px solid var(--color-border-soft, rgba(148, 163, 184, 0.24));
  border-radius: var(--radius-card, 22px);
  background: var(--color-surface-card, #fff);
  box-shadow: var(--shadow-card, 0 18px 50px rgba(15, 23, 42, 0.12));
}

.comic-skeleton-card {
  padding: var(--space-sm, 12px);
}

.comic-skeleton-line {
  height: 10px;
  margin-top: var(--space-sm, 12px);
  border-radius: 999px;
  background: linear-gradient(90deg, var(--skeleton-base, #eef2f7), var(--skeleton-highlight, #f8fafc), var(--skeleton-base, #eef2f7));
  animation: pinry-soft-pulse 1.4s ease-in-out infinite;
}

.comic-skeleton-line.is-wide {
  width: 76%;
}

.comic-state {
  margin: var(--space-lg, 24px) auto;
  max-width: 460px;
  padding: var(--space-xl, 32px);
  text-align: center;
  color: var(--color-text-muted, #6b7280);
}

@media screen and (max-width: 542px) {
  .comics-toolbar {
    display: block;
  }

  .toolbar-actions {
    margin-top: var(--space-sm, 12px);
  }

  .toolbar-actions .button.is-primary {
    width: 100%;
  }

  .comic-create-action {
    width: 100%;
  }

  .comic-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .comic-page-button {
    width: 2.8rem;
    min-width: 2.8rem;
    height: 2.8rem;
  }

  .comic-page-button.is-left {
    left: calc(var(--space-xs) * -0.5);
  }

  .comic-page-button.is-right {
    right: calc(var(--space-xs) * -0.5);
  }
}

@media (hover: none) {
  .comic-card.motion-tilt-card {
    transform: none !important;
  }

  .comic-glare {
    display: none;
  }
}

html[data-motion="reduce"] {
  .comic-card.motion-tilt-card {
    transform: none !important;
  }

  .comic-glare {
    display: none;
  }

  .comic-page-button,
  .comic-page-button__surface,
  .comic-page-button__shine,
  .comic-page-button__halo,
  .comic-page-button .icon {
    animation: none;
    transition: none;
  }

  .comic-create-action,
  .comic-create-action__shine,
  .comic-create-action .icon {
    animation: none;
    transition: none;
  }
}

@keyframes comic-create-action-shine {
  0%, 52% {
    transform: translateX(0) skewX(-18deg);
  }

  78%, 100% {
    transform: translateX(620%) skewX(-18deg);
  }
}

@keyframes comic-page-button-shine {
  0%, 48% { transform: translateX(0) skewX(-18deg); }
  76%, 100% { transform: translateX(540%) skewX(-18deg); }
}

@keyframes comic-page-button-halo {
  0%, 100% { opacity: 0; transform: scale(0.78); }
  38% { opacity: 0.48; transform: scale(1); }
  74% { opacity: 0; transform: scale(1.2); }
}

@keyframes comic-page-button-breathe {
  0%, 100% { transform: translateZ(0) scale(1); }
  50% { transform: translateZ(0) scale(1.025); }
}

@include screen-grid-layout(".comics-page.is-embedded .comics-container");

@media screen and (max-width: 760px) {
  .comics-page.is-infinite-masonry .comics-container {
    width: calc(100vw - 20px);
    max-width: calc(100vw - 20px);
  }
}

/* R6 comic reset transition */
.comic-card-shell .motion-tilt-card {
  transition: transform var(--motion-duration-standard, 280ms) var(--motion-ease-spring, cubic-bezier(0.2, 0.8, 0.2, 1));
}
.comic-card-shell:not(.is-tilting) .motion-tilt-glare {
  transition-duration: var(--motion-duration-standard, 280ms);
}
.comic-card-shell.is-tilting .motion-tilt-card,
.comic-card-shell.is-tilting .motion-tilt-glare {
  transition-duration: 44ms;
}
</style>
