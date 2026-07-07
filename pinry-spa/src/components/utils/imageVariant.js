function getCardThumbnail(image) {
  if (image && image.animated_thumbnail && image.animated_thumbnail.image) {
    return image.animated_thumbnail;
  }
  return image ? image.thumbnail : null;
}

export default {
  getCardThumbnail,
};
