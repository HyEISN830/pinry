<template>
  <div
    class="token-select"
    :class="{
      'is-disabled': disabled,
      'is-focused': focused,
      'is-open': open,
      'is-changing': changing
    }">
    <button
      :id="controlId"
      ref="control"
      class="token-select__control"
      type="button"
      role="combobox"
      aria-haspopup="listbox"
      :aria-label="ariaLabel"
      :aria-controls="listboxId"
      :aria-expanded="open ? 'true' : 'false'"
      :aria-activedescendant="activeDescendant"
      :disabled="disabled"
      @click="toggleDropdown"
      @keydown="onKeydown"
      @focus="focused = true"
      @blur="onBlur">
      <span class="token-select__value">{{ selectedLabel }}</span>
      <span class="token-select__icon" aria-hidden="true">
        <b-icon icon="chevron-down" custom-size="mdi-20px"></b-icon>
      </span>
      <span class="token-select__sheen" aria-hidden="true"></span>
    </button>

    <transition name="token-select-options">
      <div
        v-if="open"
        :id="listboxId"
        class="token-select__options"
        role="listbox"
        :aria-label="ariaLabel"
        @pointerdown.prevent>
        <button
          v-for="(option, index) in options"
          :id="optionId(index)"
          :key="optionKey(option)"
          class="token-select__option"
          :class="{
            'is-active': activeIndex === index,
            'is-selected': isOptionSelected(option)
          }"
          type="button"
          role="option"
          tabindex="-1"
          :aria-selected="isOptionSelected(option) ? 'true' : 'false'"
          :disabled="option.disabled"
          @mouseenter="setActiveIndex(index)"
          @click="selectOption(option, index)">
          <span class="token-select__option-marker" aria-hidden="true">
            <b-icon
              v-if="isOptionSelected(option)"
              icon="check"
              custom-size="mdi-16px">
            </b-icon>
          </span>
          <span class="token-select__option-label">{{ option.label }}</span>
        </button>
      </div>
    </transition>
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
      activeIndex: -1,
      changing: false,
      changeTimer: null,
      focused: false,
      instanceId: tokenSelectSequence,
      open: false,
    };
  },
  computed: {
    activeDescendant() {
      return this.open && this.activeIndex >= 0
        ? this.optionId(this.activeIndex)
        : null;
    },
    controlId() {
      return this.id || `token-select-${this.instanceId}`;
    },
    listboxId() {
      return `${this.controlId}-options`;
    },
    selectedLabel() {
      const selected = this.options.find(option => this.isOptionSelected(option));
      return selected ? selected.label : this.ariaLabel;
    },
  },
  mounted() {
    document.addEventListener('pointerdown', this.onDocumentPointerDown);
  },
  beforeDestroy() {
    document.removeEventListener('pointerdown', this.onDocumentPointerDown);
    if (this.changeTimer) {
      window.clearTimeout(this.changeTimer);
    }
  },
  methods: {
    closeDropdown() {
      this.open = false;
      this.activeIndex = -1;
    },
    enabledIndexFrom(startIndex, step) {
      const optionCount = this.options.length;
      if (!optionCount) {
        return -1;
      }
      let index = startIndex;
      for (let checked = 0; checked < optionCount; checked += 1) {
        index = (index + step + optionCount) % optionCount;
        if (!this.options[index].disabled) {
          return index;
        }
      }
      return -1;
    },
    firstEnabledIndex() {
      return this.options.findIndex(option => !option.disabled);
    },
    isOptionSelected(option) {
      return this.serialize(option.value) === this.serialize(this.value);
    },
    lastEnabledIndex() {
      for (let index = this.options.length - 1; index >= 0; index -= 1) {
        if (!this.options[index].disabled) {
          return index;
        }
      }
      return -1;
    },
    moveActive(step) {
      if (!this.open) {
        this.openDropdown(step > 0 ? 'first' : 'last');
        return;
      }
      let startIndex = this.activeIndex;
      if (startIndex < 0) {
        startIndex = step > 0 ? -1 : 0;
      }
      this.activeIndex = this.enabledIndexFrom(startIndex, step);
      this.scrollActiveOptionIntoView();
    },
    onBlur() {
      this.focused = false;
      this.closeDropdown();
    },
    onDocumentPointerDown(event) {
      if (this.open && !this.$el.contains(event.target)) {
        this.closeDropdown();
      }
    },
    onKeydown(event) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.moveActive(1);
        return;
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.moveActive(-1);
        return;
      }
      if (event.key === 'Home') {
        event.preventDefault();
        this.openDropdown('first');
        return;
      }
      if (event.key === 'End') {
        event.preventDefault();
        this.openDropdown('last');
        return;
      }
      if (event.key === 'Escape' && this.open) {
        event.preventDefault();
        this.closeDropdown();
        return;
      }
      if ((event.key === 'Enter' || event.key === ' ') && this.open) {
        event.preventDefault();
        if (this.activeIndex >= 0) {
          this.selectOption(this.options[this.activeIndex], this.activeIndex);
        }
      }
    },
    openDropdown(position) {
      if (this.disabled || !this.options.length) {
        return;
      }
      const selectedIndex = this.options.findIndex(
        option => this.isOptionSelected(option) && !option.disabled,
      );
      this.open = true;
      if (position === 'first') {
        this.activeIndex = this.firstEnabledIndex();
      } else if (position === 'last') {
        this.activeIndex = this.lastEnabledIndex();
      } else {
        this.activeIndex = selectedIndex >= 0 ? selectedIndex : this.firstEnabledIndex();
      }
      this.scrollActiveOptionIntoView();
    },
    optionId(index) {
      return `${this.listboxId}-option-${index}`;
    },
    optionKey(option) {
      return `${this.serialize(option.value)}-${option.label}`;
    },
    pulseChange() {
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
    scrollActiveOptionIntoView() {
      this.$nextTick(() => {
        if (!this.open || this.activeIndex < 0) {
          return;
        }
        const activeOption = document.getElementById(this.optionId(this.activeIndex));
        if (activeOption && typeof activeOption.scrollIntoView === 'function') {
          activeOption.scrollIntoView({ block: 'nearest' });
        }
      });
    },
    selectOption(option, index) {
      if (!option || option.disabled) {
        return;
      }
      this.activeIndex = index;
      this.$emit('input', option.value);
      this.closeDropdown();
      this.pulseChange();
      this.$nextTick(() => {
        if (this.$refs.control) {
          this.$refs.control.focus();
        }
      });
    },
    serialize(value) {
      return value === null || typeof value === 'undefined' ? '' : String(value);
    },
    setActiveIndex(index) {
      if (!this.options[index].disabled) {
        this.activeIndex = index;
      }
    },
    toggleDropdown() {
      if (this.open) {
        this.closeDropdown();
      } else {
        this.openDropdown();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.token-select {
  position: relative;
  width: 100%;
  min-width: 0;
}

.token-select.is-open {
  z-index: calc(var(--z-dropdown, 130) - 1);
}

.token-select__control {
  position: relative;
  isolation: isolate;
  display: flex;
  width: 100%;
  min-width: 0;
  height: 42px;
  align-items: center;
  padding: 0 2.65rem 0 var(--space-sm);
  overflow: hidden;
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-strong);
  background:
    radial-gradient(circle at top left, var(--color-theme-glow), transparent 150px),
    color-mix(in srgb, var(--color-surface-1) 88%, transparent);
  box-shadow: var(--shadow-xs);
  cursor: pointer;
  font: inherit;
  text-align: left;
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

.token-select.is-focused .token-select__control,
.token-select.is-open .token-select__control {
  border-color: var(--color-accent-strong);
  background: var(--color-surface-1);
  box-shadow: var(--focus-ring), 0 10px 24px var(--color-theme-glow);
  transform: translateY(-1px);
}

.token-select__value {
  position: relative;
  z-index: 2;
  min-width: 0;
  overflow: hidden;
  font-size: 0.88rem;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.token-select__icon {
  position: absolute;
  z-index: 2;
  top: 50%;
  right: var(--space-xs);
  display: inline-grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: var(--radius-xs);
  color: var(--color-accent-strong);
  background: var(--color-accent-soft-gradient);
  pointer-events: none;
  transform: translateY(-50%);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-spring),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}

.token-select.is-open .token-select__icon {
  color: var(--color-accent-text);
  background: var(--color-accent-fill);
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

.token-select__options {
  position: absolute;
  z-index: 5;
  top: calc(100% + var(--space-2xs));
  right: 0;
  left: 0;
  display: grid;
  gap: 3px;
  max-height: min(260px, 42vh);
  padding: var(--space-2xs);
  overflow-x: hidden;
  overflow-y: auto;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-sm);
  background:
    radial-gradient(circle at top right, var(--color-theme-glow), transparent 180px),
    color-mix(in srgb, var(--color-surface-card) 96%, transparent);
  box-shadow: var(--shadow-floating);
  backdrop-filter: blur(18px) saturate(1.08);
  overscroll-behavior: contain;
  scrollbar-color: var(--color-accent-border) transparent;
}

.token-select__option {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  min-height: 38px;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-2xs) var(--space-xs);
  border: 1px solid transparent;
  border-radius: var(--radius-xs);
  color: var(--color-text-strong);
  background: transparent;
  cursor: pointer;
  font: inherit;
  text-align: left;
  user-select: none;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-emphasized),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard);
}

.token-select__option:hover,
.token-select__option.is-active {
  border-color: var(--color-accent-border);
  color: var(--color-accent-strong);
  background: color-mix(in srgb, var(--color-accent-soft) 74%, var(--color-surface-1));
  box-shadow: 0 7px 18px var(--color-theme-glow);
  transform: translateX(2px);
}

.token-select__option.is-selected {
  border-color: var(--color-accent-border);
  color: var(--color-accent-strong);
  background: var(--color-accent-soft-gradient);
  font-weight: 850;
}

.token-select__option:disabled {
  opacity: 0.42;
  cursor: not-allowed;
  transform: none;
}

.token-select__option-marker {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border: 1px solid color-mix(in srgb, var(--color-line-soft) 82%, transparent);
  border-radius: 50%;
  color: transparent;
  background: color-mix(in srgb, var(--color-surface-2) 78%, transparent);
  transition:
    transform var(--motion-duration-standard) var(--motion-ease-spring),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    color var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}

.token-select__option.is-selected .token-select__option-marker {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-text);
  text-shadow: var(--color-accent-text-shadow);
  background: var(--color-accent-fill);
  box-shadow: 0 4px 12px var(--color-theme-glow-strong);
  transform: scale(1.06);
}

.token-select__option-label {
  min-width: 0;
  overflow: hidden;
  font-size: 0.84rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.token-select-options-enter-active,
.token-select-options-leave-active {
  transform-origin: top center;
  transition:
    opacity var(--motion-duration-fast) var(--motion-ease-standard),
    transform var(--motion-duration-standard) var(--motion-ease-emphasized);
}

.token-select-options-enter,
.token-select-options-leave-to {
  opacity: 0;
  transform: translateY(-7px) scale(0.975);
}

.token-select.is-disabled {
  opacity: 0.5;
}

.token-select.is-disabled .token-select__control {
  cursor: not-allowed;
}

@keyframes token-select-sheen {
  from { transform: translateX(-112%); }
  to { transform: translateX(112%); }
}

html[data-motion='reduce'] .token-select__control,
html[data-motion='reduce'] .token-select__icon,
html[data-motion='reduce'] .token-select__sheen,
html[data-motion='reduce'] .token-select__options,
html[data-motion='reduce'] .token-select__option,
html[data-motion='reduce'] .token-select__option-marker {
  animation: none;
  transition: none;
}
</style>
