<template>
  <div class="filter-select">
    <b-field v-bind:label="$t('selectBoardLabel')"
             :type="form.name.type"
             :message="form.name.error">
      <b-input
        type="text"
        v-model="form.name.value"
        v-bind:placeholder="$t('filterSelectSelectBoardPlaceholder')"
        maxlength="128"
      >
      </b-input>
    </b-field>
    <b-field>
      <div class="filter-select-actions">
        <b-dropdown
          ref="searchDropdown"
          class="board-search-dropdown"
          position="is-bottom-right"
          :mobile-modal="false"
          :close-on-click="false"
          append-to-body
          aria-role="dialog"
          @active-change="onSearchPopupActiveChange">
          <button
            slot="trigger"
            class="button board-action board-action--search"
            :class="{ 'is-active': searchPopupOpen }"
            type="button">
            <b-icon icon="magnify" custom-size="mdi-18px"></b-icon>
            <span>{{ $t("searchBoardButton") }}</span>
          </button>
          <div class="board-search-popup">
            <div class="board-search-popup__heading">
              <b-icon icon="magnify" custom-size="mdi-18px"></b-icon>
              <strong>{{ $t("searchBoardButton") }}</strong>
            </div>
            <b-input
              ref="searchInput"
              v-model="searchText"
              icon="magnify"
              expanded
              v-bind:placeholder="$t('searchBoardPlaceholder')"
              maxlength="128">
            </b-input>
            <div class="board-search-list">
              <button
                v-for="option in availableOptions"
                :key="option.value"
                class="board-search-option"
                :class="{ 'is-selected': isSelected(option.value) }"
                type="button"
                @click="select(option)">
                <b-icon icon="folder-multiple-image" custom-size="mdi-18px"></b-icon>
                <span>{{ option.name }}</span>
              </button>
              <div class="board-search-empty" v-if="availableOptions.length === 0">
                {{ $t("pinCreateModalEmptySlot") }}
              </div>
            </div>
          </div>
        </b-dropdown>
        <button
          @click="createNewBoard"
          class="button board-action board-action--create"
          type="button">
          <b-icon icon="folder-plus" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("filterSelectCreateNewBoardButton") }}</span>
        </button>
        <button
          @click="clearSelection"
          class="button board-action board-action--clear"
          type="button">
          <b-icon icon="close-circle-outline" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("clearBoardSelectionButton") }}</span>
        </button>
      </div>
    </b-field>
  </div>
</template>

<script>
import API from '../api';
import ModelForm from '../utils/ModelForm';
import AutoComplete from '../utils/AutoComplete';

const fields = ['name'];

function getBoardFromResp(boardObject) {
  return { name: boardObject.name, value: boardObject.id };
}

function getAvailableOptions(vm, filter) {
  let availableOptions;
  const options = vm.createdOptions.concat(vm.allOptions);
  if (!filter) {
    availableOptions = options;
  } else {
    availableOptions = AutoComplete.getFilteredOptions(
      options, filter,
    );
  }
  return availableOptions;
}

function arraysEqual(left, right) {
  if (left.length !== right.length) {
    return false;
  }
  return left.every(
    (value, index) => String(value) === String(right[index]),
  );
}

export default {
  name: 'FilterSelect',
  props: {
    allOptions: {
      type: Array,
      default() {
        return [];
      },
    },
    selectedValues: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    const model = ModelForm.fromFields(fields);
    return {
      form: model.form,
      selectedOptions: [],
      helper: model,
      availableOptions: [],
      createdOptions: [],
      searchPopupOpen: false,
      searchText: '',
    };
  },
  methods: {
    getSelectedBoards() {
      const options = this.createdOptions.concat(this.allOptions);
      return options.filter(
        option => this.selectedOptions.some(
          value => String(value) === String(option.value),
        ),
      );
    },
    syncNameFromSelection() {
      const boards = this.getSelectedBoards();
      this.form.name.value = boards.map(board => board.name).join(', ');
    },
    syncAvailableOptions(filter) {
      const options = getAvailableOptions(this, filter);
      this.availableOptions = options;
    },
    setSelectedOptions(values, shouldEmit) {
      const nextValues = values.slice();
      if (!arraysEqual(nextValues, this.selectedOptions)) {
        this.selectedOptions = nextValues;
      }
      this.helper.resetAllFields();
      this.syncNameFromSelection();
      if (shouldEmit) {
        this.$emit('selected', nextValues.slice());
      }
    },
    closeSearchPopup() {
      const dropdown = this.$refs.searchDropdown;
      if (dropdown) {
        dropdown.isActive = false;
      }
      this.searchPopupOpen = false;
    },
    onSearchPopupActiveChange(isActive) {
      this.searchPopupOpen = isActive;
      if (isActive) {
        this.searchText = '';
        this.syncAvailableOptions();
        this.$nextTick(
          () => {
            const input = this.$refs.searchInput;
            if (input && typeof input.focus === 'function') {
              input.focus();
            }
          },
        );
      }
    },
    isSelected(value) {
      return this.selectedOptions.some(
        selectedValue => String(selectedValue) === String(value),
      );
    },
    select(board) {
      this.setSelectedOptions([board.value], true);
      this.closeSearchPopup();
      this.searchText = '';
    },
    clearSelection() {
      this.setSelectedOptions([], true);
      this.form.name.value = '';
      this.searchText = '';
      this.closeSearchPopup();
    },
    createNewBoard() {
      const self = this;
      const boardName = (this.form.name.value || '').trim();
      if (!boardName) {
        this.form.name.value = '';
        return;
      }
      const promise = API.Board.create(boardName);
      promise.then(
        (data) => {
          self.$emit('boardCreated', data);
          const board = getBoardFromResp(data);
          self.createdOptions.unshift(board);
          self.syncAvailableOptions();
          self.select(board);
          self.$buefy.toast.open(
            {
              message: self.$t('boardCreateSucceeded'),
              type: 'is-success',
            },
          );
        },
        (resp) => {
          self.helper.markFieldsAsDanger(resp ? resp.data : {});
        },
      );
    },
  },
  watch: {
    searchText(newVal) {
      this.syncAvailableOptions(newVal);
    },
    allOptions() {
      this.syncAvailableOptions(this.searchText);
      if (this.selectedOptions.length > 0) {
        this.syncNameFromSelection();
      }
    },
    selectedValues: {
      handler(newVal) {
        const nextValues = newVal.slice();
        if (arraysEqual(nextValues, this.selectedOptions)) {
          return;
        }
        this.setSelectedOptions(nextValues, false);
      },
      immediate: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.filter-select {
  position: relative;
  min-width: 0;
  padding: var(--space-sm);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: transparent;
}
.filter-select ::v-deep .label {
  color: var(--color-text-strong);
  font-weight: 850;
}
.filter-select ::v-deep .input {
  border-color: var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-1) 76%, transparent);
  box-shadow: none;
  transition:
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}
.filter-select ::v-deep .input:focus {
  border-color: var(--color-accent-border);
  background: var(--color-surface-1);
  box-shadow: var(--focus-ring);
}
.filter-select-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs);
}
.board-search-dropdown,
.board-action--create {
  flex: 1 1 calc(50% - var(--space-xs));
  min-width: 124px;
}
.board-search-dropdown ::v-deep .dropdown-trigger,
.board-action--search {
  width: 100%;
}
.board-action {
  min-height: 40px;
  gap: var(--space-2xs);
  justify-content: center;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: var(--color-surface-1);
  box-shadow: none;
  font-size: 0.82rem;
  font-weight: 850;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard);
}
.board-action:hover,
.board-action:focus-visible,
.board-action--search.is-active {
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  box-shadow: var(--shadow-xs);
  transform: translateY(-1px);
}
.board-action:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
.board-action--create {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  text-shadow: var(--color-accent-text-shadow);
  background: var(--color-accent-fill);
  box-shadow: 0 8px 20px var(--color-theme-glow);
}
.board-action--create:hover,
.board-action--create:focus-visible {
  color: var(--color-accent-text);
  background: var(--color-accent-fill-hover);
}
.board-action--clear {
  flex: 1 1 100%;
  border-color: var(--color-accent-border);
  color: var(--color-text-muted);
  background: transparent;
}
.board-action--clear:hover,
.board-action--clear:focus-visible {
  color: var(--color-accent-foreground);
  background: transparent;
}
.board-search-popup {
  width: min(360px, calc(100vw - var(--space-lg)));
  padding: var(--space-sm);
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 180px),
    var(--color-surface-card);
  box-shadow: var(--shadow-floating);
}
.board-search-popup__heading {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin-bottom: var(--space-sm);
  color: var(--color-accent-foreground);
  font-size: 0.82rem;
}
.board-search-popup__heading strong {
  color: inherit;
}
.board-search-popup ::v-deep .input {
  border-color: var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: var(--color-surface-1);
  box-shadow: none;
  font-size: 0.88rem;
}
.board-search-popup ::v-deep .input:focus {
  border-color: var(--color-accent-border);
  box-shadow: var(--focus-ring);
}
.board-search-list {
  max-height: min(280px, 42vh);
  margin-top: var(--space-xs);
  overflow-y: auto;
  scrollbar-color: var(--color-accent-border) transparent;
}
.board-search-option {
  display: flex;
  width: 100%;
  min-height: 42px;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-strong);
  text-align: left;
  cursor: pointer;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}
.board-search-option:hover,
.board-search-option:focus-visible,
.board-search-option.is-selected {
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  transform: translateX(2px);
}
.board-search-option:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
.board-search-option span:last-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.board-search-empty {
  padding: var(--space-md) var(--space-xs);
  color: var(--color-text-muted);
  font-size: 0.86rem;
  text-align: center;
}
</style>

<style lang="scss">
.board-search-dropdown.dropdown .dropdown-menu {
  z-index: calc(var(--z-modal, 140) + 40) !important;
  min-width: 0;
  padding-top: var(--space-xs);
}
.board-search-dropdown.dropdown .dropdown-content {
  padding: 0;
  overflow: visible;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  box-shadow: none;
}
</style>
