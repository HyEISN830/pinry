<template>
  <section
    class="not-found-page"
    aria-labelledby="not-found-title"
    aria-describedby="not-found-description">
    <div class="not-found-card">
      <div class="not-found-constellation" aria-hidden="true">
        <svg viewBox="0 0 180 150" role="presentation">
          <defs>
            <linearGradient id="not-found-trail" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stop-color="var(--color-accent)" stop-opacity="0"/>
              <stop offset="0.58" stop-color="var(--color-accent)" stop-opacity="0.72"/>
              <stop offset="1" stop-color="var(--color-accent-strong)"/>
            </linearGradient>
          </defs>
          <circle class="not-found-orbit" cx="90" cy="75" r="55"/>
          <path class="not-found-trail" d="M22 112C59 102 87 81 121 42"/>
          <path class="not-found-trail is-soft" d="M36 123C72 105 101 79 137 31"/>
          <circle class="not-found-comet" cx="124" cy="39" r="7"/>
          <circle class="not-found-star is-one" cx="43" cy="44" r="3"/>
          <circle class="not-found-star is-two" cx="151" cy="86" r="2.5"/>
          <circle class="not-found-star is-three" cx="68" cy="128" r="2"/>
          <path class="not-found-spark" d="M145 20v14M138 27h14"/>
        </svg>
      </div>

      <p class="not-found-brand">{{ $t("siteBrandName") }}</p>
      <span class="not-found-code">{{ $t("error404") }}</span>
      <p class="not-found-kicker">{{ $t("notFoundKicker") }}</p>
      <h1 id="not-found-title">{{ $t("pageNotFound") }}</h1>
      <p id="not-found-description" class="not-found-description">
        {{ $t("notFoundDescription") }}
      </p>

      <div class="not-found-actions">
        <router-link class="not-found-action is-primary" :to="{ name: 'home' }">
          <b-icon icon="home" custom-size="mdi-20px"></b-icon>
          <span>{{ $t("notFoundHomeAction") }}</span>
        </router-link>
        <router-link class="not-found-action is-secondary" :to="{ name: 'search' }">
          <b-icon icon="magnify" custom-size="mdi-20px"></b-icon>
          <span>{{ $t("searchButton") }}</span>
        </router-link>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'PageNotFound',
};
</script>

<style lang="scss" scoped>
.not-found-page {
  box-sizing: border-box;
  display: grid;
  min-height: calc(100vh - var(--nav-height, 80px));
  min-height: calc(100svh - var(--nav-height, 80px));
  place-items: center;
  padding: clamp(var(--space-lg, 24px), 6vw, var(--space-3xl, 64px)) var(--space-md, 16px);
  background:
    radial-gradient(circle at 18% 24%, var(--color-theme-glow-start), transparent 280px),
    radial-gradient(circle at 82% 72%, var(--color-theme-glow-end), transparent 320px);
}

.not-found-card {
  position: relative;
  isolation: isolate;
  box-sizing: border-box;
  width: min(100%, 720px);
  overflow: hidden;
  padding: clamp(var(--space-xl, 32px), 7vw, var(--space-3xl, 64px));
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-xl, 32px);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top, var(--color-theme-glow), transparent 300px),
    var(--color-surface-card);
  box-shadow: var(--shadow-floating);
  text-align: center;
}

.not-found-card::before,
.not-found-card::after {
  content: '';
  position: absolute;
  z-index: -1;
  border-radius: 50%;
  background: var(--color-accent-soft-gradient);
  pointer-events: none;
}

.not-found-card::before {
  top: -72px;
  left: -58px;
  width: 168px;
  height: 168px;
  opacity: 0.48;
}

.not-found-card::after {
  right: -54px;
  bottom: -82px;
  width: 190px;
  height: 190px;
  opacity: 0.34;
}

.not-found-constellation {
  width: min(56vw, 190px);
  margin: 0 auto var(--space-sm, 12px);
  color: var(--color-accent-foreground);
}

.not-found-constellation svg {
  display: block;
  width: 100%;
  overflow: visible;
}

.not-found-orbit {
  fill: none;
  stroke: var(--color-accent-border);
  stroke-dasharray: 3 8;
  stroke-width: 1.4;
}

.not-found-trail {
  fill: none;
  stroke: url(#not-found-trail);
  stroke-linecap: round;
  stroke-width: 4;
}

.not-found-trail.is-soft {
  opacity: 0.32;
  stroke-width: 9;
}

.not-found-comet {
  fill: var(--color-accent-text);
  stroke: var(--color-accent-strong);
  stroke-width: 4;
  filter: drop-shadow(0 0 9px var(--color-theme-glow-strong));
}

.not-found-star {
  fill: var(--color-accent-foreground);
}

.not-found-star.is-two {
  opacity: 0.72;
}

.not-found-star.is-three {
  opacity: 0.54;
}

.not-found-spark {
  fill: none;
  stroke: var(--color-accent-foreground);
  stroke-linecap: round;
  stroke-width: 2.2;
}

.not-found-brand,
.not-found-kicker,
.not-found-description {
  margin-right: auto;
  margin-left: auto;
}

.not-found-brand {
  margin-top: 0;
  margin-bottom: var(--space-xs, 8px);
  color: var(--color-accent-foreground);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.not-found-code {
  display: inline-flex;
  min-height: 30px;
  align-items: center;
  padding: 0 var(--space-sm, 12px);
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-pill, 999px);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.not-found-kicker {
  margin-top: var(--space-md, 16px);
  margin-bottom: var(--space-2xs, 4px);
  color: var(--color-text-muted);
  font-size: 0.82rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.not-found-card h1 {
  margin: 0;
  color: var(--color-text-strong);
  font-size: clamp(2rem, 7vw, 3.6rem);
  font-weight: 950;
  letter-spacing: -0.045em;
  line-height: 1.06;
}

.not-found-description {
  max-width: 530px;
  margin-top: var(--space-md, 16px);
  margin-bottom: 0;
  color: var(--color-text-muted);
  font-size: clamp(0.94rem, 2.5vw, 1.06rem);
  line-height: 1.72;
}

.not-found-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-sm, 12px);
  margin-top: var(--space-xl, 32px);
}

.not-found-action {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 8px);
  padding: 0 var(--space-lg, 24px);
  border: 1px solid transparent;
  border-radius: var(--radius-pill, 999px);
  font-size: 0.9rem;
  font-weight: 900;
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard);
}

.not-found-action:hover {
  transform: translateY(var(--motion-hover-lift, -4px));
}

.not-found-action:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.not-found-action.is-primary {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  text-shadow: var(--color-accent-text-shadow);
  background: var(--color-accent-fill);
  box-shadow: 0 14px 30px var(--color-theme-glow);
}

.not-found-action.is-primary:hover {
  color: var(--color-accent-text);
  background: var(--color-accent-fill-hover);
}

.not-found-action.is-secondary {
  border-color: var(--color-line-soft);
  color: var(--color-text-strong);
  background: var(--color-surface-2);
}

.not-found-action.is-secondary:hover {
  border-color: var(--color-accent-border);
  color: var(--color-accent-foreground);
  background: var(--color-accent-soft-gradient);
}

@media screen and (max-width: 540px) {
  .not-found-page {
    padding: var(--space-md, 16px) var(--space-sm, 12px) var(--space-xl, 32px);
  }

  .not-found-card {
    padding: var(--space-xl, 32px) var(--space-md, 16px);
    border-radius: var(--radius-lg, 24px);
  }

  .not-found-constellation {
    width: 154px;
  }

  .not-found-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .not-found-action {
    width: 100%;
  }
}
</style>
