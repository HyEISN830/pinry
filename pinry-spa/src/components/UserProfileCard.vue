<template>
    <div class="user-profile-card">
      <div id="user-home-container">
        <div class="card">
          <div class="card-content">
            <div class="media">
              <div class="media-left">
                <figure class="image is-48x48">
                  <b-skeleton width="48px" height="48px" :active="avatarLoading"></b-skeleton>
                  <img
                    @load="onAvatarLoaded"
                    v-show="!avatarLoading"
                    :src="user.avatar"
                    alt="avatar"
                  >
                </figure>
              </div>
              <div class="media-content" v-show="!avatarLoading">
                <p class="title is-4">{{ user.username }}</p>
                <p class="subtitle is-6">@{{ location }}</p>
              </div>
            </div>
            <div class="content">
              {{ $t("userProfileCardContent") }}
              <br>
            </div>

            <div class="tabs is-toggle">
              <ul>
                <li :class="trueFalse2Class(inPins)">
                  <a @click="go2UserPins">
                    <b-icon
                      type="is-dark"
                      icon="image"
                      custom-size="mdi-24px">
                    </b-icon>
                    <span>{{ $t("pinsUserProfileCardLink") }}</span>
                  </a>
                </li>
                <li :class="trueFalse2Class(inBoard)">
                  <a @click="go2UserBoard">
                    <b-icon
                      type="is-dark"
                      icon="folder-multiple-image"
                      custom-size="mdi-24px">
                    </b-icon>
                    <span>{{ $t("boardsUserProfileCardLink") }}</span>
                  </a>
                </li>
                <li :class="trueFalse2Class(inComics)">
                  <a @click="go2UserComics">
                    <b-icon
                      type="is-dark"
                      icon="book-open-page-variant"
                      custom-size="mdi-24px">
                    </b-icon>
                    <span>{{ $t("comicsLink") }}</span>
                  </a>
                </li>
                <li :class="trueFalse2Class(inProfile)">
                  <a @click="go2UserProfile">
                    <b-icon
                      type="is-dark"
                      icon="account"
                      custom-size="mdi-24px">
                    </b-icon>
                    <span>{{ $t("profileUserProfileCardLink") }}</span>
                  </a>
                </li>
              </ul>
            </div>

          </div>
        </div>
      </div>
    </div>
</template>

<script>
import api from './api';

export default {
  name: 'UserProfileCard.vue',
  props: {
    username: String,
    inBoard: {
      type: Boolean,
      default: false,
    },
    inPins: {
      type: Boolean,
      default: false,
    },
    inComics: {
      type: Boolean,
      default: false,
    },
    inProfile: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      location: window.location.host,
      avatarLoading: true,
      user: {
        avatar: '',
        username: '',
      },
    };
  },
  beforeMount() {
    this.initializeUser(this.username);
  },
  methods: {
    go2UserBoard() {
      this.$router.push(
        { name: 'boards4user', params: { username: this.username } },
      );
    },
    go2UserComics() {
      this.$router.push(
        { name: 'comics4user', params: { username: this.username } },
      );
    },
    go2UserProfile() {
      this.$router.push(
        { name: 'profile4user', params: { username: this.username } },
      );
    },
    go2UserPins() {
      this.$router.push(
        { name: 'user', params: { user: this.username } },
      );
    },
    trueFalse2Class(boolValue) {
      if (boolValue) {
        return 'is-active';
      }
      return '';
    },
    onAvatarLoaded() {
      this.avatarLoading = false;
    },
    initializeUser(username) {
      const self = this;
      api.User.fetchUserInfoByName(username).then(
        (user) => {
          if (user === null) {
            self.$router.push(
              { name: 'PageNotFound' },
            );
          } else {
            self.user.avatar = (user.avatar && user.avatar.medium)
              || `//gravatar.com/avatar/${user.gravatar}?s=48`;
            self.user.username = user.username;
            self.user.meta = user;
          }
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
#user-home-container {
  margin-top: 2rem;
  margin-left: auto;
  margin-right: auto;
}
.card {
  overflow: hidden;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.12);
}
.card-content {
  padding: 1.25rem;
}
.media .image img {
  border-radius: 8px;
  box-shadow: 0 8px 18px rgba(16, 24, 40, 0.14);
}
.title {
  color: #22313f;
}
.subtitle,
.content {
  color: #64748b;
  font-size: 14px;
}
.tabs {
  margin-bottom: 0;
}
.tabs ul {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  width: 100%;
  border-bottom: 0;
}
.tabs li {
  min-width: 0;
}
.tabs a {
  display: flex;
  justify-content: center;
  border-radius: 6px;
  font-weight: 600;
  white-space: normal;
}
.tabs a span {
  overflow: hidden;
  text-overflow: ellipsis;
}
@import '../components/utils/grid-layout';
@include screen-grid-layout("#user-home-container");
@media screen and (max-width: 542px) {
  #user-home-container {
    max-width: calc(100vw - 24px);
  }
  .card-content {
    padding: 0.85rem;
  }
  .media {
    align-items: center;
  }
  .media-left {
    margin-right: 0.75rem;
  }
  .tabs ul {
    gap: 0.35rem;
  }
  .tabs a {
    display: grid;
    gap: 0.15rem;
    min-height: 58px;
    padding: 0.45rem 0.25rem;
    font-size: 0.78rem;
    line-height: 1.1;
    text-align: center;
  }
}
</style>
