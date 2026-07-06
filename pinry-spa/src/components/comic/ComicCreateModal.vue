<template>
  <div class="comic-create-modal">
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{ $t("NewComicTitle") }}</p>
      </header>
      <section class="modal-card-body">
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
      </section>
      <footer class="modal-card-foot">
        <button
          class="button"
          type="button"
          @click="$parent.close()">
          {{ $t("closeButton") }}
        </button>
        <button
          class="button is-primary"
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
.modal-card {
  width: min(94vw, 760px);
  max-height: 92vh;
  border-radius: 8px;
  overflow: hidden;
}
.modal-card-body {
  overflow: auto;
}
.page-list {
  max-height: 220px;
  overflow: auto;
  border: 1px solid #edf1f6;
  border-radius: 8px;
}
.page-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid #edf1f6;
}
.page-row:last-child {
  border-bottom: 0;
}
.page-row span {
  width: 28px;
  color: #64748b;
}
.button {
  border-radius: 6px;
  font-weight: 600;
}
</style>
