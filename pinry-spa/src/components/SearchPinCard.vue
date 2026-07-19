<template>
  <article class="search-pin-card">
    <div class="pin-card-frame motion-card-enter">
      <div class="search-pin-card__surface pin-card motion-hover-scale">
        <span class="pin-card-glare" aria-hidden="true"></span>
        <button
          class="search-pin-card__media"
          type="button"
          :style="coverStyle"
          @click="$emit('preview', pin)">
          <img :src="imageUrl" :alt="pin.description || $t('pinLink')">
          <span class="search-result-kind">{{ $t('pinLink') }}</span>
        </button>
        <div class="search-pin-card__body">
          <button
            v-if="pin.description"
            class="search-pin-card__title"
            type="button"
            @click="$emit('preview', pin)">
            {{ pin.description }}
          </button>
          <p v-if="submitter" class="search-pin-card__author">
            {{ $t('pinnedByInfo') }}
            <router-link :to="{ name: 'user', params: { user: submitter.username } }">
              {{ submitter.username }}
            </router-link>
          </p>
          <div v-if="pin.tags && pin.tags.length" class="search-card-tags">
            <router-link
              v-for="tag in pin.tags.slice(0, 6)"
              :key="`${pin.id}-${tag}`"
              class="content-tag-pill"
              :to="{ name: 'tag', params: { tag } }">
              {{ tag }}
            </router-link>
          </div>
          <div class="search-pin-card__actions">
            <a
              v-if="sourceHref"
              v-source-tooltip
              class="search-pin-card__source content-source-link"
              :href="sourceHref"
              :data-source-tip="sourceTip"
              target="_blank"
              rel="noopener">
              {{ $t('sourceLink') }}
            </a>
            <span
              v-else-if="sourceTip"
              v-source-tooltip
              class="search-pin-card__source content-source-link"
              tabindex="0"
              :data-source-tip="sourceTip">
              {{ sourceTip }}
            </span>
            <div class="search-card-stats">
              <button
                class="search-card-like content-like-pill"
                type="button"
                :class="{ 'is-liked': pin.viewer_liked }"
                :aria-pressed="pin.viewer_liked ? 'true' : 'false'"
                :disabled="likeBusy"
                @click.stop="$emit('toggle-like', pin)">
                <b-icon :icon="pin.viewer_liked ? 'heart' : 'heart-outline'" size="is-small"></b-icon>
                <span>{{ formattedLikes }}</span>
              </button>
              <span class="search-card-viewed" :title="$t('viewedLabel')">
                <b-icon icon="eye-outline" size="is-small" aria-hidden="true"></b-icon>
                <span>{{ formattedViewed }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<script>
import format from './utils/format';
import imageVariant from './utils/imageVariant';

export default {
  name: 'SearchPinCard',
  props: {
    pin: { type: Object, required: true },
    likeBusy: { type: Boolean, default: false },
  },
  computed: {
    submitter() { return this.pin.submitter || null; },
    imageUrl() {
      const thumbnail = imageVariant.getCardThumbnail(this.pin.image) || {};
      return thumbnail.image || '';
    },
    coverStyle() {
      return { '--search-card-image': this.imageUrl ? `url("${this.imageUrl}")` : 'none' };
    },
    sourceTip() {
      return typeof this.pin.referer === 'string' ? this.pin.referer.trim() : '';
    },
    sourceHref() {
      return /^https?:\/\//i.test(this.sourceTip) ? this.sourceTip : '';
    },
    formattedLikes() { return format.formatCount(this.pin.likes_count); },
    formattedViewed() { return format.formatCount(this.pin.viewed_count); },
  },
};
</script>

<style lang="scss">
.search-pin-card { position: relative; min-width: 0; z-index: 1; }
.search-pin-card:hover { z-index: 2; }
.search-pin-card__surface { position: relative; z-index: 1; display: block; overflow: hidden; border: 1px solid var(--color-line-soft); border-radius: var(--radius-md); color: inherit; background: var(--color-surface-1); box-shadow: var(--shadow-card); }
.search-pin-card__media { position: relative; isolation: isolate; display: block; width: 100%; min-height: 180px; padding: 0; overflow: hidden; border: 0; background: var(--color-surface-2); cursor: zoom-in; text-align: left; }
.search-pin-card__media::before { position: absolute; z-index: 0; inset: -18px; background-image: var(--search-card-image); background-position: center; background-size: cover; content: ''; filter: blur(18px) saturate(1.14); opacity: 0.38; }
.search-pin-card__media img { position: relative; z-index: 1; display: block; width: 100%; min-height: 180px; max-height: 400px; object-fit: cover; }
.search-result-kind { position: absolute; z-index: 2; top: var(--space-xs); left: var(--space-xs); padding: 0.22rem 0.52rem; border-radius: var(--radius-pill); color: var(--color-accent-text); background: var(--color-accent-fill); font-size: 12px; font-weight: 900; text-shadow: var(--color-accent-text-shadow); }
.search-pin-card__body { padding: var(--space-sm); }
.search-pin-card__title { display: -webkit-box; width: 100%; padding: 0; overflow: hidden; border: 0; color: var(--color-text-strong); background: transparent; cursor: zoom-in; font-family: inherit; font-size: 1rem; font-weight: 900; line-height: 1.35; text-align: left; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-pin-card__title:hover { color: var(--color-accent-foreground); }
.search-pin-card__author { margin: var(--space-xs) 0 0; color: var(--color-text-muted); font-size: 0.9rem; }
.search-pin-card__author a { color: var(--color-accent-foreground); font-weight: 800; }
.search-card-tags { margin-top: var(--space-xs); }
.search-pin-card__actions { display: grid; justify-items: start; gap: var(--space-xs); margin-top: var(--space-sm); }
.search-pin-card__source { display: flex; width: fit-content; max-width: 100%; }
.search-card-like { display: inline-flex; align-items: center; gap: 0.28rem; min-height: 30px; padding: 0 0.58rem; border: 1px solid var(--color-line-soft); border-radius: var(--radius-pill); color: var(--color-text-muted); background: var(--color-surface-2); cursor: pointer; font-size: 13px; font-weight: 900; }
.search-card-like:hover, .search-card-like.is-liked { border-color: var(--color-accent); color: var(--color-accent-foreground); background: var(--color-accent-soft-gradient); }
.search-card-like:disabled { opacity: 0.72; cursor: wait; }
.search-card-stats { display: flex; align-items: center; flex-wrap: wrap; gap: .48rem; }
.search-card-viewed { display: inline-flex; align-items: center; gap: .28rem; min-height: 30px; padding: 0 .48rem; color: var(--color-text-muted); font-size: 13px; font-weight: 900; }

</style>
