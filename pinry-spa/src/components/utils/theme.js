const THEME_STORAGE_KEY = 'pinry.theme';

const accentOptions = [
  { value: 'elysia', label: 'Elysia' },
  { value: 'eden', label: 'Eden' },
  { value: 'mobius', label: 'Mobius' },
  { value: 'kevin', label: 'Kevin' },
  { value: 'griseo', label: 'Griseo' },
  { value: 'pardofelis', label: 'Pardofelis' },
];

function normalizeTheme(theme) {
  const mode = theme && theme.mode === 'dark' ? 'dark' : 'light';
  const accent = theme && accentOptions.some(option => option.value === theme.accent)
    ? theme.accent
    : 'elysia';
  return { mode, accent };
}

function readTheme() {
  try {
    return normalizeTheme(JSON.parse(localStorage.getItem(THEME_STORAGE_KEY)));
  } catch (error) {
    return normalizeTheme(error && null);
  }
}

function writeTheme(theme) {
  const normalized = normalizeTheme(theme);
  localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(normalized));
  return normalized;
}

function applyTheme(theme) {
  const normalized = normalizeTheme(theme);
  document.documentElement.dataset.theme = normalized.mode;
  document.documentElement.dataset.accent = normalized.accent;
  return normalized;
}

function applySavedTheme() {
  return applyTheme(readTheme());
}

function saveAndApplyTheme(theme) {
  return applyTheme(writeTheme(theme));
}

export default {
  accentOptions,
  applySavedTheme,
  readTheme,
  saveAndApplyTheme,
};
