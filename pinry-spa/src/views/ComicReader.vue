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
            <div class="reader-source" v-if="hasSource(comic.referer)">
              <a
                v-if="isWebUrl(comic.referer)"
                :href="comic.referer"
                target="_blank">
                {{ $t("sourceLink") }}
              </a>
              <span v-else>{{ sourceText(comic.referer) }}</span>
            </div>
            <div class="reader-source is-warning" v-else>
              {{ $t("missingSourceNotice") }}
            </div>
            <div class="reader-tags" v-if="comic.tags && comic.tags.length > 0">
              <router-link
                v-for="tag in comic.tags"
                :key="tag"
                :to="{ name: 'tag', params: { tag } }">
                {{ tag }}
              </router-link>
            </div>
          </div>
          <div class="reader-actions">
            <button
              class="button is-primary"
              type="button"
              :disabled="loadingAll"
              @click="openFullReader">
              {{ loadingAll ? $t("imageLoadingText") : $t("readFullComicButton") }}
            </button>
            <button
              v-if="isOwner"
              class="button is-light"
              type="button"
              @click="editing = !editing">
              {{ $t("editComicButton") }}
            </button>
          </div>
        </div>
        <div class="comic-editor" v-if="comic && isOwner && editing">
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
          <b-field :label="$t('tagsLabel')">
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
          <button
            class="button is-light editor-save-button"
            type="button"
            :disabled="detailSaving"
            :class="{ 'is-loading': detailSaving }"
            @click="saveComicDetails">
            {{ $t("saveChangesButton") }}
          </button>
          <b-field :label="$t('comicInsertPositionLabel')">
            <b-select v-model="insertPageId">
              <option
                v-for="page in comic.pages"
                :key="page.id"
                :value="page.id">
                {{ page.order }}
              </option>
            </b-select>
            <b-select v-model="insertMode">
              <option value="after">{{ $t("comicInsertAfterLabel") }}</option>
              <option value="before">{{ $t("comicInsertBeforeLabel") }}</option>
            </b-select>
          </b-field>
          <b-field :label="$t('comicPagesLabel')">
            <input
              class="input"
              type="file"
              multiple
              accept="image/*"
              @change="onEditorFilesSelected">
          </b-field>
          <button
            class="button is-primary"
            type="button"
            :disabled="editorFiles.length === 0 || editorSaving"
            :class="{ 'is-loading': editorSaving }"
            @click="addPages">
            {{ $t("comicAddPagesButton") }}
          </button>
        </div>
        <div class="reader-pages" v-if="comic">
          <figure
            class="reader-page"
            v-for="page in visibleReaderPages"
            :key="page.id">
            <div class="page-tools" v-if="isOwner && editing">
              <button
                class="button is-small"
                @click="movePage(page, page.order - 1)">
                {{ $t("moveUpButton") }}
              </button>
              <button
                class="button is-small"
                @click="movePage(page, page.order + 1)">
                {{ $t("moveDownButton") }}
              </button>
              <button
                class="button is-small is-danger"
                @click="removePage(page)">
                {{ $t("removePageButton") }}
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
        <loadingSpinner :show="loading"></loadingSpinner>
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
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import {
  cacheImage,
  getCachedImage,
} from '../components/utils/originalImageCache';
import imageVariant from '../components/utils/imageVariant';
import niceLinks from '../components/utils/niceLinks';

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
    PHeader,
    loadingSpinner,
  },
  data() {
    return {
      comic: null,
      editing: false,
      editorFiles: [],
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
      fullReaderBodyOverflowSnapshot: null,
      fullReaderScrollElement: null,
      fullReaderOpen: false,
      currentFullPageOrder: 1,
      insertMode: 'after',
      insertPageId: null,
      loadedPages: {},
      loading: true,
      loadingAll: false,
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
      this.$set(this.pageLoading, page.id, true);
      this.$set(this.pageProgress, page.id, null);
      return API.Pin.fetchOriginalImage(page.image.id).then(
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
          return cachedImage;
        },
        (error) => {
          this.$set(this.pageLoading, page.id, false);
          throw error;
        },
      );
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
      if (!this.comic || this.loadingAll) {
        return;
      }
      this.loadingAll = true;
      const remainingPages = this.comic.pages.filter(
        page => !this.loadedPages[page.id],
      );
      this.loadPagesSequentially(remainingPages).then(
        () => {
          this.loadingAll = false;
        },
        () => {
          this.loadingAll = false;
        },
      );
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
      if (this.fullReaderBodyOverflowSnapshot !== null) {
        return;
      }
      const { body } = document;
      this.fullReaderBodyOverflowSnapshot = body.style.overflow;
      body.style.overflow = 'hidden';
    },
    unlockFullReaderScroll() {
      if (this.fullReaderBodyOverflowSnapshot === null) {
        return;
      }
      const { body } = document;
      body.style.overflow = this.fullReaderBodyOverflowSnapshot;
      this.fullReaderBodyOverflowSnapshot = null;
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
    onEditorFilesSelected(event) {
      this.editorFiles = Array.from(event.target.files || []);
    },
    uploadEditorFiles(index = 0, responses = []) {
      if (index >= this.editorFiles.length) {
        return Promise.resolve(responses);
      }
      return API.Pin.uploadImage(this.editorFiles[index]).then(
        (resp) => {
          responses.push(resp);
          return this.uploadEditorFiles(index + 1, responses);
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
          this.editorFiles = [];
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
.reader-source {
  display: inline-flex;
  align-items: center;
  margin-top: 0.5rem;
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  color: #7e57c2;
  background: #f5f0ff;
  font-size: 0.9rem;
  font-weight: 700;
}
.reader-source a {
  color: inherit;
}
.reader-source.is-warning {
  color: #8a6d1d;
  background: #fff8dc;
}
.reader-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.55rem;
}
.reader-tags a {
  padding: 0.18rem 0.45rem;
  border-radius: 999px;
  color: #4f46e5;
  background: #eef2ff;
  font-size: 0.82rem;
  font-weight: 800;
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
  color: #f8fafc;
  background: #080b12;
  overscroll-behavior: contain;
  touch-action: pan-y;
  -webkit-overflow-scrolling: touch;
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
  background: radial-gradient(circle at top, var(--theme-glow, rgba(126, 87, 194, 0.14)), transparent 38%), var(--color-page-bg, var(--app-bg, #f6f7fb));
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

.reader-source,
.reader-tags a {
  border-radius: var(--radius-pill, 999px);
  color: var(--accent-strong, #7e57c2);
  background: var(--accent-soft, #f5f0ff);
}

.reader-source.is-warning {
  color: #8a6d1d;
  background: #fff8dc;
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
  background: radial-gradient(circle at top, var(--color-accent-soft, rgba(99, 102, 241, 0.12)), transparent 36%), var(--color-page-bg, #f8fafc);
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
</style>
