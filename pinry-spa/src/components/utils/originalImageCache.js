const MAX_CACHED_IMAGES = 120;
const MAX_CACHED_IMAGE_BYTES = 2 * 1024 * 1024 * 1024;
const cachedImages = new Map();
let cachedImageBytes = 0;

function getCachedImage(imageId) {
  const cached = cachedImages.get(imageId);
  if (!cached) {
    return null;
  }
  cachedImages.delete(imageId);
  cachedImages.set(imageId, cached);
  return cached;
}

function cacheImage(imageId, blob) {
  if (blob.size > MAX_CACHED_IMAGE_BYTES) {
    return null;
  }
  const existing = cachedImages.get(imageId);
  if (existing) {
    cachedImageBytes -= existing.size;
    URL.revokeObjectURL(existing.objectUrl);
    cachedImages.delete(imageId);
  }
  const cached = {
    blob,
    objectUrl: URL.createObjectURL(blob),
    size: blob.size,
  };
  cachedImages.set(imageId, cached);
  cachedImageBytes += cached.size;
  while (
    cachedImages.size > MAX_CACHED_IMAGES
    || cachedImageBytes > MAX_CACHED_IMAGE_BYTES
  ) {
    const oldestKey = cachedImages.keys().next().value;
    const oldest = cachedImages.get(oldestKey);
    cachedImageBytes -= oldest.size;
    URL.revokeObjectURL(oldest.objectUrl);
    cachedImages.delete(oldestKey);
  }
  return cached;
}

export {
  cacheImage,
  getCachedImage,
};
