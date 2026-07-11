<template>
  <article
    class="comic-card-shell motion-card-enter motion-tilt-scene"
    :class="{ 'is-tilting': tilting }"
    @mouseenter="menuVisible = isOwner"
    @mouseleave="handleLeave"
    @pointermove="scheduleTilt"
    @pointerleave="resetTilt"
    @pointercancel="resetTilt"
    @click="openComic">
    <div ref="card" class="comic-card motion-tilt-card">
      <span class="motion-tilt-glare comic-glare" aria-hidden="true"></span>
      <transition name="comic-menu">
        <div v-if="menuVisible && isOwner" class="comic-card-menu" @click.stop>
          <button class="button is-small is-danger" type="button" @click.stop="$emit('delete', comic)">
            {{ $t('deleteButton') }}
          </button>
        </div>
      </transition>
      <div class="comic-ribbon">{{ $t('comicLink') }}</div>
      <div class="comic-cover" :style="coverStyle">
        <img v-if="coverUrl" :src="coverUrl" :alt="comic.title" @load="$emit('image-settled')" @error="$emit('image-settled')">
        <div v-else class="comic-cover-placeholder">{{ $t('imageUnavailableText') }}</div>
      </div>
      <div class="comic-info">
        <h2>{{ comic.title }}</h2>
        <div v-if="comic.tags && comic.tags.length" class="comic-tags">
          <router-link v-for="tag in visibleTags" :key="tag" :to="{ name: 'tag', params: { tag } }" @click.stop>{{ tag }}</router-link>
          <button v-if="hiddenTagCount" class="comic-tag-more" type="button" @click.stop="openComic">...</button>
        </div>
        <div v-if="comic.submitter" class="comic-author">
          <img :src="avatarUrl" alt="">
          <router-link :to="{ name: 'user', params: { user: comic.submitter.username } }" @click.stop>{{ comic.submitter.username }}</router-link>
          <span>{{ comic.total_pages }} {{ $t('comicPagesUnit') }}</span>
        </div>
        <div v-if="comic.referer" class="comic-source">
          <a v-if="isWebSource" :href="comic.referer" target="_blank" rel="noopener" @click.stop>{{ $t('sourceLink') }}</a>
          <span v-else>{{ comic.referer }}</span>
        </div>
        <div v-else class="comic-source is-warning">{{ $t('missingSourceNotice') }}</div>
        <button class="comic-like" type="button" :class="{ 'is-liked': comic.viewer_liked }" :disabled="likeBusy" @click.stop="$emit('toggle-like', comic)">
          <b-icon :icon="comic.viewer_liked ? 'heart' : 'heart-outline'" size="is-small"></b-icon>
          <span>{{ formattedLikes }}</span>
        </button>
      </div>
    </div>
  </article>
</template>

<script>
import imageVariant from './utils/imageVariant';
import motionPreference from './utils/motionPreference';
import format from './utils/format';

export default {
  name: 'ComicCard',
  props: {
    comic: { type: Object, required: true },
    currentUsername: { type: String, default: null },
    likeBusy: { type: Boolean, default: false },
  },
  data() { return { menuVisible: false, tilting: false, tiltFrame: null }; },
  computed: {
    isOwner() { return !!(this.currentUsername && this.comic.submitter && this.comic.submitter.username === this.currentUsername); },
    coverUrl() {
      const cover = this.comic.cover_image || this.comic.cover;
      if (!cover) return null;
      if (typeof cover === 'string') return cover;
      const image = cover.image || cover;
      if (typeof image === 'string') return image;
      try { const thumb = imageVariant.getCardThumbnail(image) || {}; return thumb.image || image.thumbnail || image.url || null; } catch (e) { return image.thumbnail || image.url || null; }
    },
    coverStyle() { return { '--comic-cover-image': this.coverUrl ? `url("${this.coverUrl}")` : 'none' }; },
    visibleTags() { return (this.comic.tags || []).slice(0, 4); },
    hiddenTagCount() { return Math.max(0, (this.comic.tags || []).length - 4); },
    avatarUrl() { const user = this.comic.submitter || {}; return (user.avatar && user.avatar.small) || `//gravatar.com/avatar/${user.gravatar}?s=28`; },
    isWebSource() { return /^https?:\/\//i.test((this.comic.referer || '').trim()); },
    formattedLikes() { return format.formatCount(this.comic.likes_count); },
  },
  beforeDestroy() { if (this.tiltFrame) window.cancelAnimationFrame(this.tiltFrame); },
  methods: {
    openComic() { this.$router.push({ name: 'comic', params: { comicId: this.comic.id } }); },
    scheduleTilt(event) {
      if (motionPreference.isReducedMotionEnabled()) return;
      const shell = event.currentTarget;
      if (!shell) return;
      if (this.tiltFrame) window.cancelAnimationFrame(this.tiltFrame);
      this.tiltFrame = window.requestAnimationFrame(() => {
        const rect = shell.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        const x = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height));
        shell.style.setProperty('--tilt-rotate-x', `${((0.5 - y) * 12).toFixed(2)}deg`);
        shell.style.setProperty('--tilt-rotate-y', `${((x - 0.5) * 14).toFixed(2)}deg`);
        shell.style.setProperty('--tilt-glare-x', `${x * 100}%`);
        shell.style.setProperty('--tilt-glare-y', `${y * 100}%`);
        shell.style.setProperty('--tilt-glare-opacity', '0.34');
        this.tilting = true;
        this.tiltFrame = null;
      });
    },
    resetTilt(event) { const shell = event.currentTarget; if (shell) { shell.style.setProperty('--tilt-rotate-x', '0deg'); shell.style.setProperty('--tilt-rotate-y', '0deg'); shell.style.setProperty('--tilt-glare-opacity', '0'); } this.tilting = false; },
    handleLeave(event) { this.menuVisible = false; this.resetTilt(event); },
  },
};
</script>

<style scoped lang="scss">
.comic-card-shell { position: relative; width: var(--comic-card-width, var(--personal-comic-width, 240px)); min-width: 0; z-index: 1; margin-bottom: var(--comic-grid-gutter, var(--personal-comic-gutter, 16px)); }
.comic-card-shell.is-tilting { z-index: 3; }
.comic-card { position: relative; isolation: isolate; overflow: hidden; cursor: pointer; border: 1px solid var(--accent-border, rgba(126,87,194,.42)); border-radius: var(--radius-card,22px); background: var(--surface-card,#fff); box-shadow: var(--shadow-card,0 18px 50px rgba(15,23,42,.16)); transform-style: preserve-3d; transition: transform 280ms cubic-bezier(.2,.8,.2,1); }
.comic-glare { position:absolute; inset:0; z-index:2; pointer-events:none; opacity:var(--tilt-glare-opacity,0); background:radial-gradient(circle at var(--tilt-glare-x,50%) var(--tilt-glare-y,50%),rgba(255,255,255,.52),transparent 62%); mix-blend-mode:screen; }
.comic-ribbon { position:absolute; z-index:4; top:12px; left:12px; padding:.25rem .45rem; border-radius:8px; color:#fff; background:var(--accent-strong,#7e57c2); font-size:12px; font-weight:900; }
.comic-card-menu { position:absolute; z-index:8; top:8px; right:8px; padding:5px; border-radius:8px; background:rgba(15,23,42,.58); }
.comic-cover { position:relative; isolation:isolate; min-height:220px; overflow:hidden; background:var(--surface-accent,#f7f3ff); }
.comic-cover::before { content:""; position:absolute; inset:-18px; background-image:var(--comic-cover-image); background-position:center; background-size:cover; filter:blur(18px); opacity:.42; }
.comic-cover img,.comic-cover-placeholder { position:relative; z-index:1; display:block; width:100%; height:auto; min-height:220px; object-fit:contain; }
.comic-cover-placeholder { display:grid; place-items:center; color:var(--text-muted,#64748b); }
.comic-info { padding:16px; border-top:1px solid var(--line-soft,#efe9ff); }
h2 { overflow:hidden; margin:0; font-size:16px; font-weight:900; text-overflow:ellipsis; white-space:nowrap; }
.comic-tags { display:flex; flex-wrap:wrap; gap:.32rem; max-height:3.25rem; margin-top:8px; overflow:hidden; }
.comic-tags a,.comic-tag-more { padding:.15rem .42rem; border:0; border-radius:999px; color:var(--accent-strong,#6d4bc1); background:var(--accent-soft,#f2edff); font-size:12px; font-weight:800; }
.comic-author { display:flex; align-items:center; gap:8px; margin-top:8px; color:var(--text-muted,#64748b); font-size:13px; }
.comic-author img { width:24px; height:24px; border-radius:50%; object-fit:cover; }
.comic-source { overflow:hidden; margin-top:8px; color:var(--text-muted,#64748b); font-size:13px; text-overflow:ellipsis; white-space:nowrap; }
.comic-source.is-warning { color:#8a6d1d; }
.comic-like { display:inline-flex; align-items:center; gap:.28rem; margin-top:8px; padding:.35rem .58rem; border:1px solid var(--line-soft,#e0e6ef); border-radius:999px; background:var(--surface-2,#f8fafc); cursor:pointer; }
.comic-like.is-liked { color:var(--accent-strong,#7e57c2); border-color:var(--accent,#7e57c2); }
@media (hover:none) { .motion-tilt-card { transform:none !important; } .comic-glare { display:none; } }
</style>
