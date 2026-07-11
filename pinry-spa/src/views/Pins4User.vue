<template>
  <div class="pins-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-pins="true" :username="filters.userFilter"></UserProfileCard>
    <div class="pin-collection-container">
      <div class="pin-collection-surface">
        <Pins :pin-filters="filters"></Pins>
      </div>
    </div>
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
.pin-collection-container {
  box-sizing: border-box;
  width: min(100%, 1260px);
  margin: 1rem auto 0;
  padding: 0 0.75rem;
}

.pin-collection-surface {
  box-sizing: border-box;
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  background: var(--surface-1, #fff);
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}

.user-collection-page ::v-deep .pin-collection-surface .pins > .section {
  padding: 0;
}

.user-collection-page ::v-deep .pin-collection-surface #pins-container {
  --profile-pin-columns: 5;
  --profile-pin-gap: 16px;
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
    --profile-pin-columns: 4;
    --profile-pin-gap: 14px;
  }
}

@media screen and (max-width: 768px) {
  .user-collection-page ::v-deep #pins-container {
    --profile-pin-columns: 3;
    --profile-pin-gap: 12px;
  }
}

@media screen and (max-width: 540px) {
  .pin-collection-container {
    margin-top: 0.8rem;
    padding: 0 0.55rem;
  }

  .pin-collection-surface {
    padding: 0.8rem;
  }

  .user-collection-page ::v-deep #pins-container {
    --profile-pin-columns: 1;
    --profile-pin-gap: 0px;
  }
}
</style>
