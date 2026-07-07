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
        <button
          @click="toggleSearchPopup"
          class="button is-info"
          type="button">
          {{ $t("searchBoardButton") }}
        </button>
        <button
          @click="createNewBoard"
          class="button is-primary"
          type="button">
          {{ $t("filterSelectCreateNewBoardButton") }}
        </button>
        <button
          @click="clearSelection"
          class="button is-light"
          type="button">
          {{ $t("clearBoardSelectionButton") }}
        </button>
      </div>
    </b-field>
    <div class="board-search-popup" v-if="searchPopupOpen">
      <b-input
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
          type="button"
          @click="select(option)">
          {{ option.name }}
        </button>
        <div class="board-search-empty" v-if="availableOptions.length === 0">
          {{ $t("pinCreateModalEmptySlot") }}
        </div>
      </div>
    </div>
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
  mounted() {
    document.addEventListener('click', this.onDocumentClick);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.onDocumentClick);
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
      this.searchPopupOpen = false;
    },
    onDocumentClick(event) {
      if (!this.searchPopupOpen || this.$el.contains(event.target)) {
        return;
      }
      this.closeSearchPopup();
    },
    toggleSearchPopup() {
      this.searchPopupOpen = !this.searchPopupOpen;
      if (this.searchPopupOpen) {
        this.searchText = '';
        this.syncAvailableOptions();
      }
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
  padding: 0.75rem;
  border: 1px solid #edf1f6;
  border-radius: 8px;
  background: #f8fafc;
}
.filter-select-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem;
}
.button {
  border-radius: 6px;
  font-weight: 600;
}
.board-search-popup {
  position: absolute;
  z-index: 30;
  left: 0.75rem;
  right: 0.75rem;
  margin-top: 0.15rem;
  padding: 0.75rem;
  border: 1px solid #dbe4ef;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 40px rgba(16, 24, 40, 0.18);
}
.board-search-popup ::v-deep .input {
  border-color: #d8e0eb;
  border-radius: 8px;
  font-size: 14px;
}
.board-search-list {
  max-height: 220px;
  margin-top: 0.55rem;
  overflow-y: auto;
}
.board-search-option {
  display: block;
  width: 100%;
  padding: 0.5rem 0.6rem;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #22313f;
  text-align: left;
  cursor: pointer;
}
.board-search-option:hover {
  background: #eef5ff;
  color: #1f6feb;
}
.board-search-empty {
  padding: 0.7rem 0.4rem;
  color: #8a94a6;
  font-size: 14px;
}
</style>
