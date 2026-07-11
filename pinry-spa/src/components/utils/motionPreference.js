const MOTION_STORAGE_KEY = 'pinry.motion.reduce';

function readMotionPreference() {
  try {
    return localStorage.getItem(MOTION_STORAGE_KEY) === 'true';
  } catch (error) {
    return false;
  }
}

function applyMotionPreference(reduceMotion) {
  const reduced = reduceMotion === true;
  document.documentElement.dataset.motion = reduced ? 'reduce' : 'full';
  return reduced;
}

function saveAndApplyMotionPreference(reduceMotion) {
  const reduced = reduceMotion === true;
  try {
    localStorage.setItem(MOTION_STORAGE_KEY, String(reduced));
  } catch (error) {
    // The in-memory preference still applies when storage is unavailable.
  }
  return applyMotionPreference(reduced);
}

function applySavedMotionPreference() {
  return applyMotionPreference(readMotionPreference());
}

function isReducedMotionEnabled() {
  return document.documentElement.dataset.motion === 'reduce';
}

export default {
  applySavedMotionPreference,
  isReducedMotionEnabled,
  readMotionPreference,
  saveAndApplyMotionPreference,
};
