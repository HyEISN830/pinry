<template>
  <article class="search-pin-card motion-card-enter">
    <div class="search-pin-card__surface pin-card motion-hover-scale">
      <router-link
        class="search-pin-card__media"
        :style="coverStyle"
        :to="{ name: 'pin', params: { pinId: pin.id } }">
        <img :src="imageUrl" :alt="pin.description || $t('pinLink')">
        <span class="search-result-kind">{{ $t('pinLink') }}</span>
      </router-link>
      <div class="search-pin-card__body">
        <router-link
          v-if="pin.description"
          class="search-pin-card__title"
          :to="{ name: 'pin', params: { pinId: pin.id } }">
          {{ pin.description }}
        </router-link>
        <p class="search-pin-card__author" v-if="submitter">
          {{ $t('pinnedByInfo') }}
          <router-link :to="{ name: 'user', params: { user: submitter.username } }">
            {{ submitter.username }}
          </router-link>
        </p>
        <div v-if="pin.tags && pin.tags.length" class="search-card-tags">
          <router-link
            v-for="tag in pin.tags.slice(0, 6)"
            :key="`${pin.id}-${tag}`"
            :to="{ name: 'tag', params: { tag } }">
            {{ tag }}
          </router-link>
        </div>
        <button
          class="search-card-like"
          type="button"
          :class="{ 'is-liked': pin.viewer_liked }"
          :disabled="likeBusy"
          @click="$emit('toggle-like', pin)">
          <b-icon :icon="pin.viewer_liked ? 'heart' : 'heart-outline'" size="is-small"></b-icon>
          <span>{{ formattedLikes }}</span>
        </button>
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
    formattedLikes() { return format.formatCount(this.pin.likes_count); },
  },
};
</script>

<style lang="scss" scoped>
.search-pin-card { position: relative; min-width: 0; z-index: 1; }
.search-pin-card:hover { z-index: 2; }
.search-pin-card__surface { display: block; overflow: hidden; border: 1px solid var(--color-line-soft); border-radius: var(--radius-md); color: inherit; background: var(--color-surface-1); box-shadow: var(--shadow-card); }
.search-pin-card__media { position: relative; isolation: isolate; display: block; min-height: 180px; overflow: hidden; background: var(--color-surface-2); }
.search-pin-card__media::before { position: absolute; z-index: 0; inset: -18px; background-image: var(--search-card-image); background-position: center; background-size: cover; content: ''; filter: blur(18px) saturate(1.14); opacity: 0.38; }
.search-pin-card__media img { position: relative; z-index: 1; display: block; width: 100%; min-height: 180px; max-height: 400px; object-fit: cover; }
.search-result-kind { position: absolute; z-index: 2; top: var(--space-xs); left: var(--space-xs); padding: 0.22rem 0.52rem; border-radius: var(--radius-pill); color: var(--color-accent-text); background: var(--color-accent-strong); font-size: 12px; font-weight: 900; }
.search-pin-card__body { padding: var(--space-sm); }
.search-pin-card__title { display: -webkit-box; overflow: hidden; color: var(--color-text-strong); font-size: 1rem; font-weight: 900; line-height: 1.35; text-decoration: none; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-pin-card__title:hover { color: var(--color-accent-strong); }
.search-pin-card__author { margin: var(--space-xs) 0 0; color: var(--color-text-muted); font-size: 0.9rem; }
.search-pin-card__author a { color: var(--color-accent-strong); font-weight: 800; }
.search-card-tags { display: flex; flex-wrap: wrap; gap: var(--space-xs); margin-top: var(--space-xs); }
.search-card-tags a { display: inline-flex; max-width: 100%; padding: 0.18rem 0.5rem; overflow: hidden; border-radius: var(--radius-pill); color: var(--color-accent-strong); background: var(--color-accent-soft); font-size: 12px; font-weight: 900; text-decoration: none; text-overflow: ellipsis; white-space: nowrap; }
.search-card-like { display: inline-flex; align-items: center; gap: 0.28rem; min-height: 30px; margin-top: var(--space-sm); padding: 0 0.58rem; border: 1px solid var(--color-line-soft); border-radius: var(--radius-pill); color: var(--color-text-muted); background: var(--color-surface-2); cursor: pointer; font-size: 13px; font-weight: 900; }
.search-card-like:hover, .search-card-like.is-liked { border-color: var(--color-accent); color: var(--color-accent-strong); background: var(--color-accent-soft); }
.search-card-like:disabled { opacity: 0.72; cursor: wait; }
</style>
