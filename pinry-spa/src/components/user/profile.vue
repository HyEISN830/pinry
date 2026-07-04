<template>
  <div class="profile-container">
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">
          {{ $t("avatarUserProfileCardTitle") }}
        </p>
      </header>
      <div class="card-content">
        <div class="media">
          <div class="media-left">
            <figure class="image is-96x96">
              <img class="avatar-preview" :src="avatarUrl" alt="avatar">
            </figure>
          </div>
          <div class="media-content">
            <b-field
              :message="avatarMessage"
              :type="avatarMessageType"
            >
              <b-upload
                v-model="avatarFile"
                accept="image/*"
                @input="uploadAvatar"
              >
                <a class="button is-primary" :class="{ 'is-loading': avatarUploading }">
                  <b-icon icon="upload"></b-icon>
                  <span>{{ $t("avatarUploadButton") }}</span>
                </a>
              </b-upload>
            </b-field>
            <p class="help">{{ $t("avatarUploadHint") }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <header class="card-header">
        <p class="card-header-title">
          {{ $t("tokenUserProfileCardTitle") }}
        </p>
      </header>
      <div class="card-content">
        <div class="content">
          <p>{{ $t("tokenUserProfileCardContent") }}</p>
          <pre>{{ token }}</pre>
          {{ $t("pleaseReadTokenUserProfileCardContent") }}<a target="_blank" href="https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication">{{ $t("drfApiDocumentationLink") }}</a>{{ $t("forMoreDetailsParagraph") }}
          <br>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

const MAX_AVATAR_SIZE = 2 * 1024 * 1024;

export default {
  name: 'profile',
  props: ['user'],
  data() {
    return {
      avatarFile: null,
      avatarUploading: false,
      avatarMessage: '',
      avatarMessageType: '',
    };
  },
  computed: {
    token() {
      return this.user.token;
    },
    avatarUrl() {
      if (this.user.avatar && this.user.avatar.large) {
        return this.user.avatar.large;
      }
      return `//gravatar.com/avatar/${this.user.gravatar}?s=96`;
    },
  },
  methods: {
    uploadAvatar(file) {
      if (!file) {
        return;
      }
      if (file.size > MAX_AVATAR_SIZE) {
        this.avatarMessage = this.$t('avatarUploadTooLarge');
        this.avatarMessageType = 'is-danger';
        this.avatarFile = null;
        return;
      }
      this.avatarUploading = true;
      this.avatarMessage = '';
      this.avatarMessageType = '';
      api.User.uploadAvatar(this.user, file).then(
        (resp) => {
          this.avatarUploading = false;
          this.avatarMessage = this.$t('avatarUploadSucceed');
          this.avatarMessageType = 'is-success';
          this.$emit('profile-updated', resp.data);
        },
        (error) => {
          const data = error && error.data ? error.data : {};
          this.avatarUploading = false;
          this.avatarMessage = data.avatar_file || this.$t('avatarUploadFailed');
          this.avatarMessageType = 'is-danger';
        },
      );
    },
  },
};
</script>

<style scoped lang="scss">
.profile-container {
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
.card-header {
  border-bottom-color: #edf1f6;
  background: #f8fafc;
  box-shadow: none;
}
.card-header-title {
  color: #22313f;
  font-size: 1rem;
}
.card-content {
  background: #fff;
}
.card + .card {
  margin-top: 1rem;
}
.avatar-preview {
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 12px 28px rgba(16, 24, 40, 0.14);
}
.button {
  border-radius: 6px;
  font-weight: 600;
}
pre {
  border-radius: 8px;
  background: #f8fafc;
  color: #22313f;
}

@import '../utils/grid-layout';
@include screen-grid-layout(".profile-container");
</style>
