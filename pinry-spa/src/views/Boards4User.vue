<template>
  <div class="boards-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-board="true" :username="filters.boardUsername"></UserProfileCard>
    <Boards :filters="filters"></Boards>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import UserProfileCard from '../components/UserProfileCard.vue';
import Boards from '../components/Boards.vue';

export default {
  name: 'Boards4User',
  data() {
    return {
      filters: { boardUsername: null },
    };
  },
  components: {
    PHeader,
    UserProfileCard,
    Boards,
  },
  created() {
    this.initialize();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { boardUsername: to.params.username };
    next();
  },
  methods: {
    initialize() {
      this.filters = { boardUsername: this.$route.params.username };
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.boards-for-user {
  min-height: 100vh;
  background: var(--app-bg, #f6f7fb);
}

/* R6 profile collection alignment */
.user-collection-page {
  --user-profile-content-width: min(1120px, calc(100vw - 32px));
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
