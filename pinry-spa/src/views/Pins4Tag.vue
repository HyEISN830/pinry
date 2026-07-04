<template>
  <div class="pins-for-tag">
    <PHeader></PHeader>
    <CollectionHero
      type="tag"
      :title="filters.tagFilter || ''"
      :count="collection.count">
    </CollectionHero>
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

export default {
  name: 'Pins4Tag',
  data() {
    return {
      filters: { tagFilter: null },
      collection: {
        count: null,
      },
    };
  },
  components: {
    CollectionHero,
    PHeader,
    Pins,
  },
  created() {
    this.initializeTag();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { tagFilter: to.params.tag };
    this.collection.count = null;
    next();
  },
  methods: {
    initializeTag() {
      this.filters = { tagFilter: this.$route.params.tag };
    },
    onPinsMetaLoaded(meta) {
      this.collection.count = meta.count;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
