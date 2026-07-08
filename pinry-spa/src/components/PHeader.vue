<template>
  <header
    class="p-header"
    :class="{
      'is-open': active,
      'is-hidden': navHidden
    }">
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
          class="nav-group">
          <button class="nav-pill" type="button">
            {{ $t("createLink") }}
          </button>
          <div class="nav-popover">
            <button type="button" @click="createPin">{{ $t("pinLink") }}</button>
            <button type="button" @click="createBoard">{{ $t("boardLink") }}</button>
            <button type="button" @click="createComic">{{ $t("comicLink") }}</button>
          </div>
        </div>
        <div
          v-if="user.loggedIn"
          class="nav-group">
          <button class="nav-pill" type="button">
            {{ $t("myLink") }}
          </button>
          <div class="nav-popover">
            <router-link
              :to="{ name: 'user', params: {user: user.meta.username} }">
              {{ $t("pinsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'boards4user', params: {username: user.meta.username} }">
              {{ $t("boardsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'comics4user', params: {username: user.meta.username} }">
              {{ $t("comicsLink") }}
            </router-link>
            <router-link
              :to="{ name: 'profile4user', params: {username: user.meta.username} }">
              {{ $t("profileLink") }}
            </router-link>
          </div>
        </div>
        <div class="nav-group theme-group">
          <button class="nav-pill is-icon" type="button" :title="$t('themeSettingsLabel')">
            <b-icon icon="palette" custom-size="mdi-20px"></b-icon>
          </button>
          <div class="nav-popover theme-popover">
            <button
              class="theme-mode"
              type="button"
              @click="toggleThemeMode">
              {{ themeState.mode === 'dark' ? $t("lightThemeLabel") : $t("darkThemeLabel") }}
            </button>
            <div class="accent-grid">
              <button
                v-for="accent in accentOptions"
                :key="accent.value"
                class="accent-swatch"
                type="button"
                :class="[`is-${accent.value}`, { 'is-active': themeState.accent === accent.value }]"
                :title="accent.label"
                @click="setAccent(accent.value)">
              </button>
            </div>
          </div>
        </div>
        <div class="nav-group">
          <button class="nav-pill is-icon" type="button" :title="$t('languageLabel')">
            <b-icon icon="translate" custom-size="mdi-20px"></b-icon>
          </button>
          <div class="nav-popover">
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
      <button type="button" @click="toggleThemeMode">
        {{ themeState.mode === 'dark' ? $t("lightThemeLabel") : $t("darkThemeLabel") }}
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

export default {
  name: 'p-header',
  data() {
    return {
      accentOptions: theme.accentOptions,
      active: false,
      langs: localeUtils.langCode2Name,
      lastScrollTop: 0,
      navHidden: false,
      scrollTicking: false,
      themeState: theme.readTheme(),
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  methods: {
    closeMenu() {
      this.active = false;
    },
    setLocale(locale) {
      this.$i18n.locale = locale;
      localStorage.setItem('localeCode', locale);
      this.closeMenu();
    },
    toggleMenu() {
      this.active = !this.active;
      if (this.active) {
        this.navHidden = false;
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
      const scrollTop = window.pageYOffset
        || document.documentElement.scrollTop
        || 0;
      const delta = scrollTop - this.lastScrollTop;
      if (this.active || scrollTop < 80) {
        this.navHidden = false;
      } else if (delta > 8) {
        this.navHidden = true;
      } else if (delta < -8) {
        this.navHidden = false;
      }
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
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.requestScrollUpdate);
  },
};
</script>

<style scoped lang="scss">
.p-header {
  position: sticky;
  z-index: 60;
  top: 0;
  padding: 0.65rem clamp(0.8rem, 3vw, 2rem);
  transform: translateY(0);
  transition: transform .24s ease, padding .2s ease;
}
.p-header.is-hidden {
  transform: translateY(calc(-100% - 8px));
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
  box-shadow: var(--shadow-soft);
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
.nav-group:hover .nav-popover,
.nav-group:focus-within .nav-popover {
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
  min-width: 190px;
}
.accent-grid,
.mobile-accent-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.35rem;
  padding: 0.2rem 0.35rem 0.35rem;
}
.accent-swatch {
  width: 22px;
  height: 22px;
  min-height: 22px;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.44);
}
.accent-swatch.is-active {
  border-color: var(--text-strong);
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
