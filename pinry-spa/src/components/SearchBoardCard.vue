<template>
  <article class="search-board-card">
    <div class="board-card-frame motion-card-enter">
      <div class="search-board-card__surface board-card motion-hover-scale">
        <span class="board-card-glare" aria-hidden="true"></span>
        <router-link
          class="search-board-card__primary"
          :to="{ name: 'board', params: { boardId: board.id } }">
          <div class="search-board-card__media" :style="coverStyle">
            <img v-if="coverImageUrl" :src="coverImageUrl" :alt="board.name">
            <div v-else class="search-board-card__placeholder" aria-hidden="true">
              <b-icon icon="image" size="is-medium"></b-icon>
            </div>
            <span class="search-result-kind">{{ $t('boardLink') }}</span>
          </div>
          <div class="search-board-card__body">
            <h3>{{ board.name }}</h3>
            <p v-if="board.description">{{ board.description }}</p>
          </div>
        </router-link>
        <div class="search-board-card__footer">
          <router-link
            v-if="owner"
            class="search-board-card__owner"
            :to="{ name: 'user', params: { user: owner.username } }">
            <img :src="ownerAvatar" alt="">
            <span>{{ owner.username }}</span>
          </router-link>
          <span class="search-board-card__count">
            <strong>{{ pinCount }}</strong>
            <small>{{ $t('pinsLink') }}</small>
          </span>
        </div>
      </div>
    </div>
  </article>
</template>

<script>
import imageVariant from './utils/imageVariant';

export default {
  name: 'SearchBoardCard',
  props: { board: { type: Object, required: true } },
  computed: {
    owner() {
      return this.board.submitter || null;
    },
    ownerAvatar() {
      if (!this.owner) {
        return '';
      }
      return (this.owner.avatar && this.owner.avatar.small)
        || `//gravatar.com/avatar/${this.owner.gravatar || ''}?s=28`;
    },
    pinCount() {
      return Number.isFinite(this.board.total_pins) ? this.board.total_pins : 0;
    },
    coverImageUrl() {
      if (!this.board.cover || !this.board.cover.image) return '';
      const thumbnail = imageVariant.getCardThumbnail(this.board.cover.image) || {};
      return thumbnail.image || '';
    },
    coverStyle() {
      return { '--search-card-image': this.coverImageUrl ? `url("${this.coverImageUrl}")` : 'none' };
    },
  },
};
</script>

<style lang="scss">
.search-board-card { position: relative; min-width: 0; z-index: 1; }
.search-board-card:hover { z-index: 2; }
.search-board-card__surface { position: relative; z-index: 1; display: block; overflow: hidden; border: 1px solid var(--color-line-soft); border-radius: var(--radius-md); color: inherit; background: var(--color-surface-1); box-shadow: var(--shadow-card); }
.search-board-card__primary { display: block; color: inherit; text-decoration: none; }
.search-board-card__media { position: relative; isolation: isolate; aspect-ratio: 16 / 10; overflow: hidden; background: var(--color-surface-2); }
.search-board-card__media::before { position: absolute; z-index: 0; inset: -18px; background-image: var(--search-card-image); background-position: center; background-size: cover; content: ''; filter: blur(18px) saturate(1.14); opacity: 0.38; }
.search-board-card__media img { position: relative; z-index: 1; display: block; width: 100%; height: 100%; object-fit: cover; }
.search-board-card__placeholder { position: relative; z-index: 1; display: grid; width: 100%; height: 100%; place-items: center; padding: var(--space-md); color: var(--color-text-muted); text-align: center; }
.search-result-kind { position: absolute; z-index: 2; top: var(--space-xs); left: var(--space-xs); padding: 0.22rem 0.52rem; border-radius: var(--radius-pill); color: var(--color-accent-text); background: var(--color-accent-strong); font-size: 12px; font-weight: 900; }
.search-board-card__body { padding: var(--space-sm); }
.search-board-card__body h3 { display: -webkit-box; overflow: hidden; margin: 0; color: var(--color-text-strong); font-size: 1rem; font-weight: 900; line-height: 1.35; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-board-card__body p { display: -webkit-box; overflow: hidden; margin: var(--space-xs) 0 0; color: var(--color-text-muted); font-size: 0.9rem; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-board-card__primary:hover h3 { color: var(--color-accent-strong); }
.search-board-card__footer { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); min-height: 48px; padding: var(--space-xs) var(--space-sm) var(--space-sm); border-top: 1px solid var(--color-line-soft); }
.search-board-card__owner { display: inline-flex; align-items: center; min-width: 0; gap: var(--space-xs); overflow: hidden; color: var(--color-text-strong); font-size: 0.84rem; font-weight: 900; text-decoration: none; }
.search-board-card__owner:hover { color: var(--color-accent-strong); }
.search-board-card__owner img { flex: 0 0 auto; width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.search-board-card__owner span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-board-card__count { display: inline-flex; flex: 0 0 auto; align-items: center; gap: 0.25rem; min-height: 30px; margin-left: auto; padding: 0 0.55rem; border-radius: var(--radius-pill); color: var(--color-accent-strong); background: var(--color-accent-soft); white-space: nowrap; }
.search-board-card__count strong { font-size: 0.94rem; font-weight: 950; }
.search-board-card__count small { color: inherit; font-size: 0.76rem; font-weight: 850; opacity: 0.82; }

</style>
