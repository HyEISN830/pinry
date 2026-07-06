<template>
  <div class="home">
    <PHeader></PHeader>
    <Comics embedded :title="$t('comicsLink')"></Comics>
    <section class="section home-pin-heading">
      <div class="container">
        <h1>{{ $t("pinsLink") }}</h1>
      </div>
    </section>
    <Pins></Pins>
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
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.home-pin-heading {
  padding-top: 0.5rem;
  padding-bottom: 0;
}
.home-pin-heading h1 {
  margin: 0;
  color: #22313f;
  font-size: 1.6rem;
  font-weight: 800;
}
</style>
