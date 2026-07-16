<template>
  <section class="collection-hero">
    <div class="collection-mark">{{ typeLabel }}</div>
    <div class="collection-main">
      <h1>{{ displayTitle }}</h1>
      <p>{{ description }}</p>
    </div>
    <div class="collection-count">
      <strong>{{ displayCount }}</strong>
      <span>{{ $t("collectionArtworksLabel") }}</span>
    </div>
    <div v-if="canShare || canCreatePin" class="collection-actions">
      <button
        v-if="canShare"
        class="button collection-action collection-share-action"
        type="button"
        @click="$emit('share')">
        <b-icon icon="share-variant" custom-size="mdi-18px"></b-icon>
        <span>{{ $t("shareButton") }}</span>
      </button>
      <button
        v-if="canCreatePin"
        class="button is-primary collection-action"
        type="button"
        @click="$emit('create-pin')">
        {{ $t("addPinToBoardButton") }}
      </button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CollectionHero',
  props: {
    type: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    count: {
      type: Number,
      default: null,
    },
    owner: {
      type: String,
      default: '',
    },
    isPrivate: {
      type: Boolean,
      default: false,
    },
    canCreatePin: {
      type: Boolean,
      default: false,
    },
    canShare: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    displayTitle() {
      if (this.type === 'tag') {
        return `#${this.title}`;
      }
      return this.title;
    },
    displayCount() {
      if (this.count === null || this.count === undefined) {
        return '-';
      }
      return this.count;
    },
    typeLabel() {
      if (this.type === 'tag') {
        return this.$t('collectionTagLabel');
      }
      return this.$t('collectionBoardLabel');
    },
    description() {
      if (this.type === 'tag') {
        return this.$t('collectionTagDescription');
      }
      if (this.owner) {
        const privacy = this.isPrivate
          ? this.$t('collectionPrivateBoardLabel')
          : this.$t('collectionPublicBoardLabel');
        return `${privacy} - ${this.$t('collectionByLabel')} ${this.owner}`;
      }
      return this.$t('collectionBoardDescription');
    },
  },
};
</script>

<style lang="scss" scoped>
.collection-hero {
  box-sizing: border-box;
  display: flex;
  width: min(1260px, calc(100vw - 32px));
  max-width: min(1260px, calc(100vw - 32px));
  align-items: center;
  gap: 1rem;
  margin: 2rem auto 0;
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--accent-border, #e7ebf2);
  border-radius: 8px;
  background:
    radial-gradient(circle at top left, var(--theme-glow), transparent 320px),
    var(--surface-card, #fff);
  box-shadow: var(--shadow-soft, 0 14px 34px rgba(16, 24, 40, 0.12));
}
.collection-mark {
  flex: 0 0 auto;
  padding: 0.45rem 0.7rem;
  border-radius: 6px;
  background: var(--accent-soft-gradient, var(--accent-soft, #edf5ff));
  color: var(--accent-foreground, #1f6feb);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}
.collection-main {
  min-width: 0;
  flex: 1;
}
.collection-main h1 {
  margin: 0;
  color: var(--text-strong, #22313f);
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.2;
  word-break: break-word;
}
.collection-main p {
  margin: 0.35rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 14px;
}
.collection-count {
  flex: 0 0 auto;
  min-width: 84px;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--line-soft, #edf1f6);
  border-radius: 8px;
  background: var(--surface-accent, #f8fafc);
  text-align: center;
}
.collection-count strong {
  display: block;
  color: var(--text-strong, #22313f);
  font-size: 1.25rem;
  line-height: 1.1;
}
.collection-count span {
  color: var(--text-muted, #64748b);
  font-size: 12px;
}
.collection-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: var(--space-xs, 8px);
}
.collection-action {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: var(--space-xs, 8px);
  border-radius: 7px;
  font-weight: 700;
  box-shadow: var(--accent-shadow, 0 8px 18px rgba(31, 111, 235, 0.18));
  transition:
    transform var(--motion-duration-fast, .16s) var(--motion-ease-standard, ease),
    border-color var(--motion-duration-fast, .16s) var(--motion-ease-standard, ease),
    color var(--motion-duration-fast, .16s) var(--motion-ease-standard, ease),
    background var(--motion-duration-fast, .16s) var(--motion-ease-standard, ease),
    box-shadow var(--motion-duration-fast, .16s) var(--motion-ease-standard, ease);
}
.collection-action:hover {
  transform: translateY(-2px);
  box-shadow: var(--accent-shadow, 0 12px 24px rgba(31, 111, 235, 0.24));
}
.collection-share-action {
  border-color: var(--color-accent-border, var(--accent-border));
  color: var(--color-accent-foreground, var(--accent-foreground));
  background: var(--color-accent-soft-gradient, var(--accent-soft-gradient));
  box-shadow: var(--shadow-xs, 0 4px 12px rgba(15, 23, 42, 0.08));
}
.collection-share-action:hover,
.collection-share-action:focus-visible {
  border-color: var(--color-accent-strong, var(--accent-strong));
  color: var(--color-accent-text, #fff);
  background: var(--color-accent-fill, var(--accent-fill));
  box-shadow: 0 12px 24px var(--color-theme-glow, rgba(31, 111, 235, 0.2));
}

@media screen and (max-width: 760px) {
  .collection-hero {
    width: calc(100vw - 20px);
    max-width: calc(100vw - 20px);
  }
}

@media screen and (max-width: 542px) {
  .collection-hero {
    display: block;
  }
  .collection-main {
    margin-top: 0.8rem;
  }
  .collection-count {
    margin-top: 1rem;
    text-align: left;
  }
  .collection-action {
    width: 100%;
  }
  .collection-actions {
    display: grid;
    margin-top: 1rem;
  }
}
</style>
