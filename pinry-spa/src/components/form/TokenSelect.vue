<template>
  <div
    class="token-select"
    :class="{
      'is-disabled': disabled,
      'is-focused': focused,
      'is-changing': changing
    }">
    <div class="token-select__control">
      <select
        :id="controlId"
        :value="serializedValue"
        :disabled="disabled"
        :aria-label="ariaLabel"
        @change="onChange"
        @focus="focused = true"
        @blur="focused = false">
        <option
          v-for="option in options"
          :key="optionKey(option)"
          :value="serialize(option.value)"
          :disabled="option.disabled">
          {{ option.label }}
        </option>
      </select>
      <span class="token-select__icon" aria-hidden="true">
        <b-icon icon="chevron-down" custom-size="mdi-20px"></b-icon>
      </span>
      <span class="token-select__sheen" aria-hidden="true"></span>
    </div>
  </div>
</template>

<script>
let tokenSelectSequence = 0;

export default {
  name: 'TokenSelect',
  props: {
    ariaLabel: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    id: {
      type: String,
      default: '',
    },
    options: {
      type: Array,
      default() {
        return [];
      },
    },
    value: {
      default: null,
    },
  },
  data() {
    tokenSelectSequence += 1;
    return {
      changing: false,
      changeTimer: null,
      focused: false,
      instanceId: tokenSelectSequence,
    };
  },
  computed: {
    controlId() {
      return this.id || `token-select-${this.instanceId}`;
    },
    serializedValue() {
      return this.serialize(this.value);
    },
  },
  beforeDestroy() {
    if (this.changeTimer) {
      window.clearTimeout(this.changeTimer);
    }
  },
  methods: {
    onChange(event) {
      const serialized = event.target.value;
      const matched = this.options.find(
        option => this.serialize(option.value) === serialized,
      );
      this.$emit('input', matched ? matched.value : serialized);
      this.changing = false;
      this.$nextTick(() => {
        this.changing = true;
        if (this.changeTimer) {
          window.clearTimeout(this.changeTimer);
        }
        this.changeTimer = window.setTimeout(() => {
          this.changing = false;
          this.changeTimer = null;
        }, 360);
      });
    },
    optionKey(option) {
      return `${this.serialize(option.value)}-${option.label}`;
    },
    serialize(value) {
      return value === null || typeof value === 'undefined' ? '' : String(value);
    },
  },
};
</script>

<style lang="scss" scoped>
.token-select {
  width: 100%;
  min-width: 0;
}

.token-select__control {
  position: relative;
  isolation: isolate;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 150px),
    color-mix(in srgb, var(--color-surface-1) 88%, transparent);
  box-shadow: var(--shadow-xs);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-standard) var(--motion-ease-standard);
}

.token-select__control:hover {
  border-color: var(--color-accent-border);
  background: color-mix(in srgb, var(--color-accent-soft) 48%, var(--color-surface-1));
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.token-select.is-focused .token-select__control {
  border-color: var(--color-accent-strong);
  background: var(--color-surface-1);
  box-shadow: var(--focus-ring), 0 10px 24px var(--color-theme-glow);
  transform: translateY(-1px);
}

.token-select select {
  position: relative;
  z-index: 2;
  display: block;
  width: 100%;
  min-width: 0;
  height: 42px;
  padding: 0 2.65rem 0 var(--space-sm);
  border: 0;
  outline: 0;
  color: inherit;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 850;
  appearance: none;
}

.token-select select option {
  color: var(--color-text-strong);
  background: var(--color-surface-card);
}

.token-select__icon {
  position: absolute;
  z-index: 1;
  top: 50%;
  right: var(--space-xs);
  display: inline-grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: var(--radius-xs);
  color: var(--color-accent-strong);
  background: var(--color-accent-soft);
  pointer-events: none;
  transform: translateY(-50%);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-spring),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}

.token-select.is-focused .token-select__icon {
  color: var(--color-accent-text);
  background: var(--color-accent-strong);
  transform: translateY(-50%) rotate(180deg) scale(1.04);
}

.token-select__sheen {
  position: absolute;
  z-index: 1;
  inset: 0;
  background: linear-gradient(
    108deg,
    transparent 24%,
    color-mix(in srgb, var(--color-accent-text) 34%, transparent) 50%,
    transparent 76%
  );
  opacity: 0;
  pointer-events: none;
  transform: translateX(-112%);
}

.token-select.is-changing .token-select__sheen {
  opacity: 1;
  animation: token-select-sheen 360ms var(--motion-ease-emphasized) both;
}

.token-select.is-disabled {
  opacity: 0.5;
}

.token-select.is-disabled select {
  cursor: not-allowed;
}

@keyframes token-select-sheen {
  from { transform: translateX(-112%); }
  to { transform: translateX(112%); }
}

html[data-motion='reduce'] .token-select__control,
html[data-motion='reduce'] .token-select__icon,
html[data-motion='reduce'] .token-select__sheen {
  animation: none;
  transition: none;
}
</style>
