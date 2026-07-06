<template>
  <div class="comics-for-user">
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
</style>
