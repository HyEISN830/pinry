<template>
  <div class="home">
    <PHeader></PHeader>
    <Comics embedded :title="$t('comicsLink')"></Comics>
    <section class="section home-pin-heading">
      <div class="container">
        <h1>{{ $t("pinsLink") }}</h1>
        <p v-if="pinCount !== null">
          {{ pinCount }} {{ $t("collectionArtworksLabel") }}
        </p>
      </div>
    </section>
    <Pins :max-columns="6" v-on:pins-meta-loaded="onPinsMetaLoaded"></Pins>
  </div>
</template>

<script>
import Comics from './Comics.vue';
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';

export default {
  name: 'Home',
  components: {
    Comics,
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
@import '../components/utils/grid-layout';

.home .comics-page.is-embedded {
  min-height: 0;
}
.home .comics-page.is-embedded .comics-section {
  padding-top: var(--space-lg, 24px);
  padding-bottom: var(--space-lg, 24px);
}
.home-pin-heading {
  padding-top: var(--space-sm, 12px);
  padding-bottom: var(--space-md, 16px);
}
.home-pin-heading h1 {
  margin: 0;
  color: var(--text-strong, #22313f);
  font-size: 1.6rem;
  font-weight: 800;
}
.home-pin-heading p {
  margin: 0.25rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 0.95rem;
}
@include screen-grid-layout(".home-pin-heading .container");
</style>
