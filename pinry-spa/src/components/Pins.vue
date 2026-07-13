<template>
  <div class="pins">
    <section class="section">
      <div id="pins-container" class="container" v-if="blocks">
        <div
          ref="masonryGrid"
          v-masonry=""
          v-layout-ready="{ itemSelector: '.grid-item' }"
          :key="masonryKey"
          :style="masonryGridStyle"
          class="pins-masonry-grid"
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
                 class="grid-item pin-masonry">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div class="pin-card-frame motion-card-enter" :style="item.motionStyle">
                <div
                  class="pin-card motion-hover-scale"
                  @mouseenter="showEditButtons(item)"
                  @touchstart="handleCardTouch(item)"
                  @mouseleave="hideEditButtons(item.id)">
                  <span class="pin-card-glare" aria-hidden="true"></span>
                  <div>
                  <transition name="pin-editor-menu">
                    <EditorUI
                      v-show="shouldShowEdit(item)"
                      class="pin-editor-overlay"
                      :pin="item"
                      :currentUsername="editorMeta.user.meta.username"
                      :currentBoard="editorMeta.currentBoard"
                      v-on:pin-delete-succeed="reset"
                      v-on:pin-remove-from-board-succeed="reset"
                    ></EditorUI>
                  </transition>
                  <div
                    class="pin-image-shell"
                    :style="item.style"
                    :data-pin-id="item.id">
                    <img
                       v-if="item.imageVisible && item.url"
                       :src="item.url"
                       @load="onPinImageLoaded(item.id)"
                       @click="openPreview(item, $event)"
                       :alt="item.description || $t('imageUnavailableText')"
                       class="pin-preview-image">
                    <div
                      v-else
                      class="lazy-image-placeholder"
                      :class="{ 'is-unavailable': item.imageVisible && !item.url }">
                      <span v-if="item.imageVisible && !item.url">
                        {{ $t("imageUnavailableText") }}
                      </span>
                    </div>
                    <div
                      v-if="item.motion_photo"
                      class="motion-photo-badge"
                      :title="$t('motionPhotoLabel')"
                      :aria-label="$t('motionPhotoLabel')">
                      <span class="live-photo-glyph" aria-hidden="true">
                        <span class="live-photo-ring is-outer"></span>
                        <span class="live-photo-ring is-middle"></span>
                        <span class="live-photo-ring is-inner"></span>
                        <span class="live-photo-dot"></span>
                      </span>
                    </div>
                  </div>
                </div>
                <div class="pin-footer">
                  <div
                    class="description"
                    v-show="item.description"
                    v-html="niceLinks(item.description)">
                  </div>
                  <div class="board-list" v-if="item.boards.length > 0">
                    <span class="dim">{{ $t("boardsLink") }}:&nbsp;</span>
                    <template v-for="board in item.boards">
                      <router-link
                        v-bind:key="board.id"
                        class="board-link"
                        :to="{ name: 'board', params: { boardId: board.id } }">
                        {{ board.name }}
                      </router-link>
                    </template>
                  </div>
                  <div class="details">
                    <div class="is-pulled-left">
                      <img class="avatar" :src="item.avatar" alt="">
                    </div>
                    <div class="pin-info">
                      <span class="dim">{{ $t("pinnedByInfo") }}&nbsp;
                        <span>
                          <router-link
                            :to="{ name: 'user', params: {user: item.author} }">
                            {{ item.author }}
                          </router-link>
                        </span>
                        <template v-if="item.tags.length > 0">
                          &nbsp;in&nbsp;
                          <template v-for="tag in item.tags">
                            <span v-bind:key="tag" class="pin-tag">
                              <router-link class="content-tag-pill" :to="{ name: 'tag', params: { tag } }">
                                {{ tag }}
                              </router-link>
                            </span>
                          </template>
                        </template>
                        <span v-if="hasSource(item.referer)">
                          &middot;
                          <a
                            v-if="isWebUrl(item.referer)"
                            v-source-tooltip
                            class="content-source-link"
                            :href="item.referer"
                            :data-source-tip="sourceText(item.referer)"
                            target="_blank"
                            rel="noopener">{{ $t("sourceLink") }}</a>
                          <span
                            v-else
                            v-source-tooltip
                            class="source-text content-source-link"
                            tabindex="0"
                            :data-source-tip="sourceText(item.referer)">
                            {{ sourceText(item.referer) }}
                          </span>
                        </span>
                      </span>
                    </div>
                    <div class="is-clearfix"></div>
                  </div>
                  <div class="source-warning" v-if="!hasSource(item.referer)">
                    {{ $t("missingSourceNotice") }}
                  </div>
                  <button
                    class="like-button content-like-pill"
                    type="button"
                    :class="{ 'is-liked': item.viewer_liked }"
                    :aria-pressed="item.viewer_liked ? 'true' : 'false'"
                    :disabled="item.likeBusy"
                    :title="item.viewer_liked ? $t('unlikeButton') : $t('likeButton')"
                    @click.stop="togglePinLike(item)">
                    <b-icon
                      :icon="item.viewer_liked ? 'heart' : 'heart-outline'"
                      size="is-small">
                    </b-icon>
                    <span>{{ formatLikeCount(item.likes_count) }}</span>
                  </button>
                </div>
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
        <p>{{ $t("pinsEmptyState") }}</p>
      </div>
      <noMore v-bind:show="!status.hasNext && blocks.length > 0"></noMore>
    </section>
  </div>
</template>

<script>
import API from './api';
import pinHandler from './utils/PinHandler';
import PinPreview from './PinPreview.vue';
import loadingSpinner from './loadingSpinner.vue';
import noMore from './noMore.vue';
import scroll from './utils/scroll';
import bus from './utils/bus';
import EditorUI from './editors/PinEditorUI.vue';
import niceLinks from './utils/niceLinks';
import imageVariant from './utils/imageVariant';
import format from './utils/format';

function isWebUrl(url) {
  return /^https?:\/\//i.test((url || '').trim());
}

function hasSource(url) {
  return !!(url || '').trim();
}

function sourceText(url) {
  return (url || '').trim();
}

function escapeMediaUrl(url) {
  if (!url) {
    return null;
  }
  if (/^https?:\/\//i.test(url)) {
    return pinHandler.escapeUrl(url);
  }
  return url;
}

function getResponsiveCardWidth(containerWidth) {
  if (containerWidth >= 1240) {
    return 224;
  }
  if (containerWidth >= 980) {
    return 220;
  }
  if (containerWidth >= 720) {
    return 216;
  }
  return Math.max(240, containerWidth);
}

function getResponsiveGridMetrics(containerWidth) {
  const safeWidth = Math.max(0, containerWidth || 0);
  if (safeWidth <= 540) {
    return {
      columns: 1,
      gutterWidth: 0,
      itemWidth: safeWidth,
    };
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

function createImageItem(pin) {
  const image = {};
  const pinImage = pin.image || {};
  let thumbnail = {};
  try {
    thumbnail = pinImage.id ? (imageVariant.getCardThumbnail(pinImage) || {}) : {};
  } catch (e) {
    thumbnail = {};
  }
  const thumbnailWidth = thumbnail.width || pinImage.width || 240;
  const thumbnailHeight = thumbnail.height || pinImage.height || 320;
  image.url = thumbnail.image ? pinHandler.escapeUrl(thumbnail.image) : null;
  image.id = pin.id;
  image.image_id = pinImage.id || null;
  image.owner_id = pin.submitter.id;
  image.private = pin.private;
  image.description = pin.description;
  image.tags = pin.tags || [];
  image.boards = pin.boards || [];
  image.author = pin.submitter.username;
  image.avatar = (pin.submitter.avatar && pin.submitter.avatar.small)
    || `//gravatar.com/avatar/${pin.submitter.gravatar}?s=30`;
  image.large_image_url = pinImage.image ? pinHandler.escapeUrl(pinImage.image) : null;
  image.original_image_url = pin.url || image.large_image_url;
  image.motion_photo = pinImage.motion_photo
    ? Object.assign(
      {},
      pinImage.motion_photo,
      { video: escapeMediaUrl(pinImage.motion_photo.video) },
    )
    : null;
  image.referer = pin.referer;
  image.likes_count = pin.likes_count || 0;
  image.viewer_liked = !!pin.viewer_liked;
  image.likeBusy = false;
  image.orgianl_width = pinImage.width || thumbnailWidth;
  image.style = {
    aspectRatio: `${thumbnailWidth} / ${thumbnailHeight}`,
  };
  image.imageVisible = false;
  image.class = {
    'has-board': image.boards.length > 0,
    'has-motion-photo': image.motion_photo !== null,
    'is-image-missing': image.url === null,
  };
  return image;
}

function initialData() {
  return {
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
    masonryLayoutRaf: null,
    masonryLayoutTimers: [],
    suppressNextPreviewId: null,
    suppressPreviewTimer: null,
    status: {
      loading: false,
      hasNext: true,
      offset: 0,
      error: false,
    },
    editorMeta: {
      currentEditId: null,
      currentBoard: {},
      user: {
        loggedIn: false,
        meta: {},
      },
    },
  };
}

export default {
  name: 'pins',
  components: {
    loadingSpinner,
    noMore,
    EditorUI,
  },
  data() {
    return initialData();
  },
  props: {
    pinFilters: {
      type: Object,
      default() {
        return {
          tagFilter: null,
          userFilter: null,
          boardFilter: null,
        };
      },
    },
  },
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
    '$route.fullPath': function () {
      this.queueMasonryLayout();
    },
    pinFilters() {
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

    formatLikeCount(count) {
      return format.formatCount(count);
    },
    isPinOwner(pin) {
      if (!this.editorMeta.user.loggedIn) {
        return false;
      }
      return pin.author === this.editorMeta.user.meta.username;
    },
    shouldShowEdit(pin) {
      return this.isPinOwner(pin) && this.editorMeta.currentEditId === pin.id;
    },
    showEditButtons(pin) {
      if (!this.isPinOwner(pin)) {
        return;
      }
      this.editorMeta.currentEditId = pin.id;
    },
    handleCardTouch(pin) {
      const wasVisible = this.shouldShowEdit(pin);
      this.showEditButtons(pin);
      if (this.suppressPreviewTimer) {
        window.clearTimeout(this.suppressPreviewTimer);
      }
      this.suppressNextPreviewId = (!wasVisible && this.isPinOwner(pin))
        ? pin.id
        : null;
      if (this.suppressNextPreviewId !== null) {
        this.suppressPreviewTimer = window.setTimeout(() => {
          this.suppressNextPreviewId = null;
          this.suppressPreviewTimer = null;
        }, 700);
      }
    },
    hideEditButtons() {
      this.editorMeta.currentEditId = null;
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
              const itemId = parseInt(entry.target.dataset.pinId, 10);
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
      this.$el.querySelectorAll('[data-pin-id]').forEach(
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
          const container = this.$el && this.$el.querySelector('#pins-container');
          if (container && container.clientWidth > 0) {
            this.gridMeasureAttempts = 0;
            this.redrawMasonryLayout();
            return;
          }
          if (this.gridMeasureAttempts >= 8) {
            return;
          }
          this.gridMeasureAttempts += 1;
          this.gridMeasureTimer = window.setTimeout(
            this.measureGridWhenReady,
            Math.min(40 * this.gridMeasureAttempts, 240),
          );
        });
      });
    },
    observeGridContainer() {
      if (!window.ResizeObserver || this.gridResizeObserver) {
        return;
      }
      const container = this.$el && this.$el.querySelector('#pins-container');
      if (!container) {
        return;
      }
      this.gridResizeObserver = new ResizeObserver(() => {
        if (this.updateGridMetrics()) {
          this.masonryKey += 1;
          this.$nextTick(() => this.redrawMasonryLayout());
        }
      });
      this.gridResizeObserver.observe(container);
    },
    updateGridMetrics() {
      const container = this.$el && this.$el.querySelector('#pins-container');
      const containerWidth = container ? container.clientWidth : 0;
      if (!containerWidth) {
        return false;
      }
      const metrics = getResponsiveGridMetrics(containerWidth);
      const signature = `${metrics.itemWidth}-${metrics.gutterWidth}-${metrics.columns}`;
      if (signature === this.gridSignature) {
        return false;
      }
      this.gridMetrics = metrics;
      this.gridSignature = signature;
      return true;
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
        if (!this.updateGridMetrics()) {
          return;
        }
        this.masonryKey += 1;
        this.$nextTick(() => {
          if (this.$redrawVueMasonry) {
            this.$redrawVueMasonry();
          }
        });
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
          const item = createImageItem(pin);
          blocks.push(
            item,
          );
        },
      );
      return blocks;
    },
    openPreview(pinItem, event) {
      if (this.suppressNextPreviewId === pinItem.id) {
        this.suppressNextPreviewId = null;
        if (this.suppressPreviewTimer) {
          window.clearTimeout(this.suppressPreviewTimer);
          this.suppressPreviewTimer = null;
        }
        if (event) {
          event.preventDefault();
          event.stopPropagation();
        }
        return;
      }
      const routeAtOpen = this.$route.fullPath;
      const restoreScroll = scroll.preserveModalScrollPosition(
        () => this.$route.fullPath === routeAtOpen,
      );
      const previewModal = this.$buefy.modal.open(
        {
          parent: this,
          component: PinPreview,
          props: {
            pinItem,
          },
          scroll: 'keep',
          customClass: 'pin-preview-at-home',
        },
      );
      previewModal.$once('close', restoreScroll);
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
    fetchMore(created) {
      if (!this.shouldFetchMore(created)) {
        return;
      }
      this.status.loading = true;
      let promise;
      if (this.pinFilters.tagFilter) {
        promise = API.fetchPins(this.status.offset, this.pinFilters.tagFilter, null, null);
      } else if (this.pinFilters.userFilter) {
        promise = API.fetchPins(this.status.offset, null, this.pinFilters.userFilter, null);
      } else if (this.pinFilters.boardFilter) {
        const prevPromise = API.Board.get(this.pinFilters.boardFilter);
        promise = prevPromise.then(
          (resp) => {
            this.editorMeta.currentBoard = resp.data;
            return API.fetchPins(this.status.offset, null, null, this.pinFilters.boardFilter);
          },
        );
      } else if (this.pinFilters.idFilter) {
        promise = API.fetchPin(this.pinFilters.idFilter);
      } else {
        promise = API.fetchPins(this.status.offset);
      }
      promise.then(
        (resp) => {
          const { count, results, next } = resp.data;
          if (count !== undefined) {
            this.$emit('pins-meta-loaded', { count });
          }
          let newBlocks = this.buildBlocks(results);
          newBlocks.forEach(
            (item) => { this.blocksMap[item.id] = item; },
          );
          newBlocks = this.blocks.concat(newBlocks);
          this.blocks = newBlocks;
          this.status.offset = newBlocks.length;
          this.status.hasNext = !(next === null);
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
    niceLinks,
    hasSource,
    isWebUrl,
    sourceText,
    togglePinLike(item) {
      if (item.likeBusy) {
        return;
      }
      this.$set(item, 'likeBusy', true);
      API.Pin.toggleLike(item.id).then(
        (resp) => {
          this.$set(item, 'viewer_liked', resp.data.viewer_liked);
          this.$set(item, 'likes_count', resp.data.likes_count);
          this.$set(item, 'likeBusy', false);
        },
        () => {
          this.$set(item, 'likeBusy', false);
        },
      );
    },
  },
  created() {
    this.lazyObserver = null;
    bus.bus.$on(bus.events.refreshPin, this.reset);
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
    if (this.suppressPreviewTimer) {
      window.clearTimeout(this.suppressPreviewTimer);
    }
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style lang="scss" scoped>
/* grid */
@import 'utils/pin';
@import './utils/motion-mixins';

.pins-masonry-grid {
  margin-right: auto;
  margin-left: auto;
}

.grid-sizer,
.grid-item { width: var(--pin-card-width, #{$pin-preview-width}); }
.grid-item {
  margin-bottom: 18px;
}
.gutter-sizer {
  width: var(--pin-grid-gutter, 15px);
}

/* pin-image transition */
.pin-masonry.is-visible,
.pin-masonry.image-loaded{
  opacity: 1;
  transition: opacity .38s ease;
}
.pin-masonry {
  opacity: 0;
}

/* card */
$pin-footer-position-fix: -6px;
$avatar-width: 30px;
$avatar-height: 30px;
@import './utils/fonts';
@import './utils/loader.scss';

.pin-card{
  position: relative;
  isolation: isolate;
  box-sizing: border-box;
  overflow: visible;
  background:
    radial-gradient(circle at top left, var(--theme-glow, rgba(126, 87, 194, 0.14)), transparent 220px),
    var(--surface-card, #fff);
  border: 1px solid var(--accent-border, var(--line-soft, #e8ebf0));
  border-radius: var(--radius-md, 12px);
  box-shadow: var(--shadow-soft, 0 1px 2px rgba(16, 24, 40, 0.06));
  transition:
    transform var(--motion-duration-standard, .18s) var(--motion-ease-standard, ease),
    box-shadow var(--motion-duration-standard, .18s) var(--motion-ease-standard, ease),
    border-color var(--motion-duration-fast, .18s) var(--motion-ease-standard, ease);
  will-change: transform;
  &:hover {
    transform: translateY(-4px);
    border-color: var(--accent, #d94691);
    box-shadow: var(--accent-shadow, 0 12px 28px rgba(16, 24, 40, 0.16));
  }
  .pin-image-shell {
    position: relative;
    overflow: hidden;
    background-color: var(--surface-accent, #f5f7fa);
    border-radius: 8px 8px 0 0;
  }
  .pin-preview-image {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: zoom-in;
  }
  .motion-photo-badge {
    position: absolute;
    z-index: 4;
    top: 9px;
    left: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    color: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.34);
    border-radius: 999px;
    background: rgba(12, 18, 28, 0.44);
    backdrop-filter: blur(8px);
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
    transition: transform .18s ease, background .18s ease, box-shadow .18s ease;
  }
  .motion-photo-badge:hover {
    transform: scale(1.06);
    background: rgba(12, 18, 28, 0.56);
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.22);
  }
  .live-photo-glyph {
    position: relative;
    display: block;
    width: 22px;
    height: 22px;
  }
  .live-photo-ring,
  .live-photo-dot {
    position: absolute;
    border-radius: 999px;
  }
  .live-photo-ring {
    border: 1.7px solid currentColor;
    border-right-color: transparent;
    border-bottom-color: transparent;
    opacity: 0.94;
  }
  .live-photo-ring.is-outer {
    inset: 1px;
    transform: rotate(-20deg);
  }
  .live-photo-ring.is-middle {
    inset: 5px;
    transform: rotate(42deg);
  }
  .live-photo-ring.is-inner {
    inset: 8px;
    border-width: 1.5px;
    transform: rotate(112deg);
  }
  .live-photo-dot {
    inset: 9px;
    background: currentColor;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.18);
  }
  > img {
    min-width: $pin-preview-width;
    background-color: var(--surface-card, white);
    border-radius: 3px 3px 0 0;
    @include loader();
  }
  .avatar {
    height: $avatar-height;
    width: $avatar-width;
    border-radius: 3px;
  }
  .pin-tag {
    display: inline-flex;
    margin: 0.12rem 0.18rem 0.12rem 0;
    a {
      display: inline-flex;
      align-items: center;
      max-width: 100%;
      padding: 0.12rem 0.42rem;
      border-radius: 999px;
      color: var(--accent-strong, #1f6feb);
      background: var(--accent-soft, #eaf3ff);
      font-size: 13px;
      font-weight: 800;
      line-height: 1.35;
    }
    a:hover {
      color: var(--accent-strong, #0f4fb8);
      background: var(--surface-accent, #d9eaff);
    }
  }
}
.pin-masonry:hover {
  z-index: 20;
}

.pin-editor-overlay {
  position: absolute;
  z-index: 12;
  top: 8px;
  right: 8px;
  opacity: 0.9;
  transition: opacity .18s ease;
}
.pin-card:hover .pin-editor-overlay {
  opacity: 0.98;
}
.pin-editor-menu-enter-active,
.pin-editor-menu-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.pin-editor-menu-enter,
.pin-editor-menu-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}
.lazy-image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 140px;
  background: linear-gradient(
    90deg,
    var(--skeleton-base, #f2f4f7) 0%,
    var(--skeleton-highlight, #ffffff) 45%,
    var(--skeleton-base, #f2f4f7) 100%
  );
  background-size: 220% 100%;
  animation: placeholderPulse 1.4s ease-in-out infinite;
}
.pin-masonry.has-board {
  .pin-card {
    border-color: var(--accent, #1f6feb);
    box-shadow:
      0 0 0 2px var(--accent-soft, rgba(31, 111, 235, 0.12)),
      0 8px 20px rgba(16, 24, 40, 0.08);
    &::before,
    &::after {
      content: "";
      position: absolute;
      pointer-events: none;
      transition: opacity .18s ease, box-shadow .18s ease;
    }
    &::before {
      inset: -5px;
      z-index: -1;
      border-radius: 12px;
      background:
        radial-gradient(circle, var(--accent, #1f6feb) 0 1.2px, transparent 1.5px) 0 0 / 10px 10px,
        linear-gradient(135deg, var(--theme-glow), var(--accent-soft));
      opacity: 0.72;
    }
    &::after {
      inset: 5px;
      z-index: 2;
      border: 1px dashed var(--accent-border, rgba(31, 111, 235, 0.28));
      border-radius: 6px;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.6);
      opacity: 0.72;
    }
    &:hover {
      border-color: var(--accent-strong, #1f6feb);
      box-shadow:
        0 0 0 2px var(--accent-soft, rgba(31, 111, 235, 0.18)),
        var(--accent-shadow, 0 14px 30px rgba(16, 24, 40, 0.16));
      &::before {
        opacity: 0.9;
      }
      &::after {
        border-color: var(--accent, rgba(31, 111, 235, 0.36));
        opacity: 0.86;
      }
    }
  }
}
.pin-footer {
  position: relative;
  overflow-wrap: break-word;
  background-color: var(--surface-1, white);
  border-top: 1px solid var(--line-soft, #eef1f5);
  border-radius: 0 0 8px 8px;
  text-align: left;
  .description {
    @include description-font;
    padding: 10px 12px;
    border-bottom: 1px solid var(--line-soft, #eef1f5);
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 15px;
    line-height: 1.45;
    color: var(--text-strong, #263238);
  }
  .board-list {
    @include secondary-font;
    padding: 9px 12px;
    border-bottom: 1px solid var(--line-soft, #eef1f5);
    background-color: var(--surface-2, #f7fbff);
    font-size: 14px;
  }
  .board-link {
    display: inline-block;
    margin-right: 0.4rem;
    font-weight: bold;
    color: var(--accent-strong, #1f6feb);
  }
  .details {
    @include secondary-font;
    padding: 12px;
    font-size: 14px;
    > .pin-info {
      line-height: 19px;
      width: calc(var(--pin-card-width, #{$pin-preview-width}) - 50px);
      padding-left: $avatar-width + 5px;
    }
    .pin-info a {
      font-weight: bold;
    }
  }
  .source-text {
    color: var(--accent-strong, #1f6feb);
    font-weight: 600;
  }
  .source-warning {
    margin: 0 12px 12px 47px;
    padding: 5px 8px;
    border: 1px solid #f2df9b;
    border-radius: 6px;
    background: #fffaf0;
    color: #8a6d1d;
    font-size: 13px;
    line-height: 1.35;
  }
  .like-button {
    display: inline-flex;
    align-items: center;
    gap: 0.28rem;
    min-height: 30px;
    margin: 0 12px 12px 47px;
    padding: 0 0.58rem;
    border: 1px solid var(--line-soft, #dbe3ee);
    border-radius: 999px;
    color: var(--text-muted, #64748b);
    background: var(--surface-2, #f8fafc);
    cursor: pointer;
    font-size: 13px;
    font-weight: 800;
    transition: transform .16s ease, color .16s ease, background .16s ease, border-color .16s ease;
  }
  .like-button:hover {
    transform: translateY(-1px);
    color: var(--accent-strong, #d94691);
    border-color: var(--accent, #ef7cba);
    background: var(--accent-soft, rgba(239, 124, 186, 0.16));
  }
  .like-button.is-liked {
    color: var(--accent-strong, #d94691);
    border-color: var(--accent, #ef7cba);
    background: var(--accent-soft, rgba(239, 124, 186, 0.16));
  }
  .like-button:disabled {
    opacity: 0.72;
    cursor: wait;
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
@include screen-grid-layout("#pins-container");

</style>
