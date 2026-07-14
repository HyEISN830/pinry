<template>
  <div class="comic-create-modal">
    <div class="modal-card create-modal-card create-comic-card">
      <header class="modal-card-head create-modal-head">
        <div class="create-modal-title-block">
          <span class="create-modal-icon" aria-hidden="true">
            <b-icon icon="book-plus" custom-size="mdi-22px"></b-icon>
          </span>
          <div>
            <span class="create-modal-kicker">{{ $t('comicLink') }}</span>
            <p class="modal-card-title">{{ $t("NewComicTitle") }}</p>
          </div>
        </div>
        <button
          class="create-modal-close"
          type="button"
          :title="$t('closeButton')"
          :aria-label="$t('closeButton')"
          @click="$parent.close()">
          <b-icon icon="close" custom-size="mdi-20px"></b-icon>
        </button>
      </header>
      <section class="modal-card-body create-modal-body">
        <div class="create-comic-form">
        <b-field :label="$t('comicTitleLabel')">
          <b-input
            v-model="form.title"
            maxlength="128"
            :placeholder="$t('comicTitlePlaceholder')">
          </b-input>
        </b-field>
        <b-field :label="$t('descriptionLabel')">
          <b-input
            type="textarea"
            v-model="form.description"
            maxlength="1024">
          </b-input>
        </b-field>
        <b-field :label="$t('imageSourceLabel')">
          <b-input
            v-model="form.referer"
            maxlength="2048"
            :placeholder="$t('pinCreateModalImageSourcePlaceholder')">
          </b-input>
        </b-field>
        <b-field :label="$t('tagsLabel')">
          <b-taginput
            ref="tagInput"
            v-model="form.tags"
            :data="filteredTagOptions"
            autocomplete
            allow-new
            field="name"
            :placeholder="$t('pinCreateModalImageTagsPlaceholder')"
            @typing="getFilteredTags">
            <template slot="empty">{{ $t("noResultsFound") }}</template>
          </b-taginput>
        </b-field>
        <b-field :label="$t('privacyOptionLabel')">
          <b-checkbox v-model="form.private">
            {{ $t("isPrivateCheckbox") }}
          </b-checkbox>
        </b-field>
        <b-field :label="$t('comicPagesLabel')">
          <input
            ref="comicFileInput"
            class="input"
            type="file"
            multiple
            accept="image/*"
            @change="onFilesSelected">
        </b-field>
        <div class="page-list" v-if="files.length > 0">
          <article
            class="page-row"
            v-for="(file, index) in files"
            :key="file.id">
            <div class="page-row__preview">
              <img :src="file.previewUrl" :alt="file.name">
              <span>{{ index + 1 }}</span>
            </div>
            <div class="page-row__body">
              <strong :title="file.name">{{ file.name }}</strong>
              <small>{{ formatFileSize(file.size) }} · {{ fileDimensions(file) }}</small>
              <ComicUploadMiniProgress
                :status="file.uploadStatus"
                :progress="file.uploadProgress">
              </ComicUploadMiniProgress>
            </div>
            <button
              class="page-row__remove"
              type="button"
              :disabled="saving"
              :title="$t('comicRemoveSelectedFile')"
              :aria-label="$t('comicRemoveSelectedFile')"
              @click="removeFile(file.id)">
              <b-icon icon="close" custom-size="mdi-18px"></b-icon>
            </button>
          </article>
        </div>
        </div>
      </section>
      <footer class="modal-card-foot create-modal-foot">
        <button
          class="button create-modal-cancel"
          type="button"
          @click="$parent.close()">
          {{ $t("closeButton") }}
        </button>
        <button
          class="button is-primary create-modal-submit"
          :class="{ 'is-loading': saving }"
          :disabled="!canSave"
          @click="createComic">
          {{ $t("comicCreateButton") }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
import API from '../api';
import ComicUploadMiniProgress from './ComicUploadMiniProgress.vue';

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
  name: 'ComicCreateModal',
  components: { ComicUploadMiniProgress },
  props: {
    username: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      files: [],
      fileSequence: 0,
      form: {
        title: '',
        description: '',
        referer: '',
        tags: [],
        private: false,
      },
      filteredTagOptions: [],
      saving: false,
      tagOptions: [],
    };
  },
  created() {
    this.fetchTagList();
  },
  beforeDestroy() {
    this.clearFiles();
  },
  computed: {
    canSave() {
      return this.form.title.trim().length > 0
        && this.files.length > 0
        && !this.saving;
    },
  },
  methods: {
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
      this.form.tags.forEach(
        (tag) => {
          splitTags(tag).forEach(
            item => tags.push(item),
          );
        },
      );
      this.form.tags = uniqueTags(tags);
    },
    absorbTypedTags(text) {
      if (!/[,\uFF0C]/.test(text)) {
        return text;
      }
      const parts = text.split(/[,\uFF0C]/);
      const remainingText = parts.pop();
      const tags = splitTags(parts.join(','));
      this.form.tags = uniqueTags(
        this.form.tags.concat(tags),
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
    onFilesSelected(event) {
      const selectedFiles = Array.from(event.target.files || []);
      this.clearFiles();
      this.files = selectedFiles.map(
        (file) => {
          this.fileSequence += 1;
          return {
            id: this.fileSequence,
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
      this.files.forEach(this.readFileDimensions);
      const input = this.$refs.comicFileInput;
      if (input) {
        input.value = '';
      }
    },
    readFileDimensions(file) {
      const image = new Image();
      image.onload = () => {
        const matched = this.files.find(item => item.id === file.id);
        if (!matched) {
          return;
        }
        this.$set(matched, 'width', image.naturalWidth || null);
        this.$set(matched, 'height', image.naturalHeight || null);
      };
      image.src = file.previewUrl;
    },
    revokeFile(file) {
      if (file && file.previewUrl) {
        window.URL.revokeObjectURL(file.previewUrl);
      }
    },
    clearFiles() {
      this.files.forEach(this.revokeFile);
      this.files = [];
      const input = this.$refs.comicFileInput;
      if (input) {
        input.value = '';
      }
    },
    removeFile(fileId) {
      const matched = this.files.find(file => file.id === fileId);
      this.revokeFile(matched);
      this.files = this.files.filter(file => file.id !== fileId);
    },
    formatFileSize(bytes) {
      const units = ['B', 'KB', 'MB', 'GB'];
      let size = Number(bytes) || 0;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex += 1;
      }
      const precision = unitIndex === 0 || size >= 10 ? 0 : 1;
      return `${size.toFixed(precision)} ${units[unitIndex]}`;
    },
    fileDimensions(file) {
      if (file.width && file.height) {
        return `${file.width} \u00d7 ${file.height} px`;
      }
      return this.$t('imageDimensionsReading');
    },
    onFileUploadProgress(file, event) {
      const loaded = Number(event.loaded);
      const total = Number(event.total);
      if (!Number.isFinite(loaded) || !Number.isFinite(total) || total <= 0) {
        this.$set(file, 'uploadProgress', null);
        return;
      }
      this.$set(
        file,
        'uploadProgress',
        Math.min(99, Math.max(0, Math.round((loaded / total) * 100))),
      );
    },
    uploadFiles(index = 0, responses = []) {
      if (index >= this.files.length) {
        return Promise.resolve(responses);
      }
      const file = this.files[index];
      if (file.uploadedResponse) {
        responses.push(file.uploadedResponse);
        return this.uploadFiles(index + 1, responses);
      }
      this.$set(file, 'uploadStatus', 'uploading');
      return API.Pin.uploadImage(
        file.file,
        event => this.onFileUploadProgress(file, event),
      ).then(
        (resp) => {
          this.$set(file, 'uploadedResponse', resp);
          this.$set(file, 'uploadStatus', 'complete');
          this.$set(file, 'uploadProgress', 100);
          responses.push(resp);
          return this.uploadFiles(index + 1, responses);
        },
        (error) => {
          this.$set(file, 'uploadStatus', 'failed');
          throw error;
        },
      );
    },
    createComic() {
      if (!this.canSave) {
        return;
      }
      this.saving = true;
      const finish = () => {
        this.saving = false;
      };
      this.normalizeTags();
      this.uploadFiles().then(
        (responses) => {
          const pages = responses.map(
            (resp, index) => ({
              image_by_id: resp.data.id,
              order: index + 1,
            }),
          );
          return API.Comic.create({
            title: this.form.title.trim(),
            description: this.form.description,
            referer: this.form.referer,
            tags: this.form.tags,
            private: this.form.private,
            pages_to_add: pages,
          });
        },
      ).then(
        (resp) => {
          this.$emit('comicCreated', resp.data);
          this.$parent.close();
          finish();
        },
      ).catch(
        () => {
          this.$buefy.toast.open({
            type: 'is-danger',
            message: this.$t('comicCreateFailed'),
          });
          finish();
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.create-comic-card {
  --create-modal-width: 760px;
  --comic-create-danger: #c43f62;
}
.create-comic-form { display: grid; gap: var(--space-2xs); }
.page-list {
  display: grid;
  max-height: 300px;
  overflow: auto;
  gap: var(--space-xs);
  padding: var(--space-xs);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-surface-2) 76%, transparent);
}
.page-row {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr) 36px;
  min-width: 0;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-card) 86%, transparent);
  box-shadow: var(--shadow-xs);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
}
.page-row:hover {
  border-color: var(--color-accent-border);
  background: color-mix(in srgb, var(--color-accent-soft) 46%, var(--color-surface-card));
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
.page-row__preview {
  position: relative;
  width: 68px;
  height: 68px;
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-xs);
  background: var(--color-surface-1);
}
.page-row__preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.page-row__preview > span {
  position: absolute;
  top: var(--space-2xs);
  left: var(--space-2xs);
  display: inline-grid;
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  place-items: center;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-pill);
  color: var(--color-accent-text);
  background: var(--color-accent-strong);
  box-shadow: 0 4px 12px var(--color-theme-glow-strong);
  font-size: 0.7rem;
  font-weight: 900;
  user-select: none;
}
.page-row strong {
  min-width: 0;
  overflow: hidden;
  color: var(--color-text-strong);
  text-overflow: ellipsis;
  white-space: nowrap;
}
.page-row__body {
  display: grid;
  min-width: 0;
  flex: 1 1 auto;
  gap: var(--space-xs);
}
.page-row__body small {
  color: var(--color-text-muted);
  font-size: 0.73rem;
  font-weight: 750;
}
.page-row__remove {
  display: inline-grid;
  width: 36px;
  height: 36px;
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
.page-row__remove:hover:not(:disabled),
.page-row__remove:focus-visible {
  border-color: color-mix(in srgb, var(--comic-create-danger) 36%, transparent);
  color: var(--comic-create-danger);
  background: color-mix(in srgb, var(--comic-create-danger) 10%, transparent);
  transform: scale(1.06);
}
.page-row__remove:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
.page-row__remove:disabled {
  cursor: not-allowed;
  opacity: 0.46;
}
@media screen and (max-width: 520px) {
  .page-row {
    grid-template-columns: 58px minmax(0, 1fr) 34px;
    gap: var(--space-xs);
  }
  .page-row__preview {
    width: 58px;
    height: 58px;
  }
  .page-row__remove {
    width: 34px;
    height: 34px;
  }
}
html[data-motion='reduce'] .page-row,
html[data-motion='reduce'] .page-row__remove {
  transition: none;
}
</style>
