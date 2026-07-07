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
    <b-field>
      <b-select
        class="select-list"
        multiple
        expanded
        native-size="8"
        v-model="selectedOptions">
        <template v-for="option in availableOptions">
          <option
            v-bind:key="option.value"
            :value="option.value">{{ option.name }}</option>
        </template>
      </b-select>
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
  if (!filter) {
    availableOptions = vm.allOptions;
  } else {
    availableOptions = AutoComplete.getFilteredOptions(
      vm.allOptions, vm.form.name.value,
    );
  }
  return availableOptions;
}

function arraysEqual(left, right) {
  if (left.length !== right.length) {
    return false;
  }
  return left.every(
    (value, index) => value === right[index],
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
      syncingSelectionName: false,
      syncingSelectedValues: false,
    };
  },
  methods: {
    getSelectedBoards() {
      const options = this.createdOptions.concat(this.allOptions);
      return options.filter(
        option => this.selectedOptions.indexOf(option.value) !== -1,
      );
    },
    syncNameFromSelection() {
      const boards = this.getSelectedBoards();
      this.syncingSelectionName = true;
      this.form.name.value = boards.map(board => board.name).join(', ');
      this.availableOptions = this.createdOptions.concat(this.allOptions);
    },
    select(board) {
      if (arraysEqual(this.selectedOptions, [board.value])) {
        return;
      }
      this.selectedOptions = [board.value];
    },
    clearSelection() {
      if (this.selectedOptions.length === 0) {
        return;
      }
      this.selectedOptions = [];
    },
    createNewBoard() {
      const self = this;
      const promise = API.Board.create(this.form.name.value);
      promise.then(
        (data) => {
          self.$emit('boardCreated', data);
          const board = getBoardFromResp(data);
          self.createdOptions.unshift(board);
          const options = getAvailableOptions(this);
          this.availableOptions = this.createdOptions.concat(options);
          self.select(board);
        },
        (resp) => {
          self.helper.markFieldsAsDanger(resp.data);
        },
      );
    },
  },
  watch: {
    // eslint-disable-next-line func-names
    'form.name.value': function (newVal) {
      if (this.syncingSelectionName) {
        this.syncingSelectionName = false;
        return;
      }
      const options = getAvailableOptions(this, newVal);
      this.availableOptions = this.createdOptions.concat(options);
    },
    allOptions() {
      this.availableOptions = this.allOptions;
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
        this.syncingSelectedValues = true;
        this.selectedOptions = nextValues;
      },
      immediate: true,
    },
    selectedOptions() {
      this.helper.resetAllFields();
      this.syncNameFromSelection();
      if (this.syncingSelectedValues) {
        this.syncingSelectedValues = false;
        return;
      }
      this.$emit('selected', this.selectedOptions.slice());
    },
  },
};
</script>

<style lang="scss" scoped>
.filter-select {
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
.select-list {
  width: 100%;
}
.select-list ::v-deep select {
  border-color: #d8e0eb;
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
}
</style>
