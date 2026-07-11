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
  window.addEventListener(
    'scroll',
    () => {
      onScroll2Bottom(callback);
    },
  );
}

function preserveModalScrollPosition(shouldRestore = () => true) {
  const scrollTop = getDocumentScrollTop();
  const doc = document.documentElement;
  const previousScrollBehavior = doc.style.getPropertyValue('scroll-behavior');
  const previousScrollBehaviorPriority = doc.style.getPropertyPriority('scroll-behavior');

  return () => {
    // Buefy restores scrollTop synchronously while closing a `scroll="keep"`
    // modal. Disable the app-wide smooth scrolling before that assignment so
    // the browser cannot animate from the temporary fixed-body position (0).
    doc.style.setProperty('scroll-behavior', 'auto', 'important');

    window.setTimeout(() => {
      if (shouldRestore()) {
        window.scrollTo(0, scrollTop);
      }

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
    }, 160);
  };
}

export default {
  bindScroll2Bottom,
  preserveModalScrollPosition,
};
