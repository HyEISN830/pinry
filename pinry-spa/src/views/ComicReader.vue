<template>
  <div class="comic-reader-page">
    <PHeader></PHeader>
    <section class="section">
      <div class="container comic-reader">
        <div class="reader-head" v-if="comic">
          <div>
            <h1>{{ comic.title }}</h1>
            <p>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</p>
            <div
              class="reader-description"
              v-if="hasDescription(comic.description)"
              v-html="niceLinks(comic.description)">
            </div>
            <div class="reader-source-row comic-source" v-if="hasSource(comic.referer)">
              <a
                v-if="isWebUrl(comic.referer)"
                v-source-tooltip
                class="content-source-link"
                :href="comic.referer"
                :data-source-tip="sourceText(comic.referer)"
                target="_blank"
                rel="noopener">
                {{ $t("sourceLink") }}
              </a>
              <span
                v-else
                v-source-tooltip
                class="content-source-link"
                tabindex="0"
                :data-source-tip="sourceText(comic.referer)">
                {{ sourceText(comic.referer) }}
              </span>
            </div>
            <div class="reader-source-row comic-source is-warning" v-else>
              {{ $t("missingSourceNotice") }}
            </div>
            <div
              class="reader-tags comic-tags"
              v-if="comic.tags && comic.tags.length > 0">
              <router-link
                v-for="tag in comic.tags"
                :key="tag"
                class="content-tag-pill"
                :to="{ name: 'tag', params: { tag } }">
                {{ tag }}
              </router-link>
            </div>
          </div>
          <div class="reader-actions">
            <button
              class="button reader-action-button reader-action-button--primary"
              type="button"
              :disabled="loadingAll"
              @click="openFullReader">
              <b-icon icon="book-open-page-variant" custom-size="mdi-19px"></b-icon>
              <span>{{ loadingAll ? $t("imageLoadingText") : $t("readFullComicButton") }}</span>
            </button>
            <button
              class="button reader-action-button reader-action-button--secondary"
              type="button"
              @click="shareComic">
              <b-icon icon="share-variant" custom-size="mdi-18px"></b-icon>
              <span>{{ $t("shareButton") }}</span>
            </button>
            <button
              v-if="isOwner"
              class="button reader-action-button reader-action-button--secondary"
              :class="{ 'is-active': editing }"
              type="button"
              :aria-expanded="editing ? 'true' : 'false'"
              @click="toggleEditing">
              <b-icon
                :icon="editing ? 'close' : 'pencil'"
                custom-size="mdi-18px">
              </b-icon>
              <span>{{ editing ? $t("closeButton") : $t("editComicButton") }}</span>
            </button>
          </div>
        </div>
        <transition name="comic-editor-reveal">
          <div class="comic-editor" v-if="comic && isOwner && editing">
            <div class="comic-editor__form-grid">
              <b-field :label="$t('descriptionLabel')">
                <b-input
                  type="textarea"
                  v-model="editForm.description"
                  maxlength="1024"
                  :placeholder="$t('pinCreateModalImageDescriptionPlaceholder')">
                </b-input>
              </b-field>
              <b-field :label="$t('imageSourceLabel')">
                <b-input
                  v-model="editForm.referer"
                  maxlength="2048"
                  :placeholder="$t('pinCreateModalImageSourcePlaceholder')">
                </b-input>
              </b-field>
              <b-field class="comic-editor__tags" :label="$t('tagsLabel')">
                <b-taginput
                  ref="tagInput"
                  v-model="editForm.tags"
                  :data="filteredTagOptions"
                  autocomplete
                  allow-new
                  field="name"
                  :placeholder="$t('pinCreateModalImageTagsPlaceholder')"
                  @typing="getFilteredTags">
                  <template slot="empty">{{ $t("noResultsFound") }}</template>
                </b-taginput>
              </b-field>
            </div>
            <div class="comic-editor__detail-actions">
              <button
                class="button comic-editor-button comic-editor-button--secondary editor-save-button"
                type="button"
                :disabled="detailSaving"
                :class="{ 'is-loading': detailSaving }"
                @click="saveComicDetails">
                <b-icon icon="content-save" custom-size="mdi-18px"></b-icon>
                <span>{{ $t("saveChangesButton") }}</span>
              </button>
            </div>
            <div class="comic-editor__divider"></div>
            <div
              class="comic-editor__insert-controls"
              role="group"
              :aria-label="$t('comicInsertPositionLabel')">
              <label
                class="comic-editor__insert-label"
                for="comic-insert-page">
                {{ $t('comicInsertPositionLabel') }}
              </label>
              <div class="comic-editor__insert-selects">
                <TokenSelect
                  id="comic-insert-page"
                  v-model="insertPageId"
                  :aria-label="$t('comicInsertPositionLabel')"
                  :options="insertPageOptions">
                </TokenSelect>
                <TokenSelect
                  id="comic-insert-mode"
                  v-model="insertMode"
                  :aria-label="$t('comicInsertPositionLabel')"
                  :options="insertModeOptions">
                </TokenSelect>
              </div>
            </div>
            <b-field :label="$t('comicPagesLabel')">
              <div class="comic-file-picker">
                <input
                  ref="editorFileInput"
                  class="comic-file-picker__input"
                  type="file"
                  multiple
                  accept="image/*"
                  @change="onEditorFilesSelected">
                <button
                  class="button comic-editor-button comic-file-picker__button"
                  type="button"
                  @click="openEditorFilePicker">
                  <b-icon icon="image-multiple" custom-size="mdi-20px"></b-icon>
                  <span>{{ $t("comicSelectPagesButton") }}</span>
                </button>
                <span class="comic-file-picker__count">
                  {{ $t("comicSelectedFilesCount", { count: editorFiles.length }) }}
                </span>
              </div>
            </b-field>
            <div class="comic-editor-files" v-if="editorFiles.length > 0">
              <article
                class="comic-editor-file"
                v-for="editorFile in editorFiles"
                :key="editorFile.id">
                <div class="comic-editor-file__preview">
                  <img :src="editorFile.previewUrl" :alt="editorFile.name">
                </div>
                <div class="comic-editor-file__copy">
                  <strong :title="editorFile.name">{{ editorFile.name }}</strong>
                  <span>
                    {{ formatFileSize(editorFile.size) }}
                    ·
                    {{ editorFileDimensions(editorFile) }}
                  </span>
                  <ComicUploadMiniProgress
                    :status="editorFile.uploadStatus"
                    :progress="editorFile.uploadProgress">
                  </ComicUploadMiniProgress>
                </div>
                <button
                  class="comic-editor-file__remove"
                  type="button"
                  :title="$t('comicRemoveSelectedFile')"
                  :aria-label="$t('comicRemoveSelectedFile')"
                  @click="removeEditorFile(editorFile.id)">
                  <b-icon icon="close" custom-size="mdi-18px"></b-icon>
                </button>
              </article>
            </div>
            <div class="comic-editor__add-actions">
              <button
                class="button comic-editor-button comic-editor-add-button"
                type="button"
                :disabled="editorFiles.length === 0 || editorSaving"
                :class="{ 'is-loading': editorSaving }"
                @click="addPages">
                <b-icon icon="image-plus" custom-size="mdi-20px"></b-icon>
                <span>{{ $t("comicAddPagesButton") }}</span>
              </button>
            </div>
          </div>
        </transition>
        <div class="reader-pages" v-if="comic">
          <figure
            class="reader-page"
            v-for="page in visibleReaderPages"
            :key="page.id">
            <div class="page-tools" v-if="isOwner && editing">
              <button
                class="button page-tool-button"
                type="button"
                :disabled="page.order <= 1"
                @click="movePage(page, page.order - 1)">
                <b-icon icon="arrow-up" custom-size="mdi-17px"></b-icon>
                <span>{{ $t("moveUpButton") }}</span>
              </button>
              <button
                class="button page-tool-button"
                type="button"
                :disabled="page.order >= comic.pages.length"
                @click="movePage(page, page.order + 1)">
                <b-icon icon="arrow-down" custom-size="mdi-17px"></b-icon>
                <span>{{ $t("moveDownButton") }}</span>
              </button>
              <button
                class="button page-tool-button page-tool-button--danger"
                type="button"
                @click="removePage(page)">
                <b-icon icon="delete-outline" custom-size="mdi-17px"></b-icon>
                <span>{{ $t("removePageButton") }}</span>
              </button>
            </div>
            <img
              :src="pageUrl(page)"
              :alt="`${comic.title} ${page.order}`"
              :class="{ 'is-original': loadedPages[page.id] }">
            <ComicImageLoadProgress
              v-if="pageLoading[page.id]"
              :progress="pageProgress[page.id]">
            </ComicImageLoadProgress>
            <figcaption v-if="page.caption">{{ page.caption }}</figcaption>
          </figure>
        </div>
        <div
          class="read-teaser"
          v-if="shouldShowReadTeaser"
          @click="openFullReader">
          <img
            :src="thumbnailUrl(secondPage.image)"
            :alt="`${comic.title} ${secondPage.order}`">
          <button class="button is-primary" type="button">
            {{ $t("readFullComicButton") }}
          </button>
        </div>
        <loadingSpinner :show="loading" size="large"></loadingSpinner>
      </div>
    </section>
    <div
      class="comic-full-reader"
      v-if="fullReaderOpen"
      tabindex="0"
      @keydown.left.prevent="goFullPage(-1)"
      @keydown.right.prevent="goFullPage(1)"
      @keydown.esc.prevent="closeFullReader"
      @wheel.stop
      @touchmove.stop>
      <div class="full-reader-bar">
        <strong>{{ comic.title }}</strong>
        <div class="full-reader-actions">
          <span class="full-reader-page-count">
            {{ currentFullPageOrder }} / {{ comic.total_pages }}
          </span>
          <button
            class="button is-light"
            type="button"
            @click="closeFullReader">
            {{ $t("closeButton") }}
          </button>
        </div>
      </div>
      <div class="full-reader-pages">
        <figure
          class="full-reader-page"
          v-for="page in comic.pages"
          :key="`full-${page.id}`"
          :data-page-order="page.order">
          <img
            :src="pageUrl(page)"
            :alt="`${comic.title} ${page.order}`"
            :class="{ 'is-original': loadedPages[page.id] }"
            @load="scheduleFullPageMeasure">
          <ComicImageLoadProgress
            v-if="pageLoading[page.id]"
            :progress="pageProgress[page.id]">
          </ComicImageLoadProgress>
        </figure>
      </div>
    </div>
  </div>
</template>

<script>
import API from '../components/api';
import ComicImageLoadProgress from '../components/comic/ComicImageLoadProgress.vue';
import ComicUploadMiniProgress from '../components/comic/ComicUploadMiniProgress.vue';
import TokenSelect from '../components/form/TokenSelect.vue';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import {
  cacheImage,
  getCachedImage,
} from '../components/utils/originalImageCache';
import imageVariant from '../components/utils/imageVariant';
import niceLinks from '../components/utils/niceLinks';
import scroll from '../components/utils/scroll';
import share from '../components/utils/share';

function splitTags(tagText) {
  return tagText.split(/[,\uFF0C]/)
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);
}

function uniqueTags(tags) {
  const seen = {};
  const normalized = [];
  tags.forEach(
    (tag) => {
      if (!seen[tag]) {
        seen[tag] = true;
        normalized.push(tag);
      }
    },
  );
  return normalized;
}

export default {
  name: 'ComicReader',
  components: {
    ComicImageLoadProgress,
    ComicUploadMiniProgress,
    TokenSelect,
    PHeader,
    loadingSpinner,
  },
  data() {
    return {
      comic: null,
      editing: false,
      editorFiles: [],
      editorFileSequence: 0,
      editorSaving: false,
      detailSaving: false,
      editForm: {
        description: '',
        referer: '',
        tags: [],
      },
      filteredTagOptions: [],
      fullPageObserver: null,
      fullPageMeasureFrame: null,
      fullReaderScrollLock: null,
      fullReaderScrollElement: null,
      fullReaderOpen: false,
      currentFullPageOrder: 1,
      insertMode: 'after',
      insertPageId: null,
      loadedPages: {},
      loading: true,
      loadingAll: false,
      allPagesLoadPromise: null,
      pageLoadPromises: {},
      pageLoading: {},
      pageProgress: {},
      tagOptions: [],
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    firstPage() {
      if (!this.comic || this.comic.pages.length === 0) {
        return null;
      }
      const [page] = this.comic.pages;
      return page;
    },
    isOwner() {
      return this.user.loggedIn
        && this.comic
        && this.comic.submitter.username === this.user.meta.username;
    },
    insertModeOptions() {
      return [
        {
          label: this.$t('comicInsertAfterLabel'),
          value: 'after',
        },
        {
          label: this.$t('comicInsertBeforeLabel'),
          value: 'before',
        },
      ];
    },
    insertPageOptions() {
      if (!this.comic) {
        return [];
      }
      return this.comic.pages.map(
        page => ({
          label: String(page.order),
          value: page.id,
        }),
      );
    },
    secondPage() {
      if (!this.comic || this.comic.pages.length < 2) {
        return null;
      }
      const [, page] = this.comic.pages;
      return page;
    },
    shouldShowReadTeaser() {
      return !this.editing
        && this.firstPage
        && this.secondPage
        && !!this.loadedPages[this.firstPage.id];
    },
    visibleReaderPages() {
      if (!this.comic) {
        return [];
      }
      if (this.editing) {
        return this.comic.pages;
      }
      return this.firstPage ? [this.firstPage] : [];
    },
  },
  created() {
    this.fetchUser();
    this.fetchTagList();
    this.fetchComic();
  },
  beforeDestroy() {
    this.clearEditorFiles();
    this.disconnectFullPageObserver();
    this.unlockFullReaderScroll();
  },
  methods: {
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
    fetchComic() {
      API.Comic.get(this.$route.params.comicId).then(
        (resp) => {
          this.comic = resp.data;
          this.loading = false;
          this.editForm.description = this.comic.description || '';
          this.editForm.referer = this.comic.referer || '';
          this.editForm.tags = this.comic.tags || [];
          if (this.comic.pages.length > 0) {
            if (this.insertPageId === null) {
              this.insertPageId = this.comic.pages[0].id;
            }
            this.loadPageOriginal(this.comic.pages[0]);
            if (this.editing) {
              this.loadAllPages();
            }
          }
        },
        () => {
          this.$router.push({ name: 'PageNotFound' });
        },
      );
    },
    pageUrl(page) {
      if (this.loadedPages[page.id]) {
        return this.loadedPages[page.id];
      }
      return this.thumbnailUrl(page.image);
    },
    thumbnailUrl(image) {
      if (!image) {
        return null;
      }
      try {
        const thumbnail = imageVariant.getCardThumbnail(image) || {};
        return thumbnail.image || null;
      } catch (e) {
        return null;
      }
    },
    loadPageOriginal(page) {
      if (!page || !page.image || !page.image.id) {
        return Promise.resolve(null);
      }
      const cached = getCachedImage(page.image.id);
      if (cached) {
        this.$set(this.loadedPages, page.id, cached.objectUrl);
        return Promise.resolve(cached);
      }
      if (this.pageLoadPromises[page.id]) {
        return this.pageLoadPromises[page.id];
      }
      this.$set(this.pageLoading, page.id, true);
      this.$set(this.pageProgress, page.id, null);
      const loadPromise = API.Pin.fetchOriginalImage(page.image.id).then(
        (response) => {
          if (!response.ok) {
            throw new Error('Failed to load comic page');
          }
          const total = parseInt(response.headers.get('Content-Length'), 10);
          const downloadTotal = Number.isNaN(total) ? null : total;
          if (!response.body || !response.body.getReader) {
            return response.blob();
          }
          return this.readPageStream(
            response.body.getReader(),
            [],
            page,
            downloadTotal,
            0,
          );
        },
      ).then(
        (blob) => {
          const cachedImage = cacheImage(page.image.id, blob);
          if (cachedImage) {
            this.$set(this.loadedPages, page.id, cachedImage.objectUrl);
          }
          this.$set(this.pageLoading, page.id, false);
          this.$set(this.pageProgress, page.id, 100);
          this.$delete(this.pageLoadPromises, page.id);
          return cachedImage;
        },
        (error) => {
          this.$set(this.pageLoading, page.id, false);
          this.$delete(this.pageLoadPromises, page.id);
          throw error;
        },
      );
      this.$set(this.pageLoadPromises, page.id, loadPromise);
      return loadPromise;
    },
    readPageStream(reader, chunks, page, total, loaded) {
      return reader.read().then(
        ({ done, value }) => {
          if (done) {
            return new Blob(chunks);
          }
          chunks.push(value);
          const nextLoaded = loaded + value.length;
          if (total) {
            this.$set(
              this.pageProgress,
              page.id,
              Math.round((nextLoaded / total) * 100),
            );
          }
          return this.readPageStream(
            reader,
            chunks,
            page,
            total,
            nextLoaded,
          );
        },
      );
    },
    loadPagesSequentially(pages) {
      if (pages.length === 0) {
        return Promise.resolve();
      }
      const [page] = pages;
      return this.loadPageOriginal(page).then(
        () => this.loadPagesSequentially(pages.slice(1)),
      );
    },
    loadAllPages() {
      if (!this.comic) {
        return Promise.resolve();
      }
      if (this.allPagesLoadPromise) {
        return this.allPagesLoadPromise;
      }
      this.loadingAll = true;
      const remainingPages = this.comic.pages.filter(
        page => !this.loadedPages[page.id],
      );
      this.allPagesLoadPromise = this.loadPagesSequentially(remainingPages).then(
        () => {
          this.loadingAll = false;
          this.allPagesLoadPromise = null;
        },
        () => {
          this.loadingAll = false;
          this.allPagesLoadPromise = null;
        },
      );
      return this.allPagesLoadPromise;
    },
    openFullReader() {
      if (this.fullReaderOpen) {
        return;
      }
      this.lockFullReaderScroll();
      this.fullReaderOpen = true;
      this.currentFullPageOrder = 1;
      this.$nextTick(
        () => {
          this.observeFullReaderPages();
          this.bindFullReaderScroll();
          this.scheduleFullPageMeasure();
          const fullReader = this.$el.querySelector('.comic-full-reader');
          if (fullReader) {
            fullReader.focus();
          }
        },
      );
      this.loadAllPages();
    },
    closeFullReader() {
      this.fullReaderOpen = false;
      this.disconnectFullPageObserver();
      this.unlockFullReaderScroll();
    },
    lockFullReaderScroll() {
      if (this.fullReaderScrollLock !== null) {
        return;
      }
      const { body, documentElement } = document;
      const scrollTop = Math.max(
        0,
        window.pageYOffset || documentElement.scrollTop || 0,
      );
      this.fullReaderScrollLock = {
        bodyLeft: body.style.left,
        bodyOverflow: body.style.overflow,
        bodyPosition: body.style.position,
        bodyRight: body.style.right,
        bodyTop: body.style.top,
        bodyWidth: body.style.width,
        documentOverflow: documentElement.style.overflow,
        documentOverscrollBehavior: documentElement.style.overscrollBehavior,
        scrollTop,
      };
      documentElement.style.overflow = 'hidden';
      documentElement.style.overscrollBehavior = 'none';
      body.style.overflow = 'hidden';
      body.style.position = 'fixed';
      body.style.top = `-${scrollTop}px`;
      body.style.right = '0';
      body.style.left = '0';
      body.style.width = '100%';
    },
    unlockFullReaderScroll() {
      if (this.fullReaderScrollLock === null) {
        return;
      }
      const { body, documentElement } = document;
      const lock = this.fullReaderScrollLock;
      documentElement.style.overflow = lock.documentOverflow;
      documentElement.style.overscrollBehavior = lock.documentOverscrollBehavior;
      body.style.overflow = lock.bodyOverflow;
      body.style.position = lock.bodyPosition;
      body.style.top = lock.bodyTop;
      body.style.right = lock.bodyRight;
      body.style.left = lock.bodyLeft;
      body.style.width = lock.bodyWidth;
      this.fullReaderScrollLock = null;
      scroll.restoreScrollPosition(lock.scrollTop);
    },
    disconnectFullPageObserver() {
      if (this.fullPageObserver) {
        this.fullPageObserver.disconnect();
        this.fullPageObserver = null;
      }
      if (this.fullReaderScrollElement) {
        this.fullReaderScrollElement.removeEventListener(
          'scroll',
          this.scheduleFullPageMeasure,
        );
        this.fullReaderScrollElement = null;
      }
      window.removeEventListener('resize', this.scheduleFullPageMeasure);
      if (this.fullPageMeasureFrame) {
        window.cancelAnimationFrame(this.fullPageMeasureFrame);
        this.fullPageMeasureFrame = null;
      }
    },
    bindFullReaderScroll() {
      const element = this.$el.querySelector('.comic-full-reader');
      if (!element) {
        return;
      }
      this.fullReaderScrollElement = element;
      element.addEventListener(
        'scroll',
        this.scheduleFullPageMeasure,
        { passive: true },
      );
      window.addEventListener('resize', this.scheduleFullPageMeasure);
    },
    observeFullReaderPages() {
      this.disconnectFullPageObserver();
      if (!window.IntersectionObserver) {
        return;
      }
      this.fullPageObserver = new IntersectionObserver(
        () => {
          this.scheduleFullPageMeasure();
        },
        {
          root: null,
          threshold: [0, 0.25, 0.5, 0.75, 1],
        },
      );
      this.$el.querySelectorAll('.full-reader-page').forEach(
        (element) => {
          this.fullPageObserver.observe(element);
        },
      );
    },
    scheduleFullPageMeasure() {
      if (!this.fullReaderOpen || this.fullPageMeasureFrame) {
        return;
      }
      this.fullPageMeasureFrame = window.requestAnimationFrame(
        () => {
          this.fullPageMeasureFrame = null;
          this.updateCurrentFullPage();
        },
      );
    },
    updateCurrentFullPage() {
      const pages = Array.from(
        this.$el.querySelectorAll('.full-reader-page'),
      );
      if (pages.length === 0) {
        return;
      }
      const scrollElement = this.fullReaderScrollElement
        || this.$el.querySelector('.comic-full-reader');
      const isDesktopFullReader = window.matchMedia
        ? window.matchMedia('(min-width: 543px)').matches
        : true;
      if (isDesktopFullReader && scrollElement) {
        const isScrollable = scrollElement.scrollHeight > scrollElement.clientHeight + 8;
        const isNearBottom = scrollElement.scrollTop + scrollElement.clientHeight
          >= scrollElement.scrollHeight - 8;
        if (isScrollable && isNearBottom) {
          const lastPage = pages[pages.length - 1];
          const lastPageOrder = parseInt(lastPage.dataset.pageOrder, 10);
          if (lastPageOrder !== this.currentFullPageOrder) {
            this.currentFullPageOrder = lastPageOrder;
          }
          return;
        }
      }
      const viewportHeight = window.innerHeight
        || document.documentElement.clientHeight
        || 0;
      const viewportCenter = viewportHeight / 2;
      let bestPage = null;
      pages.forEach(
        (page) => {
          const rect = page.getBoundingClientRect();
          const visibleHeight = Math.max(
            0,
            Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0),
          );
          if (visibleHeight <= 0) {
            return;
          }
          const pageCenter = rect.top + rect.height / 2;
          const centerPenalty = Math.abs(pageCenter - viewportCenter) * 0.05;
          const score = visibleHeight - centerPenalty;
          if (!bestPage || score > bestPage.score) {
            bestPage = {
              order: parseInt(page.dataset.pageOrder, 10),
              score,
            };
          }
        },
      );
      if (bestPage && bestPage.order !== this.currentFullPageOrder) {
        this.currentFullPageOrder = bestPage.order;
      }
    },
    goFullPage(direction) {
      if (!this.fullReaderOpen || !this.comic) {
        return;
      }
      const pageCount = this.comic.pages.length;
      const nextOrder = Math.max(1, Math.min(pageCount, this.currentFullPageOrder + direction));
      const target = this.$el.querySelector(`[data-page-order="${nextOrder}"]`);
      if (target && target.scrollIntoView) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      this.currentFullPageOrder = nextOrder;
    },
    fetchTagList() {
      API.Tag.fetchList().then(
        (resp) => {
          this.tagOptions = resp.data;
        },
      );
    },
    setTagInputText(text) {
      this.$nextTick(
        () => {
          if (this.$refs.tagInput) {
            this.$refs.tagInput.newTag = text;
          }
        },
      );
    },
    normalizeTags() {
      const tags = [];
      this.editForm.tags.forEach(
        (tag) => {
          splitTags(tag).forEach(
            item => tags.push(item),
          );
        },
      );
      this.editForm.tags = uniqueTags(tags);
    },
    absorbTypedTags(text) {
      if (!/[,\uFF0C]/.test(text)) {
        return text;
      }
      const parts = text.split(/[,\uFF0C]/);
      const remainingText = parts.pop();
      const tags = splitTags(parts.join(','));
      this.editForm.tags = uniqueTags(
        this.editForm.tags.concat(tags),
      );
      this.setTagInputText(remainingText);
      return remainingText;
    },
    getFilteredTags(text) {
      const filterText = this.absorbTypedTags(text);
      const filteredTagOptions = [];
      this.tagOptions.forEach(
        (option) => {
          if (option.name.toString().toLowerCase().indexOf(filterText.toLowerCase()) >= 0) {
            filteredTagOptions.push(option.name);
          }
        },
      );
      this.filteredTagOptions = filteredTagOptions;
    },
    saveComicDetails() {
      if (this.detailSaving) {
        return;
      }
      this.detailSaving = true;
      this.normalizeTags();
      API.Comic.saveChanges(
        this.comic.id,
        {
          description: this.editForm.description,
          referer: this.editForm.referer,
          tags: this.editForm.tags,
        },
      ).then(
        (resp) => {
          this.comic = resp.data;
          this.editForm.description = this.comic.description || '';
          this.editForm.referer = this.comic.referer || '';
          this.editForm.tags = this.comic.tags || [];
          this.detailSaving = false;
        },
        () => {
          this.detailSaving = false;
        },
      );
    },
    hasSource(url) {
      return !!(url || '').trim();
    },
    hasDescription(description) {
      return !!(description || '').trim();
    },
    isWebUrl(url) {
      return /^https?:\/\//i.test((url || '').trim());
    },
    sourceText(url) {
      return (url || '').trim();
    },
    niceLinks,
    shareComic() {
      if (!this.comic) {
        return;
      }
      share.shareRoute(
        this,
        { name: 'comic', params: { comicId: this.comic.id } },
      );
    },
    toggleEditing() {
      this.editing = !this.editing;
      if (this.editing) {
        this.loadAllPages();
      } else {
        this.clearEditorFiles();
      }
    },
    openEditorFilePicker() {
      const input = this.$refs.editorFileInput;
      if (input) {
        input.click();
      }
    },
    onEditorFilesSelected(event) {
      const files = Array.from(event.target.files || []);
      this.clearEditorFiles();
      this.editorFiles = files.map(
        (file) => {
          this.editorFileSequence += 1;
          return {
            id: this.editorFileSequence,
            file,
            name: file.name,
            size: file.size,
            width: null,
            height: null,
            previewUrl: window.URL.createObjectURL(file),
            uploadedResponse: null,
            uploadProgress: 0,
            uploadStatus: 'queued',
          };
        },
      );
      this.editorFiles.forEach(this.readEditorFileDimensions);
      const input = this.$refs.editorFileInput;
      if (input) {
        input.value = '';
      }
    },
    readEditorFileDimensions(editorFile) {
      const image = new Image();
      image.onload = () => {
        const matched = this.editorFiles.find(item => item.id === editorFile.id);
        if (!matched) {
          return;
        }
        this.$set(matched, 'width', image.naturalWidth || null);
        this.$set(matched, 'height', image.naturalHeight || null);
      };
      image.src = editorFile.previewUrl;
    },
    revokeEditorFile(editorFile) {
      if (
        editorFile
        && editorFile.previewUrl
        && window.URL
        && typeof window.URL.revokeObjectURL === 'function'
      ) {
        window.URL.revokeObjectURL(editorFile.previewUrl);
      }
    },
    clearEditorFiles() {
      this.editorFiles.forEach(this.revokeEditorFile);
      this.editorFiles = [];
      const input = this.$refs.editorFileInput;
      if (input) {
        input.value = '';
      }
    },
    removeEditorFile(editorFileId) {
      const matched = this.editorFiles.find(item => item.id === editorFileId);
      this.revokeEditorFile(matched);
      this.editorFiles = this.editorFiles.filter(item => item.id !== editorFileId);
    },
    formatFileSize(bytes) {
      const units = ['B', 'KB', 'MB', 'GB'];
      let size = Number(bytes) || 0;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex += 1;
      }
      const fractionDigits = unitIndex === 0 || size >= 10 ? 0 : 1;
      return `${size.toFixed(fractionDigits)} ${units[unitIndex]}`;
    },
    editorFileDimensions(editorFile) {
      if (editorFile.width && editorFile.height) {
        return `${editorFile.width} × ${editorFile.height} px`;
      }
      return this.$t('imageDimensionsReading');
    },
    onEditorFileUploadProgress(editorFile, event) {
      const loaded = Number(event.loaded);
      const total = Number(event.total);
      if (!Number.isFinite(loaded) || !Number.isFinite(total) || total <= 0) {
        this.$set(editorFile, 'uploadProgress', null);
        return;
      }
      this.$set(
        editorFile,
        'uploadProgress',
        Math.min(99, Math.max(0, Math.round((loaded / total) * 100))),
      );
    },
    uploadEditorFiles(index = 0, responses = []) {
      if (index >= this.editorFiles.length) {
        return Promise.resolve(responses);
      }
      const editorFile = this.editorFiles[index];
      if (editorFile.uploadedResponse) {
        responses.push(editorFile.uploadedResponse);
        return this.uploadEditorFiles(index + 1, responses);
      }
      this.$set(editorFile, 'uploadStatus', 'uploading');
      return API.Pin.uploadImage(
        editorFile.file,
        event => this.onEditorFileUploadProgress(editorFile, event),
      ).then(
        (resp) => {
          this.$set(editorFile, 'uploadedResponse', resp);
          this.$set(editorFile, 'uploadStatus', 'complete');
          this.$set(editorFile, 'uploadProgress', 100);
          responses.push(resp);
          return this.uploadEditorFiles(index + 1, responses);
        },
        (error) => {
          this.$set(editorFile, 'uploadStatus', 'failed');
          throw error;
        },
      );
    },
    insertionOrder() {
      if (!this.comic || this.comic.pages.length === 0) {
        return 1;
      }
      const matched = this.comic.pages.filter(
        page => page.id === this.insertPageId,
      );
      if (matched.length === 0) {
        return this.comic.pages.length + 1;
      }
      return this.insertMode === 'before'
        ? matched[0].order
        : matched[0].order + 1;
    },
    addPages() {
      if (this.editorFiles.length === 0 || this.editorSaving) {
        return;
      }
      this.editorSaving = true;
      this.uploadEditorFiles().then(
        (responses) => {
          const startOrder = this.insertionOrder();
          const pages = responses.map(
            (resp, index) => ({
              image_by_id: resp.data.id,
              order: startOrder + index,
            }),
          );
          return API.Comic.saveChanges(
            this.comic.id,
            { pages_to_add: pages },
          );
        },
      ).then(
        () => {
          this.clearEditorFiles();
          this.editorSaving = false;
          this.fetchComic();
        },
        () => {
          this.editorSaving = false;
        },
      );
    },
    removePage(page) {
      API.Comic.saveChanges(
        this.comic.id,
        { pages_to_remove: [page.id] },
      ).then(() => this.fetchComic());
    },
    movePage(page, order) {
      if (order < 1 || order > this.comic.pages.length) {
        return;
      }
      API.Comic.saveChanges(
        this.comic.id,
        { pages_to_reorder: [{ id: page.id, order }] },
      ).then(() => this.fetchComic());
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../components/utils/motion-mixins';
.comic-reader {
  max-width: min(96vw, 1180px);
}
.reader-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.12);
}
.reader-actions,
.page-tools {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}
.reader-head h1 {
  margin: 0;
  color: #22313f;
  font-size: 1.65rem;
  font-weight: 800;
}
.reader-head p {
  margin: 0.35rem 0 0;
  color: #64748b;
}
.reader-description {
  max-width: 760px;
  margin-top: 0.65rem;
  color: #475569;
  font-size: 0.96rem;
  line-height: 1.55;
  white-space: pre-wrap;
}
.reader-description ::v-deep a {
  color: #1f6feb;
  font-weight: 700;
}
.reader-source-row {
  display: flex;
  min-width: 0;
  align-items: center;
  margin-top: 0.5rem;
}
.reader-source-row.is-warning {
  width: fit-content;
  padding: 0.22rem 0.5rem;
  border: 1px solid color-mix(in srgb, #8a6d1d 24%, transparent);
  border-radius: var(--radius-sm);
  color: #8a6d1d;
  background: color-mix(in srgb, #fff8dc 78%, transparent);
  font-size: 0.8rem;
  font-weight: 750;
}
.reader-tags {
  margin-top: 0.55rem;
}
.comic-editor {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
}
.editor-save-button {
  margin-bottom: 1rem;
}
.reader-pages {
  display: grid;
  gap: 1rem;
}
.reader-page {
  position: relative;
  margin: 0;
  overflow: hidden;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #f8fafc;
  text-align: center;
}
.page-tools {
  flex-wrap: wrap;
  padding: 0.5rem;
  background: #fff;
}
.reader-page img {
  display: block;
  width: 100%;
  max-height: 88vh;
  object-fit: contain;
  filter: blur(1px);
  transition: filter .2s ease;
}
.reader-page img.is-original {
  filter: none;
}
.reader-page figcaption {
  padding: 0.65rem 0.85rem;
  color: #64748b;
  background: #fff;
  text-align: left;
}
.read-teaser {
  position: relative;
  height: clamp(120px, 18vw, 210px);
  margin-top: 1rem;
  overflow: hidden;
  border: 1px solid rgba(126, 87, 194, 0.26);
  border-radius: 8px;
  cursor: pointer;
  background: #111827;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.read-teaser::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(17, 24, 39, 0.08),
    rgba(17, 24, 39, 0.74)
  );
}
.read-teaser img {
  display: block;
  width: 100%;
  height: 300%;
  object-fit: cover;
  object-position: top center;
  filter: blur(3px);
  transform: scale(1.02);
}
.read-teaser .button {
  position: absolute;
  z-index: 1;
  top: 50%;
  left: 50%;
  min-width: 9rem;
  border-radius: 999px;
  transform: translate(-50%, -50%);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.24);
}
.comic-full-reader {
  position: fixed;
  z-index: calc(var(--z-modal, 140) + 80);
  inset: 0;
  overflow-x: hidden;
  overflow-y: auto;
  -ms-overflow-style: none;
  scrollbar-width: none;
  color: #f8fafc;
  background: #080b12;
  overscroll-behavior: contain;
  touch-action: pan-y;
  -webkit-overflow-scrolling: touch;
}
.comic-full-reader::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
.full-reader-bar {
  position: sticky;
  z-index: 2;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem clamp(1rem, 3vw, 2rem);
  background: rgba(8, 11, 18, 0.86);
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.34);
}
.full-reader-bar strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 1rem;
}
.full-reader-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 0.65rem;
}
.full-reader-page-count {
  padding: 0.32rem 0.62rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
  font-weight: 800;
}
.full-reader-pages {
  display: grid;
  gap: clamp(1.15rem, 2.8vw, 2.2rem);
  width: min(100%, 1120px);
  margin: 0 auto;
  padding: clamp(1rem, 3vw, 2.5rem);
}
.full-reader-page {
  position: relative;
  margin: 0;
  min-height: 160px;
  overflow: hidden;
  border-radius: 8px;
  background: #111827;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.34);
}
.full-reader-page img {
  display: block;
  width: 100%;
  max-height: none;
  object-fit: contain;
}
.button {
  border-radius: 7px;
  font-weight: 700;
}
@media screen and (max-width: 542px) {
  .reader-head,
  .reader-actions {
    display: block;
  }
  .reader-head .button,
  .reader-actions .button {
    width: 100%;
    margin-top: 1rem;
  }
  .full-reader-bar {
    padding: 0.75rem;
  }
  .full-reader-actions {
    gap: 0.4rem;
  }
  .full-reader-page-count {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
  .full-reader-pages {
    gap: 0.8rem;
    padding: 0.75rem;
  }
}


/* T6 reader actual toolbar and immersive polish */
.comic-reader-page .section {
  padding-top: var(--space-lg, 24px);
  background: transparent;
}

.reader-head,
.comic-editor,
.reader-page {
  border: 1px solid var(--color-border-soft, var(--line-soft, #e7ebf2));
  border-radius: var(--radius-card, 22px);
  background: var(--color-surface-card, var(--surface-card, #fff));
  box-shadow: var(--shadow-card, 0 18px 50px rgba(15, 23, 42, 0.14));
}

.reader-head {
  position: relative;
  top: auto;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.reader-head h1 {
  color: var(--color-text-primary, var(--text-strong, #22313f));
}

.reader-head p,
.reader-description,
.reader-page figcaption {
  color: var(--color-text-muted, var(--text-muted, #64748b));
}

.reader-source-row.is-warning {
  color: #8a6d1d;
  background: color-mix(in srgb, #fff8dc 78%, transparent);
}

.page-tools,
.reader-page figcaption {
  background: var(--color-surface-card, var(--surface-card, #fff));
}

.reader-page,
.full-reader-page {
  border-radius: var(--radius-card, 22px);
}

.reader-page img,
.full-reader-page img {
  border-radius: var(--radius-lg, 18px);
}

.comic-full-reader:focus {
  outline: none;
}

.full-reader-bar {
  background: color-mix(in srgb, #080b12 86%, var(--accent-strong, #7e57c2) 14%);
}

.full-reader-page {
  box-shadow: var(--shadow-card, 0 18px 50px rgba(0, 0, 0, 0.34));
}

/* T6 reader polish */
.comic-reader,
.comic-reader-page,
.reader-shell,
.reader-container {
  min-height: 100vh;
  color: var(--color-text-primary, #111827);
  background: transparent;
}

.reader-toolbar,
.comic-reader-toolbar,
.chapter-toolbar,
.chapter-nav {
  position: sticky;
  top: var(--nav-height, 72px);
  z-index: var(--z-sticky, 20);
  border: 1px solid var(--color-border-soft, rgba(148, 163, 184, 0.22));
  border-radius: var(--radius-card, 22px);
  background: color-mix(in srgb, var(--color-surface-card, #fff) 88%, transparent);
  box-shadow: var(--shadow-card, 0 18px 50px rgba(15, 23, 42, 0.12));
  backdrop-filter: blur(18px);
}

.comic-reader img,
.reader-shell img,
.reader-container img {
  border-radius: var(--radius-lg, 18px);
  box-shadow: var(--shadow-card, 0 18px 50px rgba(15, 23, 42, 0.14));
}

@media (max-width: 760px) {
  .reader-toolbar,
  .comic-reader-toolbar,
  .chapter-toolbar,
  .chapter-nav {
    top: var(--space-sm, 12px);
    border-radius: var(--radius-lg, 18px);
  }
}

/* R6 reader info card non-floating */
.reader-head {
  position: relative;
  top: auto;
  z-index: 1;
}

/* R44 comic reader controls and editor system */
.comic-reader-page {
  --comic-editor-danger: #c43f62;
  --comic-editor-danger-soft: color-mix(in srgb, var(--comic-editor-danger) 12%, transparent);
}

.reader-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.reader-action-button,
.comic-editor-button,
.page-tool-button {
  position: relative;
  overflow: hidden;
  gap: var(--space-xs);
  min-height: 42px;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: var(--color-surface-1);
  box-shadow: none;
  font-weight: 850;
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
}

.reader-action-button::before,
.comic-editor-button::before {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    110deg,
    transparent 24%,
    color-mix(in srgb, var(--color-accent-text) 32%, transparent) 50%,
    transparent 76%
  );
  content: '';
  opacity: 0;
  pointer-events: none;
  transform: translateX(-110%);
  transition:
    opacity var(--motion-duration-fast) var(--motion-ease-standard),
    transform var(--motion-duration-card) var(--motion-ease-emphasized);
}

.reader-action-button:hover:not(:disabled),
.reader-action-button:focus-visible,
.comic-editor-button:hover:not(:disabled),
.comic-editor-button:focus-visible,
.page-tool-button:hover:not(:disabled),
.page-tool-button:focus-visible {
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  box-shadow: var(--shadow-xs);
  transform: translateY(-2px);
}

.reader-action-button:hover:not(:disabled)::before,
.reader-action-button:focus-visible::before,
.comic-editor-button:hover:not(:disabled)::before,
.comic-editor-button:focus-visible::before {
  opacity: 1;
  transform: translateX(110%);
}

.reader-action-button:focus-visible,
.comic-editor-button:focus-visible,
.page-tool-button:focus-visible,
.comic-editor-file__remove:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.reader-action-button ::v-deep .icon,
.comic-editor-button ::v-deep .icon,
.page-tool-button ::v-deep .icon {
  transition: transform var(--motion-duration-standard) var(--motion-ease-spring);
}

.reader-action-button:hover:not(:disabled) ::v-deep .icon,
.comic-editor-button:hover:not(:disabled) ::v-deep .icon,
.page-tool-button:hover:not(:disabled) ::v-deep .icon {
  transform: scale(1.12) rotate(-4deg);
}

.reader-action-button--primary,
.comic-editor-add-button {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  text-shadow: var(--color-accent-text-shadow);
  background: var(--color-accent-fill);
  box-shadow: 0 10px 24px var(--color-theme-glow);
}

.reader-action-button--primary:hover:not(:disabled),
.reader-action-button--primary:focus-visible,
.comic-editor-add-button:hover:not(:disabled),
.comic-editor-add-button:focus-visible {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  background: var(--color-accent-fill-hover);
  box-shadow: 0 14px 30px var(--color-theme-glow-strong);
}

.reader-action-button--secondary.is-active {
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  box-shadow: inset 0 0 0 1px var(--color-accent-border);
}

.reader-action-button:disabled,
.comic-editor-button:disabled,
.page-tool-button:disabled {
  cursor: not-allowed;
  opacity: 0.52;
  transform: none;
}

.comic-editor-reveal-enter-active,
.comic-editor-reveal-leave-active {
  overflow: hidden;
  transition:
    opacity var(--motion-duration-standard) var(--motion-ease-standard),
    transform var(--motion-duration-card) var(--motion-ease-emphasized),
    max-height var(--motion-duration-card) var(--motion-ease-emphasized),
    margin var(--motion-duration-standard) var(--motion-ease-standard),
    padding var(--motion-duration-standard) var(--motion-ease-standard);
}

.comic-editor-reveal-enter,
.comic-editor-reveal-leave-to {
  max-height: 0;
  margin-bottom: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
  transform: translateY(-14px) scale(0.985);
}

.comic-editor-reveal-enter-to,
.comic-editor-reveal-leave {
  max-height: 1600px;
  opacity: 1;
  transform: translateY(0) scale(1);
}

.comic-editor {
  position: relative;
  overflow: hidden;
  margin-bottom: var(--space-lg);
  padding: var(--space-lg);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-lg);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 320px),
    color-mix(in srgb, var(--color-surface-card) 92%, transparent);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px) saturate(1.04);
}

.comic-editor::before {
  position: absolute;
  top: 0;
  right: var(--space-lg);
  left: var(--space-lg);
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-accent-border), transparent);
  content: '';
}

.comic-editor__form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.72fr);
  gap: var(--space-sm) var(--space-md);
}

.comic-editor__tags {
  grid-column: 1 / -1;
}

.comic-editor ::v-deep .field {
  margin-bottom: var(--space-md);
}

.comic-editor ::v-deep .label {
  margin-bottom: var(--space-xs);
  color: var(--color-text-strong);
  font-size: 0.82rem;
  font-weight: 900;
}

.comic-editor ::v-deep .input,
.comic-editor ::v-deep .textarea,
.comic-editor ::v-deep .taginput-container,
.comic-editor ::v-deep .select select {
  border-color: var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-1) 84%, transparent);
  box-shadow: none;
  font-size: 0.9rem;
  transition:
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard);
}

.comic-editor ::v-deep .textarea {
  min-height: 120px;
  resize: vertical;
}

.comic-editor ::v-deep .input::placeholder,
.comic-editor ::v-deep .textarea::placeholder,
.comic-editor ::v-deep .taginput-container input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.72;
}

.comic-editor ::v-deep .input:focus,
.comic-editor ::v-deep .textarea:focus,
.comic-editor ::v-deep .taginput-container.is-focusable:focus-within,
.comic-editor ::v-deep .select select:focus {
  border-color: var(--color-accent-border);
  background: var(--color-surface-1);
  box-shadow: var(--focus-ring);
}

.comic-editor ::v-deep .taginput .tag {
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-pill);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  font-weight: 800;
}

.comic-editor ::v-deep .autocomplete .dropdown-content {
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: var(--color-surface-card);
  box-shadow: var(--shadow-floating);
}

.comic-editor ::v-deep .autocomplete .dropdown-item {
  color: var(--color-text-strong);
}

.comic-editor ::v-deep .autocomplete .dropdown-item:hover,
.comic-editor ::v-deep .autocomplete .dropdown-item.is-hovered {
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
}

.comic-editor__detail-actions,
.comic-editor__add-actions {
  display: flex;
  justify-content: flex-end;
}

.comic-editor__divider {
  height: 1px;
  margin: var(--space-md) 0 var(--space-lg);
  background: linear-gradient(90deg, transparent, var(--color-line-soft) 10% 90%, transparent);
}

.comic-editor__insert-controls {
  display: grid;
  grid-template-columns: minmax(116px, auto) minmax(0, 1fr);
  gap: var(--space-md);
  align-items: center;
  margin-bottom: var(--space-md);
  padding: var(--space-sm);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-surface-2) 76%, transparent);
}

.comic-editor__insert-label {
  align-self: center;
  margin: 0;
  color: var(--color-text-strong);
  font-size: 0.82rem;
  font-weight: 900;
  line-height: 1.25;
}

.comic-editor__insert-selects {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-xs);
  width: 100%;
}

.editor-save-button {
  margin-bottom: 0;
}

.comic-file-picker {
  display: flex;
  width: 100%;
  min-width: 0;
  align-items: center;
  gap: var(--space-sm);
}

.comic-file-picker__input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  white-space: nowrap;
}

.comic-file-picker__button {
  flex: 0 0 auto;
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
}

.comic-file-picker__count {
  min-width: 0;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  font-weight: 800;
}

.comic-editor-files {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-xs);
  margin: calc(var(--space-xs) * -1) 0 var(--space-md);
}

.comic-editor-file {
  display: grid;
  grid-template-columns: 62px minmax(0, 1fr) 34px;
  min-width: 0;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-2) 82%, transparent);
  box-shadow: var(--shadow-xs);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
  animation: comic-editor-file-enter var(--motion-duration-card) var(--motion-ease-emphasized) both;
}

.comic-editor-file:hover {
  border-color: var(--color-accent-border);
  background: color-mix(in srgb, var(--color-accent-soft) 54%, var(--color-surface-2));
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.comic-editor-file__preview {
  width: 62px;
  height: 62px;
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-xs);
  background: var(--color-surface-1);
}

.comic-editor-file__preview img,
.comic-reader .comic-editor-file__preview img {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 0;
  object-fit: cover;
  box-shadow: none;
}

.comic-editor-file__copy {
  display: grid;
  min-width: 0;
  gap: var(--space-2xs);
}

.comic-editor-file__copy strong {
  overflow: hidden;
  color: var(--color-text-strong);
  font-size: 0.82rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comic-editor-file__copy span {
  color: var(--color-text-muted);
  font-size: 0.74rem;
  font-weight: 750;
}

.comic-editor-file__remove {
  display: inline-grid;
  width: 34px;
  height: 34px;
  padding: 0;
  place-items: center;
  border: 1px solid transparent;
  border-radius: var(--radius-xs);
  color: var(--color-text-muted);
  background: transparent;
  cursor: pointer;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-spring),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}

.comic-editor-file__remove:hover {
  border-color: color-mix(in srgb, var(--comic-editor-danger) 34%, transparent);
  color: var(--comic-editor-danger);
  background: var(--comic-editor-danger-soft);
  transform: scale(1.06);
}

.comic-editor-add-button {
  min-width: 150px;
}

.page-tools {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  padding: var(--space-xs);
  border-bottom: 1px solid var(--color-line-soft);
  background: color-mix(in srgb, var(--color-surface-2) 88%, transparent);
}

.page-tool-button {
  min-height: 34px;
  padding: var(--space-2xs) var(--space-xs);
  border-radius: var(--radius-xs);
  font-size: 0.76rem;
}

.page-tool-button--danger {
  border-color: color-mix(in srgb, var(--comic-editor-danger) 30%, transparent);
  color: var(--comic-editor-danger);
  background: var(--comic-editor-danger-soft);
}

.page-tool-button--danger:hover:not(:disabled),
.page-tool-button--danger:focus-visible {
  border-color: var(--comic-editor-danger);
  color: var(--comic-editor-danger);
  background: color-mix(in srgb, var(--comic-editor-danger) 18%, transparent);
}

@keyframes comic-editor-file-enter {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media screen and (max-width: 760px) {
  .comic-editor {
    padding: var(--space-md);
    border-radius: var(--radius-md);
  }

  .comic-editor__form-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .comic-editor__tags {
    grid-column: auto;
  }

  .comic-editor__insert-controls {
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-xs);
  }

  .comic-editor-files {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media screen and (max-width: 542px) {
  .reader-actions {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    width: 100%;
    margin-top: var(--space-md);
  }

  .reader-head .reader-action-button,
  .reader-actions .reader-action-button {
    width: 100%;
    margin-top: 0;
  }

  .comic-file-picker {
    align-items: stretch;
    flex-direction: column;
  }

  .comic-editor__insert-selects {
    grid-template-columns: minmax(0, 1fr);
  }

  .comic-file-picker__button,
  .comic-editor__detail-actions .comic-editor-button,
  .comic-editor__add-actions .comic-editor-button {
    width: 100%;
  }

  .comic-file-picker__count {
    text-align: center;
  }

  .comic-editor-file {
    grid-template-columns: 54px minmax(0, 1fr) 34px;
  }

  .comic-editor-file__preview {
    width: 54px;
    height: 54px;
  }
}

html[data-motion='reduce'] .reader-action-button,
html[data-motion='reduce'] .comic-editor-button,
html[data-motion='reduce'] .page-tool-button,
html[data-motion='reduce'] .comic-editor-file,
html[data-motion='reduce'] .comic-editor-file__remove,
html[data-motion='reduce'] .comic-editor__insert-controls,
html[data-motion='reduce'] .comic-editor-reveal-enter-active,
html[data-motion='reduce'] .comic-editor-reveal-leave-active {
  animation: none;
  transition: none;
}
</style>
