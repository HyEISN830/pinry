<template>
  <div class="search-page">
    <PHeader></PHeader>
    <section class="section search-shell">
      <div class="container search-container">
        <aside class="search-sidebar">
          <h1>{{ $t("aggregateSearchTitle") }}</h1>
          <div class="search-types">
            <button
              v-for="option in typeOptions"
              :key="option.value"
              class="button"
              type="button"
              :class="{ 'is-primary': activeType === option.value }"
              @click="activeType = option.value">
              {{ option.label }}
            </button>
          </div>
        </aside>
        <main class="search-main">
          <div class="search-card">
            <b-field>
              <b-autocomplete
                ref="tagInput"
                v-model="tagText"
                :data="filteredTags"
                :keep-first="true"
                :open-on-focus="true"
                :placeholder="$t('searchTagPlaceholder')"
                icon="magnify"
                @select="selectTag">
                <template slot="empty">{{ $t("noResultsFound") }}</template>
              </b-autocomplete>
              <p class="control">
                <button
                  class="button is-primary"
                  type="button"
                  :disabled="normalizedTag.length === 0"
                  @click="search">
                  {{ $t("searchButton") }}
                </button>
              </p>
            </b-field>
          </div>
          <div class="search-results" v-if="hasSearched">
            <div class="result-heading">
              {{ $t("searchResultsFor") }} <strong>{{ resultTag }}</strong>
            </div>
            <Comics
              v-if="showComics"
              embedded
              :show-create="false"
              :tag-filter="resultTag"
              :title="$t('comicsLink')">
            </Comics>
            <section class="result-section" v-if="showPins">
              <h2>{{ $t("pinsLink") }}</h2>
              <Pins
                :key="`pins-${resultTag}`"
                :pin-filters="pinFilters">
              </Pins>
            </section>
            <section class="result-section" v-if="showBoards">
              <h2>{{ $t("boardsLink") }}</h2>
              <Boards
                :key="`boards-${resultTag}`"
                :filters="boardFilters">
              </Boards>
            </section>
          </div>
        </main>
      </div>
    </section>
  </div>
</template>

<script>
import API from '../components/api';
import Boards from '../components/Boards.vue';
import Comics from './Comics.vue';
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';

function normalizeTag(text) {
  const [tag] = (text || '').split(/[,\uFF0C\s]+/);
  return (tag || '').trim();
}

export default {
  name: 'Search',
  components: {
    Boards,
    Comics,
    PHeader,
    Pins,
  },
  data() {
    return {
      activeType: 'all',
      hasSearched: false,
      resultTag: '',
      tagOptions: [],
      tagText: '',
    };
  },
  computed: {
    boardFilters() {
      return { boardNameContains: this.resultTag };
    },
    filteredTags() {
      return this.tagOptions.filter(
        option => option.toLowerCase().indexOf(this.normalizedTag.toLowerCase()) >= 0,
      );
    },
    normalizedTag() {
      return normalizeTag(this.tagText);
    },
    pinFilters() {
      return { tagFilter: this.resultTag };
    },
    showBoards() {
      return this.activeType === 'all' || this.activeType === 'board';
    },
    showComics() {
      return this.activeType === 'all' || this.activeType === 'comic';
    },
    showPins() {
      return this.activeType === 'all' || this.activeType === 'pin';
    },
    typeOptions() {
      return [
        { value: 'all', label: this.$t('searchAllOption') },
        { value: 'pin', label: this.$t('pinLink') },
        { value: 'board', label: this.$t('boardLink') },
        { value: 'comic', label: this.$t('comicLink') },
      ];
    },
  },
  watch: {
    tagText(value) {
      const normalized = normalizeTag(value);
      if (value !== normalized && /[,\uFF0C\s]/.test(value)) {
        this.tagText = normalized;
      }
    },
  },
  created() {
    this.fetchTags();
  },
  methods: {
    fetchTags() {
      API.Tag.fetchList().then(
        (resp) => {
          const options = [];
          resp.data.forEach(
            (tag) => {
              options.push(tag.name);
            },
          );
          this.tagOptions = options;
        },
      );
    },
    search() {
      if (this.normalizedTag.length === 0) {
        return;
      }
      this.resultTag = this.normalizedTag;
      this.tagText = this.resultTag;
      this.hasSearched = true;
    },
    selectTag(option) {
      if (!option) {
        return;
      }
      this.tagText = option;
      this.search();
    },
  },
};
</script>

<style scoped lang="scss">
.search-shell {
  padding-top: 1.5rem;
}
.search-container {
  display: grid;
  grid-template-columns: minmax(180px, 230px) minmax(0, 1fr);
  gap: 1.25rem;
}
.search-sidebar {
  align-self: start;
  padding: 1rem;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(16, 24, 40, 0.08);
}
.search-sidebar h1 {
  margin: 0 0 0.85rem;
  color: #22313f;
  font-size: 1.15rem;
  font-weight: 800;
}
.search-types {
  display: grid;
  gap: 0.5rem;
}
.search-types .button {
  justify-content: flex-start;
  border-radius: 7px;
  font-weight: 800;
}
.search-main {
  min-width: 0;
}
.search-card {
  padding: 1rem;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(16, 24, 40, 0.08);
}
.search-card .field {
  margin-bottom: 0;
}
.result-heading {
  margin: 1rem 0 0;
  padding: 0 0.25rem;
  color: #64748b;
  font-size: 1rem;
}
.result-heading strong {
  color: #22313f;
}
.result-section {
  margin-top: 0.5rem;
}
.result-section h2 {
  margin: 1.25rem 0 -0.25rem;
  padding: 0 0.75rem;
  color: #22313f;
  font-size: 1.35rem;
  font-weight: 800;
}
@media screen and (max-width: 760px) {
  .search-container {
    display: block;
  }
  .search-sidebar {
    margin-bottom: 1rem;
  }
  .search-types {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
