<template>
  <div class="comics-page" :class="{ 'is-embedded': embedded }">
    <PHeader v-if="!embedded"></PHeader>
    <section class="section comics-section">
      <div ref="comicsContainer" class="container comics-container">
        <div v-if="showToolbar" class="comics-toolbar">
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
            v-if="comics.length > 0"
            ref="masonryGrid"
            v-masonry=""
            v-layout-ready="{ itemSelector: '.comic-card-shell' }"
            :key="masonryKey"
            :style="masonryGridStyle"
            class="comic-grid comic-masonry-grid motion-stagger"
            transition-duration="0.12s"
            item-selector=".comic-card-shell"
            column-width=".comic-grid-sizer"
            gutter=".comic-gutter-sizer"
            fit-width="true">
            <div class="comic-grid-sizer"></div>
            <div class="comic-gutter-sizer"></div>
            <article
              class="comic-card-shell motion-card-enter motion-tilt-scene"
              v-for="comic in comics"
              :key="comic.id"
              @mouseenter="showMenu(comic)"
              @mouseleave="handleCardLeave($event)"
              @pointermove="scheduleTilt(comic, $event)"
              @pointerleave="resetTilt($event)"
              @pointercancel="resetTilt($event)"
              @touchstart="handleCardTouch(comic, $event)"
              @touchmove.passive="scheduleTilt(comic, $event)"
              @touchend="resetTilt($event)"
              @touchcancel="resetTilt($event)"
              @click="openComic(comic, $event)">
              <div class="comic-card motion-tilt-card">
                <span class="motion-tilt-glare comic-glare" aria-hidden="true"></span>
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
                  v-if="coverImageUrl(comic)"
                  :src="coverImageUrl(comic)"
                  :alt="comic.title"
                  @load="redrawMasonryLayout"
                  @error="redrawMasonryLayout">
                <div v-else class="comic-cover-placeholder">
                  {{ $t("imageUnavailableText") }}
                </div>
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
                <button
                  class="comic-like"
                  type="button"
                  :class="{ 'is-liked': comic.viewer_liked }"
                  :disabled="comic.likeBusy"
                  :title="comic.viewer_liked ? $t('unlikeButton') : $t('likeButton')"
                  @click.stop="toggleComicLike(comic)">
                  <b-icon
                    :icon="comic.viewer_liked ? 'heart' : 'heart-outline'"
                    size="is-small">
                  </b-icon>
                  <span>{{ formatLikeCount(comic.likes_count) }}</span>
                </button>
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
        <div v-if="showInitialSkeleton" class="comic-skeleton-grid" aria-hidden="true">
          <div v-for="index in pageLimit" :key="index" class="comic-skeleton-card">
            <div class="comic-skeleton-cover"></div>
            <div class="comic-skeleton-line is-wide"></div>
            <div class="comic-skeleton-line"></div>
          </div>
        </div>
        <div v-if="status.error" class="comic-state is-error">
          <p>{{ $t("cardLoadError") }}</p>
          <button class="button is-light" type="button" @click="fetchPage(currentPage)">
            {{ $t("loadMoreResults") }}
          </button>
        </div>
        <div v-else-if="showEmptyState" class="comic-state is-empty">
          <p>{{ $t("comicsEmptyState") }}</p>
        </div>
        <loadingSpinner :show="status.loading && comics.length > 0"></loadingSpinner>
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
import motionPreference from '../components/utils/motionPreference';
import format from '../components/utils/format';

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

function comicContainerCapacity(containerWidth) {
  if (containerWidth <= 540) {
    return 1;
  }
  if (containerWidth <= 780) {
    return 2;
  }
  if (containerWidth <= 1020) {
    return 3;
  }
  return 4;
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
    containerSizing: {
      type: Boolean,
      default: false,
    },
    showCreate: {
      type: Boolean,
      default: true,
    },
    showToolbar: {
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
      containerMeasureFrame: null,
      containerMeasureRetry: null,
      containerResizeObserver: null,
      gridMetrics: { columns: 1, gutterWidth: 0, itemWidth: 240 },
      gridSignature: '240-0-1',
      masonryKey: 0,
      currentMenuId: null,
      currentPage: 0,
      pageLimit: this.containerSizing ? 1 : comicPageLimit(this.largeCards),
      resizeTimer: null,
      status: {
        count: null,
        error: false,
        hasNext: false,
        loading: false,
      },
      suppressNextOpenId: null,
      suppressOpenTimer: null,
      tiltFrame: null,
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
    masonryGridStyle() {
      return {
        '--comic-card-width': `${this.gridMetrics.itemWidth}px`,
        '--comic-grid-gutter': `${this.gridMetrics.gutterWidth}px`,
      };
    },
  },
  watch: {
    largeCards() {
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
    this.fetchPage(0);
    if (!this.containerSizing) {
      window.addEventListener('resize', this.handleResize);
    }
  },
  mounted() {
    if (this.containerSizing) {
      this.initializeContainerSizing();
    }
  },
  beforeDestroy() {
    if (this.containerResizeObserver) {
      this.containerResizeObserver.disconnect();
    }
    if (this.containerMeasureFrame) {
      window.cancelAnimationFrame(this.containerMeasureFrame);
    }
    if (this.containerMeasureRetry) {
      window.clearTimeout(this.containerMeasureRetry);
    }
    if (this.suppressOpenTimer) {
      window.clearTimeout(this.suppressOpenTimer);
    }
    if (this.resizeTimer) {
      window.clearTimeout(this.resizeTimer);
    }
    if (this.tiltFrame) {
      window.cancelAnimationFrame(this.tiltFrame);
    }
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('resize', this.measureContainer);
  },
  methods: {
    avatarUrl(comic) {
      const submitter = comic.submitter || {};
      return (submitter.avatar && submitter.avatar.small)
        || `//gravatar.com/avatar/${submitter.gravatar}?s=28`;
    },
    coverMeta(comic) {
      const cover = comic && comic.cover ? comic.cover : null;
      if (!cover) {
        return null;
      }
      if (typeof cover === 'string') {
        return { image: cover };
      }
      const image = cover.image || cover;
      if (!image) {
        return null;
      }
      if (typeof image === 'string') {
        return { image };
      }
      try {
        const thumbnail = imageVariant.getCardThumbnail(image) || {};
        return thumbnail.image ? thumbnail : null;
      } catch (e) {
        return null;
      }
    },
    coverStyle(comic) {
      const thumbnail = this.coverMeta(comic);
      if (!thumbnail || !thumbnail.image) {
        return {
          '--comic-cover-image': 'none',
        };
      }
      return {
        '--comic-cover-image': `url("${thumbnail.image}")`,
      };
    },
    coverImageUrl(comic) {
      const thumbnail = this.coverMeta(comic);
      return thumbnail && thumbnail.image ? thumbnail.image : null;
    },
    isOwner(comic) {
      return this.user.loggedIn
        && comic.submitter
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
    scheduleTilt(comic, event) {
      if (motionPreference.isReducedMotionEnabled()) {
        return;
      }
      const target = event.currentTarget;
      const point = event.touches && event.touches.length ? event.touches[0] : event;
      if (!target || !point || !target.getBoundingClientRect) {
        return;
      }
      if (this.tiltFrame) {
        window.cancelAnimationFrame(this.tiltFrame);
      }
      this.tiltFrame = window.requestAnimationFrame(() => {
        const rect = target.getBoundingClientRect();
        if (!rect.width || !rect.height) {
          return;
        }
        const x = Math.max(0, Math.min(1, (point.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (point.clientY - rect.top) / rect.height));
        const rotateY = (x - 0.5) * 14;
        const rotateX = (0.5 - y) * 12;
        target.style.setProperty('--tilt-rotate-x', `${rotateX.toFixed(2)}deg`);
        target.style.setProperty('--tilt-rotate-y', `${rotateY.toFixed(2)}deg`);
        target.style.setProperty('--tilt-glare-x', `${(x * 100).toFixed(1)}%`);
        target.style.setProperty('--tilt-glare-y', `${(y * 100).toFixed(1)}%`);
        target.style.setProperty('--tilt-glare-opacity', '0.34');
        target.classList.add('is-tilting');
        this.tiltFrame = null;
      });
    },
    resetTilt(event) {
      const target = event && event.currentTarget;
      if (this.tiltFrame) {
        window.cancelAnimationFrame(this.tiltFrame);
        this.tiltFrame = null;
      }
      if (!target || !target.style) {
        return;
      }
      target.style.setProperty('--tilt-rotate-x', '0deg');
      target.style.setProperty('--tilt-rotate-y', '0deg');
      target.style.setProperty('--tilt-glare-opacity', '0');
      window.setTimeout(() => {
        if (target.classList) {
          target.classList.remove('is-tilting');
        }
      }, 180);
    },
    handleCardLeave(event) {
      this.hideMenu();
      this.resetTilt(event);
    },
    handleCardTouch(comic, event) {
      const wasVisible = this.shouldShowMenu(comic);
      this.showMenu(comic);
      this.scheduleTilt(comic, event);
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
      this.status.error = false;
      API.Comic.fetchList(
        page * this.pageLimit,
        this.pageLimit,
        this.tagFilter,
        this.userFilter,
      ).then(
        (resp) => {
          const { count, results, next } = resp.data;
          this.comics = (results || []).map(item => Object.assign({ likeBusy: false }, item));
          this.currentPage = page;
          this.status.count = count;
          this.status.hasNext = next !== null;
          this.status.loading = false;
          this.$emit('comics-meta-loaded', { count });
          this.$nextTick(() => {
            this.measureContainer();
            this.redrawMasonryLayout();
          });
        },
        () => {
          this.status.loading = false;
          this.status.error = true;
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
        this.applyPageLimit(nextLimit);
      }, 120);
    },
    applyPageLimit(nextLimit) {
      if (!nextLimit || nextLimit === this.pageLimit) {
        return;
      }
      this.pageLimit = nextLimit;
      this.resetPages();
    },
    redrawMasonryLayout() {
      this.$nextTick(() => {
        if (this.$redrawVueMasonry) {
          this.$redrawVueMasonry();
        }
      });
    },
    updateMasonryMetrics(width) {
      if (!width) {
        return false;
      }
      const columns = comicContainerCapacity(width);
      const gutterWidth = width <= 540 ? 0 : 16;
      const itemWidth = Math.floor(
        (width - ((columns - 1) * gutterWidth)) / columns,
      );
      const signature = `${itemWidth}-${gutterWidth}-${columns}`;
      if (signature === this.gridSignature) {
        return false;
      }
      this.gridMetrics = { columns, gutterWidth, itemWidth };
      this.gridSignature = signature;
      return true;
    },
    measureContainer() {
      const container = this.$refs.comicsContainer;
      const width = container ? container.clientWidth : 0;
      if (!width) {
        if (this.containerMeasureRetry) {
          window.clearTimeout(this.containerMeasureRetry);
        }
        this.containerMeasureRetry = window.setTimeout(() => {
          this.containerMeasureRetry = null;
          this.measureContainer();
        }, 80);
        return;
      }
      const metricsChanged = this.updateMasonryMetrics(width);
      this.applyPageLimit(comicContainerCapacity(width));
      if (metricsChanged) {
        this.masonryKey += 1;
      }
      this.redrawMasonryLayout();
    },
    initializeContainerSizing() {
      this.$nextTick(() => {
        this.containerMeasureFrame = window.requestAnimationFrame(() => {
          this.containerMeasureFrame = null;
          this.measureContainer();
          const container = this.$refs.comicsContainer;
          if (container && typeof ResizeObserver !== 'undefined') {
            this.containerResizeObserver = new ResizeObserver(() => {
              this.measureContainer();
            });
            this.containerResizeObserver.observe(container);
          } else {
            window.addEventListener('resize', this.measureContainer);
          }
        });
      });
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
    formatLikeCount(count) {
      return format.formatCount(count);
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
              if (this.status.count !== null) {
                this.status.count = Math.max(0, this.status.count - 1);
              }
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
  background: var(--color-page-bg, var(--app-bg, #f6f7fb));
}

.comics-page.is-embedded .comics-section {
  padding-top: var(--space-md, 16px);
}

.comics-container {
  margin: 0 auto;
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

.comic-row-shell {
  position: relative;
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

.comic-row-shell::before {
  left: 0;
  background: linear-gradient(to right, var(--color-page-bg, var(--app-bg, #f6f7fb)), transparent);
}

.comic-row-shell::after {
  right: 0;
  background: linear-gradient(to left, var(--color-page-bg, var(--app-bg, #f6f7fb)), transparent);
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
  box-shadow: var(--shadow-card, 0 12px 28px rgba(15, 23, 42, 0.2));
}

.comic-page-button.is-left {
  left: var(--space-xs, 8px);
}

.comic-page-button.is-right {
  right: var(--space-xs, 8px);
}

.comic-grid {
  display: block;
  width: 100%;
  perspective: 1200px;
}

.comic-masonry-grid {
  margin-right: auto;
  margin-left: auto;
}

.comic-grid-sizer,
.comic-card-shell {
  width: var(--comic-card-width, 240px);
}

.comic-gutter-sizer {
  width: var(--comic-grid-gutter, 16px);
  height: 0;
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-lg, 24px);
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

  .comic-grid {
    grid-template-columns: minmax(0, 1fr);
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
}

@include screen-grid-layout(".comics-container");

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
