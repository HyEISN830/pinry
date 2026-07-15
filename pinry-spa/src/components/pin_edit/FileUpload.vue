<template>
  <div class="image-upload">
    <div
      v-show="previewImage !== null"
      class="image-upload-preview-shell">
      <div class="has-text-centered is-center preview">
        <img :src="previewImage" @load="onPreviewLoaded">
      </div>
      <div v-if="hasSelectedFile" class="selected-image-meta">
        <span class="selected-image-meta__icon" aria-hidden="true">
          <b-icon icon="file-image" custom-size="mdi-20px"></b-icon>
        </span>
        <div class="selected-image-meta__copy">
          <strong :title="selectedFileName">{{ selectedFileName }}</strong>
          <span>{{ fileSizeLabel }} · {{ imageDimensionsLabel }}</span>
        </div>
      </div>
      <div
        v-if="showUploadStatus"
        class="image-upload-progress"
        :class="uploadStatusClass">
        <div class="image-upload-progress__heading">
          <span>
            <b-icon :icon="uploadStatusIcon" custom-size="mdi-18px"></b-icon>
            {{ uploadStatusText }}
          </span>
          <strong v-if="uploadProgressKnown">{{ uploadProgress }}%</strong>
        </div>
        <div
          class="image-upload-progress__track"
          :class="{ 'is-indeterminate': loading && !uploadProgressKnown }"
          role="progressbar"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-valuenow="uploadProgressKnown ? uploadProgress : null"
          :aria-label="uploadStatusText">
          <span
            class="image-upload-progress__fill"
            :style="uploadProgressStyle">
          </span>
        </div>
      </div>
    </div>
    <div v-show="previewImage === null">
      <b-field>
        <b-upload v-model="dropFile"
                  accept="image/*"
                  :loading="loading"
                  drag-drop>
          <section class="section">
            <div class="content has-text-centered">
              <p>
                <b-icon
                  icon="upload"
                  size="is-medium">
                </b-icon>
              </p>
              <p>{{ $t("FileUploadDescription") }}</p>
            </div>
          </section>
        </b-upload>
      </b-field>
    </div>
  </div>
</template>

<script>
import API from '../api';
import utils from '../utils/PinHandler';
import imageVariant from '../utils/imageVariant';

export default {
  name: 'FileUpload',
  data() {
    return {
      dropFile: null,
      loading: false,
      uploadedImage: null,
      localPreviewURL: null,
      imageWidth: null,
      imageHeight: null,
      uploadProgress: 0,
      uploadProgressKnown: false,
      uploadState: 'idle',
    };
  },
  props: {
    previewImageURL: {
      type: String,
      default: null,
    },
  },
  watch: {
    dropFile(newFile) {
      if (!newFile) {
        return;
      }
      this.prepareSelectedFile(newFile);
      this.$emit('imageUploadProcessing');
      this.loading = true;
      API.Pin.uploadImage(newFile, this.onUploadProgress).then(
        (resp) => {
          this.uploadedImage = resp.data;
          if (!this.imageWidth && resp.data) {
            this.imageWidth = resp.data.width || null;
            this.imageHeight = resp.data.height || null;
          }
          this.uploadProgress = 100;
          this.uploadProgressKnown = true;
          this.uploadState = 'complete';
          this.loading = false;
          this.$emit('imageUploadSucceed', this.uploadedImage.id);
        },
        () => {
          this.loading = false;
          this.uploadProgress = 0;
          this.uploadProgressKnown = false;
          this.uploadState = 'failed';
          this.$emit('imageUploadFailed');
        },
      );
    },
  },
  beforeDestroy() {
    this.revokeLocalPreview();
  },
  computed: {
    previewImage() {
      if (this.previewExists()) {
        return this.previewImageURL;
      }
      if (this.localPreviewURL !== null) {
        return this.localPreviewURL;
      }
      if (this.uploadedImage !== null) {
        const thumbnail = imageVariant.getCardThumbnail(this.uploadedImage);
        return utils.escapeUrl(thumbnail.image);
      }
      return null;
    },
    hasSelectedFile() {
      return this.dropFile !== null;
    },
    selectedFileName() {
      return this.dropFile ? this.dropFile.name : '';
    },
    fileSizeLabel() {
      if (!this.dropFile) {
        return '';
      }
      const units = ['B', 'KB', 'MB', 'GB'];
      const { size: fileSize } = this.dropFile;
      let size = fileSize;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex += 1;
      }
      const fractionDigits = unitIndex === 0 || size >= 10 ? 0 : 1;
      return `${size.toFixed(fractionDigits)} ${units[unitIndex]}`;
    },
    imageDimensionsLabel() {
      if (this.imageWidth && this.imageHeight) {
        return `${this.imageWidth} × ${this.imageHeight} px`;
      }
      return this.$t('imageDimensionsReading');
    },
    showUploadStatus() {
      return this.uploadState !== 'idle';
    },
    uploadStatusText() {
      if (this.uploadState === 'complete') {
        return this.$t('imageUploadComplete');
      }
      if (this.uploadState === 'failed') {
        return this.$t('imageUploadFailed');
      }
      return this.$t('imageUploadInProgress');
    },
    uploadStatusIcon() {
      if (this.uploadState === 'complete') {
        return 'check-circle';
      }
      if (this.uploadState === 'failed') {
        return 'alert-circle';
      }
      return 'upload';
    },
    uploadStatusClass() {
      return {
        'is-complete': this.uploadState === 'complete',
        'is-failed': this.uploadState === 'failed',
      };
    },
    uploadProgressStyle() {
      return {
        width: `${this.uploadProgress}%`,
      };
    },
  },
  methods: {
    previewExists() {
      return this.previewImageURL !== null && this.previewImageURL !== '';
    },
    prepareSelectedFile(file) {
      this.revokeLocalPreview();
      this.uploadedImage = null;
      this.imageWidth = null;
      this.imageHeight = null;
      this.uploadProgress = 0;
      this.uploadProgressKnown = false;
      this.uploadState = 'uploading';
      if (window.URL && typeof window.URL.createObjectURL === 'function') {
        this.localPreviewURL = window.URL.createObjectURL(file);
      }
    },
    revokeLocalPreview() {
      if (
        this.localPreviewURL
        && window.URL
        && typeof window.URL.revokeObjectURL === 'function'
      ) {
        window.URL.revokeObjectURL(this.localPreviewURL);
      }
      this.localPreviewURL = null;
    },
    onPreviewLoaded(event) {
      if (!this.dropFile || !event.target) {
        return;
      }
      this.imageWidth = event.target.naturalWidth || this.imageWidth;
      this.imageHeight = event.target.naturalHeight || this.imageHeight;
    },
    onUploadProgress(event) {
      const loaded = Number(event.loaded);
      const total = Number(event.total);
      if (!Number.isFinite(loaded) || !Number.isFinite(total) || total <= 0) {
        return;
      }
      this.uploadProgressKnown = true;
      this.uploadProgress = Math.min(
        99,
        Math.max(0, Math.round((loaded / total) * 100)),
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../utils/pin';
@import '../utils/loader';

.preview {
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  box-shadow: var(--shadow-card);
}
.preview > img {
  display: block;
  width: min(100%, $pin-preview-width);
  height: auto;
  margin: 0 auto;
  @include loader();
}
.image-upload {
  border-radius: var(--radius-md);
}
.image-upload-preview-shell {
  display: grid;
  gap: var(--space-xs);
}
.selected-image-meta,
.image-upload-progress {
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-2) 78%, transparent);
}
.selected-image-meta {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
}
.selected-image-meta__icon {
  display: inline-grid;
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  place-items: center;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-sm);
  color: var(--color-accent-strong);
  background: var(--color-accent-soft-gradient);
}
.selected-image-meta__copy {
  display: grid;
  min-width: 0;
  gap: 2px;
  text-align: left;
}
.selected-image-meta__copy strong {
  overflow: hidden;
  color: var(--color-text-strong);
  font-size: 0.82rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.selected-image-meta__copy span {
  color: var(--color-text-muted);
  font-size: 0.74rem;
  font-weight: 750;
}
.image-upload-progress {
  position: relative;
  overflow: hidden;
  padding: var(--space-xs) var(--space-sm) var(--space-sm);
}
.image-upload-progress::before {
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 20%, var(--color-theme-glow) 50%, transparent 80%);
  content: '';
  opacity: 0.62;
  pointer-events: none;
  transform: translateX(-100%);
  animation: image-upload-glow 2.4s var(--motion-ease-standard) infinite;
}
.image-upload-progress__heading {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs);
  margin-bottom: var(--space-xs);
  color: var(--color-text-muted);
  font-size: 0.76rem;
  font-weight: 850;
}
.image-upload-progress__heading span {
  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: var(--space-2xs);
}
.image-upload-progress__heading strong {
  color: var(--color-accent-strong);
  font-size: 0.78rem;
}
.image-upload-progress__track {
  position: relative;
  height: 7px;
  overflow: hidden;
  border-radius: var(--radius-pill);
  background: color-mix(in srgb, var(--color-line-soft) 78%, transparent);
}
.image-upload-progress__fill {
  position: absolute;
  inset: 0 auto 0 0;
  overflow: hidden;
  border-radius: inherit;
  background: var(--color-accent-progress);
  box-shadow: 0 0 16px var(--color-theme-glow-strong);
  transition: width var(--motion-duration-standard) var(--motion-ease-emphasized);
}
.image-upload-progress__fill::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    color-mix(in srgb, var(--color-accent-text) 72%, transparent),
    transparent
  );
  content: '';
  transform: translateX(-100%);
  animation: image-upload-shimmer 1.35s ease-in-out infinite;
}
.image-upload-progress__track.is-indeterminate .image-upload-progress__fill {
  width: 42% !important;
  animation: image-upload-indeterminate 1.45s var(--motion-ease-emphasized) infinite;
}
.image-upload-progress.is-complete {
  border-color: var(--color-accent-border);
}
.image-upload-progress.is-complete::before,
.image-upload-progress.is-failed::before {
  animation: none;
  opacity: 0.28;
  transform: none;
}
.image-upload-progress.is-complete .image-upload-progress__heading {
  color: var(--color-accent-strong);
}
.image-upload-progress.is-failed .image-upload-progress__fill {
  width: 0 !important;
}
@keyframes image-upload-glow {
  0%, 32% { transform: translateX(-100%); }
  72%, 100% { transform: translateX(100%); }
}
@keyframes image-upload-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
@keyframes image-upload-indeterminate {
  0% { left: -44%; }
  100% { left: 104%; }
}
.image-upload ::v-deep .upload-draggable {
  width: 100%;
  border-color: var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 180px),
    var(--color-surface-2);
  transition:
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard),
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard);
}
.image-upload ::v-deep .upload-draggable .section {
  padding: var(--space-xl) var(--space-md);
}
.image-upload ::v-deep .upload-draggable:hover {
  border-color: var(--color-accent-border);
  color: var(--color-accent-strong);
  box-shadow: var(--shadow-xs);
  transform: translateY(-2px);
}

@media (prefers-reduced-motion: reduce) {
  .image-upload-progress::before,
  .image-upload-progress__fill,
  .image-upload-progress__fill::after {
    animation: none !important;
  }
}

</style>
