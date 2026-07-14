<template>
  <div class="avatar-cropper-overlay" role="dialog" aria-modal="true">
    <div class="avatar-cropper-card">
      <header class="avatar-cropper-head">
        <div>
          <span>{{ $t('avatarCropKicker') }}</span>
          <strong>{{ $t('avatarCropTitle') }}</strong>
        </div>
        <button
          class="avatar-cropper-icon-button"
          type="button"
          :disabled="busy"
          :title="$t('closeButton')"
          :aria-label="$t('closeButton')"
          @click="$emit('cancel')">
          <b-icon icon="close" custom-size="mdi-20px"></b-icon>
        </button>
      </header>
      <section class="avatar-cropper-body">
        <div
          ref="stage"
          class="avatar-cropper-stage"
          @pointerdown="startPointerAction">
          <img
            ref="image"
            :src="sourceUrl"
            alt=""
            draggable="false"
            :style="imageStyle"
            @load="onImageLoaded"
            @error="onImageError">
          <div
            v-if="imageReady"
            class="avatar-crop-selection"
            :style="selectionStyle">
            <span class="avatar-crop-selection__grid"></span>
            <span
              v-for="handle in resizeHandles"
              :key="handle"
              class="avatar-crop-selection__handle"
              :class="`is-${handle}`"
              :data-resize-handle="handle">
            </span>
          </div>
        </div>
        <div class="avatar-cropper-controls">
          <div class="avatar-zoom-control">
            <button
              class="avatar-cropper-icon-button"
              type="button"
              :disabled="busy || zoom <= 1"
              :title="$t('avatarZoomOut')"
              @click="adjustZoom(-0.25)">
              <b-icon icon="magnify-minus-outline" custom-size="mdi-20px"></b-icon>
            </button>
            <input
              v-model.number="zoom"
              type="range"
              min="1"
              max="20"
              step="0.05"
              :disabled="busy"
              :aria-label="$t('avatarZoomLabel')">
            <button
              class="avatar-cropper-icon-button"
              type="button"
              :disabled="busy || zoom >= 20"
              :title="$t('avatarZoomIn')"
              @click="adjustZoom(0.25)">
              <b-icon icon="magnify-plus-outline" custom-size="mdi-20px"></b-icon>
            </button>
            <strong>{{ zoom.toFixed(2) }}x</strong>
          </div>
          <p>{{ $t('avatarCropHint') }}</p>
        </div>
        <div v-if="processing || uploading" class="avatar-cropper-processing">
          <div class="avatar-cropper-processing__head">
            <span>{{ processing ? $t('avatarCompressing') : $t('imageUploadInProgress') }}</span>
            <strong>{{ activeProgress }}%</strong>
          </div>
          <div class="avatar-cropper-processing__track">
            <span :style="{ width: `${activeProgress}%` }"></span>
          </div>
        </div>
        <p v-if="uploadError" class="avatar-cropper-error">{{ uploadError }}</p>
      </section>
      <footer class="avatar-cropper-foot">
        <button
          class="button avatar-cropper-cancel"
          type="button"
          :disabled="busy"
          @click="$emit('cancel')">
          {{ $t('closeButton') }}
        </button>
        <button
          class="button avatar-cropper-confirm"
          type="button"
          :disabled="!imageReady || busy"
          @click="confirmCrop">
          <b-icon icon="crop" custom-size="mdi-19px"></b-icon>
          <span>{{ $t('avatarCropConfirm') }}</span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
const MAX_OUTPUT_BYTES = 2 * 1024 * 1024;
const MAX_OUTPUT_EDGE = 2048;
const MIN_CROP_SIZE = 56;

function canvasToBlob(canvas, type, quality) {
  return new Promise(
    resolve => canvas.toBlob(resolve, type, quality),
  );
}

export default {
  name: 'AvatarCropper',
  props: {
    file: {
      type: File,
      required: true,
    },
    uploadError: {
      type: String,
      default: '',
    },
    uploadProgress: {
      type: Number,
      default: 0,
    },
    uploading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      crop: {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
      },
      displayBase: { width: 0, height: 0 },
      imageNatural: { width: 0, height: 0 },
      imageOffset: { x: 0, y: 0 },
      imageReady: false,
      pointerAction: null,
      processing: false,
      processingProgress: 0,
      resizeHandles: ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'],
      sourceUrl: null,
      stageSize: { width: 0, height: 0 },
      zoom: 1,
      bodyOverflowSnapshot: '',
    };
  },
  computed: {
    activeProgress() {
      return this.processing
        ? this.processingProgress
        : Math.min(100, Math.max(0, Math.round(this.uploadProgress || 0)));
    },
    busy() {
      return this.processing || this.uploading;
    },
    scaledImageSize() {
      return {
        width: this.displayBase.width * this.zoom,
        height: this.displayBase.height * this.zoom,
      };
    },
    imageStyle() {
      const size = this.scaledImageSize;
      return {
        width: `${size.width}px`,
        height: `${size.height}px`,
        left: `${this.imageOffset.x}px`,
        top: `${this.imageOffset.y}px`,
      };
    },
    selectionStyle() {
      return {
        width: `${this.crop.width}px`,
        height: `${this.crop.height}px`,
        left: `${this.crop.x}px`,
        top: `${this.crop.y}px`,
      };
    },
  },
  watch: {
    zoom(nextZoom, previousZoom) {
      if (!this.imageReady) {
        return;
      }
      const cropCenter = {
        x: this.crop.x + this.crop.width / 2,
        y: this.crop.y + this.crop.height / 2,
      };
      const previousSize = {
        width: this.displayBase.width * previousZoom,
        height: this.displayBase.height * previousZoom,
      };
      const sourcePoint = {
        x: (cropCenter.x - this.imageOffset.x) / previousSize.width,
        y: (cropCenter.y - this.imageOffset.y) / previousSize.height,
      };
      const nextSize = this.scaledImageSize;
      this.imageOffset = {
        x: cropCenter.x - sourcePoint.x * nextSize.width,
        y: cropCenter.y - sourcePoint.y * nextSize.height,
      };
      this.constrainImageToCrop();
    },
  },
  created() {
    this.sourceUrl = window.URL.createObjectURL(this.file);
  },
  mounted() {
    const { body } = document;
    this.bodyOverflowSnapshot = body.style.overflow;
    body.style.overflow = 'hidden';
    window.addEventListener('pointermove', this.onPointerMove);
    window.addEventListener('pointerup', this.endPointerAction);
  },
  beforeDestroy() {
    const { body } = document;
    body.style.overflow = this.bodyOverflowSnapshot;
    window.removeEventListener('pointermove', this.onPointerMove);
    window.removeEventListener('pointerup', this.endPointerAction);
    if (this.sourceUrl) {
      window.URL.revokeObjectURL(this.sourceUrl);
    }
  },
  methods: {
    onImageError(error) {
      this.$emit('error', error);
    },
    onImageLoaded(event) {
      const { stage } = this.$refs;
      const image = event.target;
      if (!stage || !image) {
        return;
      }
      const stageRect = stage.getBoundingClientRect();
      this.stageSize = { width: stageRect.width, height: stageRect.height };
      this.imageNatural = {
        width: image.naturalWidth,
        height: image.naturalHeight,
      };
      const fitScale = Math.min(
        stageRect.width / image.naturalWidth,
        stageRect.height / image.naturalHeight,
      );
      this.displayBase = {
        width: image.naturalWidth * fitScale,
        height: image.naturalHeight * fitScale,
      };
      this.imageOffset = {
        x: (stageRect.width - this.displayBase.width) / 2,
        y: (stageRect.height - this.displayBase.height) / 2,
      };
      const cropWidth = Math.max(
        MIN_CROP_SIZE,
        Math.min(this.displayBase.width * 0.72, stageRect.width * 0.72),
      );
      const cropHeight = Math.max(
        MIN_CROP_SIZE,
        Math.min(this.displayBase.height * 0.72, stageRect.height * 0.72),
      );
      this.crop = {
        width: cropWidth,
        height: cropHeight,
        x: (stageRect.width - cropWidth) / 2,
        y: (stageRect.height - cropHeight) / 2,
      };
      this.imageReady = true;
      this.constrainImageToCrop();
    },
    adjustZoom(delta) {
      this.zoom = Math.min(20, Math.max(1, Number((this.zoom + delta).toFixed(2))));
    },
    startPointerAction(event) {
      if (!this.imageReady || this.busy) {
        return;
      }
      const handle = event.target.dataset ? event.target.dataset.resizeHandle : null;
      const selection = event.target.closest('.avatar-crop-selection');
      let mode = 'image';
      if (handle) {
        mode = 'resize';
      } else if (selection) {
        mode = 'crop';
      }
      this.pointerAction = {
        handle,
        mode,
        startX: event.clientX,
        startY: event.clientY,
        crop: Object.assign({}, this.crop),
        imageOffset: Object.assign({}, this.imageOffset),
      };
      event.preventDefault();
    },
    onPointerMove(event) {
      if (!this.pointerAction) {
        return;
      }
      const dx = event.clientX - this.pointerAction.startX;
      const dy = event.clientY - this.pointerAction.startY;
      if (this.pointerAction.mode === 'image') {
        this.imageOffset = {
          x: this.pointerAction.imageOffset.x + dx,
          y: this.pointerAction.imageOffset.y + dy,
        };
        this.constrainImageToCrop();
      } else if (this.pointerAction.mode === 'crop') {
        this.crop = Object.assign({}, this.pointerAction.crop, {
          x: this.pointerAction.crop.x + dx,
          y: this.pointerAction.crop.y + dy,
        });
        this.constrainCropToImage();
      } else {
        this.resizeCrop(dx, dy);
      }
    },
    endPointerAction() {
      this.pointerAction = null;
    },
    resizeCrop(dx, dy) {
      const { crop: original, handle } = this.pointerAction;
      let left = original.x;
      let top = original.y;
      let right = original.x + original.width;
      let bottom = original.y + original.height;
      if (handle.indexOf('w') >= 0) left += dx;
      if (handle.indexOf('e') >= 0) right += dx;
      if (handle.indexOf('n') >= 0) top += dy;
      if (handle.indexOf('s') >= 0) bottom += dy;
      if (right - left < MIN_CROP_SIZE) {
        if (handle.indexOf('w') >= 0) left = right - MIN_CROP_SIZE;
        else right = left + MIN_CROP_SIZE;
      }
      if (bottom - top < MIN_CROP_SIZE) {
        if (handle.indexOf('n') >= 0) top = bottom - MIN_CROP_SIZE;
        else bottom = top + MIN_CROP_SIZE;
      }
      this.crop = {
        x: left,
        y: top,
        width: right - left,
        height: bottom - top,
      };
      this.constrainCropToImage();
    },
    imageBounds() {
      const size = this.scaledImageSize;
      return {
        left: this.imageOffset.x,
        top: this.imageOffset.y,
        right: this.imageOffset.x + size.width,
        bottom: this.imageOffset.y + size.height,
      };
    },
    constrainCropToImage() {
      const bounds = this.imageBounds();
      const width = Math.min(this.crop.width, bounds.right - bounds.left);
      const height = Math.min(this.crop.height, bounds.bottom - bounds.top);
      this.crop = {
        width,
        height,
        x: Math.min(bounds.right - width, Math.max(bounds.left, this.crop.x)),
        y: Math.min(bounds.bottom - height, Math.max(bounds.top, this.crop.y)),
      };
    },
    constrainImageToCrop() {
      const size = this.scaledImageSize;
      this.imageOffset = {
        x: Math.min(this.crop.x, Math.max(this.crop.x + this.crop.width - size.width, this.imageOffset.x)),
        y: Math.min(this.crop.y, Math.max(this.crop.y + this.crop.height - size.height, this.imageOffset.y)),
      };
    },
    renderCropCanvas(maxEdge) {
      const size = this.scaledImageSize;
      const sourceX = (this.crop.x - this.imageOffset.x) * (this.imageNatural.width / size.width);
      const sourceY = (this.crop.y - this.imageOffset.y) * (this.imageNatural.height / size.height);
      const sourceWidth = this.crop.width * (this.imageNatural.width / size.width);
      const sourceHeight = this.crop.height * (this.imageNatural.height / size.height);
      const outputScale = Math.min(1, maxEdge / Math.max(sourceWidth, sourceHeight));
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(sourceWidth * outputScale));
      canvas.height = Math.max(1, Math.round(sourceHeight * outputScale));
      const context = canvas.getContext('2d');
      context.drawImage(
        this.$refs.image,
        sourceX,
        sourceY,
        sourceWidth,
        sourceHeight,
        0,
        0,
        canvas.width,
        canvas.height,
      );
      return canvas;
    },
    compressCropAttempt(maxEdge, quality, attempt) {
      if (attempt >= 14) {
        return Promise.resolve(null);
      }
      this.processingProgress = Math.min(92, 8 + attempt * 7);
      return Promise.resolve().then(
        () => this.renderCropCanvas(maxEdge),
      ).then(
        canvas => canvasToBlob(canvas, 'image/jpeg', quality),
      ).then(
        (blob) => {
          if (blob && blob.size <= MAX_OUTPUT_BYTES) {
            this.processingProgress = 100;
            return blob;
          }
          const lowerQuality = quality > 0.56;
          const nextMaxEdge = lowerQuality
            ? maxEdge
            : Math.max(512, Math.round(maxEdge * 0.82));
          const nextQuality = lowerQuality ? quality - 0.08 : 0.78;
          return this.compressCropAttempt(nextMaxEdge, nextQuality, attempt + 1);
        },
      );
    },
    compressCrop() {
      return this.compressCropAttempt(MAX_OUTPUT_EDGE, 0.92, 0);
    },
    confirmCrop() {
      this.processing = true;
      this.processingProgress = 4;
      this.compressCrop()
        .then(
          (blob) => {
            if (!blob) {
              this.$emit('error');
              return;
            }
            const baseName = this.file.name.replace(/\.[^.]+$/, '') || 'avatar';
            const output = new File(
              [blob],
              `${baseName}-avatar.jpg`,
              { type: 'image/jpeg' },
            );
            this.$emit('confirm', output);
          },
        )
        .catch(
          error => this.$emit('error', error),
        )
        .then(
          () => {
            this.processing = false;
          },
        );
    },
  },
};
</script>

<style lang="scss" scoped>
.avatar-cropper-overlay {
  --avatar-cropper-danger: #c43f62;
  position: fixed;
  z-index: calc(var(--z-modal) + 90);
  inset: 0;
  display: grid;
  padding: var(--space-md);
  place-items: center;
  background: color-mix(in srgb, var(--color-app-bg) 54%, transparent);
  backdrop-filter: blur(14px) saturate(1.08);
}
.avatar-cropper-card {
  display: flex;
  width: min(94vw, 920px);
  max-height: calc(100dvh - var(--space-xl));
  overflow: hidden;
  flex-direction: column;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 42%),
    var(--color-surface-card);
  box-shadow: var(--shadow-floating);
}
.avatar-cropper-head,
.avatar-cropper-foot {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  border-color: var(--color-line-soft);
  background: color-mix(in srgb, var(--color-surface-2) 86%, transparent);
}
.avatar-cropper-head { border-bottom: 1px solid var(--color-line-soft); }
.avatar-cropper-foot { justify-content: flex-end; border-top: 1px solid var(--color-line-soft); }
.avatar-cropper-head div { display: grid; gap: 2px; }
.avatar-cropper-head span { color: var(--color-accent-strong); font-size: .7rem; font-weight: 900; text-transform: uppercase; }
.avatar-cropper-head strong { color: var(--color-text-strong); font-size: 1.12rem; }
.avatar-cropper-body { overflow: auto; padding: var(--space-lg); }
.avatar-cropper-stage {
  position: relative;
  width: 100%;
  height: min(58vh, 560px);
  min-height: 320px;
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-md);
  background:
    linear-gradient(45deg, var(--color-surface-2) 25%, transparent 25%) 0 0 / 24px 24px,
    linear-gradient(-45deg, var(--color-surface-2) 25%, transparent 25%) 0 12px / 24px 24px,
    var(--color-surface-1);
  cursor: grab;
  touch-action: none;
  user-select: none;
}
.avatar-cropper-stage:active { cursor: grabbing; }
.avatar-cropper-stage img { position: absolute; max-width: none; object-fit: fill; pointer-events: none; user-select: none; }
.avatar-crop-selection {
  position: absolute;
  border: 2px solid var(--color-accent-text);
  border-radius: var(--radius-xs);
  box-shadow:
    0 0 0 9999px color-mix(in srgb, var(--color-app-bg) 70%, transparent),
    0 0 0 1px var(--color-accent-strong),
    0 0 24px var(--color-theme-glow-strong);
  cursor: move;
}
.avatar-crop-selection__grid { position: absolute; inset: 0; background: linear-gradient(90deg, transparent 33%, rgba(255,255,255,.4) 33% 34%, transparent 34% 66%, rgba(255,255,255,.4) 66% 67%, transparent 67%), linear-gradient(0deg, transparent 33%, rgba(255,255,255,.4) 33% 34%, transparent 34% 66%, rgba(255,255,255,.4) 66% 67%, transparent 67%); pointer-events: none; }
.avatar-crop-selection__handle { position: absolute; width: 15px; height: 15px; border: 2px solid var(--color-accent-text); border-radius: 50%; background: var(--color-accent-strong); box-shadow: 0 2px 8px var(--color-theme-glow-strong); }
.avatar-crop-selection__handle.is-nw { top: -8px; left: -8px; cursor: nwse-resize; }.avatar-crop-selection__handle.is-n { top: -8px; left: 50%; transform: translateX(-50%); cursor: ns-resize; }.avatar-crop-selection__handle.is-ne { top: -8px; right: -8px; cursor: nesw-resize; }.avatar-crop-selection__handle.is-e { top: 50%; right: -8px; transform: translateY(-50%); cursor: ew-resize; }.avatar-crop-selection__handle.is-se { right: -8px; bottom: -8px; cursor: nwse-resize; }.avatar-crop-selection__handle.is-s { bottom: -8px; left: 50%; transform: translateX(-50%); cursor: ns-resize; }.avatar-crop-selection__handle.is-sw { bottom: -8px; left: -8px; cursor: nesw-resize; }.avatar-crop-selection__handle.is-w { top: 50%; left: -8px; transform: translateY(-50%); cursor: ew-resize; }
.avatar-cropper-controls { display: grid; gap: var(--space-xs); margin-top: var(--space-md); }
.avatar-zoom-control { display: grid; grid-template-columns: 40px minmax(0,1fr) 40px 58px; gap: var(--space-xs); align-items: center; }
.avatar-zoom-control input { width: 100%; accent-color: var(--color-accent-strong); }
.avatar-zoom-control strong { color: var(--color-accent-strong); text-align: right; }
.avatar-cropper-controls p { margin: 0; color: var(--color-text-muted); font-size: .8rem; }
.avatar-cropper-icon-button { display: inline-grid; width: 40px; height: 40px; padding: 0; place-items: center; border: 1px solid var(--color-line-soft); border-radius: var(--radius-sm); color: var(--color-text-muted); background: var(--color-surface-1); cursor: pointer; transition: transform var(--motion-duration-fast) var(--motion-ease-standard), border-color var(--motion-duration-fast), color var(--motion-duration-fast), background var(--motion-duration-fast); }
.avatar-cropper-icon-button:hover:not(:disabled),.avatar-cropper-icon-button:focus-visible { border-color: var(--color-accent-border); color: var(--color-accent-strong); background: var(--color-accent-soft); transform: translateY(-1px); }
.avatar-cropper-icon-button:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.avatar-cropper-icon-button:disabled { cursor: not-allowed; opacity: .46; }
.avatar-cropper-processing { margin-top: var(--space-md); padding: var(--space-sm); border: 1px solid var(--color-accent-border); border-radius: var(--radius-sm); background: var(--color-accent-soft); }
.avatar-cropper-processing__head { display: flex; justify-content: space-between; gap: var(--space-xs); margin-bottom: var(--space-xs); color: var(--color-accent-strong); font-size: .76rem; font-weight: 850; }
.avatar-cropper-processing__track { height: 7px; overflow: hidden; border-radius: var(--radius-pill); background: color-mix(in srgb, var(--color-line-soft) 70%, transparent); }
.avatar-cropper-processing__track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg,var(--color-accent),var(--color-accent-strong)); box-shadow: 0 0 14px var(--color-theme-glow-strong); transition: width var(--motion-duration-standard) var(--motion-ease-emphasized); }
.avatar-cropper-error { margin: var(--space-sm) 0 0; padding: var(--space-xs) var(--space-sm); border: 1px solid color-mix(in srgb, var(--avatar-cropper-danger) 34%, transparent); border-radius: var(--radius-sm); color: var(--avatar-cropper-danger); background: color-mix(in srgb, var(--avatar-cropper-danger) 10%, transparent); font-size: .8rem; font-weight: 750; }
.avatar-cropper-foot .button { min-height: 42px; border-radius: var(--radius-sm); font-weight: 900; }
.avatar-cropper-cancel { border-color: var(--color-line-soft); color: var(--color-text-muted); background: var(--color-surface-1); }
.avatar-cropper-confirm { gap: var(--space-xs); border-color: var(--color-accent-strong); color: var(--color-accent-text); background: var(--color-accent-strong); box-shadow: 0 10px 22px var(--color-theme-glow); }
@media screen and (max-width: 640px) {
  .avatar-cropper-overlay { padding: var(--space-xs); }
  .avatar-cropper-card { width: calc(100vw - var(--space-md)); max-height: calc(100dvh - var(--space-md)); }
  .avatar-cropper-body,.avatar-cropper-head,.avatar-cropper-foot { padding: var(--space-md); }
  .avatar-cropper-stage { height: 48vh; min-height: 260px; }
  .avatar-cropper-foot { flex-direction: column-reverse; }
  .avatar-cropper-foot .button { width: 100%; }
  .avatar-zoom-control { grid-template-columns: 38px minmax(0,1fr) 38px; }
  .avatar-zoom-control strong { grid-column: 1 / -1; text-align: center; }
}
</style>
