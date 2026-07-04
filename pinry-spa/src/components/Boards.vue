<template>
  <div class="boards">
    <section class="section">
      <div id="boards-container" class="container" v-if="blocks">
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
                 class="grid">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div class="board-card grid-item">
                <div @mouseenter="currentEditBoard = item.id"
                     @mouseleave="currentEditBoard = null"
                >
                  <div class="card-image">
                    <BoardEditorUI
                      v-show="shouldShowEdit(item)"
                      :board="item"
                      v-on:board-delete-succeed="reset"
                      v-on:board-save-succeed="reset"
                    ></BoardEditorUI>
                    <router-link :to="{ name: 'board', params: { boardId: item.id } }">
                      <div
                        class="board-image-shell"
                        :style="item.style"
                        :data-board-id="item.id">
                        <img
                           v-if="item.imageVisible"
                           :src="item.preview_image_url"
                           @load="onPinImageLoaded(item.id)"
                           class="preview-image">
                        <div v-else class="lazy-image-placeholder"></div>
                      </div>
                    </router-link>
                  </div>
                  <div class="board-footer">
                    <p class="sub-title board-info">{{ item.name }}</p>
                    <p class="description">
                      <small>
                        {{ $t("pinsInBoard") }}<span class="num-pins">{{ item.total_pins }}</span>
                      </small>
                    </p>
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
import loadingSpinner from './loadingSpinner.vue';
import noMore from './noMore.vue';
import scroll from './utils/scroll';
import placeholder from '../assets/pinry-placeholder.jpg';
import BoardEditorUI from './editors/BoardEditUI.vue';
import bus from './utils/bus';

function getResponsiveGridColumns() {
  if (typeof window === 'undefined') {
    return 1;
  }
  const viewportWidth = window.innerWidth
    || document.documentElement.clientWidth
    || 0;
  const itemWidth = 240;
  const gutterWidth = 15;
  const sidePadding = 48;
  return Math.max(
    1,
    Math.floor(
      (viewportWidth - sidePadding + gutterWidth) / (itemWidth + gutterWidth),
    ),
  );
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
  if (previewImage.image.thumbnail.image !== null) {
    boardItem.preview_image_url = pinHandler.escapeUrl(
      previewImage.image.thumbnail.image,
    );
  } else {
    boardItem.preview_image_url = defaultPreviewImage;
  }
  boardItem.style = {
    width: `${previewImage.image.thumbnail.width}px`,
    height: `${previewImage.image.thumbnail.height}px`,
  };
  boardItem.imageVisible = false;
  boardItem.class = {};
  boardItem.author = board.submitter.username;
  return boardItem;
}

function initialData() {
  return {
    currentEditBoard: null,
    blocks: [],
    blocksMap: {},
    gridColumns: getResponsiveGridColumns(),
    masonryKey: 0,
    resizeTimer: null,
    status: {
      loading: false,
      hasNext: true,
      offset: 0,
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
  watch: {
    filters() {
      this.reset();
    },
  },
  methods: {
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
    shouldShowEdit(board) {
      if (!this.editorMeta.user.loggedIn) {
        return false;
      }
      if (this.editorMeta.user.meta.username !== board.author) {
        return false;
      }
      return this.currentEditBoard === board.id;
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
        const columns = getResponsiveGridColumns();
        if (columns === this.gridColumns) {
          return;
        }
        this.gridColumns = columns;
        this.refreshMasonryLayout();
      }, 120);
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
          this.status.loading = false;
          this.$nextTick(() => this.observeLazyImages());
        },
        () => { this.status.loading = false; },
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
  beforeDestroy() {
    if (this.lazyObserver) {
      this.lazyObserver.disconnect();
    }
    if (this.resizeTimer) {
      window.clearTimeout(this.resizeTimer);
    }
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style lang="scss" scoped>
/* grid */
@import 'utils/pin';

.grid-sizer,
.grid-item { width: $pin-preview-width; }
.grid-item {
  margin-bottom: 22px;
}
.gutter-sizer {
  width: 15px;
}

.grid {
  opacity: 0;
}
.grid.is-visible,
.grid.image-loaded {
  opacity: 1;
  transition: opacity .24s ease;
}

/* card */
$pin-footer-position-fix: -6px;
$avatar-width: 30px;
$avatar-height: 30px;
@import './utils/fonts';
@import './utils/loader.scss';

.board-card{
  position: relative;
  overflow: visible;
  background: #fff;
  border: 1px solid #e4e8ef;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  &::before,
  &::after {
    content: "";
    position: absolute;
    left: 10px;
    right: 10px;
    height: 14px;
    border: 1px solid #d7deea;
    border-radius: 0 0 8px 8px;
    background: #f8fafc;
    pointer-events: none;
  }
  &::before {
    bottom: -8px;
    z-index: -1;
  }
  &::after {
    bottom: -14px;
    left: 20px;
    right: 20px;
    background: #eef3f8;
    z-index: -2;
  }
  &:hover {
    transform: translateY(-4px);
    border-color: #1f6feb;
    box-shadow: 0 16px 32px rgba(16, 24, 40, 0.16);
  }
  .board-image-shell {
    position: relative;
    overflow: hidden;
    background-color: #f5f7fa;
    border-radius: 8px 8px 0 0;
  }
  .card-image img {
    display: block;
    width: 100%;
    height: auto;
    min-width: $pin-preview-width;
    background-color: white;
    @include loader('../assets/loader.gif');
  }
}
.grid.is-visible .board-card,
.grid.image-loaded .board-card {
  animation: cardAppear .28s ease both;
}
.lazy-image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 150px;
  background: linear-gradient(90deg, #f2f4f7 0%, #e6eaf0 45%, #f2f4f7 100%);
  background-size: 220% 100%;
  animation: placeholderPulse 1.4s ease-in-out infinite;
}
.board-footer {
  position: relative;
  background-color: white;
  border-top: 1px solid #eef1f5;
  border-radius: 0 0 8px 8px;
  font-weight: bold;
  .description {
    @include secondary-font;
    padding: 0 12px 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 13px;
  }
  .board-info {
    padding: 12px 12px 6px;
    color: #22313f;
    font-size: 15px;
    line-height: 1.3;
  }
  .num-pins {
    font-size: 0.9rem;
    color: #1f6feb;
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
@include screen-grid-layout("#boards-container")

</style>
