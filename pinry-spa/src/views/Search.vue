<template>
  <div class="search-page">
    <PHeader></PHeader>
    <section class="section search-shell">
      <div class="container search-container">
        <aside class="search-sidebar motion-card-enter">
          <div class="sidebar-eyebrow">{{ $t("aggregateSearchTitle") }}</div>
          <h1>{{ $t("searchPlaceholder") }}</h1>
          <p>{{ activeTypeLabel }}</p>
          <div class="search-types" role="list" :aria-label="$t('aggregateSearchTitle')">
            <button
              v-for="option in typeOptions"
              :key="option.value"
              class="search-type-pill"
              type="button"
              role="listitem"
              :class="{ 'is-active': activeType === option.value }"
              :aria-pressed="activeType === option.value ? 'true' : 'false'"
              @click="setType(option.value)">
              <span class="type-dot" :class="`is-${option.value}`"></span>
              <span>{{ option.label }}</span>
            </button>
          </div>
        </aside>

        <main class="search-main">
          <form class="search-card motion-fade-up" @submit.prevent="search(true)">
            <label class="search-label" for="aggregate-search-input">
              {{ $t("aggregateSearchTitle") }}
            </label>
            <div class="search-input-row">
              <input
                id="aggregate-search-input"
                class="input"
                v-model="queryText"
                maxlength="80"
                :aria-label="$t('searchPlaceholder')"
                :placeholder="$t('searchPlaceholder')"
                @input="clearError">
              <button
                class="button is-primary search-submit"
                type="submit"
                :class="{ 'is-loading': loading }"
                :disabled="normalizedQuery.length === 0 || loading">
                <span>{{ $t("searchButton") }}</span>
              </button>
            </div>
            <p class="search-helper">
              {{ activeTypeLabel }} · {{ $t("searchPlaceholder") }}
            </p>
          </form>

          <section class="state-card is-idle motion-card-enter" v-if="!hasSearched && !loading">
            <b-icon icon="magnify" custom-size="mdi-36px"></b-icon>
            <h2>{{ $t("aggregateSearchTitle") }}</h2>
            <p>{{ $t("searchPlaceholder") }}</p>
          </section>

          <section class="state-card is-loading" v-if="loading">
            <loadingSpinner :show="loading" size="regular"></loadingSpinner>
            <div class="skeleton-lines" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </section>

          <section class="state-card is-error" v-if="errorText && !loading">
            <b-icon icon="alert-circle-outline" custom-size="mdi-34px"></b-icon>
            <h2>{{ $t("searchFailedTitle") }}</h2>
            <p>{{ errorText }}</p>
            <button class="button is-light" type="button" @click="search(true)">
              {{ $t("searchButton") }}
            </button>
          </section>

          <div class="result-heading" v-if="hasSearched && !loading && !errorText">
            <span>{{ $t("searchResultsFor") }}</span>
            <strong>{{ resultQuery }}</strong>
          </div>

          <div
            class="empty-results motion-card-enter"
            v-if="hasSearched && !loading && !errorText && !hasAnyResults">
            <b-icon icon="image-search-outline" custom-size="mdi-32px"></b-icon>
            <div>
              <h2>{{ $t("noResultsFound") }}</h2>
              <p>{{ $t("searchEmptyHint") }}</p>
            </div>
          </div>

          <section
            class="result-section motion-stagger"
            v-if="shouldShowBucket('comics') && buckets.comics.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("comicsLink") }}</h2>
            </div>
            <SearchComicMasonry
              :comics="buckets.comics.results"
              @read="readComic"
              @toggle-like="toggleComicLike">
            </SearchComicMasonry>
            <button
              v-if="buckets.comics.has_next"
              class="button is-light search-load-more"
              type="button"
              :class="{ 'is-loading': loadingMore.comics }"
              :disabled="loadingMore.comics"
              @click="loadMore('comics')">
              {{ $t("loadMoreResults") }}
            </button>
          </section>

          <section
            class="result-section motion-stagger"
            v-if="shouldShowBucket('pins') && buckets.pins.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("pinsLink") }}</h2>
            </div>
            <div class="result-grid pin-results">
              <SearchPinCard
                v-for="pin in buckets.pins.results"
                :key="`pin-${pin.id}`"
                :pin="pin"
                :like-busy="pin.likeBusy"
                @preview="openPinPreview"
                @toggle-like="togglePinLike">
              </SearchPinCard>
            </div>
            <button
              v-if="buckets.pins.has_next"
              class="button is-light search-load-more"
              type="button"
              :class="{ 'is-loading': loadingMore.pins }"
              :disabled="loadingMore.pins"
              @click="loadMore('pins')">
              {{ $t("loadMoreResults") }}
            </button>
          </section>

          <section
            class="result-section motion-stagger"
            v-if="shouldShowBucket('boards') && buckets.boards.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("boardsLink") }}</h2>
            </div>
            <div class="result-grid">
              <SearchBoardCard
                v-for="board in buckets.boards.results"
                :key="`board-${board.id}`"
                :board="board">
              </SearchBoardCard>
            </div>
            <button
              v-if="buckets.boards.has_next"
              class="button is-light search-load-more"
              type="button"
              :class="{ 'is-loading': loadingMore.boards }"
              :disabled="loadingMore.boards"
              @click="loadMore('boards')">
              {{ $t("loadMoreResults") }}
            </button>
          </section>

          <section
            class="result-section motion-stagger"
            v-if="shouldShowBucket('tags') && buckets.tags.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("tagsLabel") }}</h2>
            </div>
            <div class="tag-result-list">
              <router-link
                v-for="tag in buckets.tags.results"
                :key="`tag-${tag.name}`"
                class="search-tag-pill content-tag-pill"
                :to="{ name: 'tag', params: { tag: tag.name } }">
                {{ tag.name }}
              </router-link>
            </div>
            <button
              v-if="buckets.tags.has_next"
              class="button is-light search-load-more"
              type="button"
              :class="{ 'is-loading': loadingMore.tags }"
              :disabled="loadingMore.tags"
              @click="loadMore('tags')">
              {{ $t("loadMoreResults") }}
            </button>
          </section>
        </main>
      </div>
    </section>
  </div>
</template>

<script>
import API from '../components/api';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import SearchPinCard from '../components/SearchPinCard.vue';
import SearchBoardCard from '../components/SearchBoardCard.vue';
import SearchComicMasonry from '../components/SearchComicMasonry.vue';
import PinPreview from '../components/PinPreview.vue';
import createPinDisplayItem from '../components/utils/pinDisplayItem';
import scroll from '../components/utils/scroll';
import { loadSearchState, saveSearchState } from '../components/utils/searchStateCache';

function blankBucket() {
  return {
    results: [],
    has_next: false,
    next_offset: 0,
  };
}

function bucketKeyForType(type) {
  if (type === 'pin') {
    return 'pins';
  }
  if (type === 'board') {
    return 'boards';
  }
  if (type === 'comic') {
    return 'comics';
  }
  if (type === 'tag') {
    return 'tags';
  }
  return null;
}

function currentScrollTop() {
  return Math.max(
    0,
    window.pageYOffset || document.documentElement.scrollTop || 0,
  );
}

function validSearchType(type) {
  return type === 'all' || bucketKeyForType(type) !== null;
}

function cachedBucket(bucket) {
  const source = bucket || {};
  return {
    results: Array.isArray(source.results) ? source.results : [],
    has_next: !!source.has_next,
    next_offset: Number.isFinite(source.next_offset) ? source.next_offset : 0,
  };
}

export default {
  name: 'Search',
  components: {
    PHeader,
    loadingSpinner,
    SearchPinCard,
    SearchBoardCard,
    SearchComicMasonry,
  },
  data() {
    return {
      activeType: 'all',
      buckets: {
        pins: blankBucket(),
        boards: blankBucket(),
        comics: blankBucket(),
        tags: blankBucket(),
      },
      errorText: '',
      hasSearched: false,
      loading: false,
      loadingMore: {
        pins: false,
        boards: false,
        comics: false,
        tags: false,
      },
      queryText: '',
      resultQuery: '',
      restoreScrollTop: 0,
      restoreScrollFrame: null,
    };
  },
  computed: {
    activeTypeLabel() {
      const selected = this.typeOptions.find(option => option.value === this.activeType);
      return selected ? selected.label : this.$t('searchAllOption');
    },
    hasAnyResults() {
      return Object.keys(this.buckets).some(
        key => this.buckets[key].results.length > 0,
      );
    },
    normalizedQuery() {
      return (this.queryText || '').trim();
    },
    typeOptions() {
      return [
        { value: 'all', label: this.$t('searchAllOption') },
        { value: 'pin', label: this.$t('pinLink') },
        { value: 'board', label: this.$t('boardLink') },
        { value: 'comic', label: this.$t('comicLink') },
        { value: 'tag', label: this.$t('tagsLabel') },
      ];
    },
  },
  created() {
    this.restoreCachedSearch();
  },
  mounted() {
    if (this.restoreScrollTop <= 0) {
      return;
    }
    this.$nextTick(() => {
      this.restoreScrollFrame = window.requestAnimationFrame(() => {
        window.scrollTo(0, this.restoreScrollTop);
        this.restoreScrollFrame = null;
      });
    });
  },
  beforeRouteLeave(to, from, next) {
    this.saveCachedSearch();
    next();
  },
  beforeDestroy() {
    if (this.restoreScrollFrame) {
      window.cancelAnimationFrame(this.restoreScrollFrame);
    }
    this.saveCachedSearch();
  },
  methods: {
    bucketNamesForType(type) {
      const key = bucketKeyForType(type);
      if (key) {
        return [key];
      }
      return ['comics', 'pins', 'boards', 'tags'];
    },
    clearError() {
      this.errorText = '';
    },
    restoreCachedSearch() {
      const cached = loadSearchState();
      if (!cached || !cached.resultQuery || !validSearchType(cached.activeType)) {
        return;
      }
      this.activeType = cached.activeType;
      this.buckets = {
        pins: cachedBucket(cached.buckets && cached.buckets.pins),
        boards: cachedBucket(cached.buckets && cached.buckets.boards),
        comics: cachedBucket(cached.buckets && cached.buckets.comics),
        tags: cachedBucket(cached.buckets && cached.buckets.tags),
      };
      this.hasSearched = true;
      this.queryText = cached.resultQuery;
      this.resultQuery = cached.resultQuery;
      this.restoreScrollTop = Number.isFinite(cached.scrollTop)
        ? cached.scrollTop
        : 0;
    },
    saveCachedSearch() {
      if (!this.hasSearched || !this.resultQuery || this.loading) {
        return;
      }
      saveSearchState({
        activeType: this.activeType,
        buckets: this.buckets,
        resultQuery: this.resultQuery,
        scrollTop: currentScrollTop(),
      });
    },
    resetBuckets() {
      this.buckets = {
        pins: blankBucket(),
        boards: blankBucket(),
        comics: blankBucket(),
        tags: blankBucket(),
      };
    },
    setType(type) {
      this.activeType = type;
      if (this.hasSearched) {
        this.search(true);
      }
    },
    search(reset = true) {
      if (this.normalizedQuery.length === 0 || this.loading) {
        return;
      }
      if (reset) {
        this.resetBuckets();
      }
      this.loading = true;
      this.errorText = '';
      this.resultQuery = this.normalizedQuery;
      this.hasSearched = true;
      API.Search.aggregate(
        this.resultQuery,
        this.activeType,
        {},
        this.activeType === 'all' ? 6 : 12,
      ).then(
        (resp) => {
          this.applySearchResponse(resp.data, false);
          this.loading = false;
          this.saveCachedSearch();
        },
        () => {
          this.loading = false;
          this.errorText = this.$t('searchLoadError');
        },
      );
    },
    applySearchResponse(data, append) {
      this.bucketNamesForType(data.type).forEach(
        (name) => {
          if (!data[name]) {
            return;
          }
          const nextBucket = Object.assign({}, data[name]);
          if (append) {
            nextBucket.results = this.buckets[name].results.concat(
              data[name].results,
            );
          }
          this.$set(this.buckets, name, nextBucket);
        },
      );
    },
    loadMore(name) {
      if (this.loadingMore[name] || !this.buckets[name].has_next) {
        return;
      }
      this.$set(this.loadingMore, name, true);
      this.errorText = '';
      const offsets = {};
      offsets[name] = this.buckets[name].next_offset;
      const type = name.slice(0, -1);
      API.Search.aggregate(
        this.resultQuery,
        type,
        offsets,
        12,
      ).then(
        (resp) => {
          this.applySearchResponse(resp.data, true);
          this.$set(this.loadingMore, name, false);
          this.saveCachedSearch();
        },
        () => {
          this.$set(this.loadingMore, name, false);
          this.errorText = this.$t('searchLoadMoreError');
        },
      );
    },
    openPinPreview(pin) {
      const routeAtOpen = this.$route.fullPath;
      const restoreScroll = scroll.preserveModalScrollPosition(
        () => this.$route.fullPath === routeAtOpen,
      );
      const previewModal = this.$buefy.modal.open(
        {
          parent: this,
          component: PinPreview,
          props: {
            pinItem: createPinDisplayItem(pin),
          },
          scroll: 'keep',
          customClass: 'pin-preview-at-home',
        },
      );
      previewModal.$once('close', restoreScroll);
    },
    shouldShowBucket(name) {
      return this.activeType === 'all' || bucketKeyForType(this.activeType) === name;
    },
    readComic(comic) {
      this.$router.push({ name: 'comic', params: { comicId: comic.id } });
    },
    togglePinLike(pin) {
      if (pin.likeBusy) {
        return;
      }
      this.$set(pin, 'likeBusy', true);
      API.Pin.toggleLike(pin.id).then(
        (resp) => {
          this.$set(pin, 'viewer_liked', resp.data.viewer_liked);
          this.$set(pin, 'likes_count', resp.data.likes_count);
          this.$set(pin, 'likeBusy', false);
          this.saveCachedSearch();
        },
        () => {
          this.$set(pin, 'likeBusy', false);
        },
      );
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
          this.saveCachedSearch();
        },
        () => {
          this.$set(comic, 'likeBusy', false);
        },
      );
    },
  },
};
</script>

<style scoped lang="scss">
@import "../components/utils/motion-mixins";

.search-shell {
  padding-top: var(--space-lg);
}
.search-container {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  gap: var(--space-lg);
  width: min(100%, var(--container-max));
  max-width: calc(100vw - var(--space-xl));
}
.search-sidebar,
.search-card,
.empty-results,
.state-card {
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 260px),
    var(--color-surface-1);
  box-shadow: var(--shadow-card);
}
.search-sidebar {
  position: sticky;
  top: 6.5rem;
  align-self: start;
  padding: var(--space-md);
}
.sidebar-eyebrow {
  color: var(--color-accent-foreground);
  font-size: 0.75rem;
  font-weight: 950;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}
.search-sidebar h1 {
  margin: var(--space-xs) 0 var(--space-xs);
  color: var(--color-text-strong);
  font-size: clamp(1.35rem, 4vw, 2rem);
  font-weight: 950;
  line-height: 1.08;
}
.search-sidebar p,
.search-helper,
.result-heading,
.result-body p,
.state-card p,
.empty-results p {
  color: var(--color-text-muted);
}
.search-types {
  display: grid;
  gap: var(--space-xs);
  margin-top: var(--space-md);
}
.search-type-pill {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  min-height: 42px;
  padding: 0 var(--space-sm);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: var(--color-surface-2);
  cursor: pointer;
  font-weight: 900;
  text-align: left;
  @include hover-scale(1.018, -2px);
}
.search-type-pill.is-active {
  color: var(--color-accent-foreground);
  border-color: var(--color-accent-border);
  background: var(--color-accent-soft-gradient);
  box-shadow: var(--shadow-xs);
}
.search-type-pill:focus-visible,
.search-card .input:focus,
.search-submit:focus-visible,
.search-load-more:focus-visible,
.tag-result-list a:focus-visible,
.state-card .button:focus-visible {
  @include focus-ring;
}
.type-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-accent-fill);
  box-shadow: 0 0 0 4px var(--color-accent-soft);
}
.type-dot.is-pin { background: #ef7cba; }
.type-dot.is-board { background: #d5a344; }
.type-dot.is-comic { background: #7c8cff; }
.type-dot.is-tag { background: #32b47b; }
.search-main {
  min-width: 0;
}
.search-card {
  display: grid;
  gap: var(--space-xs);
  padding: var(--space-md);
}
.search-label {
  color: var(--color-text-strong);
  font-weight: 950;
}
.search-input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--space-xs);
}
.search-card .input {
  min-height: 46px;
  border-color: var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: var(--color-surface-2);
  box-shadow: none;
}
.search-submit {
  min-height: 46px;
  border-radius: var(--radius-md);
  font-weight: 950;
  @include hover-scale(1.018, -2px);
}
.result-heading {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  align-items: baseline;
  margin: var(--space-lg) 0 0;
  font-size: 1rem;
}
.result-heading strong {
  color: var(--color-text-strong);
  font-size: 1.2rem;
}
.empty-results,
.state-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-top: var(--space-lg);
  padding: var(--space-lg);
}
.state-card.is-loading {
  display: grid;
}
.state-card .icon,
.empty-results .icon {
  color: var(--color-accent-foreground);
}
.state-card h2,
.empty-results h2 {
  margin: 0;
  color: var(--color-text-strong);
  font-size: 1.2rem;
  font-weight: 950;
}
.state-card p,
.empty-results p {
  margin: var(--space-2xs) 0 0;
}
.skeleton-lines {
  display: grid;
  gap: var(--space-xs);
}
.skeleton-lines span {
  display: block;
  height: 12px;
  border-radius: var(--radius-pill);
  background: linear-gradient(90deg, var(--color-surface-2), var(--color-accent-soft), var(--color-surface-2));
  animation: pinry-soft-pulse 1.2s var(--motion-ease-standard) infinite;
}
.skeleton-lines span:nth-child(1) { width: 76%; }
.skeleton-lines span:nth-child(2) { width: 92%; }
.skeleton-lines span:nth-child(3) { width: 54%; }
.result-section {
  margin-top: var(--space-xl);
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}
.section-head h2 {
  margin: 0;
  color: var(--color-text-strong);
  font-size: 1.35rem;
  font-weight: 950;
}
.search-load-more {
  display: flex;
  width: 100%;
  min-height: 46px;
  align-items: center;
  justify-content: center;
  margin-top: var(--space-md);
  border-color: var(--color-line-soft);
  border-radius: var(--radius-pill);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  font-weight: 900;
  @include hover-scale(1.012, -1px);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard),
    border-color var(--motion-duration-standard) var(--motion-ease-standard),
    color var(--motion-duration-standard) var(--motion-ease-standard),
    background var(--motion-duration-standard) var(--motion-ease-standard);
}
.search-load-more:hover:not(:disabled) {
  border-color: var(--color-accent-border);
  color: var(--color-accent-text);
  text-shadow: var(--color-accent-text-shadow);
  background: var(--color-accent-fill);
}
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: var(--space-md);
}
.pin-results {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
@media screen and (max-width: 860px) {
  .search-shell {
    padding-top: calc(62px + var(--space-lg));
  }
  .search-container {
    display: block;
    max-width: calc(100vw - var(--space-md));
  }
  .search-sidebar {
    position: static;
    margin-bottom: var(--space-md);
  }
  .search-types {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media screen and (max-width: 560px) {
  .search-input-row,
  .search-types {
    grid-template-columns: 1fr;
  }
  .section-head,
  .empty-results,
  .state-card {
    align-items: flex-start;
    flex-direction: column;
  }
  .result-grid,
  .pin-results {
    grid-template-columns: 1fr;
  }
}
</style>
