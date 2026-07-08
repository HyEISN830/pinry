<template>
  <div class="search-page">
    <PHeader></PHeader>
    <section class="section search-shell">
      <div class="container search-container">
        <aside class="search-sidebar">
          <h1>{{ $t("aggregateSearchTitle") }}</h1>
          <div class="search-types">
            <button
              v-for="option in typeOptions"
              :key="option.value"
              class="button"
              type="button"
              :class="{ 'is-primary': activeType === option.value }"
              @click="setType(option.value)">
              {{ option.label }}
            </button>
          </div>
        </aside>
        <main class="search-main">
          <form class="search-card" @submit.prevent="search(true)">
            <input
              class="input"
              v-model="queryText"
              maxlength="80"
              :placeholder="$t('searchPlaceholder')">
            <button
              class="button is-primary"
              type="submit"
              :disabled="normalizedQuery.length === 0 || loading">
              {{ $t("searchButton") }}
            </button>
          </form>
          <div class="result-heading" v-if="hasSearched">
            {{ $t("searchResultsFor") }} <strong>{{ resultQuery }}</strong>
          </div>
          <loadingSpinner :show="loading"></loadingSpinner>
          <div
            class="empty-results"
            v-if="hasSearched && !loading && !hasAnyResults">
            {{ $t("noResultsFound") }}
          </div>
          <section
            class="result-section"
            v-if="shouldShowBucket('comics') && buckets.comics.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("comicsLink") }}</h2>
              <button
                v-if="buckets.comics.has_next"
                class="button is-light"
                type="button"
                :disabled="loadingMore.comics"
                @click="loadMore('comics')">
                {{ $t("loadMoreResults") }}
              </button>
            </div>
            <div class="result-grid">
              <article
                class="result-card comic-result"
                v-for="comic in buckets.comics.results"
                :key="`comic-${comic.id}`">
                <router-link
                  class="result-cover"
                  :style="comicCoverStyle(comic)"
                  :to="{ name: 'comic', params: { comicId: comic.id } }">
                  <img
                    v-if="comic.cover"
                    :src="imageUrl(comic.cover.image)"
                    :alt="comic.title">
                  <span class="type-pill">{{ $t("comicLink") }}</span>
                </router-link>
                <div class="result-body">
                  <h3>{{ comic.title }}</h3>
                  <p>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</p>
                  <div class="mini-tags" v-if="comic.tags && comic.tags.length > 0">
                    <router-link
                      v-for="tag in comic.tags.slice(0, 4)"
                      :key="`comic-${comic.id}-${tag}`"
                      :to="{ name: 'tag', params: { tag } }">
                      {{ tag }}
                    </router-link>
                  </div>
                  <button
                    class="like-button"
                    type="button"
                    :class="{ 'is-liked': comic.viewer_liked }"
                    :disabled="comic.likeBusy"
                    @click="toggleComicLike(comic)">
                    <b-icon
                      :icon="comic.viewer_liked ? 'heart' : 'heart-outline'"
                      size="is-small">
                    </b-icon>
                    <span>{{ formatCount(comic.likes_count) }}</span>
                  </button>
                </div>
              </article>
            </div>
          </section>
          <section
            class="result-section"
            v-if="shouldShowBucket('pins') && buckets.pins.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("pinsLink") }}</h2>
              <button
                v-if="buckets.pins.has_next"
                class="button is-light"
                type="button"
                :disabled="loadingMore.pins"
                @click="loadMore('pins')">
                {{ $t("loadMoreResults") }}
              </button>
            </div>
            <div class="result-grid pin-results">
              <article
                class="result-card pin-result"
                v-for="pin in buckets.pins.results"
                :key="`pin-${pin.id}`">
                <router-link
                  class="result-cover"
                  :style="pinCoverStyle(pin)"
                  :to="{ name: 'pin', params: { pinId: pin.id } }">
                  <img :src="imageUrl(pin.image)" :alt="pin.description">
                  <span class="type-pill">{{ $t("pinLink") }}</span>
                </router-link>
                <div class="result-body">
                  <h3 v-if="pin.description">{{ pin.description }}</h3>
                  <p>
                    {{ $t("pinnedByInfo") }}
                    <router-link :to="{ name: 'user', params: { user: pin.submitter.username } }">
                      {{ pin.submitter.username }}
                    </router-link>
                  </p>
                  <div class="mini-tags" v-if="pin.tags && pin.tags.length > 0">
                    <router-link
                      v-for="tag in pin.tags.slice(0, 6)"
                      :key="`pin-${pin.id}-${tag}`"
                      :to="{ name: 'tag', params: { tag } }">
                      {{ tag }}
                    </router-link>
                  </div>
                  <button
                    class="like-button"
                    type="button"
                    :class="{ 'is-liked': pin.viewer_liked }"
                    :disabled="pin.likeBusy"
                    @click="togglePinLike(pin)">
                    <b-icon
                      :icon="pin.viewer_liked ? 'heart' : 'heart-outline'"
                      size="is-small">
                    </b-icon>
                    <span>{{ formatCount(pin.likes_count) }}</span>
                  </button>
                </div>
              </article>
            </div>
          </section>
          <section
            class="result-section"
            v-if="shouldShowBucket('boards') && buckets.boards.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("boardsLink") }}</h2>
              <button
                v-if="buckets.boards.has_next"
                class="button is-light"
                type="button"
                :disabled="loadingMore.boards"
                @click="loadMore('boards')">
                {{ $t("loadMoreResults") }}
              </button>
            </div>
            <div class="result-grid">
              <router-link
                class="result-card board-result"
                v-for="board in buckets.boards.results"
                :key="`board-${board.id}`"
                :to="{ name: 'board', params: { boardId: board.id } }">
                <div
                  class="result-cover"
                  :style="boardCoverStyle(board)">
                  <img
                    v-if="board.cover"
                    :src="imageUrl(board.cover.image)"
                    :alt="board.name">
                  <span class="type-pill">{{ $t("boardLink") }}</span>
                </div>
                <div class="result-body">
                  <h3>{{ board.name }}</h3>
                  <p>{{ board.total_pins }} {{ $t("pinsLink") }}</p>
                </div>
              </router-link>
            </div>
          </section>
          <section
            class="result-section"
            v-if="shouldShowBucket('tags') && buckets.tags.results.length > 0">
            <div class="section-head">
              <h2>{{ $t("tagsLabel") }}</h2>
              <button
                v-if="buckets.tags.has_next"
                class="button is-light"
                type="button"
                :disabled="loadingMore.tags"
                @click="loadMore('tags')">
                {{ $t("loadMoreResults") }}
              </button>
            </div>
            <div class="tag-result-list">
              <router-link
                v-for="tag in buckets.tags.results"
                :key="`tag-${tag.name}`"
                :to="{ name: 'tag', params: { tag: tag.name } }">
                {{ tag.name }}
              </router-link>
            </div>
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
import format from '../components/utils/format';
import imageVariant from '../components/utils/imageVariant';

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

export default {
  name: 'Search',
  components: {
    PHeader,
    loadingSpinner,
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
    };
  },
  computed: {
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
  methods: {
    bucketNamesForType(type) {
      const key = bucketKeyForType(type);
      if (key) {
        return [key];
      }
      return ['comics', 'pins', 'boards', 'tags'];
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
        },
        () => {
          this.loading = false;
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
        },
        () => {
          this.$set(this.loadingMore, name, false);
        },
      );
    },
    shouldShowBucket(name) {
      return this.activeType === 'all' || bucketKeyForType(this.activeType) === name;
    },
    imageUrl(image) {
      const thumbnail = imageVariant.getCardThumbnail(image);
      return thumbnail.image;
    },
    imageBackground(image) {
      return {
        '--result-cover-image': `url("${this.imageUrl(image)}")`,
      };
    },
    comicCoverStyle(comic) {
      if (!comic.cover) {
        return {};
      }
      return this.imageBackground(comic.cover.image);
    },
    boardCoverStyle(board) {
      if (!board.cover) {
        return {};
      }
      return this.imageBackground(board.cover.image);
    },
    pinCoverStyle(pin) {
      return this.imageBackground(pin.image);
    },
    formatCount(count) {
      return format.formatCount(count);
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
.search-shell {
  padding-top: 1.25rem;
}
.search-container {
  display: grid;
  grid-template-columns: minmax(180px, 230px) minmax(0, 1fr);
  gap: 1.25rem;
  max-width: min(1440px, calc(100vw - 2rem));
}
.search-sidebar,
.search-card,
.result-card,
.empty-results {
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  background: var(--surface-1, #fff);
  box-shadow: var(--shadow-soft, 0 10px 24px rgba(16, 24, 40, 0.08));
}
.search-sidebar {
  position: sticky;
  top: 5rem;
  align-self: start;
  padding: 1rem;
}
.search-sidebar h1 {
  margin: 0 0 0.85rem;
  color: var(--text-strong, #22313f);
  font-size: 1.15rem;
  font-weight: 800;
}
.search-types {
  display: grid;
  gap: 0.5rem;
}
.search-types .button {
  justify-content: flex-start;
  border-radius: 7px;
  font-weight: 800;
}
.search-main {
  min-width: 0;
}
.search-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.65rem;
  padding: 1rem;
}
.search-card .input {
  min-height: 42px;
  border-radius: 7px;
}
.result-heading {
  margin: 1rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 1rem;
}
.result-heading strong {
  color: var(--text-strong, #22313f);
}
.empty-results {
  margin-top: 1rem;
  padding: 1rem;
  color: var(--text-muted, #64748b);
}
.result-section {
  margin-top: 1.25rem;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.7rem;
}
.section-head h2 {
  margin: 0;
  color: var(--text-strong, #22313f);
  font-size: 1.35rem;
  font-weight: 800;
}
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1rem;
}
.pin-results {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
.result-card {
  overflow: hidden;
  color: inherit;
  animation: resultAppear .24s ease both;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.result-card:hover {
  transform: translateY(-3px);
  border-color: var(--accent, #7e57c2);
}
.result-cover {
  position: relative;
  isolation: isolate;
  display: block;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: var(--surface-2, #f8fafc);
}
.board-result .result-cover {
  aspect-ratio: 16 / 10;
}
.result-cover::before {
  content: "";
  position: absolute;
  inset: -18px;
  z-index: 0;
  background-image: var(--result-cover-image);
  background-position: center;
  background-size: cover;
  filter: blur(18px) saturate(1.14);
  opacity: 0.38;
}
.result-cover img {
  position: relative;
  z-index: 1;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.type-pill {
  position: absolute;
  z-index: 2;
  top: 0.6rem;
  left: 0.6rem;
  padding: 0.22rem 0.48rem;
  border-radius: 999px;
  color: var(--accent-text, #fff);
  background: var(--accent-strong, #7e57c2);
  font-size: 12px;
  font-weight: 900;
}
.result-body {
  padding: 0.85rem;
}
.result-body h3 {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--text-strong, #22313f);
  font-size: 1rem;
  font-weight: 900;
  line-height: 1.35;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.result-body p {
  margin: 0.42rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 0.9rem;
}
.mini-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.5rem;
}
.mini-tags a,
.tag-result-list a {
  display: inline-flex;
  align-items: center;
  padding: 0.16rem 0.46rem;
  border-radius: 999px;
  color: var(--accent-strong, #1f6feb);
  background: var(--accent-soft, #eaf3ff);
  font-size: 12px;
  font-weight: 900;
}
.like-button {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  min-height: 30px;
  margin-top: 0.65rem;
  padding: 0 0.58rem;
  border: 1px solid var(--line-soft, #dbe3ee);
  border-radius: 999px;
  color: var(--text-muted, #64748b);
  background: var(--surface-2, #f8fafc);
  cursor: pointer;
  font-size: 13px;
  font-weight: 900;
}
.like-button.is-liked,
.like-button:hover {
  color: var(--accent-strong, #d94691);
  border-color: var(--accent, #ef7cba);
  background: var(--accent-soft, rgba(239, 124, 186, 0.16));
}
.like-button:disabled {
  opacity: 0.72;
  cursor: wait;
}
.tag-result-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
@keyframes resultAppear {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@media screen and (max-width: 820px) {
  .search-container {
    display: block;
    max-width: calc(100vw - 1rem);
  }
  .search-sidebar {
    position: static;
    margin-bottom: 1rem;
  }
  .search-types {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media screen and (max-width: 542px) {
  .search-card {
    grid-template-columns: 1fr;
  }
  .search-types {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .result-grid,
  .pin-results {
    grid-template-columns: 1fr;
  }
}
</style>
