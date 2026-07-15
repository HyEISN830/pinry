<template>
  <div class="home">
    <PHeader></PHeader>
    <Comics
      embedded
      home-showcase
      :max-columns="4"
      :title="$t('comicsLink')">
    </Comics>
    <section class="section home-pin-heading">
      <div class="container">
        <HomeCollectionStat
          :count="pinCount"
          kind="pin"
          :label="$t('collectionArtworksLabel')"
          :title="$t('pinsLink')">
        </HomeCollectionStat>
      </div>
    </section>
    <Pins v-on:pins-meta-loaded="onPinsMetaLoaded"></Pins>
  </div>
</template>

<script>
import Comics from './Comics.vue';
import HomeCollectionStat from '../components/HomeCollectionStat.vue';
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';

export default {
  name: 'Home',
  components: {
    Comics,
    HomeCollectionStat,
    PHeader,
    Pins,
  },
  data() {
    return {
      pinCount: null,
    };
  },
  methods: {
    onPinsMetaLoaded(meta) {
      this.pinCount = meta.count;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
.home {
  --home-feed-width: min(1260px, calc(100vw - 32px));
}

.home .comics-page.is-embedded {
  min-height: 0;
}
.home .comics-page.is-embedded .comics-section {
  padding-top: var(--space-lg, 24px);
  padding-right: 0;
  padding-bottom: var(--space-lg, 24px);
  padding-left: 0;
}
.home .comics-page.is-embedded .comics-container,
.home-pin-heading .container,
.home > .pins #pins-container {
  box-sizing: border-box;
  width: var(--home-feed-width);
  max-width: var(--home-feed-width);
  margin-right: auto;
  margin-left: auto;
}
.home .comics-page.is-embedded .comics-toolbar {
  padding-right: 0;
  padding-left: 0;
  border-color: transparent;
  background: transparent;
  box-shadow: none;
}
.home .comics-page.is-embedded .comic-grid,
.home .comics-page.is-embedded .comic-skeleton-grid {
  grid-template-columns: repeat(var(--comic-page-limit), minmax(0, 1fr));
  justify-content: stretch;
}
.home > .pins > .section {
  padding-right: 0;
  padding-left: 0;
}
.home-pin-heading {
  padding-top: var(--space-sm, 12px);
  padding-right: 0;
  padding-bottom: var(--space-md, 16px);
  padding-left: 0;
}
@media screen and (max-width: 760px) {
  .home {
    --home-feed-width: calc(100vw - 20px);
  }
}
</style>
