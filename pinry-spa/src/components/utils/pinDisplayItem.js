import pinHandler from './PinHandler';
import imageVariant from './imageVariant';
import cardAvatarUrl from './avatarVariant';

function escapeMediaUrl(url) {
  if (!url) {
    return null;
  }
  if (/^https?:\/\//i.test(url)) {
    return pinHandler.escapeUrl(url);
  }
  return url;
}

export default function createPinDisplayItem(pin) {
  const item = {};
  const source = pin || {};
  const pinImage = source.image || {};
  const submitter = source.submitter || {};
  let thumbnail = {};

  try {
    thumbnail = pinImage.id
      ? (imageVariant.getCardThumbnail(pinImage) || {})
      : {};
  } catch (error) {
    thumbnail = {};
  }

  const thumbnailWidth = thumbnail.width || pinImage.width || 240;
  const thumbnailHeight = thumbnail.height || pinImage.height || 320;
  item.url = thumbnail.image ? pinHandler.escapeUrl(thumbnail.image) : null;
  item.id = source.id;
  item.image_id = pinImage.id || null;
  item.owner_id = submitter.id || null;
  item.private = source.private;
  item.description = source.description || '';
  item.tags = source.tags || [];
  item.boards = source.boards || [];
  item.author = submitter.username || '';
  item.avatar = cardAvatarUrl(submitter, 30);
  item.large_image_url = pinImage.image ? pinHandler.escapeUrl(pinImage.image) : null;
  item.original_image_url = source.url || item.large_image_url;
  item.motion_photo = pinImage.motion_photo
    ? Object.assign(
      {},
      pinImage.motion_photo,
      { video: escapeMediaUrl(pinImage.motion_photo.video) },
    )
    : null;
  item.referer = source.referer || '';
  item.likes_count = source.likes_count || 0;
  item.viewer_liked = !!source.viewer_liked;
  item.viewed_count = source.viewed_count || 0;
  item.viewer_viewed = !!source.viewer_viewed;
  item.likeBusy = false;
  item.orgianl_width = pinImage.width || thumbnailWidth;
  item.style = {
    aspectRatio: `${thumbnailWidth} / ${thumbnailHeight}`,
  };
  item.imageVisible = false;
  item.class = {
    'has-board': item.boards.length > 0,
    'has-motion-photo': item.motion_photo !== null,
    'is-image-missing': item.url === null,
  };
  return item;
}
