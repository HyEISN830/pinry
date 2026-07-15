<template>
  <div class="pins-for-tag collection-detail-page">
    <PHeader></PHeader>
    <CollectionHero
      type="tag"
      :title="filters.tagFilter || ''"
      :count="collectionCount">
    </CollectionHero>
    <Comics
      embedded
      :show-create="false"
      :max-columns="4"
      :tag-filter="filters.tagFilter"
      :title="$t('comicsLink')"
      v-on:comics-meta-loaded="onComicsMetaLoaded">
    </Comics>
    <section class="section tag-pin-heading collection-detail-pin-heading">
      <div class="container">
        <h1>{{ $t("pinsLink") }}</h1>
        <p v-if="collection.pinsCount !== null">
          {{ collection.pinsCount }} {{ $t("collectionArtworksLabel") }}
        </p>
      </div>
    </section>
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
.tag-pin-heading {
  padding-top: 0.5rem;
  padding-bottom: 0;
}
.tag-pin-heading h1 {
  margin: 0;
  color: var(--color-accent-foreground);
  font-size: 1.6rem;
  font-weight: 800;
}
.tag-pin-heading p {
  margin: 0.25rem 0 0;
  color: #64748b;
  font-size: 0.95rem;
}
</style>
