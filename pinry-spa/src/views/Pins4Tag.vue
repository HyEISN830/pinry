<template>
  <div class="pins-for-tag">
    <PHeader></PHeader>
    <CollectionHero
      type="tag"
      :title="filters.tagFilter || ''"
      :count="collectionCount">
    </CollectionHero>
    <Comics
      embedded
      :show-create="false"
      :tag-filter="filters.tagFilter"
      :title="$t('comicsLink')"
      v-on:comics-meta-loaded="onComicsMetaLoaded">
    </Comics>
    <Pins
      :pin-filters="filters"
      v-on:pins-meta-loaded="onPinsMetaLoaded">
    </Pins>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';
import CollectionHero from '../components/CollectionHero.vue';
import Comics from './Comics.vue';

export default {
  name: 'Pins4Tag',
  data() {
    return {
      filters: { tagFilter: null },
      collection: {
        comicsCount: null,
        pinsCount: null,
      },
    };
  },
  components: {
    CollectionHero,
    Comics,
    PHeader,
    Pins,
  },
  computed: {
    collectionCount() {
      if (
        this.collection.comicsCount === null
        && this.collection.pinsCount === null
      ) {
        return null;
      }
      return (this.collection.comicsCount || 0)
        + (this.collection.pinsCount || 0);
    },
  },
  created() {
    this.initializeTag();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { tagFilter: to.params.tag };
    this.collection.comicsCount = null;
    this.collection.pinsCount = null;
    next();
  },
  methods: {
    initializeTag() {
      this.filters = { tagFilter: this.$route.params.tag };
    },
    onComicsMetaLoaded(meta) {
      this.collection.comicsCount = meta.count;
    },
    onPinsMetaLoaded(meta) {
      this.collection.pinsCount = meta.count;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
