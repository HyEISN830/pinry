<template>
  <div class="comics-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-comics="true" :username="filters.comicUsername"></UserProfileCard>
    <div class="comic-collection-container">
      <div class="comic-collection-surface">
        <Comics
          embedded
          container-sizing
          :user-filter="filters.comicUsername"
          :title="$t('comicsLink')">
        </Comics>
      </div>
    </div>
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

.comic-collection-container {
  width: var(--user-profile-shell-width);
  max-width: 100%;
  margin: 22px auto 36px;
}

.comic-collection-surface {
  width: 100%;
  box-sizing: border-box;
  padding: clamp(18px, 2.4vw, 30px);
  overflow: hidden;
  background: var(--surface-1);
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  box-shadow: var(--shadow-soft);
}

.comic-collection-surface ::v-deep .comics-section,
.comic-collection-surface ::v-deep .comics-container {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.comic-collection-surface ::v-deep .comic-grid {
  justify-content: center;
}

@media screen and (max-width: 768px) {
  .comic-collection-container {
    width: min(var(--user-profile-shell-width), calc(100vw - 20px));
    margin-top: 16px;
  }

  .comic-collection-surface {
    padding: 16px;
  }
}

@media screen and (max-width: 540px) {
  .comic-collection-surface {
    padding: 14px 12px;
  }

  .comic-collection-surface ::v-deep .comic-grid {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}
</style>
