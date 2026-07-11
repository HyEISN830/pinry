<template>
  <div class="comics-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-comics="true" :username="filters.comicUsername"></UserProfileCard>
    <Comics
      embedded
      :user-filter="filters.comicUsername"
      :title="$t('comicsLink')">
    </Comics>
  </div>
</template>

<script>
import Comics from './Comics.vue';
import PHeader from '../components/PHeader.vue';
import UserProfileCard from '../components/UserProfileCard.vue';

export default {
  name: 'Comics4User',
  components: {
    Comics,
    PHeader,
    UserProfileCard,
  },
  data() {
    return {
      filters: { comicUsername: null },
    };
  },
  created() {
    this.initialize();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { comicUsername: to.params.username };
    next();
  },
  methods: {
    initialize() {
      this.filters = { comicUsername: this.$route.params.username };
    },
  },
};
</script>

<style scoped lang="scss">
.comics-for-user {
  min-height: 100vh;
  background: var(--color-page-bg, var(--app-bg, #f6f7fb));
}

/* R6 profile collection alignment */
.user-collection-page {
  --user-profile-content-width: min(1040px, calc(100vw - 32px));
}
.user-collection-page .container,
.user-collection-page .section > .container {
  width: 100%;
  max-width: var(--user-profile-content-width);
  margin-right: auto;
  margin-left: auto;
}
.user-collection-page ::v-deep #pins-container,
.user-collection-page ::v-deep #boards-container,
.user-collection-page ::v-deep .comics-section,
.user-collection-page ::v-deep .comics-grid {
  width: 100%;
  max-width: 100%;
  margin-right: 0;
  margin-left: 0;
}
.user-collection-page ::v-deep .pin-masonry,
.user-collection-page ::v-deep .board-masonry,
.user-collection-page ::v-deep .comic-card-shell {
  min-width: 0;
}
@media screen and (max-width: 760px) {
  .user-collection-page {
    --user-profile-content-width: calc(100vw - 20px);
  }
}
</style>
