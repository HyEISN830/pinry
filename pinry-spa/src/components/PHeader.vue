<template>
  <header
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
        <img src="../assets/logo-dark.png" alt="Pinry">
      </router-link>
      <div class="nav-links">
        <a class="nav-link" href="https://hyeisn.cn/">HyEISN's</a>
        <router-link
          class="nav-link"
          :to="{ name: 'comics' }">
          {{ $t("comicsLink") }}
        </router-link>
        <router-link
          class="nav-icon"
          :to="{ name: 'search' }"
          :title="$t('searchButton')">
          <b-icon icon="magnify" custom-size="mdi-22px"></b-icon>
        </router-link>
      </div>
      <div class="nav-actions">
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
            @click.stop="toggleDropdown('create')">
            {{ $t("createLink") }}
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
            @click.stop="toggleDropdown('mine')">
            {{ $t("myLink") }}
          </button>
          <div class="nav-popover" @click.stop>
            <router-link
              :to="{ name: 'user', params: {user: user.meta.username} }"
              @click.native="closeDropdown">
              {{ $t("pinsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'boards4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              {{ $t("boardsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'comics4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              {{ $t("comicsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'profile4user', params: {username: user.meta.username} }"
              @click.native="closeDropdown">
              {{ $t("profileLink") }}
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
        type="button"
        :aria-label="$t('menuLabel')"
        :aria-expanded="active ? 'true' : 'false'"
        @click="toggleMenu">
        <span></span>
        <span></span>
      </button>
    </nav>
    <div class="mobile-panel" v-if="active">
      <router-link :to="{ name: 'search' }" @click.native="closeMenu">
        {{ $t("searchButton") }}
      </router-link>
      <router-link :to="{ name: 'comics' }" @click.native="closeMenu">
        {{ $t("comicsLink") }}
      </router-link>
      <button v-if="user.loggedIn" type="button" @click="createPin">{{ $t("pinLink") }}</button>
      <button v-if="user.loggedIn" type="button" @click="createBoard">{{ $t("boardLink") }}</button>
      <button v-if="user.loggedIn" type="button" @click="createComic">{{ $t("comicLink") }}</button>
      <router-link
        v-if="user.loggedIn"
        :to="{ name: 'user', params: {user: user.meta.username} }"
        @click.native="closeMenu">
        {{ $t("pinsLink") }}
      </router-link>
      <router-link
        v-if="user.loggedIn"
        :to="{ name: 'boards4user', params: {username: user.meta.username} }"
        @click.native="closeMenu">
        {{ $t("boardsLink") }}
      </router-link>
      <router-link
        v-if="user.loggedIn"
        :to="{ name: 'comics4user', params: {username: user.meta.username} }"
        @click.native="closeMenu">
        {{ $t("comicsLink") }}
      </router-link>
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
      <button v-show="!user.loggedIn" type="button" @click="logIn">{{ $t("logInLink") }}</button>
      <button v-show="user.loggedIn" type="button" @click="logOut">{{ $t("logOutLink") }}</button>
    </div>
  </header>
</template>

<script>
import localeUtils from '@/components/utils/i18n';
import api from './api';
import modals from './modals';
import theme from './utils/theme';

const NAV_HIDE_DISTANCE = 96;
const NAV_SHOW_DISTANCE = 62;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export default {
  name: 'p-header',
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
    this.initializeUser();
  },
  mounted() {
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
.p-header {
  position: fixed;
  z-index: 80;
  top: 0;
  right: 0;
  left: 0;
  padding: 0.65rem clamp(0.8rem, 3vw, 2rem);
  pointer-events: none;
  transform: translate3d(0, 0, 0);
  transition: padding .2s ease;
}
.p-header.is-hidden {
  transform: translate3d(0, 0, 0);
}
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
  gap: 0.85rem;
  width: min(100%, 1440px);
  min-height: 52px;
  margin: 0 auto;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: var(--surface-1);
  backdrop-filter: blur(16px);
  opacity: var(--nav-opacity, 1);
  pointer-events: auto;
  box-shadow: var(--shadow-soft);
  transform: translate3d(0, var(--nav-offset, 0), 0) scale(var(--nav-scale, 1));
  transition:
    border-color .2s ease,
    box-shadow .28s ease,
    opacity .12s linear,
    transform .12s linear;
  will-change: opacity, transform;
}
.p-header.is-hidden .nav-shell {
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
}
.p-header.is-open .nav-shell {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
  transition:
    border-color .2s ease,
    box-shadow .28s ease,
    opacity .28s ease,
    transform .34s cubic-bezier(0.16, 1, 0.3, 1);
}
.brand {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  min-width: 0;
  padding: 0.25rem 0.4rem;
}
.brand img {
  width: auto;
  max-width: 104px;
  height: 28px;
  object-fit: contain;
}
.nav-links,
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.nav-links {
  min-width: 0;
}
.nav-actions {
  margin-left: auto;
}
.nav-link,
.nav-icon,
.nav-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0 0.72rem;
  border: 0;
  border-radius: 7px;
  color: var(--text-strong);
  background: transparent;
  cursor: pointer;
  font-size: 0.94rem;
  font-weight: 800;
  transition: background .18s ease, color .18s ease, transform .18s ease;
}
.nav-icon,
.nav-pill.is-icon {
  width: 36px;
  padding: 0;
}
.nav-link:hover,
.nav-icon:hover,
.nav-pill:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.nav-group {
  position: relative;
}
.nav-popover {
  position: absolute;
  top: calc(100% + 0.45rem);
  right: 0;
  display: grid;
  gap: 0.15rem;
  min-width: 150px;
  padding: 0.45rem;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: var(--surface-1);
  box-shadow: var(--shadow-soft);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-6px) scale(0.98);
  transition: opacity .16s ease, transform .16s ease;
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
  min-height: 34px;
  padding: 0.45rem 0.6rem;
  border: 0;
  border-radius: 7px;
  color: var(--text-strong);
  background: transparent;
  cursor: pointer;
  font-weight: 800;
  text-align: left;
}
.nav-popover a:hover,
.nav-popover button:hover,
.mobile-panel a:hover,
.mobile-panel button:hover {
  color: var(--accent-strong);
  background: var(--accent-soft);
}
.theme-popover {
  min-width: 220px;
}
.theme-mode,
.mobile-theme-toggle {
  justify-content: space-between;
  gap: 0.85rem;
}
.mode-switch {
  position: relative;
  flex: 0 0 auto;
  width: 42px;
  height: 24px;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: var(--surface-2);
  box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.12);
  transition: background .18s ease, border-color .18s ease;
}
.mode-switch > span {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--text-muted);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.18);
  transition: transform .18s ease, background .18s ease;
}
.mode-switch.is-on {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.mode-switch.is-on > span {
  background: var(--accent-strong);
  transform: translateX(18px);
}
.accent-grid,
.mobile-accent-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.35rem;
  padding: 0.2rem 0.35rem 0.35rem;
}
.accent-swatch {
  position: relative;
  width: 26px;
  height: 26px;
  min-height: 26px;
  padding: 0;
  border: 2px solid var(--surface-1);
  border-radius: 50%;
  box-shadow:
    0 0 0 1px var(--line-soft),
    inset 0 0 0 1px rgba(255, 255, 255, 0.44);
  transition: transform .16s ease, box-shadow .16s ease;
}
.accent-swatch.is-active {
  transform: scale(1.08);
  box-shadow:
    0 0 0 2px var(--surface-1),
    0 0 0 4px var(--accent-strong),
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
  border: 0;
  border-radius: 8px;
  background: var(--accent-soft);
}
.mobile-toggle span {
  display: block;
  width: 18px;
  height: 2px;
  margin: 3px 0;
  border-radius: 999px;
  background: var(--accent-strong);
}
.mobile-panel {
  display: none;
}
@media screen and (max-width: 760px) {
  .p-header {
    padding: 0.45rem 0.65rem;
  }
  .nav-shell {
    min-height: 48px;
  }
  .nav-links,
  .nav-actions {
    display: none;
  }
  .mobile-toggle {
    display: grid;
  }
  .mobile-panel {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.45rem;
    width: min(100%, 1440px);
    margin: 0.45rem auto 0;
    padding: 0.65rem;
    border: 1px solid var(--line-soft);
    border-radius: 8px;
    background: var(--surface-1);
    pointer-events: auto;
    box-shadow: var(--shadow-soft);
  }
  .mobile-accent-row {
    grid-column: 1 / -1;
    grid-template-columns: repeat(6, 24px);
    justify-content: start;
    padding: 0.15rem 0.45rem;
  }
}
</style>
