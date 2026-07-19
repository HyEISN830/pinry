<template>
  <div id="app">
    <PHeader app-shell class="app-global-header"></PHeader>
    <main class="app-route-content">
      <PageTransition :route-key="routeTransitionKey">
        <router-view :key="routeTransitionKey"/>
      </PageTransition>
    </main>
    <BackToTopProgress></BackToTopProgress>
    <GalleryPageOpening :route-key="routeTransitionKey"></GalleryPageOpening>
  </div>
</template>

<script>
import BackToTopProgress from './components/BackToTopProgress.vue';
import GalleryPageOpening from './components/transitions/GalleryPageOpening.vue';
import PHeader from './components/PHeader.vue';
import PageTransition from './components/transitions/PageTransition.vue';
import bus from './components/utils/bus';
import theme from './components/utils/theme';

export default {
  name: 'app',
  components: {
    BackToTopProgress,
    GalleryPageOpening,
    PHeader,
    PageTransition,
  },
  computed: {
    routeTransitionKey() {
      const params = this.$route.params || {};
      const stableParams = Object.keys(params).sort().map(
        key => `${key}:${params[key]}`,
      ).join('|');
      return `${this.$route.name || this.$route.path}:${stableParams}`;
    },
  },
  created() {
    theme.applySavedTheme();
    this.$nextTick(() => {
      const meta = document.querySelector('meta[name="theme-color"]');
      if (!meta) return;
      const appBackground = window.getComputedStyle(document.documentElement)
        .getPropertyValue('--app-bg')
        .trim();
      if (appBackground) meta.setAttribute('content', appBackground);
    });
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
  @import "./components/utils/design-tokens";
  @import "./components/utils/motion-system";
  @import "./components/utils/user-shell";
  @import "./components/utils/collection-count-pill";

  :root {
    --app-bg: #f6f7fb;
    --surface-1: #ffffff;
    --surface-2: #f8fafc;
    --surface-card: #ffffff;
    --surface-accent: rgba(232, 121, 185, 0.12);
    --text-strong: #1f2937;
    --text-muted: #64748b;
    --line-soft: #e5eaf2;
    --shadow-soft: 0 14px 36px rgba(16, 24, 40, 0.12);
    --accent: #e879b9;
    --accent-strong: #d94691;
    --accent-foreground: #d94691;
    --accent-soft: rgba(232, 121, 185, 0.14);
    --accent-border: rgba(232, 121, 185, 0.34);
    --accent-shadow: 0 16px 38px rgba(217, 70, 145, 0.18);
    --accent-text: #ffffff;
    --accent-text-shadow: 0 1px 2px rgba(15, 23, 42, 0.24);
    --accent-fill: #d94691;
    --accent-fill-hover: #e879b9;
    --accent-control-text: #ffffff;
    --accent-control-fill: #d94691;
    --accent-control-fill-hover: #e879b9;
    --accent-control-gradient: linear-gradient(180deg, #e879b9 0%, #d94691 100%);
    --accent-control-gradient-horizontal: linear-gradient(90deg, #e879b9 0%, #d94691 100%);
    --accent-control-gradient-vertical: linear-gradient(180deg, #e879b9 0%, #d94691 100%);
    --accent-control-gradient-diagonal: linear-gradient(135deg, #e879b9 0%, #d94691 100%);
    --accent-gradient: linear-gradient(180deg, #e879b9 0%, #d94691 100%);
    --accent-gradient-horizontal: linear-gradient(90deg, #e879b9 0%, #d94691 100%);
    --accent-gradient-vertical: linear-gradient(180deg, #e879b9 0%, #d94691 100%);
    --accent-gradient-diagonal: linear-gradient(135deg, #e879b9 0%, #d94691 100%);
    --accent-progress: linear-gradient(90deg, #e879b9 0%, #d94691 100%);
    --accent-soft-gradient: linear-gradient(135deg, rgba(232, 121, 185, 0.2) 0%, rgba(217, 70, 145, 0.16) 100%);
    --accent-swatch: #e879b9;
    --theme-glow: rgba(232, 121, 185, 0.24);
    --theme-glow-strong: rgba(232, 121, 185, 0.36);
    --theme-glow-start: rgba(232, 121, 185, 0.36);
    --theme-glow-end: rgba(217, 70, 145, 0.24);
    --theme-backdrop: linear-gradient(150deg, rgba(232, 121, 185, 0.14) 0%, rgba(217, 70, 145, 0.1) 48%, transparent 78%);
    --skeleton-base: #f7edf4;
    --skeleton-highlight: #ffffff;
    --nav-height: calc(80px + env(safe-area-inset-top));
  }
  html[data-theme="dark"] {
    --app-bg: #0f1218;
    --surface-1: #171b24;
    --surface-2: #11151d;
    --surface-card: #171b24;
    --surface-accent: rgba(239, 124, 186, 0.12);
    --text-strong: #f4f7fb;
    --text-muted: #9aa8ba;
    --line-soft: #283142;
    --shadow-soft: 0 18px 46px rgba(0, 0, 0, 0.36);
    --skeleton-base: #1d2531;
    --skeleton-highlight: #283142;
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
    font-family: var(--font-sans);
    font-synthesis: none;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }
  #app {
    min-height: 100vh;
    background:
      radial-gradient(circle at top left, color-mix(in srgb, var(--theme-glow-start) 68%, transparent), transparent 420px),
      radial-gradient(circle at 92% 12%, color-mix(in srgb, var(--theme-glow-end) 58%, transparent), transparent 360px),
      var(--theme-backdrop),
      var(--app-bg);
  }
  .app-global-header {
    isolation: isolate;
  }
  .app-route-content {
    min-height: 100vh;
    padding-top: var(--nav-height);
  }
  @media screen and (max-width: 760px) {
    :root {
      --nav-height: calc(66px + env(safe-area-inset-top));
    }
  }
  a {
    color: var(--accent-foreground);
  }
  .button.is-primary {
    border-color: var(--accent-strong) !important;
    color: var(--color-accent-control-text) !important;
    text-shadow: none;
    background: var(--color-accent-fill) !important;
  }
  .button.is-primary:hover {
    border-color: var(--accent) !important;
    background: var(--color-accent-fill-hover) !important;
  }
  .button.is-light {
    border-color: var(--line-soft);
    color: var(--text-strong);
    background-color: var(--surface-2);
  }
  .button.is-light:hover {
    border-color: var(--accent);
    color: var(--accent-foreground);
    background: var(--accent-soft-gradient);
  }
  .button.is-link,
  .button.is-info {
    border-color: var(--accent-strong) !important;
    color: var(--color-accent-control-text) !important;
    text-shadow: none;
    background: var(--color-accent-fill) !important;
  }
  .button.is-link:hover,
  .button.is-info:hover {
    border-color: var(--accent) !important;
    background: var(--color-accent-fill-hover) !important;
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
  .box {
    color: var(--text-strong);
    border: 1px solid var(--line-soft);
    background: var(--surface-card);
    box-shadow: var(--shadow-card);
  }
  .modal-card {
    color: var(--text-strong);
    background: var(--surface-card);
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
    background: transparent;
  }
  .modal-card-body {
    background: var(--surface-card);
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
    color: var(--accent-foreground);
    background: var(--accent-soft-gradient);
  }
  .tabs.is-toggle li.is-active a {
    border-color: var(--accent-strong);
    color: var(--color-accent-control-text);
    text-shadow: none;
    background: var(--color-accent-fill);
  }
  .pin-preview-at-home .modal-content {
    display: flex;
    align-items: center;
    width: min(96vw, 1600px);
    min-width: 0;
    height: 100vh;
    height: 100dvh;
    max-height: 100vh;
    max-height: 100dvh;
    margin: 0 auto;
    overflow: hidden;
  }
  .pin-preview-at-home {
    z-index: 140;
    overflow: hidden;
  }
  .pin-preview-at-home .modal-close {
    z-index: 150;
  }
</style>
