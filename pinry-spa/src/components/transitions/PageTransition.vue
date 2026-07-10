<template>
  <transition name="page-reveal" mode="out-in" appear>
    <slot></slot>
  </transition>
</template>

<script>
export default {
  name: 'PageTransition',
};
</script>
