<template>
  <div class="comics-page">
    <PHeader></PHeader>
    <section class="section">
      <div class="container comics-container">
        <div class="comics-toolbar">
          <h1>{{ $t("comicsLink") }}</h1>
          <button
            v-if="user.loggedIn"
            class="button is-primary"
            type="button"
            @click="createComic">
            {{ $t("NewComicTitle") }}
          </button>
        </div>
        <div class="comic-grid">
          <router-link
            class="comic-card"
            v-for="comic in comics"
            :key="comic.id"
            :to="{ name: 'comic', params: { comicId: comic.id } }">
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
            </div>
          </router-link>
        </div>
        <loadingSpinner :show="status.loading"></loadingSpinner>
        <noMore :show="!status.hasNext"></noMore>
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

export default {
  name: 'Comics',
  components: {
    PHeader,
    loadingSpinner,
    noMore,
  },
  data() {
    return {
      comics: [],
      status: {
        hasNext: true,
        loading: false,
        offset: 0,
      },
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  created() {
    this.fetchUser();
    this.fetchMore(true);
    this.registerScrollEvent();
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
      API.Comic.fetchList(this.status.offset).then(
        (resp) => {
          const { results, next } = resp.data;
          this.comics = this.comics.concat(results);
          this.status.offset = this.comics.length;
          this.status.hasNext = next !== null;
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
  overflow: visible;
  color: inherit;
  border: 1px solid #e4e8ef;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.comic-card:hover {
  transform: translateY(-4px);
  border-color: #1f6feb;
  box-shadow: 0 16px 32px rgba(16, 24, 40, 0.16);
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
}
.comic-info h2 {
  margin: 0;
  color: #22313f;
  font-size: 16px;
  font-weight: 800;
}
.comic-info p {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 14px;
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
