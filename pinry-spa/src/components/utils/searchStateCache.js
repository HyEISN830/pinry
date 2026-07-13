const SEARCH_CACHE_TTL_MS = 20 * 60 * 1000;

let cachedSearchState = null;

function cloneState(state) {
  try {
    return JSON.parse(JSON.stringify(state));
  } catch (error) {
    return null;
  }
}

function saveSearchState(state) {
  const snapshot = cloneState(state);
  if (!snapshot) {
    return;
  }
  cachedSearchState = {
    expiresAt: Date.now() + SEARCH_CACHE_TTL_MS,
    state: snapshot,
  };
}

function loadSearchState() {
  if (!cachedSearchState || cachedSearchState.expiresAt <= Date.now()) {
    cachedSearchState = null;
    return null;
  }
  return cloneState(cachedSearchState.state);
}

export {
  loadSearchState,
  saveSearchState,
};
