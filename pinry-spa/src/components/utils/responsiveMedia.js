const MOBILE_MEDIA_MAX_WIDTH = 860;
const MOBILE_MEDIA_QUERY = `(max-width: ${MOBILE_MEDIA_MAX_WIDTH}px), (hover: none) and (pointer: coarse)`;

function usesMobileMediaProfile() {
  if (typeof window === 'undefined') {
    return false;
  }
  if (typeof window.matchMedia === 'function') {
    return window.matchMedia(MOBILE_MEDIA_QUERY).matches;
  }
  const documentWidth = typeof document !== 'undefined' && document.documentElement
    ? document.documentElement.clientWidth
    : 0;
  const viewportWidth = window.innerWidth || documentWidth || 0;
  return viewportWidth > 0 && viewportWidth <= MOBILE_MEDIA_MAX_WIDTH;
}

function responsiveBatchSize(desktopSize) {
  const normalizedSize = Number.isFinite(desktopSize)
    ? Math.max(1, Math.floor(desktopSize))
    : 1;
  return usesMobileMediaProfile()
    ? Math.max(1, Math.ceil(normalizedSize / 2))
    : normalizedSize;
}

export {
  MOBILE_MEDIA_QUERY,
  responsiveBatchSize,
  usesMobileMediaProfile,
};
