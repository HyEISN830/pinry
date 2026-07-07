<template>
  <div id="app">
    <router-view/>
    <BackToTopProgress></BackToTopProgress>
  </div>
</template>

<script>
import BackToTopProgress from './components/BackToTopProgress.vue';
import bus from './components/utils/bus';

export default {
  name: 'app',
  components: {
    BackToTopProgress,
  },
  created() {
    bus.bus.$on(bus.events.notify, this.showToast);
  },
  beforeDestroy() {
    bus.bus.$off(bus.events.notify, this.showToast);
  },
  methods: {
    showToast(options) {
      this.$buefy.toast.open(
        Object.assign(
          {
            duration: 5000,
            position: 'is-top',
          },
          options,
        ),
      );
    },
  },
};
</script>

<style lang="scss">
  // Import Bulma's core
  @import "~bulma/sass/utilities/_all";
  // Import Bulma and Buefy styles
  @import "~bulma";
  @import "~buefy/src/scss/buefy";
  html {
    background-color: #F5F5EB;
  }
  .body {
    font-family: 'Open Sans', sans-serif;
  }
</style>
