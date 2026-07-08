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
    --scroll-ring-start: #ff9fd0;
    --scroll-ring-mid: #ef7cba;
    --scroll-ring-end: #db4e9c;
    --scroll-ring-track: #e5eaf2;
  }
  html[data-theme="dark"] {
    --app-bg: #0f1218;
    --surface-1: #171b24;
    --surface-2: #11151d;
    --text-strong: #f4f7fb;
    --text-muted: #9aa8ba;
    --line-soft: #283142;
    --shadow-soft: 0 18px 46px rgba(0, 0, 0, 0.36);
    --scroll-ring-track: #30384a;
  }
  html[data-accent="elysia"] {
    --accent: #ef7cba;
    --accent-strong: #db4e9c;
    --accent-soft: rgba(239, 124, 186, 0.16);
    --scroll-ring-start: #ff9fd0;
    --scroll-ring-mid: #ef7cba;
    --scroll-ring-end: #db4e9c;
  }
  html[data-accent="eden"] {
    --accent: #d5a344;
    --accent-strong: #b88416;
    --accent-soft: rgba(213, 163, 68, 0.18);
    --scroll-ring-start: #ffd681;
    --scroll-ring-mid: #d5a344;
    --scroll-ring-end: #b88416;
  }
  html[data-accent="mobius"] {
    --accent: #32b47b;
    --accent-strong: #168a5a;
    --accent-soft: rgba(50, 180, 123, 0.16);
    --scroll-ring-start: #82e8b8;
    --scroll-ring-mid: #32b47b;
    --scroll-ring-end: #168a5a;
  }
  html[data-accent="kevin"] {
    --accent: #6ab7ff;
    --accent-strong: #2788dd;
    --accent-soft: rgba(106, 183, 255, 0.16);
    --scroll-ring-start: #a7d8ff;
    --scroll-ring-mid: #6ab7ff;
    --scroll-ring-end: #2788dd;
  }
  html[data-accent="griseo"] {
    --accent: #7c8cff;
    --accent-strong: #5366e6;
    --accent-soft: rgba(124, 140, 255, 0.16);
    --scroll-ring-start: #b2bdff;
    --scroll-ring-mid: #7c8cff;
    --scroll-ring-end: #5366e6;
  }
  html[data-accent="pardofelis"] {
    --accent: #f2a65e;
    --accent-strong: #dc7f24;
    --accent-soft: rgba(242, 166, 94, 0.18);
    --scroll-ring-start: #ffc889;
    --scroll-ring-mid: #f2a65e;
    --scroll-ring-end: #dc7f24;
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
    padding-top: var(--nav-height);
    background:
      radial-gradient(circle at top left, var(--accent-soft), transparent 320px),
      var(--app-bg);
  }
  @media screen and (max-width: 760px) {
    :root {
      --nav-height: 58px;
    }
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
  .button.is-light {
    border-color: var(--line-soft);
    color: var(--text-strong);
    background-color: var(--surface-2);
  }
  .button.is-light:hover {
    border-color: var(--accent);
    color: var(--accent-strong);
    background-color: var(--accent-soft);
  }
  .button.is-link,
  .button.is-info {
    border-color: var(--accent-strong);
    background-color: var(--accent-strong);
  }
  .button.is-link:hover,
  .button.is-info:hover {
    border-color: var(--accent);
    background-color: var(--accent);
  }
  .input,
  .textarea,
  .select select,
  .taginput .taginput-container.is-focusable {
    border-color: var(--line-soft);
    color: var(--text-strong);
    background-color: var(--surface-1);
  }
  .input:focus,
  .textarea:focus,
  .select select:focus,
  .taginput .taginput-container.is-focusable:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 0.125em var(--accent-soft);
  }
  .label,
  .modal-card-title,
  .card-header-title {
    color: var(--text-strong);
  }
  .help,
  .subtitle {
    color: var(--text-muted);
  }
  .card,
  .modal-card,
  .box {
    color: var(--text-strong);
    background: var(--surface-1);
  }
  .modal-card-head,
  .modal-card-foot,
  .card-header {
    border-color: var(--line-soft);
    background: var(--surface-2);
  }
  .modal-card-body,
  .card-content {
    color: var(--text-strong);
    background: var(--surface-1);
  }
  .dropdown-content,
  .autocomplete .dropdown-content {
    border: 1px solid var(--line-soft);
    background: var(--surface-1);
    box-shadow: var(--shadow-soft);
  }
  .dropdown-item,
  .autocomplete .dropdown-item {
    color: var(--text-strong);
  }
  .dropdown-item:hover,
  .autocomplete .dropdown-item:hover {
    color: var(--accent-strong);
    background: var(--accent-soft);
  }
  .tabs.is-toggle li.is-active a {
    border-color: var(--accent-strong);
    color: var(--accent-text);
    background-color: var(--accent-strong);
  }
  .pin-preview-at-home .modal-content {
    width: min(96vw, 1600px);
    max-height: 96vh;
    overflow: visible;
  }
</style>
