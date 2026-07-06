<template>
  <div class="pin-preview-modal">
    <section>
        <div class="card">
          <div class="card-image">
            <figure class="image preview-frame" :style="previewFrameStyle">
              <img
                v-if="activePreviewUrl"
                :src="activePreviewUrl"
                alt="Image"
                @error="onPreviewImageError"
                :class="{ 'is-loading-preview': imageLoading }">
              <div v-if="imageLoading || imageLoadFailed" class="preview-loading">
                <p v-if="imageLoadFailed">{{ $t("imageLoadFailedText") }}</p>
                <p v-else>{{ $t("imageLoadingText") }}</p>
                <progress
                  v-if="imageLoading && downloadPercent !== null"
                  class="progress is-info"
                  :value="downloadPercent"
                  max="100">
                  {{ downloadPercent }}%
                </progress>
              </div>
            </figure>
          </div>
          <div class="card-content">
            <div class="content">
                <p class="description title" v-html="niceLinks(pinItem.description)"></p>
            </div>
            <div class="media">
              <div class="media-left">
                <figure class="image is-48x48">
                  <img :src="pinItem.avatar" alt="Image">
                </figure>
              </div>
              <div class="media-content">
                <div class="is-pulled-left">
                  <p class="title is-4 pin-meta-info"><span class="dim">{{ $t("pinnedByTitle") }}</span><span class="author">{{ pinItem.author }}</span></p>
                  <p class="subtitle is-6" v-show="pinItem.tags.length > 0">
                    <span class="subtitle dim">in&nbsp;</span>
                    <template v-for="tag in pinItem.tags">
                      <b-tag v-bind:key="tag" type="is-info" class="pin-preview-tag">{{ tag }}</b-tag>
                    </template>
                  </p>
                </div>
                <div class="is-pulled-right">
                  <a
                    v-if="isWebUrl(pinItem.referer)"
                    :href="pinItem.referer"
                    target="_blank">
                    <b-button
                        class="meta-link"
                        type="is-warning">
                      {{ $t("sourceButton") }}
                    </b-button>
                  </a>
                  <span
                    v-else-if="hasSource(pinItem.referer)"
                    class="meta-link source-text-button"
                    :title="sourceText(pinItem.referer)">
                    {{ sourceText(pinItem.referer) }}
                  </span>
                  <span v-else class="meta-link source-missing-pill">
                    {{ $t("missingSourceNotice") }}
                  </span>
                  <a :href="pinItem.original_image_url" target="_blank">
                    <b-button
                        v-show="pinItem.original_image_url !== null"
                        class="meta-link"
                        type="is-link">
                        {{ $t("originalImageButton") }}
                    </b-button>
                  </a>
                  <b-button
                      @click="closeAndGoTo"
                      class="meta-link"
                      type="is-success">
                      {{ $t("permalinkButton") }}
                  </b-button>
                  <b-button
                      @click="downloadImage"
                      :disabled="!imageBlob"
                      :loading="imageLoading"
                      class="meta-link"
                      type="is-info">
                      {{ $t("downloadButton") }}
                  </b-button>
                </div>
              </div>
            </div>
          </div>
        </div>
    </section>
  </div>
</template>

<script>
import API from './api';
import niceLinks from './utils/niceLinks';
import {
  cacheImage,
  getCachedImage,
} from './utils/originalImageCache';

function fileNameFromUrl(url, fallback) {
  if (!url) {
    return fallback;
  }
  const cleanUrl = url.split('?')[0].split('#')[0];
  const name = cleanUrl.split('/').pop();
  return name || fallback;
}

function isWebUrl(url) {
  return /^https?:\/\//i.test((url || '').trim());
}

function hasSource(url) {
  return !!(url || '').trim();
}

function sourceText(url) {
  return (url || '').trim();
}

export default {
  name: 'PinPreview',
  props: ['pinItem'],
  data() {
    return {
      downloadLoaded: 0,
      downloadTotal: null,
      imageBlob: null,
      imageContentType: 'application/octet-stream',
      imageLoadFailed: false,
      imageLoading: true,
      imageRequestController: null,
      lastPartialPreviewAt: 0,
      partialPreviewUrl: null,
      partialPreviewFailed: false,
      previewImageUrl: null,
      previewImageUrlFromCache: false,
    };
  },
  computed: {
    activePreviewUrl() {
      if (this.previewImageUrl) {
        return this.previewImageUrl;
      }
      if (this.partialPreviewUrl && !this.partialPreviewFailed) {
        return this.partialPreviewUrl;
      }
      return this.pinItem.url;
    },
    downloadPercent() {
      if (!this.downloadTotal) {
        return null;
      }
      return Math.round((this.downloadLoaded / this.downloadTotal) * 100);
    },
    previewFrameStyle() {
      if (!this.pinItem.url) {
        return {};
      }
      return {
        backgroundImage: `url(${this.pinItem.url})`,
      };
    },
  },
  created() {
    this.loadOriginalImage();
  },
  beforeDestroy() {
    if (this.imageRequestController) {
      this.imageRequestController.abort();
    }
    if (this.partialPreviewUrl) {
      URL.revokeObjectURL(this.partialPreviewUrl);
    }
    if (this.previewImageUrl && !this.previewImageUrlFromCache) {
      URL.revokeObjectURL(this.previewImageUrl);
    }
  },
  methods: {
    updatePartialPreview(chunks) {
      const now = Date.now();
      if (now - this.lastPartialPreviewAt < 1000 || chunks.length === 0) {
        return;
      }
      this.lastPartialPreviewAt = now;
      if (this.partialPreviewUrl) {
        URL.revokeObjectURL(this.partialPreviewUrl);
      }
      this.partialPreviewUrl = URL.createObjectURL(
        new Blob(chunks, { type: this.imageContentType }),
      );
      this.partialPreviewFailed = false;
    },
    onPreviewImageError() {
      if (!this.imageLoading || !this.partialPreviewUrl) {
        return;
      }
      this.partialPreviewFailed = true;
    },
    readStream(reader, chunks) {
      return reader.read().then(
        ({ done, value }) => {
          if (done) {
            return new Blob(chunks, { type: this.imageContentType });
          }
          chunks.push(value);
          this.downloadLoaded += value.length;
          this.updatePartialPreview(chunks);
          return this.readStream(reader, chunks);
        },
      );
    },
    loadOriginalImage() {
      const cached = getCachedImage(this.pinItem.image_id);
      if (cached) {
        this.imageBlob = cached.blob;
        this.previewImageUrl = cached.objectUrl;
        this.previewImageUrlFromCache = true;
        this.imageLoading = false;
        return;
      }
      if (window.AbortController) {
        this.imageRequestController = new AbortController();
      }
      const signal = this.imageRequestController
        ? this.imageRequestController.signal
        : null;
      API.Pin.fetchOriginalImage(this.pinItem.image_id, signal).then(
        (response) => {
          if (!response.ok) {
            throw new Error('Failed to load original image');
          }
          const total = parseInt(response.headers.get('Content-Length'), 10);
          this.downloadTotal = Number.isNaN(total) ? null : total;
          this.imageContentType = response.headers.get('Content-Type')
            || 'application/octet-stream';
          if (!response.body || !response.body.getReader) {
            return response.blob();
          }
          return this.readStream(response.body.getReader(), []);
        },
      ).then(
        (blob) => {
          this.imageBlob = blob;
          if (this.partialPreviewUrl) {
            URL.revokeObjectURL(this.partialPreviewUrl);
            this.partialPreviewUrl = null;
          }
          const cachedImage = cacheImage(this.pinItem.image_id, blob);
          if (cachedImage) {
            this.previewImageUrl = cachedImage.objectUrl;
            this.previewImageUrlFromCache = true;
          } else {
            this.previewImageUrl = URL.createObjectURL(blob);
          }
          this.imageLoading = false;
        },
      ).catch(
        () => {
          this.imageLoadFailed = true;
          this.imageLoading = false;
        },
      );
    },
    downloadImage() {
      if (!this.imageBlob || !this.previewImageUrl) {
        return;
      }
      const link = document.createElement('a');
      link.href = this.previewImageUrl;
      link.download = fileNameFromUrl(
        this.pinItem.large_image_url,
        `pin-${this.pinItem.id}`,
      );
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    closeAndGoTo() {
      this.$parent.close();
      this.$router.push(
        { name: 'pin', params: { pinId: this.pinItem.id } },
      );
    },
    hasSource,
    isWebUrl,
    niceLinks,
    sourceText,
  },
};
</script>

<style lang="scss" scoped>
@import './utils/fonts.scss';

.meta-link {
  margin-left: 0.45rem;
  margin-bottom: 0.35rem;
}
.source-text-button,
.source-missing-pill {
  display: inline-flex;
  align-items: center;
  min-height: 2.25em;
  max-width: 220px;
  padding: 0 0.75em;
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.5;
  vertical-align: top;
}
.source-text-button {
  overflow: hidden;
  color: #8fb8ff;
  border: 1px solid rgba(143, 184, 255, 0.22);
  background: rgba(31, 111, 235, 0.1);
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.source-missing-pill {
  color: #d7bd75;
  border: 1px solid rgba(215, 189, 117, 0.25);
  background: rgba(215, 189, 117, 0.1);
}
.dim {
  @include secondary-font-color-in-dark;
}
.pin-meta-info {
  line-height: 16px;
}
.card {
  overflow: hidden;
  border-radius: 8px;
  background-color: rgba(12, 16, 24, 0.94);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
  .content {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  .card-content {
    .author {
      @include title-font-color-in-dark;
    }
    padding: 0;
    .content {
      padding: 0.75rem 0.9rem;
      margin-bottom: 0;
    }
    .media {
      padding: 0.85rem 0.9rem;
    }
  }
  .description {
    @include title-font;
    @include title-font-color-in-dark;
    font-size: 17px;
    line-height: 1.45;
    padding: 0;
  }
}
.pin-preview-tag {
  margin-right: 0.2rem;
  margin-bottom: 2px;
}
.preview-loading {
  position: absolute;
  z-index: 3;
  left: 50%;
  bottom: 24px;
  width: min(420px, calc(100% - 40px));
  padding: 1rem;
  transform: translateX(-50%);
  color: white;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 8px;
  background: rgba(9, 12, 18, 0.56);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
}
.preview-loading .progress {
  margin: 0.75rem auto 0;
}
.preview-frame {
  position: relative;
  min-height: 280px;
  overflow: hidden;
  background-position: center;
  background-repeat: no-repeat;
  background-size: contain;
}
.preview-frame::before {
  content: "";
  position: absolute;
  inset: -24px;
  z-index: 0;
  background: inherit;
  background-size: cover;
  filter: blur(22px);
  opacity: 0.28;
}
.preview-frame img {
  position: relative;
  z-index: 1;
  transition: filter .3s ease, opacity .3s ease;
}
.preview-frame img.is-loading-preview {
  filter: blur(1.5px);
  opacity: 0.78;
}
/* preview size should always less then screen */
.card-image img {
  padding: 10px;
  margin-left: auto;
  margin-right: auto;
  width: auto;
  max-height: 78vh;
}
</style>
