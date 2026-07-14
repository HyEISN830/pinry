const TOOLTIP_GAP = 10;
const VIEWPORT_PADDING = 12;
const tooltipStates = new WeakMap();
let tooltipSequence = 0;

function tooltipText(element) {
  return (
    element.getAttribute('data-source-tip')
    || element.getAttribute('data-tooltip')
    || element.getAttribute('aria-label')
    || ''
  ).trim();
}

function removeTooltip(element) {
  const state = tooltipStates.get(element);
  if (!state) return;

  if (state.frame) {
    window.cancelAnimationFrame(state.frame);
    state.frame = null;
  }
  if (state.tooltip && state.tooltip.parentNode) {
    state.tooltip.parentNode.removeChild(state.tooltip);
  }
  state.tooltip = null;

  if (state.previousDescribedBy) {
    element.setAttribute('aria-describedby', state.previousDescribedBy);
  } else {
    element.removeAttribute('aria-describedby');
  }
}

function positionTooltip(element) {
  const state = tooltipStates.get(element);
  if (!state || !state.tooltip || !document.body.contains(element)) {
    removeTooltip(element);
    return;
  }

  const triggerRect = element.getBoundingClientRect();
  const tooltipRect = state.tooltip.getBoundingClientRect();
  const viewportWidth = document.documentElement.clientWidth;
  const viewportHeight = document.documentElement.clientHeight;
  const preferredLeft = triggerRect.left + ((triggerRect.width - tooltipRect.width) / 2);
  const maxLeft = Math.max(VIEWPORT_PADDING, viewportWidth - tooltipRect.width - VIEWPORT_PADDING);
  const left = Math.min(Math.max(preferredLeft, VIEWPORT_PADDING), maxLeft);
  const showAbove = triggerRect.top >= tooltipRect.height + TOOLTIP_GAP + VIEWPORT_PADDING;
  const preferredTop = showAbove
    ? triggerRect.top - tooltipRect.height - TOOLTIP_GAP
    : triggerRect.bottom + TOOLTIP_GAP;
  const maxTop = Math.max(VIEWPORT_PADDING, viewportHeight - tooltipRect.height - VIEWPORT_PADDING);
  const top = Math.min(Math.max(preferredTop, VIEWPORT_PADDING), maxTop);

  state.tooltip.dataset.placement = showAbove ? 'top' : 'bottom';
  state.tooltip.style.left = `${Math.round(left)}px`;
  state.tooltip.style.top = `${Math.round(top)}px`;
}

function showTooltip(element) {
  const text = tooltipText(element);
  const state = tooltipStates.get(element);
  if (!state || !text) return;

  removeTooltip(element);

  const tooltip = document.createElement('div');
  tooltip.id = `content-source-tooltip-${tooltipSequence += 1}`;
  tooltip.className = 'content-source-tooltip';
  tooltip.setAttribute('role', 'tooltip');
  tooltip.textContent = text;
  document.body.appendChild(tooltip);
  state.tooltip = tooltip;
  element.setAttribute('aria-describedby', tooltip.id);
  positionTooltip(element);

  state.frame = window.requestAnimationFrame(() => {
    state.frame = null;
    positionTooltip(element);
  });
}

function bind(element) {
  const previousDescribedBy = element.getAttribute('aria-describedby');
  const show = () => showTooltip(element);
  const hide = () => removeTooltip(element);
  const handleKeydown = (event) => {
    if (event.key === 'Escape') hide();
  };
  const reposition = () => {
    const state = tooltipStates.get(element);
    if (!state || !state.tooltip || state.frame) return;
    state.frame = window.requestAnimationFrame(() => {
      state.frame = null;
      positionTooltip(element);
    });
  };

  tooltipStates.set(element, {
    frame: null,
    handleKeydown,
    hide,
    previousDescribedBy,
    reposition,
    show,
    tooltip: null,
  });

  element.addEventListener('mouseenter', show);
  element.addEventListener('mouseleave', hide);
  element.addEventListener('focus', show);
  element.addEventListener('blur', hide);
  element.addEventListener('keydown', handleKeydown);
  window.addEventListener('scroll', hide, true);
  window.addEventListener('resize', reposition);
}

function unbind(element) {
  const state = tooltipStates.get(element);
  if (!state) return;

  element.removeEventListener('mouseenter', state.show);
  element.removeEventListener('mouseleave', state.hide);
  element.removeEventListener('focus', state.show);
  element.removeEventListener('blur', state.hide);
  element.removeEventListener('keydown', state.handleKeydown);
  window.removeEventListener('scroll', state.hide, true);
  window.removeEventListener('resize', state.reposition);
  removeTooltip(element);
  tooltipStates.delete(element);
}

export default {
  bind,
  unbind,
};
