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
  box-shadow: 5px 5px 2px 1px rgba(0, 0, 255, .1);
}
.card + .card {
  margin-top: 1rem;
}
.avatar-preview {
  border-radius: 4px;
  object-fit: cover;
}

@import '../utils/grid-layout';
@include screen-grid-layout(".profile-container");
</style>
