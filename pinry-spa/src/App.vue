<template>
  <div id="app">
    <router-view/>
    <BackToTopProgress></BackToTopProgress>
  </div>
</template>

<script>
import BackToTopProgress from './components/BackToTopProgress.vue';
import bus from './components/utils/bus';
import theme from './components/utils/theme';

export default {
  name: 'app',
  components: {
    BackToTopProgress,
  },
  created() {
    theme.applySavedTheme();
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

  :root {
    --app-bg: #f6f7fb;
    --surface-1: #ffffff;
    --surface-2: #f8fafc;
    --text-strong: #1f2937;
    --text-muted: #64748b;
    --line-soft: #e5eaf2;
    --shadow-soft: 0 14px 36px rgba(16, 24, 40, 0.12);
    --accent: #e879b9;
    --accent-strong: #d94691;
    --accent-soft: rgba(232, 121, 185, 0.14);
    --accent-text: #ffffff;
    --nav-height: 64px;
  }
  html[data-theme="dark"] {
    --app-bg: #0f1218;
    --surface-1: #171b24;
    --surface-2: #11151d;
    --text-strong: #f4f7fb;
    --text-muted: #9aa8ba;
    --line-soft: #283142;
    --shadow-soft: 0 18px 46px rgba(0, 0, 0, 0.36);
  }
  html[data-accent="elysia"] {
    --accent: #ef7cba;
    --accent-strong: #db4e9c;
    --accent-soft: rgba(239, 124, 186, 0.16);
  }
  html[data-accent="eden"] {
    --accent: #d5a344;
    --accent-strong: #b88416;
    --accent-soft: rgba(213, 163, 68, 0.18);
  }
  html[data-accent="mobius"] {
    --accent: #32b47b;
    --accent-strong: #168a5a;
    --accent-soft: rgba(50, 180, 123, 0.16);
  }
  html[data-accent="kevin"] {
    --accent: #6ab7ff;
    --accent-strong: #2788dd;
    --accent-soft: rgba(106, 183, 255, 0.16);
  }
  html[data-accent="griseo"] {
    --accent: #7c8cff;
    --accent-strong: #5366e6;
    --accent-soft: rgba(124, 140, 255, 0.16);
  }
  html[data-accent="pardofelis"] {
    --accent: #f2a65e;
    --accent-strong: #dc7f24;
    --accent-soft: rgba(242, 166, 94, 0.18);
  }
  html {
    background-color: var(--app-bg);
    color: var(--text-strong);
    scroll-behavior: smooth;
  }
  body {
    min-height: 100vh;
    background: var(--app-bg);
    color: var(--text-strong);
    font-family: 'Open Sans', sans-serif;
  }
  #app {
    min-height: 100vh;
    background:
      radial-gradient(circle at top left, var(--accent-soft), transparent 320px),
      var(--app-bg);
  }
  a {
    color: var(--accent-strong);
  }
  .button.is-primary {
    border-color: var(--accent-strong);
    background-color: var(--accent-strong);
  }
  .button.is-primary:hover {
    border-color: var(--accent);
    background-color: var(--accent);
  }
  .card,
  .modal-card,
  .box {
    color: var(--text-strong);
    background: var(--surface-1);
  }
  .pin-preview-at-home .modal-content {
    width: min(96vw, 1600px);
    max-height: 96vh;
    overflow: visible;
  }
</style>
