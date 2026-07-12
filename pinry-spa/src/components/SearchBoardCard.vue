<template>
  <article class="search-board-card motion-card-enter">
    <router-link
      class="search-board-card__surface board-card motion-hover-scale"
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
        <span v-if="board.submitter" class="search-board-card__owner">{{ board.submitter.username }}</span>
      </div>
    </router-link>
  </article>
</template>

<script>
import imageVariant from './utils/imageVariant';

export default {
  name: 'SearchBoardCard',
  props: { board: { type: Object, required: true } },
  computed: {
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
.search-board-card__surface { position: relative; z-index: 1; display: block; overflow: hidden; border: 1px solid var(--color-line-soft); border-radius: var(--radius-md); color: inherit; background: var(--color-surface-1); box-shadow: var(--shadow-card); text-decoration: none; }
.search-board-card__media { position: relative; isolation: isolate; aspect-ratio: 16 / 10; overflow: hidden; background: var(--color-surface-2); }
.search-board-card__media::before { position: absolute; z-index: 0; inset: -18px; background-image: var(--search-card-image); background-position: center; background-size: cover; content: ''; filter: blur(18px) saturate(1.14); opacity: 0.38; }
.search-board-card__media img { position: relative; z-index: 1; display: block; width: 100%; height: 100%; object-fit: cover; }
.search-board-card__placeholder { position: relative; z-index: 1; display: grid; width: 100%; height: 100%; place-items: center; padding: var(--space-md); color: var(--color-text-muted); text-align: center; }
.search-result-kind { position: absolute; z-index: 2; top: var(--space-xs); left: var(--space-xs); padding: 0.22rem 0.52rem; border-radius: var(--radius-pill); color: var(--color-accent-text); background: var(--color-accent-strong); font-size: 12px; font-weight: 900; }
.search-board-card__body { padding: var(--space-sm); }
.search-board-card__body h3 { display: -webkit-box; overflow: hidden; margin: 0; color: var(--color-text-strong); font-size: 1rem; font-weight: 900; line-height: 1.35; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-board-card__body p { display: -webkit-box; overflow: hidden; margin: var(--space-xs) 0 0; color: var(--color-text-muted); font-size: 0.9rem; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.search-board-card__owner { display: block; margin-top: var(--space-sm); overflow: hidden; color: var(--color-accent-strong); font-size: 0.82rem; font-weight: 900; text-overflow: ellipsis; white-space: nowrap; }

@media (hover: hover) and (pointer: fine) {
  html[data-motion="full"] .search-board-card .board-card {
    position: relative;
    isolation: isolate;
    overflow: hidden;
  }

  html[data-motion="full"] .search-board-card .board-card::after {
    position: absolute;
    z-index: 4;
    top: -34%;
    bottom: -34%;
    left: -46%;
    width: 42%;
    border-radius: 42%;
    background: linear-gradient(
      112deg,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.08) 22%,
      rgba(255, 255, 255, 0.62) 48%,
      rgba(255, 255, 255, 0.12) 72%,
      rgba(255, 255, 255, 0) 100%
    );
    content: "";
    opacity: 0;
    pointer-events: none;
    transform: translate3d(-140%, 0, 0) skewX(-18deg);
    transition:
      opacity 110ms ease-out,
      transform 0ms linear 420ms;
  }

  html[data-motion="full"] .search-board-card:hover .board-card::after {
    opacity: 0.88;
    transform: translate3d(560%, 0, 0) skewX(-18deg);
    transition:
      opacity 100ms ease-out,
      transform 640ms cubic-bezier(0.16, 0.82, 0.25, 1);
  }
}
</style>
