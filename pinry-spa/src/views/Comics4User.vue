<template>
  <div class="comics-for-user user-collection-page">
    <UserProfileCard
      :username="username"
      :in-comics="true">
    </UserProfileCard>
    <div id="user-home-container" class="container">
      <div class="personal-comics-meta">作品数量: {{ comicCount }}</div>
      <PersonalComics :username="username" @meta="updateMeta"></PersonalComics>
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
    updateMeta(meta) { this.comicCount = meta && meta.count ? meta.count : 0; },
  },
};
</script>

<style lang="scss" scoped>
#user-home-container { background: transparent; }
.personal-comics-meta {
  width: 100%;
  margin: 0 0 16px;
  padding: 10px 0;
  color: var(--color-text-muted, var(--text-muted, #64748b));
  background: transparent;
  font-size: 14px;
  font-weight: 800;
}
</style>
