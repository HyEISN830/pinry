<template>
  <header
    v-if="appShell"
    class="p-header"
    :class="{
      'is-open': navOpen,
      'is-hidden': navHidden
    }"
    :style="navStyle">
    <nav class="nav-shell" role="navigation" aria-label="main navigation">
      <router-link
        class="brand"
        :to="{ name: 'home' }"
        @click.native="closeMenu">
        <span class="brand-logo">
          <img src="../assets/logo-dark.png" alt="Pinry">
        </span>
        <span class="brand-copy" aria-hidden="true">
          <strong>Pinry</strong>
          <small>HyEISN Gallery</small>
        </span>
      </router-link>

      <div class="nav-primary" aria-label="primary navigation">
        <a class="nav-link" href="https://hyeisn.cn/">HyEISN's</a>
        <router-link
          class="nav-link"
          :to="{ name: 'comics' }"
          @click.native="closeMenu">
          {{ $t("comicsLink") }}
        </router-link>
        <router-link
          class="nav-link is-search"
          :to="{ name: 'search' }"
          :title="$t('searchButton')"
          @click.native="closeMenu">
          <b-icon icon="magnify" custom-size="mdi-20px"></b-icon>
          <span>{{ $t("searchButton") }}</span>
        </router-link>
      </div>

      <div class="nav-actions" aria-label="toolbar navigation">
        <div
          v-if="user.loggedIn"
          class="nav-group"
          :class="{ 'is-active': isDropdownOpen('create') }"
          @mouseenter="openDropdown('create')"
          @mouseleave="scheduleDropdownClose"
          @focusin="openDropdown('create')"
          @focusout="scheduleDropdownClose">
          <button
            class="nav-pill"
            type="button"
            aria-haspopup="true"
            :aria-expanded="isDropdownOpen('create') ? 'true' : 'false'"
            @click.stop="toggleDropdown('create')">
            <b-icon icon="plus-circle-outline" custom-size="mdi-18px"></b-icon>
            <span>{{ $t("createLink") }}</span>
          </button>
          <div class="nav-popover" @click.stop>
            <button type="button" @click="createPin">{{ $t("pinLink") }}</button>
            <button type="button" @click="createBoard">{{ $t("boardLink") }}</button>
            <button type="button" @click="createComic">{{ $t("comicLink") }}</button>
          </div>
        </div>

        <div
          v-if="user.loggedIn"
          class="nav-group"
          :class="{ 'is-active': isDropdownOpen('mine') }"
          @mouseenter="openDropdown('mine')"
          @mouseleave="scheduleDropdownClose"
          @focusin="openDropdown('mine')"
          @focusout="scheduleDropdownClose">
          <button
            class="nav-pill"
            type="button"
            aria-haspopup="true"
            :aria-expanded="isDropdownOpen('mine') ? 'true' : 'false'"
            @click.stop="toggleDropdown('mine')">
            <b-icon icon="account-circle-outline" custom-size="mdi-18px"></b-icon>
            <span>{{ $t("myLink") }}</span>
          </button>
          <div class="nav-popover" @click.stop>
            <router-link
              :to="{ name: 'user', params: {user: user.meta.username} }"
              @click.native="closeDropdown">
              <b-icon icon="image-outline" custom-size="mdi-18px"></b-icon>
              <span>{{ $t("pinsLink") }}</span>
            </router-link>
            <router-link
              :to="{ name: 'boards4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              <b-icon icon="folder-multiple-image" custom-size="mdi-18px"></b-icon>
              <span>{{ $t("boardsLink") }}</span>
            </router-link>
            <router-link
              :to="{ name: 'comics4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              <b-icon icon="book-open-page-variant-outline" custom-size="mdi-18px"></b-icon>
              <span>{{ $t("comicsLink") }}</span>
            </router-link>
            <router-link
              :to="{ name: 'profile4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              <b-icon icon="account-outline" custom-size="mdi-18px"></b-icon>
              <span>{{ $t("profileLink") }}</span>
            </router-link>
          </div>
        </div>

        <div
          class="nav-group theme-group"
          :class="{ 'is-active': isDropdownOpen('theme') }"
          @mouseenter="openDropdown('theme')"
          @mouseleave="scheduleDropdownClose"
          @focusin="openDropdown('theme')"
          @focusout="scheduleDropdownClose">
          <button
            class="nav-pill is-icon"
            type="button"
            aria-haspopup="true"
            :aria-expanded="isDropdownOpen('theme') ? 'true' : 'false'"
            :title="$t('themeSettingsLabel')"
            @click.stop="toggleDropdown('theme')">
            <b-icon icon="palette" custom-size="mdi-20px"></b-icon>
          </button>
          <div class="nav-popover theme-popover" @click.stop>
            <button
              class="theme-mode"
              type="button"
              @click="toggleThemeMode">
              <span>
                {{ themeState.mode === 'dark' ? $t("darkThemeLabel") : $t("lightThemeLabel") }}
              </span>
              <span
                class="mode-switch"
                :class="{ 'is-on': themeState.mode === 'dark' }"
                aria-hidden="true">
                <span></span>
              </span>
            </button>
            <button
              class="theme-mode motion-preference"
              type="button"
              role="switch"
              :aria-checked="reduceMotion ? 'true' : 'false'"
              :aria-label="$t('reduceMotionLabel')"
              @click="toggleReduceMotion">
              <span>{{ $t("reduceMotionLabel") }}</span>
              <span
                class="mode-switch"
                :class="{ 'is-on': reduceMotion }"
                aria-hidden="true">
                <span></span>
              </span>
            </button>
            <div class="accent-grid">
              <button
                v-for="accent in accentOptions"
                :key="accent.value"
                class="accent-swatch"
                type="button"
                :class="[`is-${accent.value}`, { 'is-active': themeState.accent === accent.value }]"
                :title="accent.label"
                @click.stop="setAccent(accent.value)">
              </button>
            </div>
          </div>
        </div>

        <div
          class="nav-group"
          :class="{ 'is-active': isDropdownOpen('language') }"
          @mouseenter="openDropdown('language')"
          @mouseleave="scheduleDropdownClose"
          @focusin="openDropdown('language')"
          @focusout="scheduleDropdownClose">
          <button
            class="nav-pill is-icon"
            type="button"
            aria-haspopup="true"
            :aria-expanded="isDropdownOpen('language') ? 'true' : 'false'"
            :title="$t('languageLabel')"
            @click.stop="toggleDropdown('language')">
            <b-icon icon="translate" custom-size="mdi-20px"></b-icon>
          </button>
          <div class="nav-popover" @click.stop>
            <button
              v-for="locale in $i18n.availableLocales"
              :key="`locale-${locale}`"
              type="button"
              @click="setLocale(locale)">
              {{ langs[locale] }}
            </button>
          </div>
        </div>

        <button
          v-show="!user.loggedIn"
          class="nav-pill"
          type="button"
          @click="signUp">
          {{ $t("signUpLink") }}
        </button>
        <button
          v-show="!user.loggedIn"
          class="nav-pill"
          type="button"
          @click="logIn">
          {{ $t("logInLink") }}
        </button>
        <button
          v-show="user.loggedIn"
          class="nav-pill"
          type="button"
          @click="logOut">
          {{ $t("logOutLink") }}
        </button>
      </div>

      <button
        class="mobile-toggle"
        :class="{ 'is-active': active }"
        type="button"
        :aria-label="$t('menuLabel')"
        :aria-expanded="active ? 'true' : 'false'"
        aria-controls="pinry-mobile-panel"
        @click="toggleMenu">
        <span></span>
        <span></span>
      </button>
    </nav>

    <div class="mobile-backdrop" v-if="active" @click="closeMenu"></div>
    <div class="mobile-panel" id="pinry-mobile-panel" v-if="active">
      <section class="mobile-section is-primary">
        <router-link :to="{ name: 'search' }" @click.native="closeMenu">
          <b-icon icon="magnify" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("searchButton") }}</span>
        </router-link>
        <router-link :to="{ name: 'comics' }" @click.native="closeMenu">
          <b-icon icon="book-open-page-variant-outline" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("comicsLink") }}</span>
        </router-link>
      </section>

      <section class="mobile-section" v-if="user.loggedIn">
        <button type="button" @click="createPin">{{ $t("pinLink") }}</button>
        <button type="button" @click="createBoard">{{ $t("boardLink") }}</button>
        <button type="button" @click="createComic">{{ $t("comicLink") }}</button>
      </section>

      <section class="mobile-section" v-if="user.loggedIn">
        <router-link
          :to="{ name: 'user', params: {user: user.meta.username} }"
          @click.native="closeMenu">
          <b-icon icon="image-outline" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("pinsLink") }}</span>
        </router-link>
        <router-link
          :to="{ name: 'boards4user', params: {username: user.meta.username} }"
          @click.native="closeMenu">
          <b-icon icon="folder-multiple-image" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("boardsLink") }}</span>
        </router-link>
        <router-link
          :to="{ name: 'comics4user', params: {username: user.meta.username} }"
          @click.native="closeMenu">
          <b-icon icon="book-open-page-variant-outline" custom-size="mdi-18px"></b-icon>
          <span>{{ $t("comicsLink") }}</span>
        </router-link>
      </section>

      <section class="mobile-section is-preferences">
        <button class="mobile-theme-toggle" type="button" @click="toggleThemeMode">
          <span>
            {{ themeState.mode === 'dark' ? $t("darkThemeLabel") : $t("lightThemeLabel") }}
          </span>
          <span
            class="mode-switch"
            :class="{ 'is-on': themeState.mode === 'dark' }"
            aria-hidden="true">
            <span></span>
          </span>
        </button>
        <button
          class="mobile-theme-toggle motion-preference"
          type="button"
          role="switch"
          :aria-checked="reduceMotion ? 'true' : 'false'"
          :aria-label="$t('reduceMotionLabel')"
          @click="toggleReduceMotion">
          <span>{{ $t("reduceMotionLabel") }}</span>
          <span
            class="mode-switch"
            :class="{ 'is-on': reduceMotion }"
            aria-hidden="true">
            <span></span>
          </span>
        </button>
        <div class="mobile-accent-row">
          <button
            v-for="accent in accentOptions"
            :key="`mobile-${accent.value}`"
            class="accent-swatch"
            type="button"
            :class="[`is-${accent.value}`, { 'is-active': themeState.accent === accent.value }]"
            :title="accent.label"
            @click="setAccent(accent.value)">
          </button>
        </div>
        <div class="mobile-language-row">
          <button
            v-for="locale in $i18n.availableLocales"
            :key="`mobile-locale-${locale}`"
            type="button"
            @click="setLocale(locale)">
            {{ langs[locale] }}
          </button>
        </div>
      </section>

      <section class="mobile-section is-account">
        <button v-show="!user.loggedIn" type="button" @click="signUp">{{ $t("signUpLink") }}</button>
        <button v-show="!user.loggedIn" type="button" @click="logIn">{{ $t("logInLink") }}</button>
        <button v-show="user.loggedIn" type="button" @click="logOut">{{ $t("logOutLink") }}</button>
      </section>
    </div>
  </header>
</template>

<script>
import localeUtils from '@/components/utils/i18n';
import api from './api';
import modals from './modals';
import motionPreference from './utils/motionPreference';
import theme from './utils/theme';

const NAV_HIDE_DISTANCE = 96;
const NAV_SHOW_DISTANCE = 62;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export default {
  name: 'p-header',
  props: {
    appShell: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      accentOptions: theme.accentOptions,
      active: false,
      activeDropdown: null,
      dropdownCloseTimer: null,
      langs: localeUtils.langCode2Name,
      lastScrollTop: 0,
      navHidden: false,
      navProgress: 0,
      pinnedDropdown: null,
      scrollTicking: false,
      reduceMotion: motionPreference.readMotionPreference(),
      themeState: theme.readTheme(),
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    navOpen() {
      return this.active
        || this.activeDropdown !== null
        || this.pinnedDropdown !== null;
    },
    navStyle() {
      const progress = this.navOpen ? 0 : this.navProgress;
      const opacity = 1 - progress;
      const scale = 1 - (progress * 0.018);
      const offsetPercent = (-108 * progress).toFixed(2);
      const offsetPixels = Math.round(18 * progress);
      return {
        '--nav-opacity': opacity.toFixed(3),
        '--nav-offset': `calc(${offsetPercent}% - ${offsetPixels}px)`,
        '--nav-scale': scale.toFixed(4),
      };
    },
  },
  methods: {
    clearDropdownCloseTimer() {
      if (this.dropdownCloseTimer) {
        window.clearTimeout(this.dropdownCloseTimer);
        this.dropdownCloseTimer = null;
      }
    },
    closeDropdown() {
      this.clearDropdownCloseTimer();
      this.activeDropdown = null;
      this.pinnedDropdown = null;
    },
    closeMenu() {
      this.active = false;
      this.closeDropdown();
    },
    handleDocumentClick(event) {
      if (!this.$el.contains(event.target)) {
        this.closeDropdown();
      }
    },
    isDropdownOpen(name) {
      return this.activeDropdown === name || this.pinnedDropdown === name;
    },
    revealNav() {
      this.navHidden = false;
      this.navProgress = 0;
    },
    openDropdown(name) {
      this.clearDropdownCloseTimer();
      this.activeDropdown = name;
      this.revealNav();
    },
    scheduleDropdownClose() {
      if (this.pinnedDropdown) {
        return;
      }
      this.clearDropdownCloseTimer();
      this.dropdownCloseTimer = window.setTimeout(
        () => {
          this.activeDropdown = null;
          this.dropdownCloseTimer = null;
        },
        260,
      );
    },
    setLocale(locale) {
      this.$i18n.locale = locale;
      localStorage.setItem('localeCode', locale);
      this.closeMenu();
    },
    toggleDropdown(name) {
      this.clearDropdownCloseTimer();
      if (this.pinnedDropdown === name) {
        this.pinnedDropdown = null;
        this.activeDropdown = null;
        return;
      }
      this.pinnedDropdown = name;
      this.activeDropdown = name;
      this.revealNav();
    },
    toggleMenu() {
      this.active = !this.active;
      if (this.active) {
        this.revealNav();
      }
    },
    onLoginSucceed() {
      this.initializeUser(true);
    },
    onSignUpSucceed() {
      this.initializeUser(true);
    },
    logOut() {
      api.User.logOut().then(
        () => {
          window.location.reload();
        },
      );
    },
    logIn() {
      this.closeMenu();
      modals.openLogin(this, this.onLoginSucceed);
    },
    createPin() {
      this.closeMenu();
      modals.openPinEdit(
        this,
        { username: this.user.meta.username },
      );
    },
    createBoard() {
      this.closeMenu();
      modals.openBoardCreate(this);
    },
    createComic() {
      this.closeMenu();
      modals.openComicCreate(
        this,
        this.user.meta.username,
        () => this.$router.push({ name: 'comics' }),
      );
    },
    signUp() {
      this.closeMenu();
      modals.openSignUp(this, this.onSignUpSucceed);
    },
    toggleReduceMotion() {
      this.reduceMotion = motionPreference.saveAndApplyMotionPreference(!this.reduceMotion);
      window.dispatchEvent(new CustomEvent('pinry-motion-change', {
        detail: { reduceMotion: this.reduceMotion },
      }));
    },
    toggleThemeMode() {
      const mode = this.themeState.mode === 'dark' ? 'light' : 'dark';
      this.themeState = theme.saveAndApplyTheme({
        mode,
        accent: this.themeState.accent,
      });
    },
    setAccent(accent) {
      this.themeState = theme.saveAndApplyTheme({
        mode: this.themeState.mode,
        accent,
      });
    },
    requestScrollUpdate() {
      if (this.scrollTicking) {
        return;
      }
      this.scrollTicking = true;
      window.requestAnimationFrame(
        () => {
          this.scrollTicking = false;
          this.updateNavVisibility();
        },
      );
    },
    updateNavVisibility() {
      const scrollTop = Math.max(
        0,
        window.pageYOffset
        || document.documentElement.scrollTop
        || 0,
      );
      const delta = scrollTop - this.lastScrollTop;
      const distance = Math.abs(delta);
      if (this.navOpen || scrollTop < 96) {
        this.revealNav();
        this.lastScrollTop = scrollTop;
        return;
      }
      if (distance < 2) {
        this.lastScrollTop = scrollTop;
        return;
      }
      if (delta > 0) {
        this.navProgress = clamp(
          this.navProgress + (distance / NAV_HIDE_DISTANCE),
          0,
          1,
        );
      } else {
        this.navProgress = clamp(
          this.navProgress - (distance / NAV_SHOW_DISTANCE),
          0,
          1,
        );
      }
      this.navHidden = this.navProgress >= 0.995;
      this.lastScrollTop = scrollTop;
    },
    initializeUser(force = false) {
      api.User.fetchUserInfo(force).then(
        (user) => {
          if (user === null) {
            this.user.loggedIn = false;
            this.user.meta = {};
          } else {
            this.user.meta = user;
            this.user.loggedIn = true;
          }
        },
      );
    },
  },
  beforeMount() {
    if (!this.appShell) {
      return;
    }
    this.initializeUser();
  },
  mounted() {
    if (!this.appShell) {
      return;
    }
    this.lastScrollTop = window.pageYOffset || 0;
    window.addEventListener('scroll', this.requestScrollUpdate, { passive: true });
    document.addEventListener('click', this.handleDocumentClick);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.requestScrollUpdate);
    document.removeEventListener('click', this.handleDocumentClick);
    this.clearDropdownCloseTimer();
  },
};
</script>

<style scoped lang="scss">
@import "./utils/motion-mixins";

.p-header {
  position: fixed;
  z-index: var(--z-nav);
  top: 0;
  right: 0;
  left: 0;
  padding: var(--space-sm) clamp(var(--space-sm), 3vw, var(--space-xl));
  pointer-events: none;
  transform: translate3d(0, 0, 0);
  transition: padding var(--motion-duration-fast) var(--motion-ease-standard);
}
.p-header.is-hidden,
.p-header.is-open {
  transform: translate3d(0, 0, 0);
}
.p-header.is-hidden .nav-shell,
.p-header.is-hidden .mobile-panel {
  pointer-events: none;
}
.nav-shell {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: min(100%, var(--container-max));
  min-height: 56px;
  margin: 0 auto;
  padding: var(--space-xs);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 260px),
    color-mix(in srgb, var(--color-surface-1) 86%, transparent);
  backdrop-filter: blur(18px);
  opacity: var(--nav-opacity, 1);
  pointer-events: auto;
  box-shadow: var(--shadow-card);
  transform: translate3d(0, var(--nav-offset, 0), 0) scale(var(--nav-scale, 1));
  transition:
    border-color var(--motion-duration-standard) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard),
    opacity 120ms linear,
    transform 120ms linear;
  will-change: opacity, transform;
}
.p-header.is-hidden .nav-shell {
  box-shadow: var(--shadow-xs);
}
.p-header.is-open .nav-shell {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
  transition:
    border-color var(--motion-duration-standard) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard),
    opacity var(--motion-duration-standard) var(--motion-ease-standard),
    transform 340ms var(--motion-ease-emphasized);
}
.brand {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  min-width: 0;
  gap: var(--space-xs);
  padding: var(--space-2xs) var(--space-xs);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  @include hover-scale(1.018, -2px);
}
.brand:focus-visible {
  @include focus-ring;
}
.brand-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  min-width: 104px;
  height: 38px;
  padding: 0 var(--space-sm);
  overflow: hidden;
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
}
.brand img {
  display: block;
  width: auto;
  max-width: 86px;
  height: 24px;
  object-fit: contain;
}
.brand-copy {
  display: grid;
  line-height: 1.05;
}
.brand-copy strong {
  color: var(--color-text-strong);
  font-size: 0.95rem;
  font-weight: 950;
}
.brand-copy small {
  color: var(--color-text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.nav-primary,
.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
}
.nav-primary {
  min-width: 0;
}
.nav-actions {
  margin-left: auto;
}
.nav-link,
.nav-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 38px;
  padding: 0 var(--space-sm);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: transparent;
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 850;
  text-decoration: none;
  @include hover-scale(1.018, -2px);
}
.nav-link:hover,
.nav-pill:hover,
.nav-link.router-link-exact-active,
.nav-link.router-link-active {
  color: var(--color-accent-strong);
  border-color: var(--color-accent-border);
  background: var(--color-accent-soft);
}
.nav-link:focus-visible,
.nav-pill:focus-visible,
.nav-popover a:focus-visible,
.nav-popover button:focus-visible,
.mobile-panel a:focus-visible,
.mobile-panel button:focus-visible,
.mobile-toggle:focus-visible,
.accent-swatch:focus-visible {
  @include focus-ring;
}
.nav-pill.is-icon {
  width: 38px;
  padding: 0;
}
.nav-group {
  position: relative;
}
.nav-popover {
  position: absolute;
  top: calc(100% + var(--space-xs));
  right: 0;
  display: grid;
  gap: var(--space-2xs);
  min-width: 168px;
  padding: var(--space-xs);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: var(--color-surface-1);
  box-shadow: var(--shadow-floating);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-8px) scale(0.98);
  transform-origin: top right;
  transition:
    opacity var(--motion-duration-fast) var(--motion-ease-standard),
    transform var(--motion-duration-fast) var(--motion-ease-standard);
}
.nav-group.is-active .nav-popover {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0) scale(1);
}
.nav-popover a,
.nav-popover button,
.mobile-panel a,
.mobile-panel button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  min-height: 38px;
  padding: 0 var(--space-sm);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: transparent;
  cursor: pointer;
  font-weight: 850;
  text-align: left;
  text-decoration: none;
  transition:
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard);
}
.nav-popover a:hover,
.nav-popover button:hover,
.mobile-panel a:hover,
.mobile-panel button:hover {
  color: var(--color-accent-strong);
  border-color: var(--color-accent-border);
  background: var(--color-accent-soft);
}
.theme-popover {
  min-width: 228px;
}
.theme-mode,
.mobile-theme-toggle {
  justify-content: space-between;
  gap: var(--space-sm);
}
.mode-switch {
  position: relative;
  flex: 0 0 auto;
  width: 42px;
  height: 24px;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-pill);
  background: var(--color-surface-2);
  box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.12);
  transition:
    background var(--motion-duration-fast) var(--motion-ease-standard),
    border-color var(--motion-duration-fast) var(--motion-ease-standard);
}
.mode-switch > span {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-text-muted);
  box-shadow: var(--shadow-xs);
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}
.mode-switch.is-on {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}
.mode-switch.is-on > span {
  background: var(--color-accent-strong);
  transform: translateX(18px);
}
.accent-grid,
.mobile-accent-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-xs);
  padding: var(--space-2xs) var(--space-xs) var(--space-xs);
}
.accent-swatch {
  position: relative;
  width: 28px;
  height: 28px;
  min-height: 28px;
  padding: 0;
  border: 2px solid var(--color-surface-1);
  border-radius: 50%;
  box-shadow:
    0 0 0 1px var(--color-line-soft),
    inset 0 0 0 1px rgba(255, 255, 255, 0.44);
  cursor: pointer;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard);
}
.accent-swatch:hover,
.accent-swatch.is-active {
  transform: scale(1.1);
}
.accent-swatch.is-active {
  box-shadow:
    0 0 0 2px var(--color-surface-1),
    0 0 0 4px var(--color-accent-strong),
    inset 0 0 0 1px rgba(255, 255, 255, 0.5);
}
.accent-swatch.is-active::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, -50%);
}
.accent-swatch.is-elysia { background: #ef7cba; }
.accent-swatch.is-eden { background: #d5a344; }
.accent-swatch.is-mobius { background: #32b47b; }
.accent-swatch.is-kevin { background: #6ab7ff; }
.accent-swatch.is-griseo { background: #7c8cff; }
.accent-swatch.is-pardofelis { background: #f2a65e; }
.mobile-toggle {
  display: none;
  place-items: center;
  width: 42px;
  height: 42px;
  margin-left: auto;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  background: var(--color-accent-soft);
  box-shadow: var(--shadow-xs);
  pointer-events: auto;
}
.mobile-toggle span {
  display: block;
  width: 18px;
  height: 2px;
  margin: 3px 0;
  border-radius: var(--radius-pill);
  background: var(--color-accent-strong);
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    opacity var(--motion-duration-fast) var(--motion-ease-standard);
}
.mobile-toggle.is-active span:first-child {
  transform: translateY(4px) rotate(45deg);
}
.mobile-toggle.is-active span:last-child {
  transform: translateY(-4px) rotate(-45deg);
}
.mobile-backdrop,
.mobile-panel {
  display: none;
}
@media screen and (max-width: 1180px) {
  .nav-shell {
    gap: var(--space-xs);
  }
  .nav-primary {
    flex: 1 1 auto;
    min-width: 0;
    gap: var(--space-2xs);
    overflow: hidden;
  }
  .nav-actions {
    flex: 0 0 auto;
    gap: var(--space-2xs);
  }
  .nav-link,
  .nav-pill {
    padding: 0 var(--space-xs);
    white-space: nowrap;
    font-size: 0.86rem;
  }
  .brand-copy {
    display: none;
  }
}
@media screen and (max-width: 980px) {
  .p-header {
    padding: var(--space-xs);
  }
  .nav-shell {
    min-height: 50px;
    border-radius: var(--radius-lg);
  }
  .brand-logo {
    min-width: 92px;
    height: 36px;
    padding: 0 var(--space-xs);
  }
  .brand img {
    max-width: 76px;
  }
  .nav-primary,
  .nav-actions {
    display: none;
  }
  .mobile-toggle {
    display: grid;
  }
  .mobile-backdrop {
    position: fixed;
    inset: 0;
    z-index: calc(var(--z-nav) - 1);
    display: block;
    pointer-events: auto;
    background: rgba(12, 18, 28, 0.14);
    backdrop-filter: blur(2px);
  }
  .mobile-panel {
    position: relative;
    z-index: var(--z-nav);
    display: grid;
    gap: var(--space-sm);
    width: min(100%, var(--container-max));
    margin: var(--space-xs) auto 0;
    padding: var(--space-sm);
    border: 1px solid var(--color-line-soft);
    border-radius: var(--radius-lg);
    background:
      radial-gradient(circle at top right, var(--color-theme-glow), transparent 240px),
      var(--color-surface-1);
    pointer-events: auto;
    box-shadow: var(--shadow-floating);
    @include card-entrance;
  }
  .mobile-section {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-xs);
  }
  .mobile-section.is-primary a {
    min-height: 46px;
    border-color: var(--color-accent-border);
    background: var(--color-accent-soft);
  }
  .mobile-section.is-preferences,
  .mobile-section.is-account {
    grid-template-columns: 1fr;
  }
  .mobile-accent-row {
    grid-template-columns: repeat(6, 28px);
    justify-content: start;
    padding: var(--space-2xs);
  }
  .mobile-language-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-xs);
  }
}
@media screen and (max-width: 460px) {
  .mobile-section {
    grid-template-columns: 1fr;
  }
  .mobile-accent-row {
    grid-template-columns: repeat(6, 1fr);
  }
  .accent-swatch {
    justify-self: center;
  }
}

/* R6 nav anti-overlap polish */
.brand {
  flex: 0 1 auto;
  min-width: 0;
  max-width: min(34vw, 270px);
  overflow: hidden;
}
.brand-copy {
  min-width: 0;
  max-width: 154px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-user,
.user-menu a,
.mobile-menu a {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
}
.user-menu a .icon,
.mobile-menu a .icon,
.nav-user .icon {
  flex: 0 0 auto;
}
@media screen and (max-width: 1180px) {
  .brand {
    max-width: 128px;
  }
}
@media screen and (max-width: 760px) {
  .brand {
    max-width: calc(100vw - 142px);
  }
}
</style>
