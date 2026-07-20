import { usesMobileMediaProfile } from './responsiveMedia';

function availableVariant(variant) {
  return variant && variant.image ? variant : null;
}

function getCardThumbnail(image) {
  if (!image) {
    return null;
  }
  // Preserve animated cards. Mobile cards retain the sharper 600px derivative,
  // while desktop cards use the 480px medium tier sized for a 240px card at 2x.
  const animated = availableVariant(image.animated_thumbnail);
  if (animated) {
    return animated;
  }
  const standard = availableVariant(image.standard);
  const medium = availableVariant(image.medium);
  const thumbnail = availableVariant(image.thumbnail);
  return usesMobileMediaProfile()
    ? (standard || medium || thumbnail)
    : (medium || standard || thumbnail);
}

export default {
  getCardThumbnail,
};
