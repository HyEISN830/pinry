<template>
  <div class="pin-share-page">
    <PHeader></PHeader>
    <Pins
      :pin-filters="filters"
      :single-pin-view="true"
      :auto-open-preview="true">
    </Pins>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';

export default {
  name: 'Pins4Id',
  data() {
    return {
      filters: { idFilter: null },
    };
  },
  components: {
    PHeader,
    Pins,
  },
  created() {
    this.initialize();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { idFilter: to.params.pinId };
    next();
  },
  methods: {
    initialize() {
      this.filters = { idFilter: this.$route.params.pinId };
    },
  },
};
</script>

<style scoped lang="scss">
.pin-share-page {
  min-height: 100vh;
  background: transparent;
}
</style>
