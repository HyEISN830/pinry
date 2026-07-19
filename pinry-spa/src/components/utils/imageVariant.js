function availableVariant(variant) {
  return variant && variant.image ? variant : null;
}

function getCardThumbnail(image) {
  if (!image) {
    return null;
  }
  // Preserve animated cards.  Static cards use the same 600px derivative on
  // every viewport so a desktop card never falls back to the visibly soft
  // 240px thumbnail while the mobile profile is loading.
  const animated = availableVariant(image.animated_thumbnail);
  if (animated) {
    return animated;
  }
  const standard = availableVariant(image.standard);
  const thumbnail = availableVariant(image.thumbnail);
  return standard || thumbnail;
}

export default {
  getCardThumbnail,
};
