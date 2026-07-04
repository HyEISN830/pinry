<template>
  <div class="pin-create-modal">
    <div>
      <div class="modal-card" style="width: auto">
        <header class="modal-card-head">
          <p class="modal-card-title">{{ $t(editorMeta.title) }}</p>
        </header>
        <section class="modal-card-body">
          <div class="columns">
            <div class="column">
              <FileUpload
                :previewImageURL="pinModel.form.url.value"
                v-on:imageUploadSucceed="onUploadDone"
                v-on:imageUploadProcessing="onUploadProcessing"
              ></FileUpload>
              <div class="description" v-show="pinModel.form.description.value" v-html="niceLinks(pinModel.form.description.value)"></div>
            </div>
            <div class="column">
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
            <div class="column" v-if="!isEdit">
              <FilterSelect
                :allOptions="boardOptions"
                v-on:selected="onSelectBoard"
              ></FilterSelect>
            </div>
          </div>
        </section>
        <footer class="modal-card-foot">
          <button class="button" type="button" @click="$parent.close()">{{ $t("closeButton") }}</button>
          <button
            v-if="!isEdit"
            @click="createPin"
            class="button is-primary">{{ $t("pinCreateModalCreatePinButton") }}
          </button>
          <button
            v-if="isEdit"
            @click="savePin"
            class="button is-primary">{{ $t("pinCreateModalSaveChangesButton") }}
          </button>
        </footer>
      </div>
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
      pinModel,
      formUpload: {
        imageId: null,
      },
      boardId: null,
      boardOptions: [],
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
    if (this.isEdit) {
      this.editorMeta.title = 'EditPinTitle';
      this.pinModel.form.url.value = this.existedPin.url;
      this.pinModel.form.referer.value = this.existedPin.referer;
      this.pinModel.form.description.value = this.existedPin.description;
      this.pinModel.form.tags.value = this.existedPin.tags;
      this.pinModel.form.private.value = this.existedPin.private;
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
          console.log('Error occurs while fetch board full list');
        },
      );
    },
    onSelectBoard(boardIds) {
      this.boardIds = boardIds;
    },
    onUploadProcessing() {
      this.disableUrlField = true;
    },
    onUploadDone(imageId) {
      this.formUpload.imageId = imageId;
    },
    savePin() {
      const self = this;
      this.normalizeTags();
      const data = this.pinModel.asDataByFields(
        ['referer', 'description', 'tags', 'private'],
      );
      const promise = API.Pin.updateById(this.existedPin.id, data);
      promise.then(
        (resp) => {
          bus.bus.$emit(bus.events.refreshPin);
          self.$emit('pinUpdated', resp);
          self.$parent.close();
        },
      );
    },
    createPin() {
      const loading = Loading.open(this);
      const self = this;
      let promise;
      if (isURLBlank(this.pinModel.form.url.value) && this.formUpload.imageId === null) {
        return;
      }
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
            self.$emit('pinCreated', resp);
            self.$parent.close();
            loading.close();
          }
          bus.bus.$emit(bus.events.refreshPin);
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
      ).catch((error) => {
        console.log('Cannot create pin:', error);
        loading.close();
      });
    },
    niceLinks,
  },
};
</script>

<style lang="scss" scoped>
.modal-card {
  overflow: hidden;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  box-shadow: 0 24px 70px rgba(16, 24, 40, 0.22);
}
.modal-card-head,
.modal-card-foot {
  border-color: #edf1f6;
  background: #f8fafc;
}
.modal-card-title {
  color: #22313f;
  font-size: 1.15rem;
  font-weight: 700;
}
.modal-card-body {
  background: #fff;
}
.description {
  margin-top: 0.75rem;
  padding: 0.8rem;
  border: 1px solid #edf1f6;
  border-radius: 8px;
  background: #f8fafc;
  color: #263238;
  font-size: 14px;
  line-height: 1.45;
}
.button {
  border-radius: 6px;
  font-weight: 600;
}
</style>
