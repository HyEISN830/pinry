<template>
  <div class="search-panel motion-fade-up">
    <div class="filter-selector">
      <div class="panel-kicker">{{ $t("chooseFilterPlaceholder") }}</div>
      <b-field class="filter-field">
        <b-select
          expanded
          v-bind:placeholder="$t('chooseFilterPlaceholder')"
          v-model="filterType">
          <option value="Tag">{{ $t("SearchPanelTagOption") }}</option>
          <option value="Board">{{ $t("SearchPanelBoardOption") }}</option>
        </b-select>
      </b-field>

      <b-field v-if="filterType === 'Tag'" class="filter-field is-stacked">
        <b-autocomplete
          class="search-input"
          v-model="name"
          :data="filteredDataArray"
          :keep-first="true"
          :loading="loadingTags"
          :open-on-focus="true"
          v-bind:placeholder="$t('selectFilterPlaceholder')"
          icon="magnify"
          @select="option => selected = option">
          <template slot="empty">
            <span v-if="loadingTags">...</span>
            <span v-else>{{ $t("noResultsFound") }}</span>
          </template>
        </b-autocomplete>
      </b-field>

      <form
        v-if="filterType === 'Board'"
        class="board-filter"
        @submit.prevent="searchBoard">
        <b-input
          class="search-input"
          type="search"
          v-model="boardText"
          v-bind:placeholder="$t('searchBoardPlaceholder')"
          icon="magnify">
        </b-input>
        <b-button
          native-type="submit"
          class="button is-primary"
          :disabled="boardText.trim() === ''">
          {{ $t("searchButton") }}
        </b-button>
      </form>

      <p class="panel-state is-error" v-if="tagFetchFailed">
        {{ $t("tagLoadError") }}
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'FilterSelector',
  data() {
    return {
      boardText: '',
      filterType: null,
      loadingTags: false,
      name: '',
      options: {
        Tag: [],
      },
      selected: null,
      selectedOption: [],
      tagFetchFailed: false,
    };
  },
  methods: {
    selectOption(filterName) {
      this.name = '';
      this.boardText = '';
      if (filterName === 'Tag') {
        this.selectedOption = this.options.Tag;
      } else {
        this.selectedOption = [];
      }
    },
    searchBoard() {
      const selected = this.boardText.trim();
      if (selected === '') {
        return;
      }
      this.$emit(
        'selected',
        { filterType: this.filterType, selected },
      );
    },
  },
  watch: {
    filterType(newVal) {
      this.selectOption(newVal);
    },
    selected(newVal) {
      if (!newVal) {
        return;
      }
      this.$emit(
        'selected',
        { filterType: this.filterType, selected: newVal },
      );
    },
  },
  computed: {
    filteredDataArray() {
      return this.selectedOption.filter(
        (option) => {
          const ret = option
            .toString()
            .toLowerCase()
            .indexOf(this.name.toLowerCase()) >= 0;
          return ret;
        },
      );
    },
  },
  created() {
    this.loadingTags = true;
    api.Tag.fetchList().then(
      (resp) => {
        const options = [];
        resp.data.forEach(
          (tag) => {
            options.push(tag.name);
          },
        );
        this.options.Tag = options;
        this.loadingTags = false;
      },
      () => {
        this.loadingTags = false;
        this.tagFetchFailed = true;
      },
    );
  },
};
</script>

<style scoped="scoped" lang="scss">
@import "../utils/motion-mixins";

.search-panel {
  width: 100%;
}
.filter-selector {
  display: grid;
  gap: var(--space-xs);
  padding: var(--space-sm);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
}
.panel-kicker {
  color: var(--color-text-muted);
  font-size: 0.74rem;
  font-weight: 950;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.filter-field {
  margin-bottom: 0;
}
.search-input {
  width: 100%;
}
.board-filter {
  display: grid;
  gap: var(--space-xs);
}
.board-filter .button {
  border-radius: var(--radius-sm);
  font-weight: 950;
  @include hover-scale(1.018, -2px);
}
.panel-state {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.82rem;
  line-height: 1.35;
}
.panel-state.is-error {
  color: var(--color-accent-strong);
}
::v-deep .select select,
::v-deep .input {
  min-height: 40px;
  border-color: var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: var(--color-surface-1);
  box-shadow: none;
}
::v-deep .select select:focus,
::v-deep .input:focus {
  @include focus-ring;
}
</style>
