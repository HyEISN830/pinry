<template>
  <section class="user-profile-card">
    <div id="user-home-container">
      <div class="profile-surface">
        <div class="profile-main">
          <figure class="profile-avatar">
            <b-skeleton width="72px" height="72px" :active="avatarLoading"></b-skeleton>
            <img
              v-show="!avatarLoading"
              :src="user.avatar"
              alt="avatar"
              @load="onAvatarLoaded">
          </figure>
          <div class="profile-copy">
            <span class="profile-kicker">@{{ location }}</span>
            <h1>{{ user.username || username }}</h1>
            <p>{{ $t("userProfileCardContent") }}</p>
          </div>
        </div>
        <nav class="profile-nav" aria-label="profile navigation">
          <button
            class="profile-tab"
            type="button"
            :class="trueFalse2Class(inPins)"
            @click="go2UserPins">
            <b-icon icon="image" custom-size="mdi-22px"></b-icon>
            <span>{{ $t("pinsUserProfileCardLink") }}</span>
          </button>
          <button
            class="profile-tab"
            type="button"
            :class="trueFalse2Class(inBoard)"
            @click="go2UserBoard">
            <b-icon icon="folder-multiple-image" custom-size="mdi-22px"></b-icon>
            <span>{{ $t("boardsUserProfileCardLink") }}</span>
          </button>
          <button
            class="profile-tab"
            type="button"
            :class="trueFalse2Class(inComics)"
            @click="go2UserComics">
            <b-icon icon="book-open-page-variant" custom-size="mdi-22px"></b-icon>
            <span>{{ $t("comicsLink") }}</span>
          </button>
          <button
            class="profile-tab"
            type="button"
            :class="trueFalse2Class(inProfile)"
            @click="go2UserProfile">
            <b-icon icon="account" custom-size="mdi-22px"></b-icon>
            <span>{{ $t("profileUserProfileCardLink") }}</span>
          </button>
        </nav>
      </div>
    </div>
  </section>
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
      api.User.fetchUserInfoByName(username).then(
        (user) => {
          if (user === null) {
            this.$router.push(
              { name: 'PageNotFound' },
            );
            return;
          }
          this.user.avatar = (user.avatar && user.avatar.medium)
            || `//gravatar.com/avatar/${user.gravatar}?s=72`;
          this.user.username = user.username;
          this.user.meta = user;
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
#user-home-container {
  width: min(100%, 1260px);
  margin: 1.35rem auto 0;
  padding: 0 0.75rem;
}
.profile-surface {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  color: var(--text-strong, #22313f);
  background:
    radial-gradient(circle at top left, var(--accent-soft, rgba(126, 87, 194, 0.12)), transparent 290px),
    var(--surface-1, #fff);
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}
.profile-main {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 0.95rem;
}
.profile-avatar {
  position: relative;
  flex: 0 0 auto;
  width: 72px;
  height: 72px;
  margin: 0;
}
.profile-avatar img {
  display: block;
  width: 72px;
  height: 72px;
  border: 3px solid var(--surface-1, #fff);
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 12px 26px rgba(16, 24, 40, 0.18);
}
.profile-copy {
  min-width: 0;
}
.profile-kicker {
  display: inline-flex;
  max-width: 100%;
  overflow: hidden;
  color: var(--accent-strong, #7e57c2);
  font-size: 0.85rem;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.profile-copy h1 {
  overflow: hidden;
  margin: 0.15rem 0 0;
  color: var(--text-strong, #22313f);
  font-size: clamp(1.25rem, 2vw, 1.75rem);
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.profile-copy p {
  margin: 0.28rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 0.95rem;
  line-height: 1.45;
}
.profile-nav {
  display: grid;
  grid-template-columns: repeat(4, minmax(74px, 1fr));
  gap: 0.45rem;
  min-width: min(100%, 430px);
}
.profile-tab {
  display: grid;
  place-items: center;
  gap: 0.25rem;
  min-height: 64px;
  padding: 0.5rem 0.55rem;
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  color: var(--text-muted, #64748b);
  background: var(--surface-2, #f8fafc);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 900;
  line-height: 1.15;
  text-align: center;
  transition: transform .16s ease, color .16s ease, background .16s ease, border-color .16s ease;
}
.profile-tab:hover {
  transform: translateY(-1px);
  color: var(--accent-strong, #7e57c2);
  border-color: var(--accent, #7e57c2);
  background: var(--accent-soft, rgba(126, 87, 194, 0.12));
}
.profile-tab.is-active {
  color: var(--accent-strong, #7e57c2);
  border-color: var(--accent, #7e57c2);
  background: var(--accent-soft, rgba(126, 87, 194, 0.12));
}
.profile-tab span {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@media screen and (max-width: 920px) {
  .profile-surface {
    grid-template-columns: 1fr;
  }
  .profile-nav {
    min-width: 0;
    width: 100%;
  }
}
@media screen and (max-width: 542px) {
  #user-home-container {
    margin-top: 0.8rem;
    padding: 0 0.55rem;
  }
  .profile-surface {
    padding: 0.8rem;
  }
  .profile-main {
    align-items: flex-start;
  }
  .profile-avatar,
  .profile-avatar img {
    width: 58px;
    height: 58px;
  }
  .profile-copy p {
    font-size: 0.88rem;
  }
  .profile-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .profile-tab {
    min-height: 52px;
    grid-template-columns: auto minmax(0, auto);
    place-items: center;
    justify-content: center;
  }
}
</style>
