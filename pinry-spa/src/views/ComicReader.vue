<template>
  <div class="comic-reader-page">
    <PHeader></PHeader>
    <section class="section">
      <div class="container comic-reader">
        <div class="reader-head" v-if="comic">
          <div>
            <h1>{{ comic.title }}</h1>
            <p>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</p>
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
          <b-field :label="$t('imageSourceLabel')">
            <b-input
              v-model="editForm.referer"
              maxlength="2048"
              :placeholder="$t('pinCreateModalImageSourcePlaceholder')">
            </b-input>
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
            v-for="page in comic.pages"
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
            <div class="page-progress" v-if="pageLoading[page.id]">
              <span>{{ pageProgressText(page) }}</span>
              <progress
                v-if="pageProgress[page.id] !== null"
                class="progress is-info"
                :value="pageProgress[page.id]"
                max="100">
                {{ pageProgress[page.id] }}%
              </progress>
            </div>
            <figcaption v-if="page.caption">{{ page.caption }}</figcaption>
          </figure>
        </div>
        <loadingSpinner :show="loading"></loadingSpinner>
      </div>
    </section>
    <div class="comic-full-reader" v-if="fullReaderOpen">
      <div class="full-reader-bar">
        <strong>{{ comic.title }}</strong>
        <button
          class="button is-light"
          type="button"
          @click="fullReaderOpen = false">
          {{ $t("closeButton") }}
        </button>
      </div>
      <div class="full-reader-pages">
        <figure
          class="full-reader-page"
          v-for="page in comic.pages"
          :key="`full-${page.id}`">
          <img
            :src="pageUrl(page)"
            :alt="`${comic.title} ${page.order}`"
            :class="{ 'is-original': loadedPages[page.id] }">
          <div class="page-progress" v-if="pageLoading[page.id]">
            <span>{{ pageProgressText(page) }}</span>
            <progress
              v-if="pageProgress[page.id] !== null"
              class="progress is-info"
              :value="pageProgress[page.id]"
              max="100">
              {{ pageProgress[page.id] }}%
            </progress>
          </div>
        </figure>
      </div>
    </div>
  </div>
</template>

<script>
import API from '../components/api';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import {
  cacheImage,
  getCachedImage,
} from '../components/utils/originalImageCache';

export default {
  name: 'ComicReader',
  components: {
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
        referer: '',
      },
      fullReaderOpen: false,
      insertMode: 'after',
      insertPageId: null,
      loadedPages: {},
      loading: true,
      loadingAll: false,
      pageLoading: {},
      pageProgress: {},
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    isOwner() {
      return this.user.loggedIn
        && this.comic
        && this.comic.submitter.username === this.user.meta.username;
    },
  },
  created() {
    this.fetchUser();
    this.fetchComic();
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
          this.editForm.referer = this.comic.referer || '';
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
      return page.image.thumbnail.image;
    },
    loadPageOriginal(page) {
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
      this.fullReaderOpen = true;
      this.loadAllPages();
    },
    pageProgressText(page) {
      if (this.pageProgress[page.id] === null) {
        return this.$t('imageLoadingText');
      }
      return `${this.pageProgress[page.id]}%`;
    },
    saveComicDetails() {
      if (this.detailSaving) {
        return;
      }
      this.detailSaving = true;
      API.Comic.saveChanges(
        this.comic.id,
        { referer: this.editForm.referer },
      ).then(
        (resp) => {
          this.comic = resp.data;
          this.editForm.referer = this.comic.referer || '';
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
    isWebUrl(url) {
      return /^https?:\/\//i.test((url || '').trim());
    },
    sourceText(url) {
      return (url || '').trim();
    },
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
.page-progress {
  position: absolute;
  right: 12px;
  bottom: 12px;
  left: 12px;
  padding: 0.65rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 8px;
  color: #fff;
  background: rgba(15, 23, 42, 0.58);
  backdrop-filter: blur(8px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.24);
  text-align: left;
}
.page-progress span {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.85rem;
  font-weight: 800;
}
.page-progress .progress {
  height: 0.45rem;
  margin-bottom: 0;
}
.comic-full-reader {
  position: fixed;
  z-index: 80;
  inset: 0;
  overflow: auto;
  color: #f8fafc;
  background: #080b12;
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
  .full-reader-pages {
    gap: 0.8rem;
    padding: 0.75rem;
  }
  .page-progress {
    right: 8px;
    bottom: 8px;
    left: 8px;
  }
}
</style>
