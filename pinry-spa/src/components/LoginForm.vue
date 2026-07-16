<template>
  <form
    class="modal-card create-modal-card auth-modal-card"
    @submit.prevent="doLogin">
    <header class="create-modal-head auth-modal-head">
      <div class="create-modal-title-block">
        <span class="create-modal-icon auth-modal-icon" aria-hidden="true">
          <b-icon icon="account-key" custom-size="mdi-24px"></b-icon>
        </span>
        <div>
          <span class="create-modal-kicker">Pinry</span>
          <p class="modal-card-title">{{ $t("loginTitle") }}</p>
        </div>
      </div>
      <button
        class="create-modal-close"
        type="button"
        :aria-label="$t('closeButton')"
        :title="$t('closeButton')"
        @click="closeModal">
        <b-icon icon="close" custom-size="mdi-20px"></b-icon>
      </button>
    </header>

    <section class="create-modal-body auth-modal-body">
      <div class="auth-modal-intro" aria-hidden="true">
        <span class="auth-modal-orbit auth-modal-orbit-one"></span>
        <span class="auth-modal-orbit auth-modal-orbit-two"></span>
        <span class="auth-modal-spark auth-modal-spark-one"></span>
        <span class="auth-modal-spark auth-modal-spark-two"></span>
        <b-icon icon="image-multiple" custom-size="mdi-42px"></b-icon>
      </div>

      <div class="auth-modal-fields">
        <b-field
          class="auth-field"
          :label="$t('usernameLabel')"
          :type="form.username.type"
          :message="form.username.error">
          <b-input
            ref="usernameInput"
            v-model="form.username.value"
            name="username"
            type="text"
            icon="account-outline"
            :placeholder="$t('usernamePlaceholder')"
            maxlength="30"
            autocomplete="username"
            :disabled="submitting"
            required>
          </b-input>
        </b-field>

        <b-field
          class="auth-field"
          :label="$t('passwordLabel')"
          :type="form.password.type"
          :message="form.password.error">
          <b-input
            v-model="form.password.value"
            name="password"
            type="password"
            icon="lock-outline"
            password-reveal
            :placeholder="$t('passwordLoginPlaceholder')"
            autocomplete="current-password"
            :disabled="submitting"
            required>
          </b-input>
        </b-field>

        <p v-if="requestError" class="auth-request-error" role="alert">
          <b-icon icon="alert-circle-outline" custom-size="mdi-18px"></b-icon>
          <span>{{ requestError }}</span>
        </p>
      </div>
    </section>

    <footer class="create-modal-foot auth-modal-foot">
      <button
        class="button create-modal-cancel"
        type="button"
        :disabled="submitting"
        @click="closeModal">
        {{ $t("closeButton") }}
      </button>
      <button
        class="button is-primary create-modal-submit auth-modal-submit"
        :class="{ 'is-loading': submitting }"
        type="submit"
        :disabled="submitting">
        <b-icon v-if="!submitting" icon="login" custom-size="mdi-18px"></b-icon>
        <span>{{ $t("loginButton") }}</span>
      </button>
    </footer>
  </form>
</template>

<script>
import api from './api';
import ModelForm from './utils/ModelForm';

const fields = ['username', 'password'];

function errorMessage(value) {
  if (Array.isArray(value)) {
    const [message] = value;
    return message || '';
  }
  return typeof value === 'string' ? value : '';
}

export default {
  name: 'LoginForm',
  data() {
    const model = ModelForm.fromFields(fields);
    return {
      form: model.form,
      helper: model,
      requestError: '',
      submitting: false,
    };
  },
  mounted() {
    this.$nextTick(() => {
      const input = this.$refs.usernameInput;
      if (input && input.focus) {
        input.focus();
      }
    });
  },
  methods: {
    closeModal() {
      if (!this.submitting && this.$parent && this.$parent.close) {
        this.$parent.close();
      }
    },
    doLogin() {
      if (this.submitting) {
        return;
      }
      this.helper.resetAllFields();
      this.requestError = '';
      this.submitting = true;
      api.User.logIn(
        this.form.username.value,
        this.form.password.value,
      ).then(
        (user) => {
          this.$emit('login.succeed', user);
          this.$parent.close();
          window.location.reload();
        },
        (response) => {
          this.submitting = false;
          const data = response && response.data ? response.data : null;
          if (data && typeof data === 'object') {
            const fieldErrors = {};
            fields.forEach((field) => {
              if (data[field]) {
                fieldErrors[field] = data[field];
              }
            });
            if (Object.keys(fieldErrors).length > 0) {
              this.helper.markFieldsAsDanger(fieldErrors);
              return;
            }
            this.requestError = errorMessage(data.detail)
              || errorMessage(data.non_field_errors);
          }
          this.requestError = this.requestError || this.$t('loginFailedMessage');
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.auth-modal-card {
  --create-modal-width: 560px;
  animation: auth-modal-arrive var(--motion-duration-standard) var(--motion-ease-emphasized) both;
}

.auth-modal-head {
  position: relative;
  overflow: hidden;
}

.auth-modal-head::after {
  content: '';
  position: absolute;
  right: 72px;
  bottom: -54px;
  width: 132px;
  height: 132px;
  border: 1px solid var(--color-accent-border);
  border-radius: 50%;
  opacity: 0.5;
  pointer-events: none;
}

.auth-modal-icon {
  position: relative;
  overflow: hidden;
}

.auth-modal-icon::after {
  content: '';
  position: absolute;
  inset: -45%;
  background: linear-gradient(110deg, transparent 36%, rgba(255, 255, 255, 0.66) 50%, transparent 64%);
  animation: auth-icon-shine 3.8s var(--motion-ease-standard) infinite;
  transform: translateX(-70%) rotate(10deg);
}

.auth-modal-body {
  display: grid;
  grid-template-columns: minmax(128px, 0.72fr) minmax(0, 1.65fr);
  align-items: center;
  gap: var(--space-lg);
  min-height: 286px;
}

.auth-modal-intro {
  position: relative;
  display: grid;
  width: 100%;
  aspect-ratio: 1;
  place-items: center;
  overflow: hidden;
  border: 1px solid var(--color-accent-border);
  border-radius: var(--radius-lg);
  color: var(--color-accent-foreground);
  background:
    radial-gradient(circle at 28% 20%, var(--color-theme-glow-strong), transparent 44%),
    var(--color-accent-soft-gradient);
  box-shadow: inset 0 0 34px var(--color-theme-glow), var(--shadow-xs);
}

.auth-modal-intro > .icon {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 8px 18px var(--color-theme-glow-strong));
  animation: auth-symbol-float 3.4s var(--motion-ease-standard) infinite;
}

.auth-modal-orbit {
  position: absolute;
  border: 1px solid var(--color-accent-border);
  border-radius: 50%;
}

.auth-modal-orbit-one {
  width: 74%;
  height: 74%;
  animation: auth-orbit-spin 9s linear infinite;
}

.auth-modal-orbit-two {
  width: 46%;
  height: 88%;
  opacity: 0.6;
  animation: auth-orbit-spin 7s linear infinite reverse;
}

.auth-modal-spark {
  position: absolute;
  z-index: 1;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-accent-fill);
  box-shadow: 0 0 16px var(--color-theme-glow-strong);
}

.auth-modal-spark-one {
  top: 20%;
  right: 18%;
}

.auth-modal-spark-two {
  bottom: 17%;
  left: 20%;
  animation-delay: -1.2s;
}

.auth-modal-fields {
  min-width: 0;
}

.auth-field + .auth-field {
  margin-top: var(--space-md);
}

.auth-field ::v-deep .label {
  margin-bottom: var(--space-xs);
  color: var(--color-text-strong);
  font-size: 0.82rem;
  font-weight: 900;
}

.auth-field ::v-deep .input {
  height: 46px;
  border-color: var(--color-line-soft);
  border-radius: var(--radius-md);
  color: var(--color-text-strong);
  background: color-mix(in srgb, var(--color-surface-1) 90%, transparent);
  box-shadow: inset 0 1px 0 color-mix(in srgb, var(--color-line-soft) 42%, transparent);
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    border-color var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard),
    background var(--motion-duration-fast) var(--motion-ease-standard);
}

.auth-field ::v-deep .input:hover:not(:disabled) {
  border-color: var(--color-accent-border);
  background: var(--color-surface-1);
}

.auth-field ::v-deep .input:focus {
  border-color: var(--color-accent);
  background: var(--color-surface-1);
  box-shadow: var(--focus-ring), inset 0 1px 0 var(--color-line-soft);
  transform: translateY(-1px);
}

.auth-field ::v-deep .icon {
  color: var(--color-text-muted);
  transition: color var(--motion-duration-fast) var(--motion-ease-standard);
}

.auth-field ::v-deep .control.has-icons-left:focus-within > .icon {
  color: var(--color-accent-foreground);
}

.auth-field ::v-deep .help.is-danger {
  color: color-mix(in srgb, var(--color-accent-strong) 44%, #dc2626);
  font-weight: 750;
}

.auth-request-error {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin: var(--space-md) 0 0;
  padding: var(--space-sm);
  border: 1px solid color-mix(in srgb, var(--color-accent-border) 50%, #dc2626);
  border-radius: var(--radius-sm);
  color: color-mix(in srgb, var(--color-accent-strong) 40%, #dc2626);
  background: color-mix(in srgb, var(--color-accent-soft) 52%, transparent);
  font-size: 0.84rem;
  font-weight: 800;
}

.auth-modal-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  min-width: 126px;
  transition:
    transform var(--motion-duration-fast) var(--motion-ease-standard),
    box-shadow var(--motion-duration-fast) var(--motion-ease-standard),
    filter var(--motion-duration-fast) var(--motion-ease-standard);
}

.auth-modal-submit:hover:not(:disabled) {
  filter: saturate(1.08) brightness(1.03);
  transform: translateY(-2px);
  box-shadow: 0 14px 30px var(--color-theme-glow-strong);
}

.auth-modal-submit:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

@keyframes auth-modal-arrive {
  from {
    opacity: 0;
    transform: translate3d(0, 18px, 0) scale(0.97);
  }

  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
}

@keyframes auth-icon-shine {
  0%, 66% {
    transform: translateX(-75%) rotate(10deg);
  }

  90%, 100% {
    transform: translateX(75%) rotate(10deg);
  }
}

@keyframes auth-symbol-float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }

  50% {
    transform: translateY(-5px) scale(1.035);
  }
}

@keyframes auth-orbit-spin {
  to {
    transform: rotate(360deg);
  }
}

@media screen and (max-width: 640px) {
  .auth-modal-body {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .auth-modal-intro {
    width: 88px;
    margin: 0 auto;
  }
}
</style>
