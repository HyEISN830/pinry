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
  width: $pin-preview-width;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 10px 26px rgba(16, 24, 40, 0.14);
  @include loader('../../assets/loader.gif');
}
.image-upload {
  border-radius: 8px;
}
.image-upload ::v-deep .upload-draggable {
  border-color: #d8e0eb;
  border-radius: 8px;
  background: #f8fafc;
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}
.image-upload ::v-deep .upload-draggable:hover {
  border-color: #1f6feb;
  box-shadow: 0 10px 26px rgba(16, 24, 40, 0.12);
  transform: translateY(-2px);
}

</style>
