<template>
  <div class="profile-container">
    <div class="profile-setting-card">
      <header class="setting-head">
        <p>
          {{ $t("avatarUserProfileCardTitle") }}
        </p>
      </header>
      <div class="setting-body avatar-setting">
        <figure class="avatar-frame">
          <img class="avatar-preview" :src="avatarUrl" alt="avatar">
        </figure>
        <div class="avatar-actions">
          <b-field
            :message="avatarMessage"
            :type="avatarMessageType"
          >
            <b-upload
              v-model="avatarFile"
              accept="image/*"
              @input="uploadAvatar"
            >
              <a
                class="button is-primary"
                :class="{ 'is-loading': avatarUploading }">
                <b-icon icon="upload"></b-icon>
                <span>{{ $t("avatarUploadButton") }}</span>
              </a>
            </b-upload>
          </b-field>
          <p class="help">{{ $t("avatarUploadHint") }}</p>
        </div>
      </div>
    </div>

    <div class="profile-setting-card">
      <header class="setting-head">
        <p>
          {{ $t("tokenUserProfileCardTitle") }}
        </p>
      </header>
      <div class="setting-body">
        <div class="token-content">
          <p>{{ $t("tokenUserProfileCardContent") }}</p>
          <pre>{{ token }}</pre>
          {{ $t("pleaseReadTokenUserProfileCardContent") }}
          <a
            target="_blank"
            :href="tokenHelpUrl">
            {{ $t("drfApiDocumentationLink") }}
          </a>
          {{ $t("forMoreDetailsParagraph") }}
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
    tokenHelpUrl() {
      return 'https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication';
    },
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
  width: min(100%, 1260px);
  margin: 1rem auto 0;
  padding: 0 0.75rem 2rem;
}
.profile-setting-card {
  overflow: hidden;
  border: 1px solid var(--line-soft, #e7ebf2);
  border-radius: 8px;
  color: var(--text-strong, #22313f);
  background: var(--surface-1, #fff);
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}
.setting-head {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--line-soft, #edf1f6);
  background: var(--surface-2, #f8fafc);
}
.setting-head p {
  margin: 0;
  color: var(--text-strong, #22313f);
  font-size: 1rem;
  font-weight: 900;
}
.setting-body {
  padding: 1rem;
  background: var(--surface-1, #fff);
}
.profile-setting-card + .profile-setting-card {
  margin-top: 1rem;
}
.avatar-setting {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
}
.avatar-frame {
  width: 96px;
  height: 96px;
  margin: 0;
}
.avatar-preview {
  display: block;
  width: 96px;
  height: 96px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 12px 28px rgba(16, 24, 40, 0.14);
}
.avatar-actions {
  min-width: 0;
}
.help,
.token-content {
  color: var(--text-muted, #64748b);
}
.button {
  border-radius: 6px;
  font-weight: 600;
}
pre {
  overflow: auto;
  border-radius: 8px;
  background: var(--surface-2, #f8fafc);
  color: var(--text-strong, #22313f);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

@media screen and (max-width: 542px) {
  .profile-container {
    margin-top: 0.75rem;
    padding: 0 0.55rem 1.5rem;
  }
  .setting-body {
    padding: 0.85rem;
  }
  .avatar-setting {
    grid-template-columns: 1fr;
  }
  .avatar-frame,
  .avatar-preview {
    width: 72px;
    height: 72px;
  }
  .button {
    width: 100%;
  }
}
</style>
