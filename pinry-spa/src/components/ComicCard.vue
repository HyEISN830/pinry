<template>
  <article
    ref="shell"
    class="comic-card-shell motion-tilt-scene"
    :class="{
      'is-tilting': tilting,
      'is-shelf-layout': shelfLayout
    }"
    @mouseenter="showMenu"
    @mouseleave="handleLeave"
    @pointermove="scheduleTilt"
    @pointerout="handlePointerExit"
    @pointerleave="handlePointerExit"
    @pointercancel="resetTilt"
    @lostpointercapture="resetTilt"
    @touchstart="handleTouchStart"
    @touchend="resetTilt"
    @touchcancel="resetTilt"
    @focusin="showMenu"
    @focusout="handlePointerExit"
    @click="readComic">
    <div ref="frame" class="comic-card-frame motion-card-enter">
      <div ref="book" class="comic-book motion-tilt-card">
        <span class="comic-stack-sheet is-rear" aria-hidden="true"></span>
        <span class="comic-stack-sheet is-near" aria-hidden="true"></span>
        <div class="comic-card">
          <span class="motion-tilt-glare comic-glare" aria-hidden="true"></span>
          <div class="comic-ribbon">{{ $t('comicLink') }}</div>
          <button
            class="comic-cover comic-open-button"
            type="button"
            :aria-label="comic.title"
            :style="coverStyle"
            @click.stop="readComic">
            <img
              v-if="coverImageUrl"
              :src="coverImageUrl"
              :alt="comic.title"
              loading="lazy"
              decoding="async"
              @load="$emit('image-settled')"
              @error="$emit('image-settled')">
            <div v-else class="comic-cover-placeholder">{{ $t('imageUnavailableText') }}</div>
          </button>
          <div class="comic-info">
            <h2>
              <button class="comic-title-button" type="button" @click.stop="readComic">
                {{ comic.title }}
              </button>
            </h2>
            <div v-if="comic.tags && comic.tags.length" class="comic-tags">
              <router-link v-for="tag in visibleTags" :key="tag" class="content-tag-pill" :to="{ name: 'tag', params: { tag } }" @click.stop>{{ tag }}</router-link>
              <button v-if="hiddenTagCount" class="comic-tag-more content-tag-pill" type="button" :title="comic.title" @click.stop="readComic">...</button>
            </div>
            <div v-if="comic.submitter" class="comic-author">
              <img :src="avatarUrl" alt="">
              <router-link :to="{ name: 'user', params: { user: comic.submitter.username } }" @click.stop>{{ comic.submitter.username }}</router-link>
              <span>{{ comic.total_pages }} {{ $t('comicPagesUnit') }}</span>
            </div>
            <div class="comic-meta-footer">
              <div v-if="hasSource" class="comic-source">
                <a
                  v-if="isWebSource"
                  v-source-tooltip
                  class="content-source-link"
                  :href="comic.referer"
                  :data-source-tip="sourceText"
                  target="_blank"
                  rel="noopener"
                  @click.stop>{{ $t('sourceLink') }}</a>
                <span
                  v-else
                  v-source-tooltip
                  class="content-source-link"
                  tabindex="0"
                  :data-source-tip="sourceText"
                  @click.stop>{{ sourceText }}</span>
              </div>
              <div v-else class="comic-source is-warning">{{ $t('missingSourceNotice') }}</div>
              <div class="comic-stats content-stats" role="group" :aria-label="$t('comicStatsLabel')">
                <button class="comic-like content-like-pill content-stat content-stat--interactive" type="button" :class="{ 'is-liked': comic.viewer_liked }" :aria-pressed="comic.viewer_liked ? 'true' : 'false'"
                  :disabled="likeBusy" :title="comic.viewer_liked ? $t('unlikeButton') : $t('likeButton')" :aria-label="`${comic.viewer_liked ? $t('unlikeButton') : $t('likeButton')}: ${formattedLikes}`" @click.stop="$emit('toggle-like', comic)">
                  <b-icon :icon="comic.viewer_liked ? 'heart' : 'heart-outline'" size="is-small"></b-icon>
                  <span>{{ formattedLikes }}</span>
                </button>
                <span class="comic-viewed content-stat content-stat--passive" :aria-label="`${$t('viewedLabel')}: ${formattedViewed}`" :title="$t('viewedLabel')">
                  <b-icon icon="eye-outline" size="is-small" aria-hidden="true"></b-icon>
                  <span>{{ formattedViewed }}</span>
                </span>
              </div>
            </div>
          </div>
          <transition name="comic-menu">
            <div v-if="menuVisible" class="comic-card-menu" @click.stop @touchstart.stop>
              <button class="button is-small is-danger" type="button" :title="$t('deleteButton')" @click.stop="$emit('delete', comic)">
                {{ $t('deleteButton') }}
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </article>
</template>

<script>
import imageVariant from './utils/imageVariant';
import motionPreference from './utils/motionPreference';
import format from './utils/format';
import cardAvatarUrl from './utils/avatarVariant';

const VISIBLE_COMIC_TAGS = 4;

export default {
  name: 'ComicCard',
  props: {
    comic: { type: Object, required: true },
    currentUsername: { type: String, default: null },
    likeBusy: { type: Boolean, default: false },
    shelfLayout: { type: Boolean, default: false },
  },
  data() {
    return {
      menuVisible: false, tilting: false, tiltFrame: null, suppressRead: false, suppressTimer: null,
    };
  },
  computed: {
    isOwner() { return !!(this.currentUsername && this.comic.submitter && this.comic.submitter.username === this.currentUsername); },
    coverMeta() {
      const cover = this.comic && this.comic.cover ? this.comic.cover : null;
      if (!cover) return null;
      if (typeof cover === 'string') return { image: cover };
      const image = cover.image || cover;
      if (!image) return null;
      if (typeof image === 'string') return { image };
      try { const thumbnail = imageVariant.getCardThumbnail(image) || {}; return thumbnail.image ? thumbnail : null; } catch (e) { return null; }
    },
    coverImageUrl() { return this.coverMeta && this.coverMeta.image ? this.coverMeta.image : null; },
    coverStyle() { return { '--comic-cover-image': this.coverImageUrl ? `url("${this.coverImageUrl}")` : 'none' }; },
    visibleTags() { return (this.comic.tags || []).slice(0, VISIBLE_COMIC_TAGS); },
    hiddenTagCount() { return Math.max(0, (this.comic.tags || []).length - VISIBLE_COMIC_TAGS); },
    avatarUrl() { return cardAvatarUrl(this.comic.submitter, 28); },
    hasSource() { return !!(this.comic.referer || '').trim(); },
    isWebSource() { return /^https?:\/\//i.test((this.comic.referer || '').trim()); },
    sourceText() { return (this.comic.referer || '').trim(); },
    formattedLikes() { return format.formatCount(this.comic.likes_count); },
    formattedViewed() { return format.formatCount(this.comic.viewed_count); },
  },
  mounted() {
    this.notifyLayoutSettled();
  },
  watch: {
    'comic.tags': {
      deep: true,
      handler() {
        this.notifyLayoutSettled();
      },
    },
  },
  beforeDestroy() {
    this.cancelTiltFrame();
    if (this.suppressTimer) window.clearTimeout(this.suppressTimer);
    this.resetTiltState(this.$refs.shell);
  },
  methods: {
    notifyLayoutSettled() {
      this.$nextTick(() => this.$emit('layout-settled'));
    },
    showMenu() { if (this.isOwner) this.menuVisible = true; },
    readComic(event) {
      if (this.suppressRead) { if (event) event.preventDefault(); return; }
      this.$emit('read', this.comic);
    },
    handleTouchStart() {
      const wasVisible = this.menuVisible;
      this.showMenu();
      if (!wasVisible && this.isOwner) {
        this.suppressRead = true;
        if (this.suppressTimer) window.clearTimeout(this.suppressTimer);
        this.suppressTimer = window.setTimeout(() => { this.suppressRead = false; this.suppressTimer = null; }, 700);
      }
    },
    cancelTiltFrame() { if (this.tiltFrame) { window.cancelAnimationFrame(this.tiltFrame); this.tiltFrame = null; } },
    scheduleTilt(event) {
      if (motionPreference.isReducedMotionEnabled()) return;
      if (!window.matchMedia || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
      if (event.pointerType && event.pointerType !== 'mouse') return;
      const { frame, shell } = this.$refs;
      const point = event;
      if (!frame || !shell || !point) return;
      this.cancelTiltFrame();
      this.tiltFrame = window.requestAnimationFrame(() => {
        this.tiltFrame = null;
        const rect = frame.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        const x = Math.max(0, Math.min(1, (point.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (point.clientY - rect.top) / rect.height));
        shell.style.setProperty('--tilt-rotate-x', `${((0.5 - y) * 7).toFixed(2)}deg`);
        shell.style.setProperty('--tilt-rotate-y', `${((x - 0.5) * 8).toFixed(2)}deg`);
        shell.style.setProperty('--tilt-glare-x', `${(x * 100).toFixed(1)}%`);
        shell.style.setProperty('--tilt-glare-y', `${(y * 100).toFixed(1)}%`);
        shell.style.setProperty('--tilt-glare-opacity', '0.2');
        this.tilting = true;
      });
    },
    resetTiltState(shell) {
      if (!shell) return;
      shell.style.setProperty('--tilt-rotate-x', '0deg');
      shell.style.setProperty('--tilt-rotate-y', '0deg');
      shell.style.setProperty('--tilt-glare-x', '50%');
      shell.style.setProperty('--tilt-glare-y', '50%');
      shell.style.setProperty('--tilt-glare-opacity', '0');
      shell.classList.remove('is-tilting');
      this.tilting = false;
    },
    resetTilt() { this.cancelTiltFrame(); this.resetTiltState(this.$refs.shell); },
    handlePointerExit(event) {
      // Vue may deliver a queued pointer/focus event after this card has been
      // removed by a route/list update.  Never dereference a cleared ref.
      const { shell } = this.$refs;
      if (!shell) {
        this.cancelTiltFrame();
        this.tilting = false;
        this.menuVisible = false;
        return;
      }
      if ((event.type === 'pointerout' || event.type === 'focusout') && event.relatedTarget && shell.contains(event.relatedTarget)) return;
      if (event.type === 'focusout') this.menuVisible = false;
      this.resetTilt();
    },
    handleLeave(event) { this.menuVisible = false; this.handlePointerExit(event); },
  },
};
</script>

<style lang="scss" scoped>
.comic-card-shell {
  position: relative;
  isolation: isolate;
  min-width: 0;
  z-index: 1;
}
.comic-card-shell.is-tilting { z-index: 3; }
.comic-card-frame,
.comic-book { min-width: 0; }
.comic-book {
  position: relative;
  isolation: isolate;
  box-sizing: border-box;
  padding-bottom: var(--comic-stack-depth, 12px);
  transform-style: preserve-3d;
}
.comic-book.motion-tilt-card {
  overflow: visible;
  border-radius: 0;
  will-change: auto;
}
.comic-book.motion-tilt-card::after {
  content: none;
  display: none;
}
.comic-card-shell.is-tilting .comic-book { will-change: transform; }
.comic-stack-sheet {
  position: absolute;
  box-sizing: border-box;
  height: var(--comic-stack-sheet-height, 10px);
  border: 1px solid color-mix(in srgb, var(--color-accent-border, rgba(126, 87, 194, .22)) 72%, var(--color-border-soft, rgba(126, 87, 194, .16)));
  border-radius: 0 0 var(--radius-sm, 12px) var(--radius-sm, 12px);
  pointer-events: none;
}
.comic-stack-sheet.is-near {
  right: var(--comic-stack-near-inset, var(--space-sm, 12px));
  bottom: calc(var(--comic-stack-depth, 12px) - var(--comic-stack-near-reveal, 7px));
  left: var(--comic-stack-near-inset, var(--space-sm, 12px));
  z-index: 1;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-surface-card, #fff) 90%, var(--color-accent-soft, #f2edff)),
    color-mix(in srgb, var(--color-surface-accent, #f7f3ff) 84%, var(--color-accent-soft, #f2edff))
  );
}
.comic-stack-sheet.is-rear {
  right: var(--comic-stack-rear-inset, var(--space-lg, 24px));
  bottom: calc(var(--comic-stack-depth, 12px) - var(--comic-stack-rear-reveal, 12px));
  left: var(--comic-stack-rear-inset, var(--space-lg, 24px));
  z-index: 0;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-surface-card, #fff) 86%, var(--color-accent-soft, #f2edff)),
    color-mix(in srgb, var(--color-surface-accent, #f7f3ff) 78%, var(--color-accent-soft, #f2edff))
  );
  box-shadow: 0 5px 11px color-mix(in srgb, var(--color-theme-glow, rgba(126, 87, 194, .18)) 12%, transparent);
}
.comic-card-shell.is-shelf-layout,
.comic-card-shell.is-shelf-layout .comic-card-frame,
.comic-card-shell.is-shelf-layout .comic-book,
.comic-card-shell.is-shelf-layout .comic-card {
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
}
.comic-card-shell.is-shelf-layout .comic-card-frame,
.comic-card-shell.is-shelf-layout .comic-book,
.comic-card-shell.is-shelf-layout .comic-card,
.comic-card-shell.is-shelf-layout .comic-info {
  flex-direction: column;
}
.comic-card-shell.is-shelf-layout .comic-book,
.comic-card-shell.is-shelf-layout .comic-card { width: 100%; }
.comic-card-shell.is-shelf-layout .comic-info {
  display: flex;
  flex: 1 1 auto;
}
.comic-card-shell.is-shelf-layout .comic-meta-footer {
  margin-top: auto;
  padding-top: var(--space-xs, 8px);
}
.comic-card { position:relative; z-index:2; isolation:isolate; overflow:hidden; min-width:0; color:inherit; cursor:pointer; border:1px solid var(--color-border-soft,var(--line-soft,rgba(126,87,194,.28))); border-radius:var(--radius-card,22px); background:radial-gradient(circle at top left,color-mix(in srgb,var(--theme-glow-start,var(--theme-glow)) 48%,transparent),transparent 260px),var(--color-surface-card,var(--surface-card,#fff)); box-shadow:var(--shadow-card,0 18px 50px rgba(15,23,42,.14)); }
.comic-glare { position:absolute; inset:0; z-index:2; pointer-events:none; opacity:var(--tilt-glare-opacity,0); background:radial-gradient(circle at var(--tilt-glare-x,50%) var(--tilt-glare-y,50%),rgba(255,255,255,.52),rgba(255,255,255,.08) 34%,transparent 62%); mix-blend-mode:screen; transition:opacity var(--motion-duration-fast,160ms) var(--motion-ease-standard,ease); }
.comic-ribbon { position:absolute; z-index:4; top:var(--space-sm,12px); left:var(--space-sm,12px); padding:.25rem .45rem; border-radius:var(--radius-sm,8px); color:var(--color-accent-control-text,#fff); background:var(--color-accent-fill,var(--accent-strong,#7e57c2)); font-size:12px; font-weight:900; letter-spacing:.02em; text-shadow:none; }
.comic-card-menu { position:absolute; z-index:8; top:var(--space-xs,8px); right:var(--space-xs,8px); padding:5px; border:1px solid rgba(255,255,255,.14); border-radius:var(--radius-sm,8px); background:rgba(15,23,42,.58); backdrop-filter:blur(8px); }
.comic-menu-enter-active,.comic-menu-leave-active { transition:opacity 160ms ease,transform 160ms ease; }.comic-menu-enter,.comic-menu-leave-to { opacity:0; transform:translateY(-6px) scale(.96); }
.comic-cover { position:relative; isolation:isolate; aspect-ratio:2 / 3; min-height:220px; overflow:hidden; border-radius:var(--radius-card,22px) var(--radius-card,22px) 0 0; background:var(--color-surface-muted,var(--surface-accent,#f7f3ff)); }
.comic-open-button { display:block; width:100%; padding:0; border:0; color:inherit; cursor:pointer; text-align:inherit; }
.comic-open-button:focus-visible { outline:none; box-shadow:inset 0 0 0 3px var(--color-focus-ring); }
.comic-cover::before { content:""; position:absolute; z-index:0; inset:-18px; background-image:var(--comic-cover-image); background-position:center; background-size:cover; filter:blur(18px) saturate(1.18); opacity:.42; transform:scale(1.06); }.comic-cover::after { content:""; position:absolute; z-index:0; inset:0; background:var(--theme-glow,rgba(255,255,255,.18)); }
.comic-cover img,.comic-cover-placeholder { position:relative; z-index:1; display:block; width:100%; height:100%; }.comic-cover img { object-fit:cover; }.comic-cover-placeholder { display:grid; min-height:220px; place-items:center; padding:16px; color:var(--color-text-muted,var(--text-muted,#64748b)); background:linear-gradient(135deg,var(--color-surface-muted,#f1f5f9),var(--color-surface-card,#fff)); text-align:center; }
.comic-info { padding:var(--space-md,16px); border-top:1px solid var(--color-border-soft,var(--line-soft,#efe9ff)); }.comic-info h2 { overflow:hidden; margin:0; color:var(--color-text-primary,var(--text-strong,#22313f)); font-size:16px; font-weight:800; text-overflow:ellipsis; white-space:nowrap; }
.comic-title-button { display:block; width:100%; padding:0; overflow:hidden; border:0; color:inherit; background:transparent; cursor:pointer; font:inherit; text-align:left; text-overflow:ellipsis; white-space:nowrap; }
.comic-title-button:hover { color:var(--color-accent-foreground); }
.comic-title-button:focus-visible { border-radius:var(--radius-xs); outline:none; box-shadow:inset 0 0 0 2px var(--color-focus-ring); }
.comic-tags { display:flex; flex-wrap:wrap; gap:.32rem; max-height:3.25rem; margin-top:8px; overflow:hidden; }.comic-tags a,.comic-tag-more { max-width:100%; padding:.15rem .42rem; border:0; border-radius:999px; color:var(--accent-foreground,#6d4bc1); background:var(--accent-soft-gradient,var(--accent-soft,#f2edff)); font-size:12px; font-weight:800; line-height:1.35; text-overflow:ellipsis; white-space:nowrap; overflow:hidden; }.comic-tag-more { color:var(--color-text-muted,var(--text-muted,#64748b)); background:var(--color-surface-muted,var(--surface-2,#eef1f5)); cursor:pointer; }
.comic-author { display:flex; align-items:center; gap:8px; min-width:0; margin-top:8px; color:var(--color-text-muted,var(--text-muted,#64748b)); font-size:13px; }.comic-author img { width:24px; height:24px; border-radius:50%; object-fit:cover; }.comic-author a { overflow:hidden; min-width:0; color:var(--color-text-primary,var(--text-strong,#334155)); font-weight:800; text-overflow:ellipsis; white-space:nowrap; }.comic-author span { flex:0 0 auto; }
.comic-meta-footer { margin-top:var(--space-xs,8px); }
.comic-meta-footer .comic-source { margin-top:0; }
.comic-source { overflow:hidden; margin:8px 0 0; color:var(--color-text-muted,var(--text-muted,#64748b)); font-size:13px; text-overflow:ellipsis; white-space:nowrap; }.comic-source a,.comic-source span { color:var(--accent-foreground,#7e57c2); font-weight:700; }.comic-source.is-warning { color:var(--color-warning-text); }
.comic-stats { margin-top:8px; }
.comic-like { display:inline-flex; align-items:center; gap:.28rem; min-height:30px; margin-top:0; padding:0 .58rem; border:1px solid var(--color-border-soft,var(--line-soft,#e0e6ef)); border-radius:999px; color:var(--color-text-muted,var(--text-muted,#64748b)); background:var(--color-surface-muted,var(--surface-2,#f8fafc)); cursor:pointer; font-size:13px; font-weight:800; }.comic-like:hover,.comic-like.is-liked { color:var(--accent-foreground,#7e57c2); border-color:var(--accent,#7e57c2); background:var(--accent-soft-gradient,var(--accent-soft,rgba(126,87,194,.14))); }.comic-like:disabled { opacity:.72; cursor:wait; }
.comic-viewed { display:inline-flex; align-items:center; gap:.28rem; min-height:30px; padding:0 .48rem; color:var(--color-text-muted,var(--text-muted,#64748b)); font-size:13px; font-weight:800; }
@media (hover:none) { .motion-tilt-card { transform:none !important; }.comic-glare { display:none; } }
</style>
