<template>
  <div class="board-modal">
      <div class="modal-card create-modal-card create-board-card">
        <header class="modal-card-head create-modal-head">
          <div class="create-modal-title-block">
            <span class="create-modal-icon" aria-hidden="true">
              <b-icon icon="folder-multiple-image" custom-size="mdi-22px"></b-icon>
            </span>
            <div>
              <span class="create-modal-kicker">{{ $t('boardLink') }}</span>
              <p class="modal-card-title">{{ $t(UIMeta.title) }}</p>
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
          <div class="create-board-form" v-if="!isEdit">
            <b-field v-bind:label="$t('nameLabel')"
                       :type="createModel.form.name.type"
                       :message="createModel.form.name.error">
                <b-input
                  type="text"
                  v-model="createModel.form.name.value"
                  v-bind:placeholder="$t('boardNamePlaceholder')"
                  maxlength="128"
                  >
                </b-input>
            </b-field>
            <b-field v-bind:label="$t('privacyOptionLabel')"
                       :type="createModel.form.private.type"
                       :message="createModel.form.private.error">
                <b-checkbox v-model="createModel.form.private.value">
                    {{ $t("isPrivateCheckbox") }}
                </b-checkbox>
              </b-field>
          </div>
          <div class="create-board-form" v-if="isEdit">
            <b-field v-bind:label="$t('nameLabel')"
                       :type="editModel.form.name.type"
                       :message="editModel.form.name.error">
                <b-input
                  type="text"
                  v-model="editModel.form.name.value"
                  v-bind:placeholder="$t('boardNamePlaceholder')"
                  maxlength="128"
                  >
                </b-input>
            </b-field>
            <b-field v-bind:label="$t('privacyOptionLabel')"
                       :type="editModel.form.private.type"
                       :message="editModel.form.private.error">
                <b-checkbox v-model="editModel.form.private.value">
                    {{ $t("isPrivateCheckbox") }}
                </b-checkbox>
              </b-field>
          </div>
        </section>
        <footer class="modal-card-foot create-modal-foot">
          <button class="button create-modal-cancel" type="button" @click="$parent.close()">{{ $t("closeButton") }}</button>
          <button
            v-if="!isEdit"
            @click="createBoard"
            class="button is-primary create-modal-submit">{{ $t("createBoardButton") }}
          </button>
          <button
            v-if="isEdit"
            @click="saveBoardChanges"
            class="button is-primary create-modal-submit">{{ $t("saveChangesButton") }}
          </button>
        </footer>
      </div>
  </div>
</template>

<script>
import API from './api';
import ModelForm from './utils/ModelForm';
import bus from './utils/bus';

const fields = ['name', 'private'];

export default {
  name: 'BoardEditModal',
  data() {
    const createModel = ModelForm.fromFields(fields);
    const editModel = ModelForm.fromFields(fields);
    return {
      UIMeta: {
        title: 'BoardCreateTitle',
      },
      createModel,
      editModel,
    };
  },
  props: {
    isEdit: {
      type: Boolean,
      default: false,
    },
    board: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  created() {
    if (this.isEdit) {
      this.UIMeta.title = 'BoardEditTitle';
      this.editModel.assignToForm(this.board);
    } else {
      this.createModel.form.private.value = false;
    }
  },
  methods: {
    saveBoardChanges() {
      const self = this;
      const promise = API.Board.saveChanges(
        this.board.id,
        this.editModel.asData(),
      );
      promise.then(
        (resp) => {
          self.$emit('boardSaved', resp);
          self.$parent.close();
        },
        (error) => {
          self.editModel.markFieldsAsDanger(error.response.data);
        },
      );
    },
    createBoard() {
      const self = this;
      const promise = API.Board.create(
        this.createModel.form.name.value,
        this.createModel.form.private.value,
      );
      promise.then(
        (resp) => {
          bus.bus.$emit(bus.events.refreshBoards);
          self.$emit('boardCreated', resp);
          self.$parent.close();
        },
        (resp) => {
          self.createModel.markFieldsAsDanger(resp.data);
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.create-board-card { --create-modal-width: 560px; }
.create-board-form { display: grid; gap: var(--space-xs); }
</style>
