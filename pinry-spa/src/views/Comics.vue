<template>
  <div class="comics-page">
    <PHeader v-if="!embedded"></PHeader>
    <section class="section comics-section">
      <div class="container comics-container">
        <div class="comics-toolbar">
          <div>
            <h1>{{ displayTitle }}</h1>
            <p v-if="status.count !== null">
              {{ status.count }} {{ $t("collectionArtworksLabel") }}
            </p>
          </div>
          <div class="toolbar-actions">
            <button
              v-if="user.loggedIn && !embedded && showCreate"
              class="button is-primary"
              type="button"
              @click="createComic">
              {{ $t("NewComicTitle") }}
            </button>
          </div>
        </div>
        <div
          class="comic-row-shell"
          :class="{
            'can-page-left': currentPage > 0,
            'can-page-right': status.hasNext
          }">
          <button
            v-if="currentPage > 0"
            class="button is-light comic-page-button is-left"
            type="button"
            :disabled="status.loading"
            :aria-label="$t('previousPageButton')"
            :title="$t('previousPageButton')"
            @click="previousPage">
            &lsaquo;
          </button>
          <div
            class="comic-grid"
            :style="gridStyle">
            <article
              class="comic-card"
              v-for="comic in comics"
              :key="comic.id"
              @mouseenter="showMenu(comic)"
              @mouseleave="hideMenu"
              @touchstart="handleCardTouch(comic)"
              @click="openComic(comic, $event)">
            <transition name="comic-menu">
              <div
                class="comic-card-menu"
                v-if="shouldShowMenu(comic)"
                @click.stop
                @touchstart.stop="noop">
                <button
                  class="button is-small is-danger"
                  type="button"
                  :title="$t('deleteButton')"
                  :aria-label="$t('deleteButton')"
                  @click.stop="deleteComic(comic)">
                  {{ $t("deleteButton") }}
                </button>
              </div>
            </transition>
            <div class="comic-ribbon">{{ $t("comicLink") }}</div>
            <div
              class="comic-cover"
              :style="coverStyle(comic)">
              <img
                v-if="comic.cover"
                :src="coverImageUrl(comic)"
                :alt="comic.title">
            </div>
            <div class="comic-info">
              <h2>{{ comic.title }}</h2>
              <div class="comic-tags" v-if="comic.tags && comic.tags.length > 0">
                <router-link
                  v-for="tag in visibleTags(comic)"
                  :key="tag"
                  :to="{ name: 'tag', params: { tag } }"
                  @click.stop>
                  {{ tag }}
                </router-link>
                <button
                  v-if="hiddenTagCount(comic) > 0"
                  class="comic-tag-more"
                  type="button"
                  :title="comic.title"
                  @click.stop="openComic(comic, $event)">
                  ...
                </button>
              </div>
              <div class="comic-author">
                <img :src="avatarUrl(comic)" alt="">
                <router-link :to="{ name: 'user', params: { user: comic.submitter.username } }">
                  {{ comic.submitter.username }}
                </router-link>
                <span>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</span>
              </div>
              <div class="comic-source" v-if="hasSource(comic.referer)">
                <a
                  v-if="isWebUrl(comic.referer)"
                  :href="comic.referer"
                  target="_blank"
                  @click.stop>
                  {{ $t("sourceLink") }}
                </a>
                <span v-else>{{ sourceText(comic.referer) }}</span>
              </div>
              <div class="comic-source is-warning" v-else>
                {{ $t("missingSourceNotice") }}
              </div>
            </div>
            </article>
          </div>
          <button
            v-if="status.hasNext"
            class="button is-light comic-page-button is-right"
            type="button"
            :disabled="status.loading"
            :aria-label="$t('nextPageButton')"
            :title="$t('nextPageButton')"
            @click="nextPage">
            &rsaquo;
          </button>
        </div>
        <loadingSpinner :show="status.loading"></loadingSpinner>
      </div>
    </section>
  </div>
</template>

<script>
import API from '../components/api';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import modals from '../components/modals';
import imageVariant from '../components/utils/imageVariant';

function isWebUrl(url) {
  return /^https?:\/\//i.test((url || '').trim());
}

function hasSource(url) {
  return !!(url || '').trim();
}

function sourceText(url) {
  return (url || '').trim();
}

const VISIBLE_COMIC_TAGS = 4;

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

function comicPageLimit(largeCards = false) {
  if (typeof window === 'undefined') {
    return largeCards ? 3 : 4;
  }
  const viewportWidth = window.innerWidth
    || document.documentElement.clientWidth
    || 0;
  const capacity = comicGridCapacity(viewportWidth);
  return largeCards ? Math.max(1, capacity - 1) : capacity;
}

export default {
  name: 'Comics',
  components: {
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
      currentMenuId: null,
      currentPage: 0,
      pageLimit: comicPageLimit(this.largeCards),
      resizeTimer: null,
      status: {
        count: null,
        hasNext: false,
        loading: false,
      },
      suppressNextOpenId: null,
      suppressOpenTimer: null,
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    displayTitle() {
      return this.title || this.$t('comicsLink');
    },
    gridStyle() {
      return {
        '--comic-page-limit': this.pageLimit,
      };
    },
  },
  watch: {
    tagFilter() {
      this.resetPages();
    },
    userFilter() {
      this.resetPages();
    },
  },
  created() {
    this.fetchUser();
    this.fetchPage(0);
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    if (this.suppressOpenTimer) {
      window.clearTimeout(this.suppressOpenTimer);
    }
    if (this.resizeTimer) {
      window.clearTimeout(this.resizeTimer);
    }
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    avatarUrl(comic) {
      return (comic.submitter.avatar && comic.submitter.avatar.small)
        || `//gravatar.com/avatar/${comic.submitter.gravatar}?s=28`;
    },
    coverStyle(comic) {
      if (!comic.cover) {
        return {};
      }
      const thumbnail = imageVariant.getCardThumbnail(comic.cover.image);
      return {
        '--comic-cover-image': `url("${thumbnail.image}")`,
      };
    },
    coverImageUrl(comic) {
      const thumbnail = imageVariant.getCardThumbnail(comic.cover.image);
      return thumbnail.image;
    },
    isOwner(comic) {
      return this.user.loggedIn
        && comic.submitter.username === this.user.meta.username;
    },
    shouldShowMenu(comic) {
      return this.isOwner(comic) && this.currentMenuId === comic.id;
    },
    showMenu(comic) {
      if (this.isOwner(comic)) {
        this.currentMenuId = comic.id;
      }
    },
    hideMenu() {
      this.currentMenuId = null;
    },
    handleCardTouch(comic) {
      const wasVisible = this.shouldShowMenu(comic);
      this.showMenu(comic);
      if (this.suppressOpenTimer) {
        window.clearTimeout(this.suppressOpenTimer);
      }
      this.suppressNextOpenId = (!wasVisible && this.isOwner(comic))
        ? comic.id
        : null;
      if (this.suppressNextOpenId !== null) {
        this.suppressOpenTimer = window.setTimeout(() => {
          this.suppressNextOpenId = null;
          this.suppressOpenTimer = null;
        }, 700);
      }
    },
    openComic(comic, event) {
      if (this.suppressNextOpenId === comic.id) {
        this.suppressNextOpenId = null;
        if (this.suppressOpenTimer) {
          window.clearTimeout(this.suppressOpenTimer);
          this.suppressOpenTimer = null;
        }
        event.preventDefault();
        event.stopPropagation();
        return;
      }
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
      if (this.status.loading || page < 0) {
        return;
      }
      this.status.loading = true;
      API.Comic.fetchList(
        page * this.pageLimit,
        this.pageLimit,
        this.tagFilter,
        this.userFilter,
      ).then(
        (resp) => {
          const { count, results, next } = resp.data;
          this.comics = results;
          this.currentPage = page;
          this.status.count = count;
          this.status.hasNext = next !== null;
          this.status.loading = false;
          this.$emit('comics-meta-loaded', { count });
        },
        () => {
          this.status.loading = false;
        },
      );
    },
    resetPages() {
      this.comics = [];
      this.currentPage = 0;
      this.status.count = null;
      this.status.hasNext = false;
      this.fetchPage(0);
    },
    handleResize() {
      if (this.resizeTimer) {
        window.clearTimeout(this.resizeTimer);
      }
      this.resizeTimer = window.setTimeout(() => {
        const nextLimit = comicPageLimit(this.largeCards);
        if (nextLimit === this.pageLimit) {
          return;
        }
        this.pageLimit = nextLimit;
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
    hiddenTagCount(comic) {
      return Math.max(0, (comic.tags || []).length - VISIBLE_COMIC_TAGS);
    },
    visibleTags(comic) {
      return (comic.tags || []).slice(0, VISIBLE_COMIC_TAGS);
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
      this.$buefy.dialog.confirm({
        message: this.$t('deleteComicConfirm'),
        type: 'is-danger',
        onConfirm: () => {
          API.Comic.delete(comic.id).then(
            () => {
              this.comics = this.comics.filter(item => item.id !== comic.id);
              this.currentMenuId = null;
              if (this.comics.length === 0 && this.currentPage > 0) {
                this.fetchPage(this.currentPage - 1);
              }
            },
          );
        },
      });
    },
    hasSource,
    isWebUrl,
    noop() {
      return true;
    },
    sourceText,
  },
};
</script>

<style lang="scss" scoped>
@import '../components/utils/grid-layout';

.comics-container {
  margin: 0 auto;
}
.comics-section {
  padding-bottom: 1.25rem;
}
.comics-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.comics-toolbar h1 {
  margin: 0;
  color: #22313f;
  font-size: 1.6rem;
  font-weight: 800;
}
.comics-toolbar p {
  margin: 0.25rem 0 0;
  color: #64748b;
  font-size: 0.95rem;
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.comic-row-shell {
  position: relative;
}
.comic-row-shell::before,
.comic-row-shell::after {
  content: "";
  position: absolute;
  z-index: 5;
  top: 0;
  bottom: -16px;
  width: 76px;
  opacity: 0;
  pointer-events: none;
  transition: opacity .18s ease;
}
.comic-row-shell::before {
  left: 0;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0));
}
.comic-row-shell::after {
  right: 0;
  background: linear-gradient(to left, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0));
}
.comic-row-shell.can-page-left::before,
.comic-row-shell.can-page-right::after {
  opacity: 1;
}
.comic-page-button {
  position: absolute;
  z-index: 6;
  top: 50%;
  width: 2.35rem;
  min-width: 2.35rem;
  height: 3.1rem;
  padding: 0;
  border-radius: 999px;
  font-size: 1.45rem;
  line-height: 1;
  transform: translateY(-50%);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.2);
}
.comic-page-button.is-left {
  left: 0.45rem;
}
.comic-page-button.is-right {
  right: 0.45rem;
}
.comic-grid {
  display: grid;
  grid-template-columns: repeat(
    var(--comic-page-limit),
    minmax(0, var(--comic-card-width, var(--pin-card-width, 240px)))
  );
  gap: var(--pin-grid-gutter, 15px);
  justify-content: start;
}
.comic-card {
  position: relative;
  isolation: isolate;
  overflow: visible;
  min-width: 0;
  color: inherit;
  cursor: pointer;
  border: 1px solid rgba(126, 87, 194, 0.42);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(126, 87, 194, 0.08), 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.comic-card::before,
.comic-card::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  height: 12px;
  border: 1px solid rgba(126, 87, 194, 0.22);
  border-radius: 0 0 8px 8px;
  background: #faf7ff;
  pointer-events: none;
}
.comic-card::before {
  bottom: -7px;
  z-index: -1;
}
.comic-card::after {
  bottom: -13px;
  left: 24px;
  right: 24px;
  background: #f0ebff;
  z-index: -2;
}
.comic-card:hover {
  transform: translateY(-4px);
  border-color: rgba(126, 87, 194, 0.74);
  box-shadow: 0 0 0 2px rgba(126, 87, 194, 0.14), 0 16px 32px rgba(16, 24, 40, 0.16);
}
.comic-ribbon {
  position: absolute;
  z-index: 4;
  top: 10px;
  left: 10px;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  color: #fff;
  background: rgba(126, 87, 194, 0.9);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.02em;
}
.comic-card-menu {
  position: absolute;
  z-index: 8;
  top: 8px;
  right: 8px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(15, 23, 42, 0.58);
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.24);
}
.comic-menu-enter-active,
.comic-menu-leave-active {
  transition: opacity .18s ease, transform .18s ease;
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
  border-radius: 8px 8px 0 0;
  background: #f7f3ff;
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
  background: rgba(255, 255, 255, 0.18);
}
.comic-cover img {
  position: relative;
  z-index: 1;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.comic-info {
  padding: 0.85rem;
  border-top: 1px solid #efe9ff;
}
.comic-info h2 {
  overflow: hidden;
  margin: 0;
  color: #22313f;
  font-size: 16px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
  max-height: 3.25rem;
  margin-top: 0.48rem;
  overflow: hidden;
}
.comic-tags a,
.comic-tag-more {
  max-width: 100%;
  padding: 0.15rem 0.42rem;
  border: 0;
  border-radius: 999px;
  color: #6d4bc1;
  background: #f2edff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}
.comic-tag-more {
  color: #64748b;
  background: #eef1f5;
  cursor: pointer;
}
.comic-tag-more:hover {
  color: #334155;
  background: #e2e8f0;
}
.comic-author {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
  margin-top: 0.45rem;
  color: #64748b;
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
  color: #334155;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comic-author span {
  flex: 0 0 auto;
}
.comic-source {
  overflow: hidden;
  margin: 0.45rem 0 0;
  color: #64748b;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comic-source a,
.comic-source span {
  color: #7e57c2;
  font-weight: 700;
}
.comic-source.is-warning {
  color: #8a6d1d;
}
@media screen and (max-width: 542px) {
  .comics-toolbar {
    display: block;
  }
  .toolbar-actions {
    margin-top: 0.8rem;
  }
  .toolbar-actions .button.is-primary {
    flex: 1 1 auto;
  }
}
@include screen-grid-layout(".comics-container");
</style>
