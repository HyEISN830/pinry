<template>
  <div class="home">
    <PHeader></PHeader>
    <Comics embedded></Comics>
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
</style>
