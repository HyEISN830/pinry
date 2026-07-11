const layoutObservers = new WeakMap();

function nextFrame(callback) {
  const requestFrame = window.requestAnimationFrame
    || (handler => window.setTimeout(handler, 16));
  requestFrame(callback);
}

function masonryHasLayout(element, itemSelector) {
  const items = Array.from(element.querySelectorAll(itemSelector));
  if (items.length === 0) {
    return false;
  }
  return Boolean(element.style.height)
    && items.every(item => item.style.position === 'absolute');
}

function markReady(element, observer) {
  if (element.classList.contains('masonry-layout-ready')) {
    return;
  }
  element.classList.remove('masonry-layout-pending');
  element.classList.add('masonry-layout-ready');
  if (observer) {
    observer.disconnect();
  }
}

function checkLayout(element, binding, observer) {
  const itemSelector = binding.value && binding.value.itemSelector;
  const computedDisplay = window.getComputedStyle(element).display;
  if (computedDisplay === 'grid') {
    nextFrame(() => markReady(element, observer));
    return;
  }
  if (masonryHasLayout(element, itemSelector || '.grid-item')) {
    markReady(element, observer);
  }
}

export default {
  bind(element) {
    // Hide before insertion so the browser can never paint the unpositioned
    // one-column fallback while Masonry is mounting.
    element.classList.add('masonry-layout-pending');
  },
  inserted(element, binding) {
    const observer = new MutationObserver(() => {
      checkLayout(element, binding, observer);
    });
    // Never leave real content permanently hidden if Masonry fails before it
    // writes its inline geometry (for example, after a sibling render error).
    const failOpenTimer = window.setTimeout(() => {
      markReady(element, observer);
    }, 1500);
    layoutObservers.set(element, { observer, failOpenTimer });
    observer.observe(element, {
      attributes: true,
      attributeFilter: ['style'],
      childList: true,
      subtree: true,
    });
    nextFrame(() => checkLayout(element, binding, observer));
  },
  unbind(element) {
    const state = layoutObservers.get(element);
    if (state) {
      state.observer.disconnect();
      window.clearTimeout(state.failOpenTimer);
      layoutObservers.delete(element);
    }
  },
};
