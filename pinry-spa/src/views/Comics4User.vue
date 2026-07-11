<template>
  <div class="comics-for-user user-collection-page">
    <PHeader></PHeader>
    <UserProfileCard :in-comics="true" :username="filters.comicUsername"></UserProfileCard>
    <div class="comic-stat-card">
      <span class="comic-stat-label">{{ $t('comicsLink') }}</span>
      <strong class="comic-stat-value">{{ comicCount }}</strong>
    </div>
    <div class="comic-collection-container">
      <div class="comic-collection-surface">
        <Comics
          embedded
          container-sizing
          :show-toolbar="false"
          :user-filter="filters.comicUsername"
          :title="$t('comicsLink')"
          @comics-meta-loaded="handleComicsMeta">
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
      comicCount: 0,
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
    handleComicsMeta(meta) {
      this.comicCount = meta && Number.isFinite(meta.count) ? meta.count : 0;
    },
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

.comic-stat-card {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: var(--user-profile-shell-width);
  max-width: 100%;
  margin: 18px auto 0;
  padding: 16px 20px;
  background: var(--surface-1);
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  box-shadow: var(--shadow-soft);
}

.comic-stat-label {
  color: var(--text-secondary);
  font-weight: 600;
}

.comic-stat-value {
  color: var(--text-primary);
  font-size: 1.35rem;
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
  .comic-stat-card,
  .comic-collection-container {
    width: min(var(--user-profile-shell-width), calc(100vw - 20px));
  }

  .comic-stat-card {
    margin-top: 14px;
    padding: 14px 16px;
  }

  .comic-collection-container {
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

}
</style>
