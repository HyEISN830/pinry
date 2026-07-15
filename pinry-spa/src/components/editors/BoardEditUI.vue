<template>
  <div class="editor board-editor">
    <div class="editor-buttons">
      <button
        class="icon-container"
        v-source-tooltip
        type="button"
        :data-tooltip="$t('deleteBoardTooltip')"
        :aria-label="$t('deleteBoardTooltip')"
        :disabled="deleting"
        @click.stop="deleteBoard"
        @touchstart.stop="noop">
         <b-icon
           type="is-light"
           icon="delete"
           custom-size="mdi-24px">
          </b-icon>
      </button>
      <button
        class="icon-container"
        v-source-tooltip
        type="button"
        :data-tooltip="$t('editBoardTooltip')"
        :aria-label="$t('editBoardTooltip')"
        :disabled="deleting"
        @click.stop="editBoard"
        @touchstart.stop="noop">
       <b-icon
         type="is-light"
         icon="pencil"
         custom-size="mdi-24px">
       </b-icon>
      </button>
    </div>
    <div
      class="board-delete-progress"
      v-if="deleting"
      role="status"
      aria-live="polite">
      <div class="board-delete-progress-heading">
        <span class="board-delete-progress-dot" aria-hidden="true"></span>
        <span>{{ deleteStatusText }}</span>
        <strong>{{ deleteProgress }}%</strong>
      </div>
      <progress
        class="progress board-delete-progress-bar"
        :value="deleteProgress"
        max="100">
        {{ deleteProgress }}%
      </progress>
    </div>
  </div>
</template>

<script>
import API from '../api';
import modals from '../modals';


const REMOVE_BATCH_SIZE = 10;

export default {
  name: 'BoardEditor',
  props: {
    board: {
      default() {
        return {};
      },
      type: Object,
    },
  },
  data() {
    return {
      deleting: false,
      deleteProgress: 0,
      deleteStatusText: '',
    };
  },
  methods: {
    noop() {
      return true;
    },
    onBoardSaved() {
      this.$emit('board-save-succeed');
    },
    editBoard() {
      if (this.deleting) {
        return;
      }
      modals.openBoardEdit(
        this,
        this.board,
        this.onBoardSaved,
      );
    },
    fetchAffectedPinIds(offset = 0, affectedPinIds = []) {
      return API.fetchPins(offset, null, null, this.board.id)
        .then(
          (resp) => {
            const nextPinIds = affectedPinIds.concat(
              resp.data.results.map(pin => pin.id),
            );
            if (!resp.data.next) {
              return nextPinIds;
            }
            return this.fetchAffectedPinIds(
              offset + resp.data.results.length,
              nextPinIds,
            );
          },
        );
    },
    removePinsInBatches(pinIds, batchIndex = 0) {
      const totalBatches = Math.ceil(pinIds.length / REMOVE_BATCH_SIZE);
      if (pinIds.length === 0 || batchIndex >= totalBatches) {
        this.deleteProgress = 92;
        this.deleteStatusText = this.$t('boardDeleteProgressDeleting');
        return Promise.resolve();
      }
      const start = batchIndex * REMOVE_BATCH_SIZE;
      const batch = pinIds.slice(start, start + REMOVE_BATCH_SIZE);
      this.deleteProgress = Math.max(
        10,
        Math.round((batchIndex / totalBatches) * 82),
      );
      this.deleteStatusText = this.$t('boardDeleteProgressRemoving');
      return API.Board.removeFromBoard(this.board.id, batch)
        .then(
          () => this.removePinsInBatches(pinIds, batchIndex + 1),
        );
    },
    deleteBoardWithProgress() {
      this.deleting = true;
      this.deleteProgress = 5;
      this.deleteStatusText = this.$t('boardDeleteProgressPreparing');
      this.fetchAffectedPinIds()
        .then(
          pinIds => this.removePinsInBatches(pinIds),
        )
        .then(
          () => API.Board.delete(this.board.id),
        )
        .then(
          () => {
            this.deleteProgress = 100;
            this.deleteStatusText = this.$t('boardDeleteSucceeded');
            this.$buefy.toast.open(this.$t('boardDeleteSucceeded'));
            this.$emit('board-delete-succeed', this.board.id);
          },
        )
        .catch(
          () => {
            this.deleting = false;
            this.deleteProgress = 0;
            this.$buefy.toast.open(
              { type: 'is-danger', message: this.$t('boardDeleteFailed') },
            );
          },
        );
    },
    deleteBoard() {
      if (this.deleting) {
        return;
      }
      modals.openActionConfirm(
        this,
        {
          title: this.$t('boardDeleteTitle'),
          message: this.$t(
            'boardDeleteConfirm',
            { count: this.board.total_pins || 0 },
          ),
          confirmLabel: this.$t('deleteButton'),
          cancelLabel: this.$t('cancelButton'),
          icon: 'delete-outline',
        },
        this.deleteBoardWithProgress,
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@import './editor';
</style>
