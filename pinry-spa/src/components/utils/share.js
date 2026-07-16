function buildRouteUrl(router, route) {
  const resolved = router.resolve(route);
  return new URL(resolved.href, window.location.origin).toString();
}

function copyWithSelection(value) {
  return new Promise((resolve, reject) => {
    const textarea = document.createElement('textarea');
    textarea.value = value;
    textarea.setAttribute('readonly', 'readonly');
    textarea.style.position = 'fixed';
    textarea.style.top = '-9999px';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);
    const copied = document.execCommand && document.execCommand('copy');
    document.body.removeChild(textarea);
    if (copied) {
      resolve();
      return;
    }
    reject(new Error('Unable to copy share URL'));
  });
}

function copyText(value) {
  return copyWithSelection(value).catch(
    () => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(value);
      }
      return Promise.reject(new Error('Unable to copy share URL'));
    },
  );
}

function shareRoute(vm, route) {
  const url = buildRouteUrl(vm.$router, route);
  return copyText(url).then(
    () => {
      vm.$buefy.toast.open({
        message: vm.$t('shareLinkCopied'),
        type: 'is-success',
      });
      return { method: 'copy', url };
    },
    () => {
      vm.$buefy.toast.open({
        message: vm.$t('shareLinkFailed'),
        type: 'is-danger',
      });
      return { failed: true, url };
    },
  );
}

export default {
  buildRouteUrl,
  shareRoute,
};
