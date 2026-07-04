<template>
  <div class="board-modal">
    <div>
      <div class="modal-card" style="width: auto">
        <header class="modal-card-head">
          <p class="modal-card-title">{{ $t(UIMeta.title) }}</p>
        </header>
        <section class="modal-card-body">
          <div v-if="!isEdit">
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
          <div v-if="isEdit">
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
        <footer class="modal-card-foot">
          <button class="button" type="button" @click="$parent.close()">{{ $t("closeButton") }}</button>
          <button
            v-if="!isEdit"
            @click="createBoard"
            class="button is-primary">{{ $t("createBoardButton") }}
          </button>
          <button
            v-if="isEdit"
            @click="saveBoardChanges"
            class="button is-primary">{{ $t("saveChangesButton") }}
          </button>
        </footer>
      </div>
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
.button {
  border-radius: 6px;
  font-weight: 600;
}
</style>
