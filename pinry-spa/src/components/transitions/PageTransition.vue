<template>
  <div class="page-transition-shell">
    <div :key="routeKey" class="page-transition-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageTransition',
  props: {
    routeKey: {
      type: String,
      default: '',
    },
  },
};
</script>

<style scoped lang="scss">
.page-transition-shell,
.page-transition-content {
  min-height: calc(100vh - var(--nav-height));
  background: transparent;
}
</style>
