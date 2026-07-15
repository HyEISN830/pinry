<template>
  <div class="action-confirm-modal">
    <div
      class="modal-card create-modal-card action-confirm-card"
      :class="toneClass">
      <header class="modal-card-head create-modal-head action-confirm-head">
        <div class="create-modal-title-block">
          <span class="create-modal-icon action-confirm-icon" aria-hidden="true">
            <b-icon :icon="icon" custom-size="mdi-22px"></b-icon>
          </span>
          <div>
            <span class="create-modal-kicker">{{ $t('confirmationLabel') }}</span>
            <p class="modal-card-title">{{ title }}</p>
          </div>
        </div>
        <button
          class="create-modal-close"
          type="button"
          :title="$t('closeButton')"
          :aria-label="$t('closeButton')"
          @click="close">
          <b-icon icon="close" custom-size="mdi-20px"></b-icon>
        </button>
      </header>
      <section class="modal-card-body create-modal-body action-confirm-body">
        <span class="action-confirm-pulse" aria-hidden="true"></span>
        <p>{{ message }}</p>
      </section>
      <footer class="modal-card-foot create-modal-foot action-confirm-foot">
        <button
          class="button create-modal-cancel"
          type="button"
          @click="close">
          {{ cancelButtonLabel }}
        </button>
        <button
          class="button action-confirm-submit"
          type="button"
          @click="confirm">
          <b-icon :icon="icon" custom-size="mdi-18px"></b-icon>
          <span>{{ confirmButtonLabel }}</span>
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActionConfirmModal',
  props: {
    cancelLabel: {
      type: String,
      default: '',
    },
    confirmLabel: {
      type: String,
      default: '',
    },
    icon: {
      type: String,
      default: 'alert-outline',
    },
    message: {
      type: String,
      default: '',
    },
    title: {
      type: String,
      required: true,
    },
    tone: {
      type: String,
      default: 'danger',
      validator: value => ['danger', 'accent'].indexOf(value) !== -1,
    },
  },
  computed: {
    cancelButtonLabel() {
      return this.cancelLabel || this.$t('cancelButton');
    },
    confirmButtonLabel() {
      return this.confirmLabel || this.$t('deleteButton');
    },
    toneClass() {
      return `is-${this.tone}`;
    },
  },
  methods: {
    close() {
      this.$parent.close();
    },
    confirm() {
      this.$emit('confirm');
      this.close();
    },
  },
};
</script>
