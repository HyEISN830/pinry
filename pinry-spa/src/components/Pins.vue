<template>
  <div class="pins">
    <section class="section">
      <div id="pins-container" class="container" v-if="blocks">
        <div
          v-masonry=""
          :key="masonryKey"
          transition-duration="0.12s"
          item-selector=".grid-item"
          column-width=".grid-sizer"
          gutter=".gutter-sizer"
        >
          <template v-for="item in blocks">
            <div v-bind:key="item.id"
                 v-masonry-tile
                 :class="item.class"
                 class="grid pin-masonry">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div
                class="pin-card grid-item"
                @mouseenter="showEditButtons(item)"
                @touchstart="handleCardTouch(item)"
                @mouseleave="hideEditButtons(item.id)">
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
                       v-if="item.imageVisible"
                       :src="item.url"
                       @load="onPinImageLoaded(item.id)"
                       @click="openPreview(item, $event)"
                       :alt="item.description"
                       class="pin-preview-image">
                    <div v-else class="lazy-image-placeholder"></div>
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
                              <router-link :to="{ name: 'tag', params: {tag: tag} }"
                                           params="{tag: tag}">{{ tag }}</router-link>
                            </span>
                          </template>
                        </template>
                        <span v-if="hasSource(item.referer)">
                          &middot;
                          <a
                            v-if="isWebUrl(item.referer)"
                            :href="item.referer"
                            target="_blank">{{ $t("sourceLink") }}</a>
                          <span v-else class="source-text">{{ sourceText(item.referer) }}</span>
                        </span>
                      </span>
                    </div>
                    <div class="is-clearfix"></div>
                  </div>
                  <div class="source-warning" v-if="!hasSource(item.referer)">
                    {{ $t("missingSourceNotice") }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
      <loadingSpinner v-bind:show="status.loading"></loadingSpinner>
      <noMore v-bind:show="!status.hasNext"></noMore>
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

function isWebUrl(url) {
  return /^https?:\/\//i.test((url || '').trim());
}

function hasSource(url) {
  return !!(url || '').trim();
}

function sourceText(url) {
  return (url || '').trim();
}

function getResponsiveCardWidth(viewportWidth) {
  if (viewportWidth >= 2328) {
    return 320;
  }
  if (viewportWidth >= 2073) {
    return 300;
  }
  if (viewportWidth >= 1563) {
    return 270;
  }
  return 240;
}

function getResponsiveGridSignature() {
  if (typeof window === 'undefined') {
    return '240-1';
  }
  const viewportWidth = window.innerWidth
    || document.documentElement.clientWidth
    || 0;
  const itemWidth = getResponsiveCardWidth(viewportWidth);
  const gutterWidth = viewportWidth >= 1563 ? 18 : 15;
  const sidePadding = 48;
  const columns = Math.max(
    1,
    Math.floor(
      (viewportWidth - sidePadding + gutterWidth) / (itemWidth + gutterWidth),
    ),
  );
  return `${itemWidth}-${columns}`;
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
  image.url = pinHandler.escapeUrl(pin.image.thumbnail.image);
  image.id = pin.id;
  image.image_id = pin.image.id;
  image.owner_id = pin.submitter.id;
  image.private = pin.private;
  image.description = pin.description;
  image.tags = pin.tags;
  image.boards = pin.boards || [];
  image.author = pin.submitter.username;
  image.avatar = (pin.submitter.avatar && pin.submitter.avatar.small)
    || `//gravatar.com/avatar/${pin.submitter.gravatar}?s=30`;
  image.large_image_url = pinHandler.escapeUrl(pin.image.image);
  image.original_image_url = pin.url;
  image.referer = pin.referer;
  image.orgianl_width = pin.image.width;
  image.style = {
    aspectRatio: `${pin.image.thumbnail.width} / ${pin.image.thumbnail.height}`,
  };
  image.imageVisible = false;
  image.class = {
    'has-board': image.boards.length > 0,
  };
  return image;
}

function initialData() {
  return {
    blocks: [],
    blocksMap: {},
    gridSignature: getResponsiveGridSignature(),
    fillViewportTimer: null,
    masonryKey: 0,
    resizeTimer: null,
    suppressNextPreviewId: null,
    suppressPreviewTimer: null,
    status: {
      loading: false,
      hasNext: true,
      offset: 0,
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
  watch: {
    pinFilters() {
      this.reset();
    },
  },
  methods: {
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
    refreshMasonryLayout() {
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
        const signature = getResponsiveGridSignature();
        if (signature === this.gridSignature) {
          return;
        }
        this.gridSignature = signature;
        this.refreshMasonryLayout();
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
      this.$buefy.modal.open(
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
          this.status.loading = false;
          this.$nextTick(() => {
            this.observeLazyImages();
            this.scheduleViewportFillCheck();
          });
        },
        () => { this.status.loading = false; },
      );
    },
    niceLinks,
    hasSource,
    isWebUrl,
    sourceText,
  },
  created() {
    this.lazyObserver = null;
    bus.bus.$on(bus.events.refreshPin, this.reset);
    this.registerScrollEvent();
    window.addEventListener('resize', this.handleResize);
    this.initialize();
  },
  beforeDestroy() {
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
  transition: opacity .24s ease;
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
  background: #fff;
  border: 1px solid #e8ebf0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  will-change: transform;
  &:hover {
    transform: translateY(-4px);
    border-color: #d3d9e4;
    box-shadow: 0 12px 28px rgba(16, 24, 40, 0.16);
  }
  .pin-image-shell {
    position: relative;
    overflow: hidden;
    background-color: #f5f7fa;
    border-radius: 8px 8px 0 0;
  }
  .pin-preview-image {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: zoom-in;
  }
  > img {
    min-width: $pin-preview-width;
    background-color: white;
    border-radius: 3px 3px 0 0;
    @include loader('../assets/loader.gif');
  }
  .avatar {
    height: $avatar-height;
    width: $avatar-width;
    border-radius: 3px;
  }
  .pin-tag {
    margin-right: 0.2rem;
  }
}
.pin-masonry.is-visible .pin-card,
.pin-masonry.image-loaded .pin-card {
  animation: cardAppear .28s ease;
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
  background: linear-gradient(90deg, #f2f4f7 0%, #e6eaf0 45%, #f2f4f7 100%);
  background-size: 220% 100%;
  animation: placeholderPulse 1.4s ease-in-out infinite;
}
.pin-masonry.has-board {
  .pin-card {
    border-color: rgba(31, 111, 235, 0.68);
    box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.12), 0 8px 20px rgba(16, 24, 40, 0.08);
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
        radial-gradient(circle, rgba(31, 111, 235, 0.3) 0 1.4px, transparent 1.6px) 0 0 / 10px 10px,
        linear-gradient(135deg, rgba(31, 111, 235, 0.12), rgba(20, 184, 166, 0.1));
      opacity: 0.72;
    }
    &::after {
      inset: 5px;
      z-index: 2;
      border: 1px dashed rgba(31, 111, 235, 0.28);
      border-radius: 6px;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.6);
      opacity: 0.72;
    }
    &:hover {
      border-color: rgba(31, 111, 235, 0.82);
      box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.18), 0 14px 30px rgba(16, 24, 40, 0.16);
      &::before {
        opacity: 0.9;
      }
      &::after {
        border-color: rgba(31, 111, 235, 0.36);
        opacity: 0.86;
      }
    }
  }
}
.pin-footer {
  position: relative;
  overflow-wrap: break-word;
  background-color: white;
  border-top: 1px solid #eef1f5;
  border-radius: 0 0 8px 8px;
  text-align: left;
  .description {
    @include description-font;
    padding: 10px 12px;
    border-bottom: 1px solid #eef1f5;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 15px;
    line-height: 1.45;
    color: #263238;
  }
  .board-list {
    @include secondary-font;
    padding: 9px 12px;
    border-bottom: 1px solid #eef1f5;
    background-color: #f7fbff;
    font-size: 14px;
  }
  .board-link {
    display: inline-block;
    margin-right: 0.4rem;
    font-weight: bold;
    color: #1f6feb;
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
    color: #1f6feb;
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
}

@keyframes placeholderPulse {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
@keyframes cardAppear {
  from {
    opacity: 0.86;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@import 'utils/grid-layout';
@include screen-grid-layout("#pins-container")

</style>
