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
              @input="openAvatarCropper"
            >
              <a
                class="button avatar-upload-button"
                :class="{ 'is-loading': avatarUploading }">
                <b-icon icon="account-edit"></b-icon>
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

    <AvatarCropper
      v-if="avatarCropSource"
      :file="avatarCropSource"
      :uploading="avatarUploading"
      :upload-progress="avatarUploadProgress"
      :upload-error="avatarCropError"
      @cancel="closeAvatarCropper"
      @error="onAvatarCropError"
      @confirm="uploadAvatar">
    </AvatarCropper>
  </div>
</template>

<script>
import api from '../api';
import AvatarCropper from './AvatarCropper.vue';

const MAX_AVATAR_SOURCE_SIZE = 10 * 1024 * 1024;

export default {
  name: 'profile',
  props: ['user'],
  components: { AvatarCropper },
  data() {
    return {
      avatarCropError: '',
      avatarCropSource: null,
      avatarFile: null,
      avatarUploadProgress: 0,
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
    openAvatarCropper(file) {
      if (!file) {
        return;
      }
      if (file.size > MAX_AVATAR_SOURCE_SIZE) {
        this.avatarMessage = this.$t('avatarUploadTooLarge');
        this.avatarMessageType = 'is-danger';
        this.avatarFile = null;
        return;
      }
      this.avatarCropSource = file;
      this.avatarCropError = '';
      this.avatarUploadProgress = 0;
      this.avatarMessage = '';
      this.avatarMessageType = '';
    },
    closeAvatarCropper() {
      if (this.avatarUploading) {
        return;
      }
      this.avatarCropSource = null;
      this.avatarCropError = '';
      this.avatarFile = null;
      this.avatarUploadProgress = 0;
    },
    onAvatarUploadProgress(event) {
      const loaded = Number(event.loaded);
      const total = Number(event.total);
      if (!Number.isFinite(loaded) || !Number.isFinite(total) || total <= 0) {
        return;
      }
      this.avatarUploadProgress = Math.min(
        99,
        Math.max(0, Math.round((loaded / total) * 100)),
      );
    },
    onAvatarCropError() {
      this.avatarCropError = this.$t('avatarCropFailed');
      this.avatarMessage = this.avatarCropError;
      this.avatarMessageType = 'is-danger';
    },
    uploadAvatar(file) {
      this.avatarUploading = true;
      this.avatarCropError = '';
      this.avatarUploadProgress = 0;
      this.avatarMessage = '';
      this.avatarMessageType = '';
      api.User.uploadAvatar(file, this.onAvatarUploadProgress).then(
        (resp) => {
          this.avatarUploadProgress = 100;
          this.avatarUploading = false;
          this.avatarMessage = this.$t('avatarUploadSucceed');
          this.avatarMessageType = 'is-success';
          this.$emit('profile-updated', resp.data);
          this.closeAvatarCropper();
        },
        (error) => {
          const response = error && error.response ? error.response : error;
          const data = response && response.data ? response.data : {};
          this.avatarUploading = false;
          this.avatarCropError = data.avatar_file || this.$t('avatarUploadFailed');
          this.avatarMessage = this.avatarCropError;
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
.avatar-upload-button {
  gap: var(--space-xs);
  min-height: 42px;
  border: 1px solid var(--color-accent-strong);
  border-radius: var(--radius-sm);
  color: var(--color-accent-text);
  background: var(--color-accent-strong);
  box-shadow: 0 10px 24px var(--color-theme-glow);
  font-weight: 900;
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
}
.avatar-upload-button:hover,
.avatar-upload-button:focus-visible {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  background: var(--color-accent);
  box-shadow: 0 14px 30px var(--color-theme-glow-strong);
  transform: translateY(-2px);
}
.avatar-upload-button:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
.avatar-upload-button ::v-deep .icon {
  transition: transform var(--motion-duration-standard) var(--motion-ease-spring);
}
.avatar-upload-button:hover ::v-deep .icon {
  transform: rotate(-5deg) scale(1.12);
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
  .avatar-upload-button {
    width: 100%;
  }
}
</style>
