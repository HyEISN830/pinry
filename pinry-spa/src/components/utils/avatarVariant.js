import { usesMobileMediaProfile } from './responsiveMedia';

const MOBILE_CARD_AVATAR_SIZE = 48;
const MOBILE_PROFILE_AVATAR_SIZE = 96;

function firstAvatarUrl(candidates) {
  return candidates.find(value => typeof value === 'string' && value.trim());
}

function preferredAvatarUrl(user, variants, gravatarSize) {
  const profile = user || {};
  const avatar = profile.avatar || {};

  if (typeof avatar === 'string' && avatar.trim()) {
    return avatar;
  }

  const avatarUrl = firstAvatarUrl(variants.map(variant => avatar[variant]));

  if (avatarUrl) {
    return avatarUrl;
  }

  return `//gravatar.com/avatar/${profile.gravatar || ''}?s=${gravatarSize}`;
}

function cardAvatarUrl(user, desktopGravatarSize = 30) {
  const mobileProfile = usesMobileMediaProfile();
  const gravatarSize = mobileProfile
    ? MOBILE_CARD_AVATAR_SIZE
    : desktopGravatarSize;
  const variants = mobileProfile
    ? ['medium', 'large', 'small', 'original']
    : ['small', 'medium', 'large', 'original'];
  return preferredAvatarUrl(user, variants, gravatarSize);
}

function profileCardAvatarUrl(user) {
  const mobileProfile = usesMobileMediaProfile();
  const variants = mobileProfile
    ? ['large', 'medium', 'small', 'original']
    : ['medium', 'large', 'small', 'original'];
  const gravatarSize = mobileProfile ? MOBILE_PROFILE_AVATAR_SIZE : 72;
  return preferredAvatarUrl(user, variants, gravatarSize);
}

export {
  profileCardAvatarUrl,
};

export default cardAvatarUrl;
