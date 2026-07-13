<template>
  <div class="comics-for-user user-collection-page">
    <UserProfileCard
      :username="username"
      :in-comics="true">
    </UserProfileCard>
    <div id="user-home-container" class="container comic-collection-container">
      <div class="user-collection-heading">
        <span class="user-collection-count" aria-live="polite">
          <span class="user-collection-count__label">{{ $t('comicsLink') }}</span>
          <strong>{{ comicCount }}</strong>
        </span>
      </div>
      <div class="comic-collection-surface">
        <PersonalComics :username="username" @meta="updateMeta"></PersonalComics>
      </div>
    </div>
  </div>
</template>

<script>
import UserProfileCard from '../components/UserProfileCard.vue';
import PersonalComics from '../components/PersonalComics.vue';

export default {
  name: 'Comics4User',
  components: { UserProfileCard, PersonalComics },
  data() {
    return { comicCount: 0 };
  },
  computed: {
    username() { return this.$route.params.username; },
  },
  methods: {
    updateMeta(meta) {
      this.comicCount = meta && Number.isFinite(meta.count) ? meta.count : 0;
    },
  },
};
</script>

<style lang="scss" scoped>
#user-home-container {
  background: transparent;
}

.comic-collection-container {
  width: var(--user-profile-shell-width);
  max-width: var(--user-profile-shell-width);
  margin: 1rem auto 0;
  padding: 0;
}

.comic-collection-surface {
  box-sizing: border-box;
  width: 100%;
  padding: 1rem;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  box-shadow: none;
}

@media screen and (max-width: 540px) {
  .comic-collection-container { margin-top: 0.8rem; }
  .comic-collection-surface { padding: 0.8rem; }
}
</style>
