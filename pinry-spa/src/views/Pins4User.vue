<template>
  <div class="pins-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-pins="true" :username="filters.userFilter"></UserProfileCard>
    <div class="pin-collection-container">
      <div class="user-collection-heading">
        <span class="user-collection-count" aria-live="polite">
          <span class="user-collection-count__label">{{ $t('pinsLink') }}</span>
          <strong>{{ pinsCount }}</strong>
        </span>
      </div>
      <div class="pin-collection-surface">
        <Pins :pin-filters="filters" @pins-meta-loaded="onPinsMetaLoaded"></Pins>
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
      pinsCount: 0,
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
    this.pinsCount = 0;
    this.filters = { userFilter: to.params.user };
    next();
  },
  methods: {
    initializeBoard() {
      this.filters = { userFilter: this.$route.params.user };
    },
    onPinsMetaLoaded(meta) {
      this.pinsCount = meta && Number.isFinite(meta.count) ? meta.count : 0;
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
  width: var(--user-profile-content-width);
  max-width: 100%;
  margin: 1rem auto 0;
  padding: 0;
}

.pin-collection-surface {
  box-sizing: border-box;
  width: 100%;
  padding: 1rem;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  box-shadow: none;
}

.user-collection-page ::v-deep .pin-collection-surface .pins > .section {
  padding: 0;
}

.user-collection-page ::v-deep .pin-collection-surface #pins-container {
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
  .pin-collection-container {
    margin-top: 0.8rem;
  }

  .pin-collection-surface {
    padding: 0.8rem;
  }

}
</style>
