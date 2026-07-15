import {
  getThemePreset,
  gradientThemePresets,
  solidThemePresets,
  themePresets,
} from './gradientThemePresets';

const THEME_STORAGE_KEY = 'pinry.theme';
const accentOptions = themePresets;

function normalizeTheme(theme) {
  const mode = theme && theme.mode === 'dark' ? 'dark' : 'light';
  const accent = theme && getThemePreset(theme.accent)
    ? theme.accent
    : 'elysia';
  return { mode, accent };
}

function readTheme() {
  try {
    return normalizeTheme(JSON.parse(localStorage.getItem(THEME_STORAGE_KEY)));
  } catch (error) {
    return normalizeTheme(null);
  }
}

function writeTheme(theme) {
  const normalized = normalizeTheme(theme);
  localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(normalized));
  return normalized;
}

function applyTheme(theme) {
  const normalized = normalizeTheme(theme);
  if (typeof document === 'undefined') {
    return normalized;
  }
  const preset = getThemePreset(normalized.accent);
  const root = document.documentElement;
  const cssVariables = normalized.mode === 'dark'
    ? preset.cssVariablesDark
    : preset.cssVariables;

  Object.keys(cssVariables).forEach(
    variable => root.style.setProperty(variable, cssVariables[variable]),
  );
  root.dataset.theme = normalized.mode;
  root.dataset.accent = normalized.accent;
  root.dataset.accentKind = preset.kind;
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
  gradientThemePresets,
  readTheme,
  saveAndApplyTheme,
  solidThemePresets,
  themePresets,
};
