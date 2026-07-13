<template>
  <div class="image-upload">
    <div
      v-show="previewImage !== null"
      class="has-text-centered is-center preview">
      <img :src="previewImage">
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
      this.$emit('imageUploadProcessing');
      this.loading = true;
      API.Pin.uploadImage(newFile).then(
        (resp) => {
          this.uploadedImage = resp.data;
          this.loading = false;
          this.$emit('imageUploadSucceed', this.uploadedImage.id);
        },
        () => {
          this.loading = false;
          this.$emit('imageUploadFailed');
        },
      );
    },
  },
  computed: {
    previewImage() {
      if (this.previewExists()) {
        return this.previewImageURL;
      }
      if (this.uploadedImage !== null) {
        const thumbnail = imageVariant.getCardThumbnail(this.uploadedImage);
        return utils.escapeUrl(thumbnail.image);
      }
      return null;
    },
  },
  methods: {
    previewExists() {
      return this.previewImageURL !== null && this.previewImageURL !== '';
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../utils/pin';
@import '../utils/loader';

.preview > img {
  width: min(100%, $pin-preview-width);
  height: auto;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  @include loader();
}
.image-upload {
  border-radius: var(--radius-md);
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

</style>
