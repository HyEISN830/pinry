<template>
  <div class="pin-create-modal">
      <div class="modal-card create-modal-card create-pin-card">
        <header class="modal-card-head create-modal-head">
          <div class="create-modal-title-block">
            <span class="create-modal-icon" aria-hidden="true">
              <b-icon icon="image-plus" custom-size="mdi-22px"></b-icon>
            </span>
            <div>
              <span class="create-modal-kicker">{{ $t('pinLink') }}</span>
              <p class="modal-card-title">{{ $t(editorMeta.title) }}</p>
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
          <div class="columns create-pin-layout">
            <div class="column create-pin-media-column">
              <FileUpload
                :previewImageURL="pinModel.form.url.value"
                v-on:imageUploadSucceed="onUploadDone"
                v-on:imageUploadProcessing="onUploadProcessing"
                v-on:imageUploadFailed="onUploadFailed"
              ></FileUpload>
              <div
                class="description"
                v-show="pinModel.form.description.value"
                v-html="niceLinks(pinModel.form.description.value)">
              </div>
            </div>
            <div class="column create-pin-fields-column">
              <b-field v-bind:label="$t('imageUrlLabel')"
                       v-show="!disableUrlField && !isEdit"
                       :type="pinModel.form.url.type"
                       :message="pinModel.form.url.error">
                <b-input
                  type="text"
                  v-model="pinModel.form.url.value"
                  v-bind:placeholder="$t('pinCreateModalImageURLPlaceholder')"
                  maxlength="2048"
                >
                </b-input>
              </b-field>
              <b-field v-bind:label="$t('privacyOptionLabel')"
                       :type="pinModel.form.private.type"
                       :message="pinModel.form.private.error">
                <b-checkbox v-model="pinModel.form.private.value">
                    {{ $t("isPrivateCheckbox") }}
                </b-checkbox>
              </b-field>
              <b-field v-bind:label="$t('imageSourceLabel')"
                       :type="pinModel.form.referer.type"
                       :message="pinModel.form.referer.error">
                <b-input
                  type="text"
                  v-model="pinModel.form.referer.value"
                  v-bind:placeholder="$t('pinCreateModalImageSourcePlaceholder')"
                  maxlength="2048"
                >
                </b-input>
              </b-field>
              <b-field v-bind:label="$t('tagsLabel')">
                <b-taginput
                    ref="tagInput"
                    v-model="pinModel.form.tags.value"
                    :data="editorMeta.filteredTagOptions"
                    autocomplete
                    ellipsis
                    icon="label"
                    :allow-new="true"
                    v-bind:placeholder="$t('pinCreateModalImageTagsPlaceholder')"
                    @typing="getFilteredTags">
                  <template slot-scope="props">
                    <strong>{{ props.option }}</strong>
                  </template>
                  <template slot="empty">
                    {{ $t("pinCreateModalEmptySlot") }}
                  </template>
                </b-taginput>
              </b-field>
              <b-field v-bind:label="$t('descriptionLabel')"
                       :type="pinModel.form.description.type"
                       :message="pinModel.form.description.error">
                <b-input
                  type="textarea"
                  v-model="pinModel.form.description.value"
                  v-bind:placeholder="$t('pinCreateModalImageDescriptionPlaceholder')"
                  maxlength="1024"
                >
                </b-input>
              </b-field>
            </div>
            <div class="column create-pin-board-column" v-if="!isEdit && defaultBoard">
              <div class="fixed-board-card">
                <span class="fixed-board-label">{{ $t("fixedBoardLabel") }}</span>
                <strong>{{ defaultBoard.name }}</strong>
              </div>
            </div>
            <div class="column create-pin-board-column" v-if="!isEdit && !defaultBoard">
              <FilterSelect
                :allOptions="boardOptions"
                v-on:selected="onSelectBoard"
              ></FilterSelect>
            </div>
            <div class="column create-pin-board-column" v-if="isEdit">
              <FilterSelect
                :allOptions="boardOptions"
                :selected-values="boardIds"
                v-on:selected="onSelectBoard"
              ></FilterSelect>
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
            v-if="!isEdit"
            @click="createPin"
            class="button is-primary create-modal-submit"
            :disabled="uploadingImage">{{ $t("pinCreateModalCreatePinButton") }}
          </button>
          <button
            v-if="isEdit"
            @click="savePin"
            class="button is-primary create-modal-submit">{{ $t("pinCreateModalSaveChangesButton") }}
          </button>
        </footer>
      </div>
  </div>
</template>

<script>
import axios from 'axios';

import API from '../api';
import FileUpload from './FileUpload.vue';
import FilterSelect from './FilterSelect.vue';
import bus from '../utils/bus';
import ModelForm from '../utils/ModelForm';
import Loading from '../utils/Loading';
import AutoComplete from '../utils/AutoComplete';
import niceLinks from '../utils/niceLinks';


function isURLBlank(url) {
  return url !== null && url === '';
}

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

function normalizeBoardIds(boardIds) {
  const seen = {};
  const normalized = [];
  boardIds.forEach(
    (boardId) => {
      const normalizedId = Number(boardId);
      if (!normalizedId || seen[normalizedId]) {
        return;
      }
      seen[normalizedId] = true;
      normalized.push(normalizedId);
    },
  );
  return normalized;
}

const fields = ['url', 'referer', 'description', 'tags', 'private'];

export default {
  name: 'PinCreateModal',
  props: {
    fromUrl: {
      type: Object,
      default: null,
    },
    username: {
      type: String,
      default: null,
    },
    isEdit: {
      type: Boolean,
      default: false,
    },
    existedPin: {
      type: Object,
      default: null,
    },
    defaultBoard: {
      type: Object,
      default: null,
    },
  },
  components: {
    FileUpload,
    FilterSelect,
  },
  data() {
    const pinModel = ModelForm.fromFields(fields);
    pinModel.form.tags.value = [];
    return {
      disableUrlField: false,
      uploadingImage: false,
      pinModel,
      formUpload: {
        imageId: null,
      },
      boardIds: [],
      boardOptions: [],
      originalBoardIds: [],
      tagOptions: [],
      editorMeta: {
        title: 'NewPinTitle',
        filteredTagOptions: [],
      },
    };
  },
  created() {
    this.fetchBoardList();
    this.fetchTagList();
    if (this.defaultBoard) {
      this.boardIds = [this.defaultBoard.id];
    }
    if (this.isEdit) {
      this.editorMeta.title = 'EditPinTitle';
      this.pinModel.form.url.value = this.existedPin.url;
      this.pinModel.form.referer.value = this.existedPin.referer;
      this.pinModel.form.description.value = this.existedPin.description;
      this.pinModel.form.tags.value = this.existedPin.tags;
      this.pinModel.form.private.value = this.existedPin.private;
      this.originalBoardIds = normalizeBoardIds(
        (this.existedPin.boards || []).map(
          board => board.id,
        ),
      );
      this.boardIds = this.originalBoardIds.slice();
    } else {
      this.pinModel.form.private.value = false;
    }
    if (this.fromUrl) {
      this.pinModel.form.url.value = this.fromUrl.url;
      this.pinModel.form.referer.value = this.fromUrl.referer;
      this.pinModel.form.description.value = this.fromUrl.description;
    }
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
      this.pinModel.form.tags.value.forEach(
        (tag) => {
          splitTags(tag).forEach(
            item => tags.push(item),
          );
        },
      );
      this.pinModel.form.tags.value = uniqueTags(tags);
    },
    absorbTypedTags(text) {
      if (text.indexOf(',') === -1 && text.indexOf('\uFF0C') === -1) {
        return text;
      }
      const shouldKeepLastText = !(/[,\uFF0C]\s*$/.test(text));
      const parts = text.split(/[,\uFF0C]/);
      const remainingText = shouldKeepLastText ? parts.pop().trim() : '';
      const tags = splitTags(parts.join(','));
      this.pinModel.form.tags.value = uniqueTags(
        this.pinModel.form.tags.value.concat(tags),
      );
      this.setTagInputText(remainingText);
      return remainingText;
    },
    getFilteredTags(text) {
      const filterText = this.absorbTypedTags(text);
      const filteredTagOptions = [];
      AutoComplete.getFilteredOptions(
        this.tagOptions,
        filterText,
      ).forEach(
        (option) => {
          filteredTagOptions.push(option.name);
        },
      );
      this.editorMeta.filteredTagOptions = filteredTagOptions;
    },
    fetchBoardList() {
      if (this.defaultBoard) {
        this.boardOptions = [
          { name: this.defaultBoard.name, value: this.defaultBoard.id },
        ];
        return;
      }
      API.Board.fetchFullList(this.username).then(
        (resp) => {
          const boardOptions = [];
          resp.data.forEach(
            (board) => {
              const boardOption = { name: board.name, value: board.id };
              boardOptions.push(boardOption);
            },
          );
          this.boardOptions = boardOptions;
        },
        () => {
          this.boardOptions = [];
        },
      );
    },
    onSelectBoard(boardIds) {
      this.boardIds = normalizeBoardIds(boardIds);
    },
    syncPinBoards(pinId) {
      const currentBoardIds = normalizeBoardIds(this.boardIds);
      const originalBoardIds = normalizeBoardIds(this.originalBoardIds);
      const boardIdsToAdd = currentBoardIds.filter(
        boardId => originalBoardIds.indexOf(boardId) === -1,
      );
      const boardIdsToRemove = originalBoardIds.filter(
        boardId => currentBoardIds.indexOf(boardId) === -1,
      );
      let promise = Promise.resolve();
      boardIdsToAdd.forEach(
        (boardId) => {
          promise = promise.then(
            () => API.Board.addToBoard(boardId, [pinId]),
          );
        },
      );
      boardIdsToRemove.forEach(
        (boardId) => {
          promise = promise.then(
            () => API.Board.removeFromBoard(boardId, [pinId]),
          );
        },
      );
      return promise.then(
        () => {
          this.originalBoardIds = currentBoardIds.slice();
          this.boardIds = currentBoardIds.slice();
        },
      );
    },
    onUploadProcessing() {
      this.disableUrlField = true;
      this.uploadingImage = true;
    },
    onUploadDone(imageId) {
      this.formUpload.imageId = imageId;
      this.uploadingImage = false;
    },
    onUploadFailed() {
      this.uploadingImage = false;
    },
    savePin() {
      const self = this;
      const loading = Loading.open(this);
      this.normalizeTags();
      const data = this.pinModel.asDataByFields(
        ['referer', 'description', 'tags', 'private'],
      );
      const promise = API.Pin.updateById(this.existedPin.id, data);
      promise.then(
        (resp) => {
          self.syncPinBoards(this.existedPin.id).then(
            () => {
              bus.bus.$emit(bus.events.refreshPin);
              bus.bus.$emit(bus.events.refreshBoards);
              self.$emit('pinUpdated', resp);
              loading.close();
              self.$parent.close();
            },
            () => {
              loading.close();
              this.$buefy.toast.open(
                {
                  message: this.$t('pinBoardUpdateFailed'),
                  type: 'is-danger',
                },
              );
            },
          );
        },
        () => {
          loading.close();
        },
      );
    },
    createPin() {
      if (isURLBlank(this.pinModel.form.url.value) && this.formUpload.imageId === null) {
        return;
      }
      const loading = Loading.open(this);
      const self = this;
      let promise;
      if (this.formUpload.imageId === null) {
        this.normalizeTags();
        const data = this.pinModel.asDataByFields(fields);
        promise = API.Pin.createFromURL(data);
      } else {
        this.normalizeTags();
        const data = this.pinModel.asDataByFields(
          ['referer', 'description', 'tags', 'private'],
        );
        data.image_by_id = this.formUpload.imageId;
        promise = API.Pin.createFromUploaded(data);
      }
      promise.then(
        (resp) => {
          const promises = [];
          function done() {
            bus.bus.$emit(bus.events.refreshPin);
            self.$emit('pinCreated', resp.data);
            self.$parent.close();
            loading.close();
          }
          if (self.boardIds) {
            // FIXME(winkidney): Should handle error for add-to board
            self.boardIds.forEach(
              (boardId) => {
                promises.push(API.Board.addToBoard(boardId, [resp.data.id]));
              },
            );
          }
          if (promises.length > 0) {
            axios.all(promises).then(done);
          } else {
            done();
          }
        },
      ).catch(() => {
        loading.close();
      });
    },
    niceLinks,
  },
};
</script>

<style lang="scss" scoped>
.create-pin-card { --create-modal-width: 1180px; }
.create-pin-layout {
  display: grid;
  grid-template-columns:
    minmax(220px, 260px)
    minmax(330px, 1fr)
    minmax(290px, 340px);
  gap: var(--space-md);
  align-items: start;
  margin: 0;
}
.create-pin-layout > .column {
  min-width: 0;
  padding: 0;
}
.description {
  margin-top: var(--space-sm);
  padding: var(--space-sm);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  background: var(--color-surface-2);
  font-size: 0.9rem;
  line-height: 1.45;
}
.fixed-board-card {
  padding: var(--space-md);
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: transparent;
  box-shadow: none;
}
.fixed-board-label {
  display: block;
  margin-bottom: var(--space-2xs);
  color: var(--color-text-muted);
  font-size: 0.78rem;
  font-weight: 850;
}
@media screen and (max-width: 960px) {
  .create-pin-layout {
    grid-template-columns: minmax(220px, 260px) minmax(320px, 1fr);
  }
  .create-pin-board-column {
    grid-column: 1 / -1;
  }
}
@media screen and (max-width: 768px) {
  .create-pin-layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .create-pin-board-column {
    grid-column: auto;
  }
}
</style>
