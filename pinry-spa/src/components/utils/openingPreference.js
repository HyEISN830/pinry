const OPENING_STORAGE_KEY = 'pinry.opening.enabled';

let memoryPreference = false;

function readOpeningPreference() {
  try {
    return localStorage.getItem(OPENING_STORAGE_KEY) === 'true';
  } catch (error) {
    return memoryPreference;
  }
}

function applyOpeningPreference(openingEnabled) {
  const enabled = openingEnabled === true;
  memoryPreference = enabled;
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.pageOpening = enabled ? 'enabled' : 'disabled';
  }
  return enabled;
}

function saveAndApplyOpeningPreference(openingEnabled) {
  const enabled = openingEnabled === true;
  try {
    localStorage.setItem(OPENING_STORAGE_KEY, String(enabled));
  } catch (error) {
    // The in-memory preference still applies when storage is unavailable.
  }
  return applyOpeningPreference(enabled);
}

function applySavedOpeningPreference() {
  return applyOpeningPreference(readOpeningPreference());
}

function isOpeningEnabled() {
  if (typeof document !== 'undefined') {
    const value = document.documentElement.dataset.pageOpening;
    if (value) {
      return value === 'enabled';
    }
  }
  return readOpeningPreference();
}

export default {
  applySavedOpeningPreference,
  isOpeningEnabled,
  readOpeningPreference,
  saveAndApplyOpeningPreference,
};
