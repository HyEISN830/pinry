<template>
  <div class="add2board-modal">
    <div class="modal-card create-modal-card add2board-card">
      <header class="modal-card-head create-modal-head">
        <div class="create-modal-title-block">
          <span class="create-modal-icon" aria-hidden="true">
            <b-icon icon="folder-plus" custom-size="mdi-22px"></b-icon>
          </span>
          <div>
            <span class="create-modal-kicker">{{ $t('boardsLink') }}</span>
            <p class="modal-card-title">{{ $t('Add2BoardModalCardTitle') }}</p>
          </div>
        </div>
        <button
          class="create-modal-close"
          type="button"
          :title="$t('closeButton')"
          :aria-label="$t('closeButton')"
          @click="close">
          <b-icon icon="close" custom-size="mdi-20px"></b-icon>
        </button>
      </header>
      <section class="modal-card-body create-modal-body add2board-body">
        <div class="add2board-layout">
          <div class="add2board-preview-region">
            <div class="add2board-preview">
              <img
                v-if="previewUrl"
                :src="previewUrl"
                :alt="pin.description || $t('imageUnavailableText')">
              <div v-else class="add2board-preview-empty">
                <b-icon icon="image-off-outline" custom-size="mdi-30px"></b-icon>
                <span>{{ $t('imageUnavailableText') }}</span>
              </div>
              <span class="add2board-preview-label">{{ $t('pinLink') }}</span>
            </div>
            <p v-if="pin.description" class="add2board-pin-description">
              {{ pin.description }}
            </p>
          </div>
          <div class="add2board-select-region">
            <p class="add2board-description">{{ $t('add2BoardModalDescription') }}</p>
            <div v-if="loadingBoards" class="add2board-loading" role="status">
              <b-icon
                class="add2board-loading-icon"
                icon="loading"
                custom-size="mdi-24px">
              </b-icon>
              <span>{{ $t('boardListLoading') }}</span>
            </div>
            <FilterSelect
              v-else
              :allOptions="boardOptions"
              v-on:selected="onSelectBoard">
            </FilterSelect>
            <transition name="add2board-selection">
              <div v-if="boardIds.length" class="add2board-selection-status">
                <b-icon icon="check-circle" custom-size="mdi-18px"></b-icon>
                <span>{{ selectedBoardSummary }}</span>
              </div>
            </transition>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot create-modal-foot">
        <button
          class="button create-modal-cancel"
          type="button"
          :disabled="saving"
          @click="close">
          {{ $t('cancelButton') }}
        </button>
        <button
          class="button is-primary create-modal-submit add2board-submit"
          type="button"
          :class="{ 'is-loading': saving }"
          :disabled="saving || boardIds.length === 0"
          @click="doAdd2Board">
          <b-icon icon="folder-plus" custom-size="mdi-18px"></b-icon>
          <span>{{ $t('Add2BoardModalCardButton') }}</span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
import API from '../api';
import FilterSelect from './FilterSelect.vue';

export default {
  name: 'Add2Board',
  components: {
    FilterSelect,
  },
  props: {
    pin: {
      type: Object,
      default() {
        return {};
      },
    },
    username: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      boardOptions: [],
      boardIds: [],
      loadingBoards: true,
      saving: false,
    };
  },
  computed: {
    previewUrl() {
      return this.pin.url || this.pin.large_image_url || this.pin.original_image_url || '';
    },
    selectedBoardSummary() {
      return this.$t('add2BoardSelectedCount', { count: this.boardIds.length });
    },
  },
  created() {
    this.fetchBoardList();
  },
  methods: {
    close() {
      this.$parent.close();
    },
    doAdd2Board() {
      if (this.saving) {
        return;
      }
      if (this.boardIds.length === 0) {
        this.$buefy.toast.open({
          message: this.$t('add2BoardSelectionRequired'),
          type: 'is-warning',
        });
        return;
      }

      this.saving = true;
      const requests = this.boardIds.map(
        boardId => API.Board.addToBoard(boardId, [this.pin.id]),
      );
      Promise.all(requests)
        .then(
          () => {
            this.$buefy.toast.open({
              message: this.$t('add2BoardSucceeded'),
              type: 'is-success',
            });
            this.close();
          },
        )
        .catch(
          () => {
            this.saving = false;
            this.$buefy.toast.open({
              message: this.$t('add2BoardFailed'),
              type: 'is-danger',
            });
          },
        );
    },
    onSelectBoard(boardIds) {
      this.boardIds = boardIds;
    },
    fetchBoardList() {
      API.Board.fetchFullList(this.username)
        .then(
          (resp) => {
            this.boardOptions = resp.data.map(
              board => ({ name: board.name, value: board.id }),
            );
            this.loadingBoards = false;
          },
        )
        .catch(
          () => {
            this.loadingBoards = false;
            this.$buefy.toast.open({
              message: this.$t('boardListLoadFailed'),
              type: 'is-danger',
            });
          },
        );
    },
  },
};
</script>

<style lang="scss" scoped>
.add2board-card {
  --create-modal-width: 880px;
}

.add2board-body {
  overflow-x: hidden;
}

.add2board-layout {
  display: grid;
  grid-template-columns: minmax(220px, 0.78fr) minmax(340px, 1.22fr);
  align-items: start;
  gap: var(--space-lg);
}

.add2board-preview-region,
.add2board-select-region {
  min-width: 0;
}

.add2board-select-region {
  padding-left: var(--space-lg);
  border-left: 1px solid var(--color-line-soft);
}

.add2board-preview {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4 / 3;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 64%),
    var(--color-surface-2);
  box-shadow: var(--shadow-sm);
}

.add2board-preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform var(--motion-duration-standard) var(--motion-ease-standard);
}

.add2board-preview:hover img {
  transform: scale(1.018);
}

.add2board-preview-empty {
  display: grid;
  height: 100%;
  place-content: center;
  gap: var(--space-xs);
  color: var(--color-text-muted);
  text-align: center;
}

.add2board-preview-label {
  position: absolute;
  top: var(--space-xs);
  left: var(--space-xs);
  padding: 0.28rem 0.58rem;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-pill);
  color: var(--color-accent-strong);
  background: color-mix(in srgb, var(--color-surface-card) 86%, transparent);
  box-shadow: var(--shadow-xs);
  font-size: 0.72rem;
  font-weight: 900;
  backdrop-filter: blur(10px);
  user-select: none;
}

.add2board-pin-description {
  display: -webkit-box;
  overflow: hidden;
  margin: var(--space-sm) 0 0;
  color: var(--color-text-muted);
  font-size: 0.84rem;
  font-weight: 650;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.add2board-description {
  margin: 0 0 var(--space-md);
  color: var(--color-text-muted);
  font-size: 0.88rem;
  font-weight: 650;
  line-height: 1.6;
}

.add2board-loading {
  display: flex;
  min-height: 148px;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  border: 1px dashed var(--color-accent-border);
  border-radius: var(--radius-md);
  color: var(--color-accent-strong);
  background: var(--color-accent-soft-gradient);
  font-size: 0.86rem;
  font-weight: 850;
}

.add2board-loading-icon {
  animation: add2board-spin 900ms linear infinite;
}

.add2board-selection-status {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
  margin-top: var(--space-sm);
  color: var(--color-accent-strong);
  font-size: 0.8rem;
  font-weight: 850;
}

.add2board-submit {
  gap: var(--space-2xs);
}

.add2board-selection-enter-active,
.add2board-selection-leave-active {
  transition:
    opacity var(--motion-duration-fast) var(--motion-ease-standard),
    transform var(--motion-duration-fast) var(--motion-ease-standard);
}

.add2board-selection-enter,
.add2board-selection-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

@keyframes add2board-spin {
  to {
    transform: rotate(360deg);
  }
}

@media screen and (max-width: 760px) {
  .add2board-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .add2board-preview {
    max-height: 34vh;
  }

  .add2board-select-region {
    padding-top: var(--space-lg);
    padding-left: 0;
    border-top: 1px solid var(--color-line-soft);
    border-left: 0;
  }
}
</style>
