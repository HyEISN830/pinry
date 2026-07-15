/*
 * The theme catalog is the single source of truth for both the legacy solid
 * accents and the new gradient palettes. theme.js turns a preset into the
 * CSS variables consumed by the UI.
 */

function rgba(hex, alpha) {
  const value = hex.slice(1);
  const red = parseInt(value.slice(0, 2), 16);
  const green = parseInt(value.slice(2, 4), 16);
  const blue = parseInt(value.slice(4, 6), 16);
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

function buildGradient(from, to) {
  return {
    diagonal: `linear-gradient(135deg, ${from} 0%, ${to} 100%)`,
    horizontal: `linear-gradient(90deg, ${from} 0%, ${to} 100%)`,
    vertical: `linear-gradient(180deg, ${from} 0%, ${to} 100%)`,
  };
}

function buildCssVariables(palette, mode) {
  const isDark = mode === 'dark';
  const gradient = buildGradient(palette.from, palette.to);
  const softAlpha = isDark ? 0.2 : 0.16;
  const surfaceAlpha = isDark ? 0.17 : 0.12;
  const glowAlpha = isDark ? 0.18 : 0.24;
  const strongGlowAlpha = isDark ? 0.28 : 0.36;
  const fill = palette.kind === 'gradient' ? gradient.diagonal : palette.to;
  const fillHover = palette.kind === 'gradient'
    ? `linear-gradient(135deg, ${palette.to} 0%, ${palette.from} 100%)`
    : palette.from;

  return {
    '--accent': palette.from,
    '--accent-strong': palette.to,
    '--accent-text': palette.accentText,
    '--accent-text-shadow': palette.accentText === '#FFFFFF'
      ? '0 1px 2px rgba(15, 23, 42, 0.24)'
      : 'none',
    '--accent-fill': fill,
    '--accent-fill-hover': fillHover,
    '--accent-gradient': gradient.vertical,
    '--accent-gradient-horizontal': gradient.horizontal,
    '--accent-gradient-vertical': gradient.vertical,
    '--accent-gradient-diagonal': gradient.diagonal,
    '--accent-progress': gradient.horizontal,
    '--accent-swatch': palette.kind === 'gradient' ? gradient.horizontal : palette.from,
    '--accent-soft': rgba(palette.from, softAlpha),
    '--accent-soft-gradient': `linear-gradient(135deg, ${rgba(palette.from, softAlpha + 0.04)} 0%, ${rgba(palette.to, softAlpha)} 100%)`,
    '--surface-accent': rgba(palette.from, surfaceAlpha),
    '--accent-border': rgba(palette.from, isDark ? 0.42 : 0.36),
    '--accent-shadow': `0 16px 38px ${rgba(palette.to, isDark ? 0.26 : 0.2)}`,
    '--theme-glow': rgba(palette.from, glowAlpha),
    '--theme-glow-strong': rgba(palette.to, strongGlowAlpha),
    '--theme-glow-start': rgba(palette.from, strongGlowAlpha),
    '--theme-glow-end': rgba(palette.to, glowAlpha),
    '--theme-backdrop': `linear-gradient(150deg, ${rgba(palette.from, isDark ? 0.16 : 0.14)} 0%, ${rgba(palette.to, isDark ? 0.12 : 0.1)} 48%, transparent 78%)`,
  };
}

const solidThemeDefinitions = [
  {
    value: 'elysia',
    label: 'Elysia',
    labelEn: 'Elysia',
    labelFr: 'Elysia',
    from: '#EF7CBA',
    to: '#DB4E9C',
    accentText: '#FFFFFF',
  },
  {
    value: 'eden',
    label: 'Eden',
    labelEn: 'Eden',
    labelFr: 'Eden',
    from: '#D5A344',
    to: '#B88416',
    accentText: '#FFFFFF',
  },
  {
    value: 'mobius',
    label: 'Mobius',
    labelEn: 'Mobius',
    labelFr: 'Mobius',
    from: '#32B47B',
    to: '#168A5A',
    accentText: '#FFFFFF',
  },
  {
    value: 'kevin',
    label: 'Kevin',
    labelEn: 'Kevin',
    labelFr: 'Kevin',
    from: '#6AB7FF',
    to: '#2788DD',
    accentText: '#FFFFFF',
  },
  {
    value: 'griseo',
    label: 'Griseo',
    labelEn: 'Griseo',
    labelFr: 'Griseo',
    from: '#7C8CFF',
    to: '#5366E6',
    accentText: '#FFFFFF',
  },
  {
    value: 'pardofelis',
    label: 'Pardofelis',
    labelEn: 'Pardofelis',
    labelFr: 'Pardofelis',
    from: '#F2A65E',
    to: '#DC7F24',
    accentText: '#FFFFFF',
  },
];

const gradientThemeDefinitions = [
  {
    value: 'fresh-healing',
    label: '清新治愈',
    labelEn: 'Fresh healing',
    labelFr: 'Fraicheur apaisante',
    from: '#80E484',
    to: '#2B693F',
    accentText: '#FFFFFF',
  },
  {
    value: 'sweet-soft',
    label: '甜系柔和',
    labelEn: 'Sweet soft',
    labelFr: 'Douceur sucree',
    from: '#E4F6AA',
    to: '#FF81A6',
    accentText: '#3D1325',
  },
  {
    value: 'muted-atmosphere',
    label: '小众氛围',
    labelEn: 'Muted atmosphere',
    labelFr: 'Atmosphere feutree',
    from: '#B8A9C6',
    to: '#2F2B55',
    accentText: '#FFFFFF',
  },
  {
    value: 'warm-vitality',
    label: '元气暖调',
    labelEn: 'Warm vitality',
    labelFr: 'Vitalite chaleureuse',
    from: '#FBE693',
    to: '#FE8E28',
    accentText: '#3D2100',
  },
  {
    value: 'cool-refined',
    label: '清冷高级',
    labelEn: 'Cool refined',
    labelFr: 'Fraicheur raffinee',
    from: '#C9DDC4',
    to: '#1F5CAC',
    accentText: '#FFFFFF',
  },
  {
    value: 'gentle-clean',
    label: '温柔干净',
    labelEn: 'Gentle clean',
    labelFr: 'Douceur lumineuse',
    from: '#F4DC84',
    to: '#79BEDF',
    accentText: '#17324D',
  },
];

function createPreset(definition, kind) {
  const palette = Object.assign({ kind }, definition);
  const gradient = buildGradient(palette.from, palette.to);
  return Object.assign(palette, {
    cssVariables: buildCssVariables(palette, 'light'),
    cssVariablesDark: buildCssVariables(palette, 'dark'),
    gradient: {
      angle: '180deg',
      css: gradient.vertical,
      diagonalCss: gradient.diagonal,
      horizontalCss: gradient.horizontal,
      stops: [palette.from, palette.to],
      verticalCss: gradient.vertical,
    },
    preview: palette.kind === 'gradient' ? gradient.horizontal : palette.from,
  });
}

const solidThemePresets = solidThemeDefinitions.map(
  definition => createPreset(definition, 'solid'),
);
const gradientThemePresets = gradientThemeDefinitions.map(
  definition => createPreset(definition, 'gradient'),
);
const themePresets = solidThemePresets.concat(gradientThemePresets);

function getThemePreset(value) {
  return themePresets.find(palette => palette.value === value);
}

function getGradientThemePreset(value) {
  return gradientThemePresets.find(palette => palette.value === value);
}

export {
  getGradientThemePreset,
  getThemePreset,
  gradientThemePresets,
  solidThemeDefinitions,
  solidThemePresets,
  themePresets,
};
export default themePresets;
