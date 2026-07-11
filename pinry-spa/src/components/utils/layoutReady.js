const layoutObservers = new WeakMap();

function nextFrame(callback) {
  const requestFrame = window.requestAnimationFrame
    || (handler => window.setTimeout(handler, 16));
  requestFrame(callback);
}

function masonryHasLayout(element, itemSelector) {
  const items = Array.from(element.querySelectorAll(itemSelector));
  if (items.length === 0) {
    return true;
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
    layoutObservers.set(element, observer);
    observer.observe(element, {
      attributes: true,
      attributeFilter: ['style'],
      childList: true,
      subtree: true,
    });
    nextFrame(() => checkLayout(element, binding, observer));
  },
  unbind(element) {
    const observer = layoutObservers.get(element);
    if (observer) {
      observer.disconnect();
      layoutObservers.delete(element);
    }
  },
};
