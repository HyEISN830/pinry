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
            class="input"
            type="file"
            multiple
            accept="image/*"
            @change="onFilesSelected">
        </b-field>
        <div class="page-list" v-if="files.length > 0">
          <div
            class="page-row"
            v-for="(file, index) in files"
            :key="`${file.name}-${index}`">
            <span>{{ index + 1 }}</span>
            <strong>{{ file.name }}</strong>
          </div>
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
import Loading from '../utils/Loading';

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
  props: {
    username: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      files: [],
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
      this.files = Array.from(event.target.files || []);
    },
    uploadFiles() {
      const uploads = this.files.map(file => API.Pin.uploadImage(file));
      return Promise.all(uploads);
    },
    createComic() {
      if (!this.canSave) {
        return;
      }
      this.saving = true;
      const loading = Loading.open(this);
      const finish = () => {
        this.saving = false;
        loading.close();
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
.create-comic-card { --create-modal-width: 760px; }
.create-comic-form { display: grid; gap: var(--space-2xs); }
.page-list {
  max-height: 240px;
  overflow: auto;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
}
.page-row {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--color-line-soft);
}
.page-row:last-child {
  border-bottom: 0;
}
.page-row span {
  display: inline-grid;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  color: var(--color-accent-strong);
  background: var(--color-accent-soft);
  font-size: 0.8rem;
  font-weight: 900;
}
.page-row strong {
  min-width: 0;
  overflow: hidden;
  color: var(--color-text-strong);
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
