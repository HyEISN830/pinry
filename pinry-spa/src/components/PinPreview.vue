<template>
  <div class="pin-preview-modal">
    <section class="pin-preview-surface">
        <article class="pin-preview-card motion-card-enter" :style="previewCardStyle">
          <section
            class="pin-preview-stage"
            :class="{ 'is-landscape-preview': isLandscapePreview }">
            <div
              class="pin-preview-backdrop"
              :style="previewBackdropStyle"
              aria-hidden="true"></div>
            <img
              v-if="activePreviewUrl"
              class="pin-preview-image"
              :src="activePreviewUrl"
              :style="previewImageStyle"
              alt="Image"
              @load="onPreviewImageLoad"
              @error="onPreviewImageError"
              :class="{ 'is-loading-preview': imageLoading }">
            <video
              v-if="hasMotionPhoto"
              ref="motionVideo"
              class="motion-preview-video"
              :class="{ 'is-active': motionVideoActive }"
              :src="pinItem.motion_photo.video"
              muted
              playsinline
              preload="metadata"
              @play="motionVideoActive = true"
              @ended="onMotionVideoEnded"
              @error="motionVideoFailed = true">
            </video>
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
          </section>
          <section ref="previewContent" class="pin-preview-details">
            <p
              v-if="pinItem.description"
              class="pin-preview-description"
              v-html="niceLinks(pinItem.description)"></p>
            <div class="pin-preview-footer">
              <div class="pin-preview-meta">
                <div class="pin-preview-actions">
                  <a
                    v-if="isWebUrl(pinItem.referer)"
                    v-source-tooltip
                    :href="pinItem.referer"
                    :data-source-tip="sourceText(pinItem.referer)"
                    target="_blank"
                    rel="noopener">
                    <b-button class="meta-link" type="is-warning">{{ $t("sourceButton") }}</b-button>
                  </a>
                  <span
                    v-else-if="hasSource(pinItem.referer)"
                    v-source-tooltip
                    class="meta-link source-text-button"
                    tabindex="0"
                    :data-source-tip="sourceText(pinItem.referer)">
                    {{ sourceText(pinItem.referer) }}
                  </span>
                  <span v-else class="meta-link source-missing-pill">{{ $t("missingSourceNotice") }}</span>
                  <a v-if="pinItem.original_image_url" :href="pinItem.original_image_url" target="_blank" rel="noopener">
                    <b-button class="meta-link" type="is-link">{{ $t("originalImageButton") }}</b-button>
                  </a>
                  <b-button @click="closeAndGoTo" class="meta-link" type="is-success">{{ $t("permalinkButton") }}</b-button>
                  <b-button
                    @click="openFullView"
                    :disabled="!previewImageUrl || imageLoading"
                    class="meta-link"
                    type="is-primary">
                    {{ $t("viewFullImageButton") }}
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
                <div v-if="pinItem.tags.length > 0" class="pin-preview-tag-container">
                  <div class="pin-preview-tags">
                    <template v-for="tag in pinItem.tags">
                      <b-tag v-bind:key="tag" type="is-info" class="content-tag-pill pin-preview-tag">{{ tag }}</b-tag>
                    </template>
                  </div>
                </div>
                <div class="pin-preview-identity">
                  <img class="pin-preview-avatar" :src="pinItem.avatar" alt="Image">
                  <p class="pin-preview-author"><span class="dim">{{ $t("pinnedByTitle") }}</span><span class="author">{{ pinItem.author }}</span></p>
                </div>
              </div>
            </div>
          </section>
        </article>
    </section>
    <div
      v-if="fullViewOpen"
      class="full-image-viewer"
      role="dialog"
      aria-modal="true"
      @click.self="closeFullView"
      @wheel.stop
      @touchmove.stop
      @mousedown.stop>
      <div class="full-image-toolbar">
        <strong>{{ $t("viewFullImageButton") }}</strong>
        <button type="button" @click="closeFullView">
          {{ $t("closeButton") }}
        </button>
      </div>
      <div class="full-image-stage">
        <img :src="previewImageUrl" alt="Image">
      </div>
    </div>
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
      bodyOverflowSnapshot: null,
      fullViewOpen: false,
      imageContentType: 'application/octet-stream',
      imageLoadFailed: false,
      imageLoading: true,
      imageRequestController: null,
      previewImageUrl: null,
      previewImageUrlFromCache: false,
      previewLayoutFrame: null,
      previewNaturalHeight: 0,
      previewNaturalWidth: 0,
      previewPopupGeometry: null,
      motionReplayTimer: null,
      motionVideoActive: false,
      motionVideoFailed: false,
    };
  },
  computed: {
    activePreviewUrl() {
      return this.previewImageUrl || this.pinItem.url;
    },
    previewBackdropStyle() {
      const source = this.pinItem.url || this.previewImageUrl;
      return source ? { backgroundImage: `url("${source}")` } : {};
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
    hasMotionPhoto() {
      return !!(
        this.pinItem.motion_photo
        && this.pinItem.motion_photo.video
        && !this.motionVideoFailed
      );
    },
    isLandscapePreview() {
      return this.previewNaturalWidth > this.previewNaturalHeight;
    },
    previewImageStyle() {
      if (!this.previewPopupGeometry) {
        return {};
      }
      return {
        height: `${this.previewPopupGeometry.imageHeight}px`,
        width: `${this.previewPopupGeometry.imageWidth}px`,
      };
    },
    previewCardStyle() {
      if (!this.previewPopupGeometry) {
        return {};
      }
      return {
        '--pin-preview-details-height': `${this.previewPopupGeometry.detailsHeight}px`,
        '--pin-preview-stage-height': `${this.previewPopupGeometry.stageHeight}px`,
        '--pin-preview-stage-padding-x': `${this.previewPopupGeometry.horizontalPadding}px`,
        '--pin-preview-stage-padding-y': `${this.previewPopupGeometry.verticalPadding}px`,
        width: `${this.previewPopupGeometry.width}px`,
      };
    },
  },
  created() {
    this.loadOriginalImage();
  },
  mounted() {
    document.addEventListener('keydown', this.onKeydown);
    window.addEventListener('resize', this.queuePreviewLayout);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.queuePreviewLayout);
    if (this.previewLayoutFrame) {
      window.cancelAnimationFrame(this.previewLayoutFrame);
    }
    if (this.imageRequestController) {
      this.imageRequestController.abort();
    }
    if (this.previewImageUrl && !this.previewImageUrlFromCache) {
      URL.revokeObjectURL(this.previewImageUrl);
    }
    if (this.motionReplayTimer) {
      window.clearTimeout(this.motionReplayTimer);
    }
    document.removeEventListener('keydown', this.onKeydown);
    this.unlockBodyScroll();
  },
  methods: {
    lockBodyScroll() {
      if (this.bodyOverflowSnapshot !== null) {
        return;
      }
      const { body } = document;
      this.bodyOverflowSnapshot = body.style.overflow;
      body.style.overflow = 'hidden';
    },
    unlockBodyScroll() {
      if (this.bodyOverflowSnapshot === null) {
        return;
      }
      const { body } = document;
      body.style.overflow = this.bodyOverflowSnapshot;
      this.bodyOverflowSnapshot = null;
    },
    openFullView() {
      if (!this.previewImageUrl || this.imageLoading) {
        return;
      }
      this.fullViewOpen = true;
      this.lockBodyScroll();
    },
    closeFullView() {
      if (!this.fullViewOpen) {
        return;
      }
      this.fullViewOpen = false;
      this.unlockBodyScroll();
    },
    onKeydown(event) {
      if (event.key === 'Escape') {
        this.closeFullView();
      }
    },
    onPreviewImageError() {
      this.previewNaturalWidth = 0;
      this.previewNaturalHeight = 0;
      this.previewPopupGeometry = null;
      this.imageLoadFailed = !this.pinItem.url;
    },
    onPreviewImageLoad(event) {
      const image = event.target;
      if (!image || !image.naturalWidth || !image.naturalHeight) {
        return;
      }
      this.previewNaturalWidth = image.naturalWidth;
      this.previewNaturalHeight = image.naturalHeight;
      this.queuePreviewLayout();
    },
    queuePreviewLayout() {
      if (!this.previewNaturalWidth || !this.previewNaturalHeight || this.previewLayoutFrame) {
        return;
      }
      this.previewLayoutFrame = window.requestAnimationFrame(() => {
        this.previewLayoutFrame = null;
        this.updatePreviewPopupGeometry();
      });
    },
    updatePreviewPopupGeometry() {
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      if (!viewportWidth || !viewportHeight) {
        return;
      }

      const viewportGap = Math.min(32, Math.max(9, viewportWidth * 0.024));
      const horizontalPadding = Math.min(24, Math.max(10, viewportWidth * 0.018));
      const isLandscape = this.previewNaturalWidth > this.previewNaturalHeight;
      const verticalPadding = isLandscape
        ? Math.min(16, Math.max(9, viewportWidth * 0.011))
        : horizontalPadding;
      const maxWidth = Math.max(1, viewportWidth - (viewportGap * 2));
      const maxHeight = Math.max(1, viewportHeight - (viewportGap * 2));
      const content = this.$refs.previewContent;
      // Details remain a single natural-height information flow.  Reserve a
      // sensible viewport share for it when sizing the image; if long metadata
      // needs more than that, the *modal viewport* scrolls rather than clipping
      // the details or creating an inner details scroller.
      const naturalDetailsHeight = Math.max(96, content ? content.scrollHeight + 2 : 136);
      const detailsBudget = Math.max(96, Math.floor(maxHeight * 0.42));
      const allocatedDetailsHeight = Math.min(naturalDetailsHeight, detailsBudget);
      const availableImageWidth = Math.max(1, maxWidth - (horizontalPadding * 2));
      const availableImageHeight = Math.max(1, maxHeight - allocatedDetailsHeight - (verticalPadding * 2));
      // Standard contain geometry: one scale preserves the natural image ratio.
      // Do not cap at 1: thumbnails must grow to the available workspace too.
      const scale = Math.min(
        availableImageWidth / this.previewNaturalWidth,
        availableImageHeight / this.previewNaturalHeight,
      );
      const imageWidth = Math.max(1, Math.round(this.previewNaturalWidth * scale));
      const imageHeight = Math.max(1, Math.round(this.previewNaturalHeight * scale));
      const minimumCardWidth = Math.min(360, maxWidth);
      const width = Math.round(Math.min(
        maxWidth,
        Math.max(minimumCardWidth, imageWidth + (horizontalPadding * 2)),
      ));
      const stageHeight = imageHeight + (verticalPadding * 2);
      const nextGeometry = {
        detailsHeight: naturalDetailsHeight,
        horizontalPadding,
        imageHeight,
        imageWidth,
        stageHeight,
        verticalPadding,
        width,
      };
      const geometryChanged = !this.previewPopupGeometry
        || this.previewPopupGeometry.detailsHeight !== naturalDetailsHeight
        || this.previewPopupGeometry.horizontalPadding !== horizontalPadding
        || this.previewPopupGeometry.imageWidth !== imageWidth
        || this.previewPopupGeometry.imageHeight !== imageHeight
        || this.previewPopupGeometry.stageHeight !== stageHeight
        || this.previewPopupGeometry.verticalPadding !== verticalPadding
        || this.previewPopupGeometry.width !== width;
      this.previewPopupGeometry = nextGeometry;

      if (geometryChanged) {
        this.$nextTick(this.queuePreviewLayout);
      }
    },
    readStream(reader, chunks) {
      return reader.read().then(
        ({ done, value }) => {
          if (done) {
            return new Blob(chunks, { type: this.imageContentType });
          }
          chunks.push(value);
          this.downloadLoaded += value.length;
          return this.readStream(reader, chunks);
        },
      );
    },
    loadOriginalImage() {
      if (!this.pinItem.image_id) {
        this.imageLoading = false;
        this.imageLoadFailed = !this.pinItem.url;
        this.$nextTick(this.playMotionVideo);
        return;
      }
      const cached = getCachedImage(this.pinItem.image_id);
      if (cached) {
        this.imageBlob = cached.blob;
        this.previewImageUrl = cached.objectUrl;
        this.previewImageUrlFromCache = true;
        this.imageLoading = false;
        this.$nextTick(this.playMotionVideo);
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
          const cachedImage = cacheImage(this.pinItem.image_id, blob);
          if (cachedImage) {
            this.previewImageUrl = cachedImage.objectUrl;
            this.previewImageUrlFromCache = true;
          } else {
            this.previewImageUrl = URL.createObjectURL(blob);
          }
          this.imageLoading = false;
          this.$nextTick(this.playMotionVideo);
        },
      ).catch(
        () => {
          this.imageLoadFailed = true;
          this.imageLoading = false;
        },
      );
    },
    playMotionVideo() {
      if (!this.hasMotionPhoto || this.imageLoading) {
        return;
      }
      const video = this.$refs.motionVideo;
      if (!video) {
        return;
      }
      if (this.motionReplayTimer) {
        window.clearTimeout(this.motionReplayTimer);
        this.motionReplayTimer = null;
      }
      video.currentTime = 0;
      const promise = video.play();
      if (promise && promise.catch) {
        promise.catch(
          () => {
            this.motionVideoFailed = true;
          },
        );
      }
    },
    onMotionVideoEnded() {
      this.motionVideoActive = false;
      if (!this.hasMotionPhoto) {
        return;
      }
      this.motionReplayTimer = window.setTimeout(
        this.playMotionVideo,
        2000,
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
      const { body } = document;
      body.appendChild(link);
      link.click();
      body.removeChild(link);
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
@import './utils/motion-mixins';

.pin-preview-modal {
  --pin-preview-viewport-gap: clamp(12px, 2.4vw, 32px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
  min-height: 0;
  max-height: calc(100vh - (var(--pin-preview-viewport-gap) * 2));
  padding: var(--pin-preview-viewport-gap) 0;
  overflow-y: auto;
  overscroll-behavior: contain;
}
.pin-preview-surface {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: auto;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
}
.pin-preview-card {
  display: grid;
  grid-template-rows: var(--pin-preview-stage-height, auto) auto;
  width: min(92vw, 680px);
  height: auto;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
  overflow: visible;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-md);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 44%),
    var(--color-surface-card);
  box-shadow:
    0 0 0 1px var(--color-accent-soft),
    var(--shadow-floating);
  transition: width 180ms cubic-bezier(0.2, 0.8, 0.2, 1), height 180ms cubic-bezier(0.2, 0.8, 0.2, 1);
}
.pin-preview-stage {
  position: relative;
  display: grid;
  place-items: center;
  min-width: 0;
  min-height: 0;
  padding: var(--pin-preview-stage-padding-y, clamp(10px, 1.8vw, 24px)) var(--pin-preview-stage-padding-x, clamp(10px, 1.8vw, 24px));
  overflow: hidden;
  isolation: isolate;
  background: var(--color-surface-2);
}
.pin-preview-backdrop {
  position: absolute;
  z-index: 0;
  inset: -36px;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  filter: blur(22px) saturate(0.84) brightness(0.72);
  opacity: 0.5;
  transform: scale(1.08);
}
.pin-preview-stage::after {
  position: absolute;
  z-index: 0;
  inset: 0;
  background:
    radial-gradient(ellipse at center, transparent 24%, color-mix(in srgb, var(--color-text-strong) 20%, transparent) 70%, color-mix(in srgb, var(--color-text-strong) 52%, transparent) 100%),
    linear-gradient(180deg, color-mix(in srgb, var(--color-text-strong) 8%, transparent), color-mix(in srgb, var(--color-text-strong) 28%, transparent));
  content: '';
  pointer-events: none;
}
.pin-preview-image {
  position: relative;
  z-index: 1;
  display: block;
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  object-position: center;
  transition: filter 180ms ease, opacity 180ms ease;
}
.pin-preview-image.is-loading-preview {
  filter: blur(1.5px);
  opacity: 0.78;
}
.motion-preview-video {
  position: absolute;
  z-index: 2;
  inset: clamp(10px, 1.8vw, 24px);
  width: calc(100% - clamp(20px, 3.6vw, 48px));
  height: calc(100% - clamp(20px, 3.6vw, 48px));
  object-fit: contain;
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms ease;
}
.motion-preview-video.is-active {
  opacity: 1;
}
.pin-preview-details {
  z-index: 4;
  box-sizing: border-box;
  max-height: none;
  overflow: visible;
  border-top: 1px solid var(--color-line-soft);
  background: var(--color-surface-card);
  overscroll-behavior: contain;
}
.pin-preview-description {
  margin: 0;
  padding: 0.7rem clamp(0.85rem, 1.8vw, 1.2rem);
  border-bottom: 1px solid var(--color-line-soft);
  color: var(--color-text-strong);
  font-family: var(--font-display, inherit);
  font-size: 0.98rem;
  line-height: 1.45;
}
.pin-preview-footer {
  display: block;
  padding: 0.78rem clamp(0.85rem, 1.8vw, 1.2rem);
}
.pin-preview-avatar {
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-accent-border);
  border-radius: 50%;
  object-fit: cover;
}
.pin-preview-meta {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-width: 0;
}
.pin-preview-identity {
  display: flex;
  align-items: center;
  gap: 0.52rem;
  min-width: 0;
  order: 3;
}
.pin-preview-author,
.pin-preview-tags {
  margin: 0;
}
.pin-preview-author {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: baseline;
  font-size: 0.92rem;
  line-height: 1.35;
}
.pin-preview-author .author {
  overflow: hidden;
  color: var(--color-text-strong);
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dim {
  @include secondary-font-color-in-dark;
}
.pin-preview-tags {
  margin-top: 0.32rem;
  color: var(--color-text-muted);
  font-size: 0.76rem;
  line-height: 1.55;
}
.pin-preview-tag-container {
  order: 2;
  min-width: 0;
  padding-top: 0.08rem;
}
.pin-preview-tags {
  margin-top: 0;
}
.pin-preview-tag {
  margin: 0 0.2rem 0.22rem 0 !important;
}
.pin-preview-actions {
  display: flex;
  order: 1;
  flex: 0 0 auto;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 0.42rem;
  min-width: 0;
}
.pin-preview-actions > a,
.pin-preview-actions > span {
  display: inline-flex;
  min-width: 0;
}
.pin-preview-actions .button,
.pin-preview-actions .source-text-button,
.pin-preview-actions .source-missing-pill {
  min-height: 32px;
  border: 1px solid var(--color-accent-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-accent-strong) !important;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--color-surface-card) 32%, transparent), transparent 46%),
    var(--color-accent-soft) !important;
  box-shadow: inset 0 1px 0 color-mix(in srgb, var(--color-surface-card) 36%, transparent);
  font-weight: 750;
  transition:
    color var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease),
    border-color var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease),
    background-color var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease),
    box-shadow var(--motion-duration-standard, 240ms) var(--motion-ease-standard, ease),
    transform var(--motion-duration-fast, 160ms) var(--motion-ease-standard, ease);
}
.pin-preview-actions .button:hover:not([disabled]),
.pin-preview-actions .button:focus-visible,
.pin-preview-actions .source-text-button:hover,
.pin-preview-actions .source-text-button:focus-visible {
  border-color: var(--color-accent) !important;
  color: var(--color-accent-text) !important;
  background: var(--color-accent-strong) !important;
  box-shadow: 0 7px 18px var(--color-theme-glow);
  transform: translate3d(0, -1px, 0);
}
.pin-preview-actions .button:focus-visible,
.pin-preview-actions .source-text-button:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring), 0 7px 18px var(--color-theme-glow);
}
.pin-preview-actions .button:disabled {
  opacity: 0.54;
}
.pin-preview-actions .source-missing-pill {
  color: var(--color-text-muted) !important;
  background: var(--color-surface-2) !important;
}
.meta-link {
  margin: 0 !important;
}
.source-text-button,
.source-missing-pill {
  display: inline-flex;
  align-items: center;
  min-height: 2.25em;
  max-width: 220px;
  padding: 0 0.75em;
  border-radius: var(--radius-sm, 8px);
  font-size: 0.8125rem;
  line-height: 1.5;
}
.source-text-button {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.source-missing-pill {
  color: var(--color-text-muted);
}
.preview-loading {
  position: absolute;
  z-index: 3;
  left: 50%;
  bottom: clamp(10px, 2vw, 24px);
  width: min(420px, calc(100% - 32px));
  padding: 0.8rem 1rem;
  transform: translateX(-50%);
  color: var(--color-accent-text);
  text-align: center;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-text-primary) 64%, transparent);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-soft);
}
.preview-loading .progress {
  margin: 0.65rem auto 0;
}
.full-image-viewer {
  position: fixed;
  inset: 0;
  z-index: 220;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  color: #fff;
  background: rgba(3, 6, 12, 0.96);
  pointer-events: auto;
  overscroll-behavior: contain;
}
.full-image-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(9, 12, 18, 0.88);
  backdrop-filter: blur(12px);
}
.full-image-toolbar strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.full-image-toolbar button {
  flex: 0 0 auto;
  min-height: 34px;
  padding: 0 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 7px;
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  font-weight: 800;
}
.full-image-stage {
  min-height: 0;
  overflow: auto;
  padding: 1.25rem;
  overscroll-behavior: contain;
}
.full-image-stage img {
  display: block;
  width: auto;
  max-width: none;
  height: auto;
  max-height: none;
  margin: 0 auto;
  box-shadow: 0 18px 54px rgba(0, 0, 0, 0.45);
}
@media screen and (max-width: 720px) {
  .pin-preview-meta {
    grid-template-columns: 1fr;
    gap: 0.62rem;
  }
  .pin-preview-actions {
    justify-content: flex-start;
  }
}
@media screen and (max-width: 542px) {
  .pin-preview-modal {
    --pin-preview-viewport-gap: 9px;
  }
  .pin-preview-card {
    max-width: 96vw;
  }
  .pin-preview-footer {
    gap: 0.58rem;
    padding: 0.7rem 0.8rem;
  }
  .pin-preview-avatar {
    width: 36px;
    height: 36px;
  }
  .full-image-stage {
    padding: 0.8rem;
  }
}

html[data-motion='reduce'] .pin-preview-card {
  transition: none;
}
</style>
