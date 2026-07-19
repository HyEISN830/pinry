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

function notifyCopyResult(vm, succeeded) {
  vm.$buefy.toast.open({
    message: vm.$t(succeeded ? 'shareLinkCopied' : 'shareLinkFailed'),
    type: succeeded ? 'is-success' : 'is-danger',
  });
}

function copyRouteUrl(vm, url) {
  return copyText(url).then(
    () => {
      notifyCopyResult(vm, true);
      return { method: 'copy', url };
    },
    () => {
      notifyCopyResult(vm, false);
      return { failed: true, url };
    },
  );
}

function shareRoute(vm, route, options = {}) {
  const url = buildRouteUrl(vm.$router, route);
  if (!navigator.share) {
    return copyRouteUrl(vm, url);
  }
  const payload = { url };
  if (options.title) payload.title = options.title;
  if (options.text) payload.text = options.text;
  let nativeShare;
  try {
    nativeShare = navigator.share(payload);
  } catch {
    return copyRouteUrl(vm, url);
  }
  return Promise.resolve(nativeShare).then(
    () => ({ method: 'native', url }),
    (error) => {
      if (error && error.name === 'AbortError') {
        return { cancelled: true, url };
      }
      return copyRouteUrl(vm, url);
    },
  );
}

export default {
  buildRouteUrl,
  shareRoute,
};
