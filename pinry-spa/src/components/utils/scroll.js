import utils from './browser';

function getDocumentScrollTop() {
  const doc = document.documentElement;
  return (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
}

function onScroll2Bottom(callback) {
  const windowPosition = getDocumentScrollTop() + window.innerHeight;
  const bottom = utils.getDocumentHeight() - 100;
  if (windowPosition > bottom) {
    callback();
  }
}

function bindScroll2Bottom(callback) {
  const listener = () => {
    onScroll2Bottom(callback);
  };
  window.addEventListener('scroll', listener, { passive: true });
  return () => window.removeEventListener('scroll', listener);
}

function runWithoutSmoothScroll(callback, restoreDelay = 0) {
  const doc = document.documentElement;
  const previousScrollBehavior = doc.style.getPropertyValue('scroll-behavior');
  const previousScrollBehaviorPriority = doc.style.getPropertyPriority('scroll-behavior');
  doc.style.setProperty('scroll-behavior', 'auto', 'important');
  callback();

  window.setTimeout(() => {
    window.requestAnimationFrame(() => {
      if (previousScrollBehavior) {
        doc.style.setProperty(
          'scroll-behavior',
          previousScrollBehavior,
          previousScrollBehaviorPriority,
        );
      } else {
        doc.style.removeProperty('scroll-behavior');
      }
    });
  }, restoreDelay);
}

function restoreScrollPosition(scrollTop) {
  runWithoutSmoothScroll(() => window.scrollTo(0, scrollTop));
}

function preserveModalScrollPosition(shouldRestore = () => true) {
  const scrollTop = getDocumentScrollTop();

  return () => {
    // Buefy restores scrollTop synchronously while closing a `scroll="keep"`
    // modal. Disable the app-wide smooth scrolling before that assignment so
    // the browser cannot animate from the temporary fixed-body position (0).
    runWithoutSmoothScroll(
      () => {
        window.setTimeout(() => {
          if (shouldRestore()) {
            window.scrollTo(0, scrollTop);
          }
        }, 160);
      },
      180,
    );
  };
}

export default {
  bindScroll2Bottom,
  preserveModalScrollPosition,
  restoreScrollPosition,
};
