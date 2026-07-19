import { usesMobileMediaProfile } from './responsiveMedia';

function availableVariant(variant) {
  return variant && variant.image ? variant : null;
}

function getCardThumbnail(image) {
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
  return usesMobileMediaProfile()
    ? (standard || thumbnail)
    : (thumbnail || standard);
}

export default {
  getCardThumbnail,
};
