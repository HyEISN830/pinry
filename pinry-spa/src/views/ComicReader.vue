<template>
  <div class="comic-reader-page">
    <PHeader></PHeader>
    <section class="section">
      <div class="container comic-reader">
        <div class="reader-head" v-if="comic">
          <div>
            <h1>{{ comic.title }}</h1>
            <p>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</p>
          </div>
          <div class="reader-actions">
            <button
              class="button is-primary"
              type="button"
              :disabled="loadingAll"
              @click="loadAllPages">
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
            <figcaption v-if="page.caption">{{ page.caption }}</figcaption>
          </figure>
        </div>
        <loadingSpinner :show="loading"></loadingSpinner>
      </div>
    </section>
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
      insertMode: 'after',
      insertPageId: null,
      loadedPages: {},
      loading: true,
      loadingAll: false,
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
      return API.Pin.fetchOriginalImage(page.image.id).then(
        (response) => {
          if (!response.ok) {
            throw new Error('Failed to load comic page');
          }
          return response.blob();
        },
      ).then(
        (blob) => {
          const cachedImage = cacheImage(page.image.id, blob);
          if (cachedImage) {
            this.$set(this.loadedPages, page.id, cachedImage.objectUrl);
          }
          return cachedImage;
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
.comic-editor {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
}
.reader-pages {
  display: grid;
  gap: 1rem;
}
.reader-page {
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
}
</style>
