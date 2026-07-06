<template>
  <div class="comics-page">
    <PHeader v-if="!embedded"></PHeader>
    <section class="section comics-section">
      <div class="container comics-container">
        <div class="comics-toolbar">
          <h1>{{ $t("comicsLink") }}</h1>
          <button
            v-if="user.loggedIn && !embedded"
            class="button is-primary"
            type="button"
            @click="createComic">
            {{ $t("NewComicTitle") }}
          </button>
        </div>
        <div class="comic-grid">
          <article
            class="comic-card"
            v-for="comic in comics"
            :key="comic.id"
            @mouseenter="showMenu(comic)"
            @mouseleave="hideMenu"
            @touchstart="handleCardTouch(comic)"
            @click="openComic(comic, $event)">
            <transition name="comic-menu">
              <div
                class="comic-card-menu"
                v-if="shouldShowMenu(comic)"
                @click.stop
                @touchstart.stop="noop">
                <button
                  class="button is-small is-danger"
                  type="button"
                  :title="$t('deleteButton')"
                  :aria-label="$t('deleteButton')"
                  @click.stop="deleteComic(comic)">
                  {{ $t("deleteButton") }}
                </button>
              </div>
            </transition>
            <div class="comic-ribbon">{{ $t("comicLink") }}</div>
            <div
              class="comic-cover"
              :style="coverStyle(comic)">
              <img
                v-if="comic.cover"
                :src="comic.cover.image.thumbnail.image"
                :alt="comic.title">
            </div>
            <div class="comic-info">
              <h2>{{ comic.title }}</h2>
              <p>{{ comic.total_pages }} {{ $t("comicPagesUnit") }}</p>
              <div class="comic-source" v-if="hasSource(comic.referer)">
                <a
                  v-if="isWebUrl(comic.referer)"
                  :href="comic.referer"
                  target="_blank"
                  @click.stop>
                  {{ $t("sourceLink") }}
                </a>
                <span v-else>{{ sourceText(comic.referer) }}</span>
              </div>
              <div class="comic-source is-warning" v-else>
                {{ $t("missingSourceNotice") }}
              </div>
            </div>
          </article>
        </div>
        <loadingSpinner v-if="!embedded" :show="status.loading"></loadingSpinner>
        <noMore v-if="!embedded" :show="!status.hasNext"></noMore>
      </div>
    </section>
  </div>
</template>

<script>
import API from '../components/api';
import PHeader from '../components/PHeader.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import noMore from '../components/noMore.vue';
import modals from '../components/modals';
import scroll from '../components/utils/scroll';

function isWebUrl(url) {
  return /^https?:\/\//i.test((url || '').trim());
}

function hasSource(url) {
  return !!(url || '').trim();
}

function sourceText(url) {
  return (url || '').trim();
}

export default {
  name: 'Comics',
  components: {
    PHeader,
    loadingSpinner,
    noMore,
  },
  props: {
    embedded: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      comics: [],
      currentMenuId: null,
      status: {
        hasNext: true,
        loading: false,
        offset: 0,
      },
      suppressNextOpenId: null,
      suppressOpenTimer: null,
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  created() {
    this.fetchUser();
    this.fetchMore(true);
    if (!this.embedded) {
      this.registerScrollEvent();
    }
  },
  beforeDestroy() {
    if (this.suppressOpenTimer) {
      window.clearTimeout(this.suppressOpenTimer);
    }
  },
  methods: {
    coverStyle(comic) {
      if (!comic.cover) {
        return {};
      }
      const { thumbnail } = comic.cover.image;
      return {
        aspectRatio: `${thumbnail.width} / ${thumbnail.height}`,
      };
    },
    isOwner(comic) {
      return this.user.loggedIn
        && comic.submitter.username === this.user.meta.username;
    },
    shouldShowMenu(comic) {
      return this.isOwner(comic) && this.currentMenuId === comic.id;
    },
    showMenu(comic) {
      if (this.isOwner(comic)) {
        this.currentMenuId = comic.id;
      }
    },
    hideMenu() {
      this.currentMenuId = null;
    },
    handleCardTouch(comic) {
      const wasVisible = this.shouldShowMenu(comic);
      this.showMenu(comic);
      if (this.suppressOpenTimer) {
        window.clearTimeout(this.suppressOpenTimer);
      }
      this.suppressNextOpenId = (!wasVisible && this.isOwner(comic))
        ? comic.id
        : null;
      if (this.suppressNextOpenId !== null) {
        this.suppressOpenTimer = window.setTimeout(() => {
          this.suppressNextOpenId = null;
          this.suppressOpenTimer = null;
        }, 700);
      }
    },
    openComic(comic, event) {
      if (this.suppressNextOpenId === comic.id) {
        this.suppressNextOpenId = null;
        if (this.suppressOpenTimer) {
          window.clearTimeout(this.suppressOpenTimer);
          this.suppressOpenTimer = null;
        }
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      this.$router.push({ name: 'comic', params: { comicId: comic.id } });
    },
    fetchUser() {
      API.User.fetchUserInfo().then(
        (user) => {
          if (user === null) {
            this.user.loggedIn = false;
            this.user.meta = {};
            return;
          }
          this.user.loggedIn = true;
          this.user.meta = user;
        },
      );
    },
    fetchMore(created) {
      if (!created && (this.status.loading || !this.status.hasNext)) {
        return;
      }
      this.status.loading = true;
      const limit = this.embedded ? 6 : 18;
      API.Comic.fetchList(this.status.offset, limit).then(
        (resp) => {
          const { results, next } = resp.data;
          this.comics = this.comics.concat(results);
          this.status.offset = this.comics.length;
          this.status.hasNext = next !== null && !this.embedded;
          this.status.loading = false;
        },
        () => {
          this.status.loading = false;
        },
      );
    },
    registerScrollEvent() {
      scroll.bindScroll2Bottom(
        () => this.fetchMore(),
      );
    },
    createComic() {
      modals.openComicCreate(
        this,
        this.user.meta.username,
        () => {
          this.comics = [];
          this.status.offset = 0;
          this.status.hasNext = true;
          this.fetchMore(true);
        },
      );
    },
    deleteComic(comic) {
      this.$buefy.dialog.confirm({
        message: this.$t('deleteComicConfirm'),
        type: 'is-danger',
        onConfirm: () => {
          API.Comic.delete(comic.id).then(
            () => {
              this.comics = this.comics.filter(item => item.id !== comic.id);
              this.currentMenuId = null;
            },
          );
        },
      });
    },
    hasSource,
    isWebUrl,
    noop() {
      return true;
    },
    sourceText,
  },
};
</script>

<style lang="scss" scoped>
@import '../components/utils/grid-layout';

.comics-container {
  margin: 0 auto;
}
.comics-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.comics-toolbar h1 {
  margin: 0;
  color: #22313f;
  font-size: 1.6rem;
  font-weight: 800;
}
.comic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--pin-card-width, 240px), 1fr));
  gap: var(--pin-grid-gutter, 15px);
}
.comic-card {
  position: relative;
  isolation: isolate;
  overflow: visible;
  color: inherit;
  cursor: pointer;
  border: 1px solid rgba(126, 87, 194, 0.42);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(126, 87, 194, 0.08), 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.comic-card::before,
.comic-card::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  height: 12px;
  border: 1px solid rgba(126, 87, 194, 0.22);
  border-radius: 0 0 8px 8px;
  background: #faf7ff;
  pointer-events: none;
}
.comic-card::before {
  bottom: -7px;
  z-index: -1;
}
.comic-card::after {
  bottom: -13px;
  left: 24px;
  right: 24px;
  background: #f0ebff;
  z-index: -2;
}
.comic-card:hover {
  transform: translateY(-4px);
  border-color: rgba(126, 87, 194, 0.74);
  box-shadow: 0 0 0 2px rgba(126, 87, 194, 0.14), 0 16px 32px rgba(16, 24, 40, 0.16);
}
.comic-ribbon {
  position: absolute;
  z-index: 4;
  top: 10px;
  left: 10px;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  color: #fff;
  background: rgba(126, 87, 194, 0.9);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.02em;
}
.comic-card-menu {
  position: absolute;
  z-index: 8;
  top: 8px;
  right: 8px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(15, 23, 42, 0.58);
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.24);
}
.comic-menu-enter-active,
.comic-menu-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.comic-menu-enter,
.comic-menu-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}
.comic-cover {
  min-height: 170px;
  overflow: hidden;
  border-radius: 8px 8px 0 0;
  background: #f5f7fa;
}
.comic-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.comic-info {
  padding: 0.85rem;
  border-top: 1px solid #efe9ff;
}
.comic-info h2 {
  margin: 0;
  color: #22313f;
  font-size: 16px;
  font-weight: 800;
}
.comic-info p,
.comic-source {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 14px;
}
.comic-source a,
.comic-source span {
  color: #7e57c2;
  font-weight: 700;
}
.comic-source.is-warning {
  color: #8a6d1d;
}
@media screen and (max-width: 542px) {
  .comics-toolbar {
    display: block;
  }
  .comics-toolbar .button {
    width: 100%;
    margin-top: 1rem;
  }
}
@include screen-grid-layout(".comics-container");
</style>
