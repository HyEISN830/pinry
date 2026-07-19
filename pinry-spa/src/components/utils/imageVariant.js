import { usesMobileMediaProfile } from './responsiveMedia';

const DESKTOP_HIGH_DENSITY_RATIO = 1.5;
const TALL_IMAGE_DETAIL_RATIO = 1.75;

function availableVariant(variant) {
  return variant && variant.image ? variant : null;
}

function positiveNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : 0;
}

function imageDimensions(image, standard, thumbnail) {
  const fallback = standard || thumbnail || {};
  return {
    height: positiveNumber(image.height) || positiveNumber(fallback.height),
    width: positiveNumber(image.width) || positiveNumber(fallback.width),
  };
}

function usesHighDensityDisplay() {
  if (typeof window === 'undefined') {
    return false;
  }
  return positiveNumber(window.devicePixelRatio) >= DESKTOP_HIGH_DENSITY_RATIO;
}

function isTallDetailImage(image, standard, thumbnail) {
  const { height, width } = imageDimensions(image, standard, thumbnail);
  return width > 0 && (height / width) >= TALL_IMAGE_DETAIL_RATIO;
}

function getCardThumbnail(image, options = {}) {
  if (!image) {
    return null;
  }
  // Preserve animated cards; static mobile cards can use the existing 600px
  // standard derivative instead of stretching the 240px thumbnail.
  const animated = availableVariant(image.animated_thumbnail);
  if (animated) {
    return animated;
  }
  const standard = availableVariant(image.standard);
  const thumbnail = availableVariant(image.thumbnail);
  const preferDesktopDetail = usesHighDensityDisplay()
    || (options.preferTallDetail && isTallDetailImage(image, standard, thumbnail));
  return usesMobileMediaProfile() || preferDesktopDetail
    ? (standard || thumbnail)
    : (thumbnail || standard);
}

export default {
  getCardThumbnail,
};
