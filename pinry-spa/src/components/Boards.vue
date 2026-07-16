<template>
  <div class="boards">
    <section class="section">
      <div id="boards-container" class="container" v-if="blocks">
        <div
          ref="masonryGrid"
          v-masonry=""
          v-layout-ready="{ itemSelector: '.grid-item' }"
          :key="masonryKey"
          :style="masonryGridStyle"
          class="boards-masonry-grid"
          transition-duration="0.12s"
          item-selector=".grid-item"
          column-width=".grid-sizer"
          gutter=".gutter-sizer"
          fit-width="true"
        >
          <template v-for="item in blocks">
            <div v-bind:key="item.id"
                 v-masonry-tile
                 :class="item.class"
                 class="grid-item board-masonry">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div class="board-card-frame motion-card-enter" :style="item.motionStyle">
                <div
                  class="board-card motion-hover-scale"
                  @mouseenter="currentEditBoard = item.id"
                  @touchstart="handleBoardTouch(item)"
                  @mouseleave="currentEditBoard = null">
                  <span class="board-card-glare" aria-hidden="true"></span>
                  <div class="board-stack" aria-hidden="true"></div>
                <BoardEditorUI
                  v-show="shouldShowTools(item)"
                  :board="item"
                  :can-manage="isBoardOwner(item)"
                  v-on:board-delete-succeed="reset"
                  v-on:board-save-succeed="reset"
                ></BoardEditorUI>
                <router-link
                  class="board-card-link"
                  :to="{ name: 'board', params: { boardId: item.id } }"
                  @click.native="handleBoardNavigation(item, $event)">
                  <div class="card-image">
                    <div
                      class="board-image-shell"
                      :style="item.style"
                      :data-board-id="item.id">
                      <img
                         v-if="item.imageVisible && item.preview_image_url"
                         :src="item.preview_image_url"
                         @load="onPinImageLoaded(item.id)"
                         :alt="item.name || $t('imageUnavailableText')"
                         class="preview-image">
                      <div
                        v-else
                        class="lazy-image-placeholder"
                        :class="{ 'is-unavailable': item.imageVisible && !item.preview_image_url }">
                        <span v-if="item.imageVisible && !item.preview_image_url">
                          {{ $t("imageUnavailableText") }}
                        </span>
                      </div>
                      <span class="board-kind-pill content-tag-pill">
                        {{ boardVisibilityLabel(item) }}
                      </span>
                    </div>
                  </div>
                  <div class="board-footer">
                    <h2 class="board-title">{{ item.name }}</h2>
                    <div class="board-meta">
                      <span>{{ item.total_pins }}</span>
                      <small>{{ $t("pinsLink") }}</small>
                    </div>
                  </div>
                </router-link>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
      <loadingSpinner :show="status.loading" size="compact"></loadingSpinner>
      <div v-if="showInitialSkeleton" class="card-skeleton-grid" aria-hidden="true">
        <div v-for="index in 6" :key="index" class="card-skeleton">
          <div class="card-skeleton-image"></div>
          <div class="card-skeleton-line is-wide"></div>
          <div class="card-skeleton-line"></div>
        </div>
      </div>
      <div v-if="status.error" class="card-state is-error">
        <p>{{ $t("cardLoadError") }}</p>
        <button type="button" @click="reset">{{ $t("loadMoreResults") }}</button>
      </div>
      <div v-else-if="showEmptyState" class="card-state is-empty">
        <p>{{ $t("boardsEmptyState") }}</p>
      </div>
      <noMore v-bind:show="!status.hasNext && blocks.length > 0"></noMore>
    </section>
  </div>
</template>

<script>
import API from './api';
import pinHandler from './utils/PinHandler';
import loadingSpinner from './loadingSpinner.vue';
import noMore from './noMore.vue';
import scroll from './utils/scroll';
import placeholder from '../assets/pinry-placeholder.jpg';
import BoardEditorUI from './editors/BoardEditUI.vue';
import bus from './utils/bus';
import imageVariant from './utils/imageVariant';

function getResponsiveCardWidth(containerWidth) {
  if (containerWidth >= 1240) return 224;
  if (containerWidth >= 980) return 220;
  if (containerWidth >= 720) return 216;
  return Math.max(240, containerWidth);
}

function getResponsiveGridMetrics(containerWidth) {
  const safeWidth = Math.max(0, containerWidth || 0);
  if (safeWidth <= 540) {
    return { columns: 1, gutterWidth: 0, itemWidth: safeWidth };
  }
  const gutterWidth = safeWidth >= 980 ? 16 : 14;
  const preferredWidth = getResponsiveCardWidth(safeWidth);
  const columns = Math.max(
    1,
    Math.floor((safeWidth + gutterWidth) / (preferredWidth + gutterWidth)),
  );
  const itemWidth = Math.floor(
    (safeWidth - ((columns - 1) * gutterWidth)) / columns,
  );
  return { columns, gutterWidth, itemWidth };
}

function isDocumentScrollable() {
  const { body, documentElement: doc } = document;
  const scrollHeight = Math.max(
    doc.scrollHeight,
    body ? body.scrollHeight : 0,
  );
  return scrollHeight > window.innerHeight + 120;
}

function createBoardItem(board) {
  const defaultPreviewImage = placeholder;
  const boardItem = {};
  let previewImage = {
    image: { thumbnail: { image: null, width: 240, height: 240 } },
  };
  if (board.cover !== null) {
    previewImage = board.cover;
  }
  boardItem.id = board.id;
  boardItem.name = board.name;
  boardItem.private = board.private;
  boardItem.total_pins = board.total_pins;
  let thumbnail = {};
  try {
    thumbnail = imageVariant.getCardThumbnail(previewImage.image) || {};
  } catch (e) {
    thumbnail = {};
  }
  if (thumbnail.image !== null && thumbnail.image !== undefined) {
    boardItem.preview_image_url = pinHandler.escapeUrl(
      thumbnail.image,
    );
  } else {
    boardItem.preview_image_url = defaultPreviewImage;
  }
  const thumbnailWidth = thumbnail.width || 240;
  const thumbnailHeight = thumbnail.height || 240;
  boardItem.style = {
    aspectRatio: `${thumbnailWidth} / ${thumbnailHeight}`,
    '--board-cover-image': boardItem.preview_image_url
      ? `url("${boardItem.preview_image_url}")`
      : 'none',
  };
  boardItem.imageVisible = false;
  boardItem.class = {
    'is-private': board.private,
  };
  boardItem.author = board.submitter.username;
  return boardItem;
}

function initialData() {
  return {
    currentEditBoard: null,
    blocks: [],
    blocksMap: {},
    gridMetrics: getResponsiveGridMetrics(240),
    gridSignature: '240-0-1',
    gridMeasureAttempts: 0,
    gridMeasureTimer: null,
    gridResizeObserver: null,
    fillViewportTimer: null,
    masonryKey: 0,
    resizeTimer: null,
    suppressBoardNavigationId: null,
    suppressBoardNavigationTimer: null,
    masonryLayoutRaf: null,
    masonryLayoutTimers: [],
    status: {
      loading: false,
      hasNext: true,
      offset: 0,
      error: false,
    },
    editorMeta: {
      user: { loggedIn: false, meta: { username: null } },
    },
  };
}

export default {
  name: 'boards',
  components: {
    loadingSpinner,
    noMore,
    BoardEditorUI,
  },
  data: initialData,
  props: ['filters'],
  computed: {
    masonryGridStyle() {
      return {
        '--pin-card-width': `${this.gridMetrics.itemWidth}px`,
        '--pin-grid-gutter': `${this.gridMetrics.gutterWidth}px`,
      };
    },
    showInitialSkeleton() {
      return this.status.loading && this.blocks.length === 0;
    },
    showEmptyState() {
      return !this.status.loading
        && !this.status.error
        && this.blocks.length === 0
        && !this.status.hasNext;
    },
  },
  // R6 route/category switching layout guard
  watch: {
    '$route.fullPath': function routeFullPathChanged() {
      this.queueMasonryLayout();
    },
    filters() {
      this.reset();
    },
  },
  updated() {
    this.queueMasonryLayout();
  },
  activated() {
    this.queueMasonryLayout();
  },
  methods: {
    measureGridWhenReady() {
      this.$nextTick(() => {
        const requestFrame = window.requestAnimationFrame
          || (callback => window.setTimeout(callback, 16));
        requestFrame(() => {
          if (this.updateGridMetrics()) {
            this.gridMeasureAttempts = 0;
            this.masonryKey += 1;
            this.$nextTick(() => this.redrawMasonryLayout());
            return;
          }
          const container = this.$el && this.$el.querySelector('#boards-container');
          if (container && container.clientWidth > 0) {
            this.gridMeasureAttempts = 0;
            this.redrawMasonryLayout();
            return;
          }
          if (this.gridMeasureAttempts >= 8) return;
          this.gridMeasureAttempts += 1;
          this.gridMeasureTimer = window.setTimeout(
            this.measureGridWhenReady,
            Math.min(40 * this.gridMeasureAttempts, 240),
          );
        });
      });
    },
    observeGridContainer() {
      if (!window.ResizeObserver || this.gridResizeObserver) return;
      const container = this.$el && this.$el.querySelector('#boards-container');
      if (!container) return;
      this.gridResizeObserver = new ResizeObserver(() => {
        if (this.updateGridMetrics()) {
          this.masonryKey += 1;
          this.$nextTick(() => this.redrawMasonryLayout());
        }
      });
      this.gridResizeObserver.observe(container);
    },
    updateGridMetrics() {
      const container = this.$el && this.$el.querySelector('#boards-container');
      const containerWidth = container ? container.clientWidth : 0;
      if (!containerWidth) return false;
      const metrics = getResponsiveGridMetrics(containerWidth);
      const signature = `${metrics.itemWidth}-${metrics.gutterWidth}-${metrics.columns}`;
      if (signature === this.gridSignature) return false;
      this.gridMetrics = metrics;
      this.gridSignature = signature;
      return true;
    },
    bindMasonryMediaEvents() {
      if (this.$el && this.$el.addEventListener) {
        this.$el.addEventListener('load', this.handleMasonryMediaEvent, true);
        this.$el.addEventListener('error', this.handleMasonryMediaEvent, true);
      }
    },
    unbindMasonryMediaEvents() {
      if (this.$el && this.$el.removeEventListener) {
        this.$el.removeEventListener('load', this.handleMasonryMediaEvent, true);
        this.$el.removeEventListener('error', this.handleMasonryMediaEvent, true);
      }
    },
    handleMasonryMediaEvent(event) {
      const target = event && event.target;
      if (!target || target.tagName !== 'IMG') {
        return;
      }
      this.queueMasonryLayout();
    },
    queueMasonryLayout() {
      this.clearMasonryTimers();
      this.$nextTick(() => {
        const requestFrame = window.requestAnimationFrame
          || (callback => window.setTimeout(callback, 16));
        this.masonryLayoutRaf = requestFrame(() => {
          this.masonryLayoutRaf = null;
          this.redrawMasonryLayout();
        });
        [80, 180, 360].forEach((delay) => {
          const timer = window.setTimeout(() => {
            this.redrawMasonryLayout();
          }, delay);
          this.masonryLayoutTimers.push(timer);
        });
      });
    },
    clearMasonryTimers() {
      if (this.masonryLayoutRaf) {
        const cancelFrame = window.cancelAnimationFrame || window.clearTimeout;
        cancelFrame(this.masonryLayoutRaf);
        this.masonryLayoutRaf = null;
      }
      this.masonryLayoutTimers.forEach(timer => window.clearTimeout(timer));
      this.masonryLayoutTimers = [];
    },
    redrawMasonryLayout() {
      if (typeof this.$redrawVueMasonry === 'function') {
        this.$redrawVueMasonry();
      }
    },

    boardVisibilityLabel(board) {
      return board.private
        ? this.$t('collectionPrivateBoardLabel')
        : this.$t('collectionPublicBoardLabel');
    },
    initialize() {
      this.initializeMeta();
      this.fetchMore(true);
    },
    initializeMeta() {
      const self = this;
      API.User.fetchUserInfo().then(
        (user) => {
          if (user === null) {
            self.editorMeta.user.loggedIn = false;
            self.editorMeta.user.meta = {};
          } else {
            self.editorMeta.user.meta = user;
            self.editorMeta.user.loggedIn = true;
          }
        },
      );
    },
    reset() {
      if (this.suppressBoardNavigationTimer) {
        window.clearTimeout(this.suppressBoardNavigationTimer);
        this.suppressBoardNavigationTimer = null;
      }
      if (this.lazyObserver) {
        this.lazyObserver.disconnect();
        this.lazyObserver = null;
      }
      const data = initialData();
      Object.entries(data).forEach(
        (kv) => {
          const [key, value] = kv;
          this[key] = value;
        },
      );
      this.initialize();
    },
    isBoardOwner(board) {
      return this.editorMeta.user.loggedIn
        && this.editorMeta.user.meta.username === board.author;
    },
    shouldShowTools(board) {
      return this.currentEditBoard === board.id;
    },
    handleBoardTouch(board) {
      const wasVisible = this.shouldShowTools(board);
      this.currentEditBoard = board.id;
      if (this.suppressBoardNavigationTimer) {
        window.clearTimeout(this.suppressBoardNavigationTimer);
      }
      this.suppressBoardNavigationId = wasVisible ? null : board.id;
      if (this.suppressBoardNavigationId === null) {
        return;
      }
      this.suppressBoardNavigationTimer = window.setTimeout(() => {
        this.suppressBoardNavigationId = null;
        this.suppressBoardNavigationTimer = null;
      }, 700);
    },
    handleBoardNavigation(board, event) {
      if (this.suppressBoardNavigationId !== board.id) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      this.suppressBoardNavigationId = null;
      if (this.suppressBoardNavigationTimer) {
        window.clearTimeout(this.suppressBoardNavigationTimer);
        this.suppressBoardNavigationTimer = null;
      }
    },
    createLazyObserver() {
      if (this.lazyObserver || !window.IntersectionObserver) {
        return;
      }
      this.lazyObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach(
            (entry) => {
              if (!entry.isIntersecting) {
                return;
              }
              const itemId = parseInt(entry.target.dataset.boardId, 10);
              if (this.blocksMap[itemId]) {
                this.blocksMap[itemId].imageVisible = true;
                this.blocksMap[itemId].class = Object.assign(
                  {},
                  this.blocksMap[itemId].class,
                  { 'is-visible': true },
                );
              }
              this.lazyObserver.unobserve(entry.target);
            },
          );
        },
        { rootMargin: '420px 0px' },
      );
    },
    observeLazyImages() {
      if (!window.IntersectionObserver) {
        this.blocks.forEach(
          (item) => {
            const block = this.blocksMap[item.id];
            block.imageVisible = true;
            block.class = Object.assign({}, block.class, { 'is-visible': true });
          },
        );
        return;
      }
      this.createLazyObserver();
      this.$el.querySelectorAll('[data-board-id]').forEach(
        (element) => {
          const target = element;
          if (target.dataset.lazyObserved === 'true') {
            return;
          }
          target.dataset.lazyObserved = 'true';
          this.lazyObserver.observe(target);
        },
      );
    },
    onPinImageLoaded(itemId) {
      this.blocksMap[itemId].class = Object.assign(
        {},
        this.blocksMap[itemId].class,
        { 'image-loaded': true },
      );
      this.blocksMap[itemId].style.height = 'auto';
      this.scheduleViewportFillCheck();
    },
    refreshMasonryLayout() {
      this.updateGridMetrics();
      this.masonryKey += 1;
      this.$nextTick(() => {
        this.observeLazyImages();
        if (this.$redrawVueMasonry) {
          this.$redrawVueMasonry();
        }
      });
    },
    handleResize() {
      if (this.resizeTimer) {
        window.clearTimeout(this.resizeTimer);
      }
      this.resizeTimer = window.setTimeout(() => {
        if (!this.updateGridMetrics()) return;
        this.masonryKey += 1;
        this.$nextTick(() => this.redrawMasonryLayout());
        this.scheduleViewportFillCheck();
      }, 120);
    },
    scheduleViewportFillCheck() {
      if (this.fillViewportTimer) {
        window.clearTimeout(this.fillViewportTimer);
      }
      this.fillViewportTimer = window.setTimeout(() => {
        this.fillViewportTimer = null;
        if (
          this.status.loading
          || !this.status.hasNext
          || isDocumentScrollable()
        ) {
          return;
        }
        this.fetchMore();
      }, 180);
    },
    registerScrollEvent() {
      const self = this;
      scroll.bindScroll2Bottom(
        () => {
          if (self.status.loading || !self.status.hasNext) {
            return;
          }
          self.fetchMore();
        },
      );
    },
    buildBlocks(results) {
      const blocks = [];
      results.forEach(
        (pin) => {
          const item = createBoardItem(pin);
          blocks.push(
            item,
          );
        },
      );
      return blocks;
    },
    shouldFetchMore(created) {
      if (!created) {
        if (this.status.loading) {
          return false;
        }
        if (!this.status.hasNext) {
          return false;
        }
      }
      return true;
    },
    fetchMore(created) {
      if (!this.shouldFetchMore(created)) {
        return;
      }
      let promise;
      if (this.filters.boardUsername) {
        promise = API.fetchBoardForUser(
          this.filters.boardUsername,
          this.status.offset,
        );
      } else if (this.filters.boardNameContains) {
        promise = API.Board.fetchListWhichContains(
          this.filters.boardNameContains,
          this.status.offset,
        );
      } else {
        return;
      }
      this.status.loading = true;
      promise.then(
        (resp) => {
          const { results, next } = resp.data;
          let newBlocks = this.buildBlocks(results);
          newBlocks.forEach(
            (item) => { this.blocksMap[item.id] = item; },
          );
          newBlocks = this.blocks.concat(newBlocks);
          this.blocks = newBlocks;
          this.status.offset = newBlocks.length;
          this.status.hasNext = !(next === null);
          this.$emit('boards-meta-loaded', { count: Number.isFinite(resp.data.count) ? resp.data.count : newBlocks.length });
          this.status.error = false;
          this.status.loading = false;
          this.$nextTick(() => {
            this.measureGridWhenReady();
            this.observeLazyImages();
            this.scheduleViewportFillCheck();
          });
        },
        () => {
          this.status.error = true;
          this.status.loading = false;
        },
      );
    },
  },
  created() {
    this.lazyObserver = null;
    bus.bus.$on(bus.events.refreshBoards, this.reset);
    this.registerScrollEvent();
    window.addEventListener('resize', this.handleResize);
    this.initialize();
  },
  mounted() {
    this.bindMasonryMediaEvents();
    this.observeGridContainer();
    this.measureGridWhenReady();
  },
  beforeDestroy() {
    this.unbindMasonryMediaEvents();
    this.clearMasonryTimers();
    if (this.gridResizeObserver) {
      this.gridResizeObserver.disconnect();
      this.gridResizeObserver = null;
    }
    if (this.gridMeasureTimer) {
      window.clearTimeout(this.gridMeasureTimer);
      this.gridMeasureTimer = null;
    }
    if (this.lazyObserver) {
      this.lazyObserver.disconnect();
    }
    if (this.resizeTimer) {
      window.clearTimeout(this.resizeTimer);
    }
    if (this.fillViewportTimer) {
      window.clearTimeout(this.fillViewportTimer);
    }
    if (this.suppressBoardNavigationTimer) {
      window.clearTimeout(this.suppressBoardNavigationTimer);
    }
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style lang="scss" scoped>
/* grid */
@import 'utils/pin';
@import './utils/motion-mixins';

.boards-masonry-grid {
  margin-right: auto;
  margin-left: auto;
}

.grid-sizer,
.grid-item { width: var(--pin-card-width, #{$pin-preview-width}); }
.grid-item {
  margin-bottom: 22px;
}
.gutter-sizer {
  width: var(--pin-grid-gutter, 15px);
}

.grid {
  opacity: 0;
}
.grid.is-visible,
.grid.image-loaded {
  opacity: 1;
  transition: opacity .38s ease;
}

/* card */
$pin-footer-position-fix: -6px;
$avatar-width: 30px;
$avatar-height: 30px;
@import './utils/fonts';
@import './utils/loader.scss';

.board-card{
  position: relative;
  isolation: isolate;
  overflow: visible;
  background:
    radial-gradient(circle at top left, var(--theme-glow), transparent 220px),
    var(--surface-card, #fff);
  border: 1px solid var(--accent-border, #e4e8ef);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  will-change: transform;
  .board-card-link {
    display: block;
    overflow: hidden;
    color: inherit;
    border-radius: 8px;
  }
  .board-stack,
  .board-stack::before {
    position: absolute;
    pointer-events: none;
  }
  .board-stack {
    inset: auto 12px -10px 12px;
    z-index: -1;
    height: 18px;
    border: 1px solid var(--accent-border, rgba(31, 111, 235, 0.22));
    border-radius: 0 0 8px 8px;
    background: var(--accent-soft-gradient, var(--accent-soft, #eef3f8));
  }
  .board-stack::before {
    content: "";
    inset: auto 10px -7px 10px;
    height: 13px;
    border: 1px solid var(--accent-border, rgba(31, 111, 235, 0.16));
    border-radius: 0 0 8px 8px;
    background: var(--surface-accent, #eef3f8);
  }
  &:hover {
    transform: translateY(-4px);
    border-color: var(--accent, #1f6feb);
    box-shadow: var(--accent-shadow, 0 16px 32px rgba(16, 24, 40, 0.16));
  }
  .board-image-shell {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    min-height: 170px;
    background-color: var(--surface-accent, #f5f7fa);
    border-radius: 8px 8px 0 0;
  }
  .board-image-shell::before {
    content: "";
    position: absolute;
    inset: -18px;
    z-index: 0;
    background-image: var(--board-cover-image);
    background-position: center;
    background-size: cover;
    filter: blur(18px) saturate(1.1);
    opacity: 0.28;
  }
  .card-image img {
    position: relative;
    z-index: 1;
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    background-color: var(--surface-1, white);
    @include loader();
  }
  .board-kind-pill {
    position: absolute;
    z-index: 2;
    top: 9px;
    left: 9px;
    max-width: calc(100% - 18px);
    padding: 0.22rem 0.48rem;
    overflow: hidden;
    border-radius: 999px;
    color: var(--accent-text, #fff);
    background: var(--accent-fill, var(--accent-strong, #1f6feb));
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.16);
    font-size: 12px;
    font-weight: 900;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
.grid.is-visible .board-card,
.grid.image-loaded .board-card {
  animation: cardAppear .46s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.lazy-image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 170px;
  background: linear-gradient(
    90deg,
    var(--skeleton-base, #f2f4f7) 0%,
    var(--skeleton-highlight, #ffffff) 45%,
    var(--skeleton-base, #f2f4f7) 100%
  );
  background-size: 220% 100%;
  animation: placeholderPulse 1.4s ease-in-out infinite;
}
.board-footer {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.7rem;
  position: relative;
  padding: 0.85rem;
  background-color: var(--surface-card, white);
  border-top: 1px solid var(--line-soft, #eef1f5);
  border-radius: 0 0 8px 8px;
  font-weight: bold;
  .board-title {
    display: -webkit-box;
    overflow: hidden;
    margin: 0;
    color: var(--text-strong, #22313f);
    font-size: 16px;
    line-height: 1.3;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .board-meta {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 0.25rem;
    min-height: 30px;
    padding: 0 0.55rem;
    border-radius: 999px;
    color: var(--accent-foreground, #1f6feb);
    background: var(--accent-soft-gradient, var(--accent-soft, #eaf3ff));
    white-space: nowrap;
  }
  .board-meta span {
    font-size: 0.95rem;
    font-weight: 900;
  }
  .board-meta small {
    color: inherit;
    font-size: 0.78rem;
    font-weight: 800;
    opacity: 0.8;
  }
}

@keyframes placeholderPulse {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@import 'utils/grid-layout';
@include screen-grid-layout("#boards-container");

</style>
