<template>
  <div class="boards-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-board="true" :username="filters.boardUsername"></UserProfileCard>
    <div class="board-collection-container">
      <div class="board-collection-surface">
        <Boards :filters="filters"></Boards>
      </div>
    </div>
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
  --user-profile-content-width: var(--user-profile-shell-width);
}
.user-collection-page .container,
.user-collection-page .section > .container {
  width: 100%;
  max-width: var(--user-profile-content-width);
  margin-right: auto;
  margin-left: auto;
}
.board-collection-container {
  box-sizing: border-box;
  width: var(--user-profile-content-width);
  max-width: 100%;
  margin: 1rem auto 0;
  padding: 0;
}

.board-collection-surface {
  box-sizing: border-box;
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  background: var(--surface-1, #fff);
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}

.user-collection-page ::v-deep .board-collection-surface .boards > .section {
  padding: 0;
}

.user-collection-page ::v-deep .board-collection-surface #boards-container {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
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
@media screen and (max-width: 540px) {
  .board-collection-container {
    margin-top: 0.8rem;
  }

  .board-collection-surface {
    padding: 0.8rem;
  }
}
</style>
