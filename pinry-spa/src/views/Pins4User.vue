<template>
  <div class="pins-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-pins="true" :username="filters.userFilter"></UserProfileCard>
    <Pins :pin-filters="filters"></Pins>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import UserProfileCard from '../components/UserProfileCard.vue';
import Pins from '../components/Pins.vue';

export default {
  name: 'Pins4User',
  data() {
    return {
      filters: { userFilter: null },
    };
  },
  components: {
    PHeader,
    UserProfileCard,
    Pins,
  },
  created() {
    this.initializeBoard();
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { userFilter: to.params.user };
    next();
  },
  methods: {
    initializeBoard() {
      this.filters = { userFilter: this.$route.params.user };
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

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
.user-collection-page ::v-deep #pins-container {
  --profile-pin-columns: 4;
  --profile-pin-gap: 20px;
}

.user-collection-page ::v-deep #pins-container .pin-masonry {
  width: calc(
    (100% - (var(--profile-pin-columns) - 1) * var(--profile-pin-gap))
    / var(--profile-pin-columns)
  );
}

.user-collection-page ::v-deep #pins-container .gutter-sizer {
  width: var(--profile-pin-gap);
}

@media screen and (max-width: 1040px) {
  .user-collection-page ::v-deep #pins-container {
    --profile-pin-columns: 3;
    --profile-pin-gap: 18px;
  }
}

@media screen and (max-width: 720px) {
  .user-collection-page ::v-deep #pins-container {
    --profile-pin-columns: 2;
    --profile-pin-gap: 14px;
  }
}

@media screen and (max-width: 420px) {
  .user-collection-page ::v-deep #pins-container {
    --profile-pin-columns: 1;
  }
}

@media screen and (max-width: 760px) {
  .user-collection-page {
    --user-profile-content-width: calc(100vw - 20px);
  }
}
</style>
