<template>
  <div class="profile-for-user">
    <PHeader></PHeader>
    <UserProfileCard :key="profileCardKey" :in-profile="true" :username="filters.userFilter"></UserProfileCard>
    <loadingSpinner :show="profileLoading" size="regular"></loadingSpinner>
    <Profile v-if="profile.token" :user="profile" v-on:profile-updated="onProfileUpdated"></Profile>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import UserProfileCard from '../components/UserProfileCard.vue';
import Profile from '../components/user/profile.vue';
import loadingSpinner from '../components/loadingSpinner.vue';
import api from '../components/api';

export default {
  name: 'Profile4User',
  data() {
    return {
      filters: { userFilter: null },
      profile: {},
      profileLoading: true,
      profileRequestId: 0,
    };
  },
  components: {
    PHeader,
    UserProfileCard,
    Profile,
    loadingSpinner,
  },
  computed: {
    profileCardKey() {
      const avatar = this.profile.avatar && this.profile.avatar.medium
        ? this.profile.avatar.medium
        : '';
      return `${this.filters.userFilter}-${avatar}`;
    },
  },
  created() {
    this.initializeBoard();
    this.initializeUser(this.filters.userFilter);
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { userFilter: to.params.username };
    this.profile = {};
    this.initializeUser(to.params.username);
    next();
  },
  methods: {
    initializeBoard() {
      this.filters = { userFilter: this.$route.params.username };
    },
    initializeUser(username) {
      const self = this;
      const requestId = this.profileRequestId + 1;
      this.profileRequestId = requestId;
      this.profileLoading = true;
      api.User.fetchUserInfoByName(username).then(
        (user) => {
          if (requestId !== self.profileRequestId) {
            return;
          }
          if (user === null) {
            self.profileLoading = false;
            self.$router.push(
              { name: 'PageNotFound' },
            );
          } else {
            self.profile = user;
            self.profileLoading = false;
          }
        },
        () => {
          if (requestId !== self.profileRequestId) {
            return;
          }
          self.profileLoading = false;
        },
      );
    },
    onProfileUpdated(user) {
      this.profile = user;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.profile-for-user {
  min-height: 100vh;
  background: var(--app-bg, #f6f7fb);
}
</style>
