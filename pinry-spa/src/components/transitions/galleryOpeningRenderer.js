const COMET_DELAY = 80;
const COMET_DURATION = 1520;
const MOVEMENT_START = 0.08;
const MOVEMENT_END = 0.82;
const MAX_PIXEL_RATIO = 2;
const MAX_BACKING_PIXELS = 4147200;
const FRAME_PIXEL_THRESHOLD = 3000000;
const FRAME_INTERVAL = 1000 / 60;
const FRAME_EARLY_TOLERANCE = 1;
const OFFSCREEN_REVEAL_PIXEL_RATIO = 1.75;
const MAX_PARTICLE_DELTA = 120;
const MAX_TRAIL_CATCHUP = 120;
const TRAIL_LIFETIME = 1120;
const TRAIL_SAMPLE_INTERVAL = 16;
const AFTERGLOW_ENTRY_DURATION = 90;
const AFTERGLOW_LINGER_DURATION = 270;
const VEIL_REVEAL_START = 260;
const VEIL_REVEAL_END = 1300;
const VEIL_FADE_START = 1180;
const VEIL_FADE_END = 1650;
const PARTICLE_DISSIPATION_START = 0.38;
const PARTICLE_DISSIPATION_END = 0.94;
const WHITE = [255, 255, 255];
const PEARL_WHITE = [255, 250, 253];
const PEARL_COOL = [198, 226, 255];
const PEARL_WARM = [255, 207, 237];
const DEEP_SPACE_TOP = [5, 7, 20];
const DEEP_SPACE_MIDDLE = [11, 9, 28];
const DEEP_SPACE_BOTTOM = [4, 7, 19];
const DEEP_SPACE_EDGE = [2, 3, 10];
const NEBULA_BLUE = [77, 118, 186];
const NEBULA_VIOLET = [121, 76, 176];
const DISTANT_STAR_COOL = [184, 218, 255];
const DISTANT_STAR_WARM = [255, 220, 241];
const AIRFLOW_LANES = [
  {
    alpha: 0.19,
    dash: [],
    lead: 54,
    offset: 18,
    phase: 0,
    spread: 10,
    wake: 80,
    width: 0.9,
  },
  {
    alpha: 0.14,
    dash: [32, 24],
    lead: 68,
    offset: 30,
    phase: 11,
    spread: 14,
    wake: 108,
    width: 0.78,
  },
  {
    alpha: 0.1,
    dash: [20, 31],
    lead: 82,
    offset: 43,
    phase: 23,
    spread: 17,
    wake: 134,
    width: 0.68,
  },
];

function clamp(value, minimum = 0, maximum = 1) {
  return Math.min(maximum, Math.max(minimum, value));
}

function smoothstep(start, end, value) {
  const progress = clamp((value - start) / (end - start));
  return progress * progress * (3 - (2 * progress));
}

function pulseAround(value, center, radius) {
  return 1 - smoothstep(0, radius, Math.abs(value - center));
}

function seededUnit(index, salt) {
  const value = Math.sin(((index + 1) * 12.9898) + (salt * 78.233)) * 43758.5453;
  return value - Math.floor(value);
}

function seededSigned(index, salt) {
  return (seededUnit(index, salt) * 2) - 1;
}

function parseHexColor(value) {
  const hex = value.replace('#', '').trim();
  let color = null;
  if (hex.length === 3) {
    color = hex
      .split('')
      .map(character => Number.parseInt(`${character}${character}`, 16));
  } else if (hex.length >= 6) {
    color = [
      Number.parseInt(hex.slice(0, 2), 16),
      Number.parseInt(hex.slice(2, 4), 16),
      Number.parseInt(hex.slice(4, 6), 16),
    ];
  }
  return color && color.every(channel => Number.isFinite(channel)) ? color : null;
}

function parseCssColor(value, fallback) {
  const normalized = (value || '').trim();
  if (normalized.startsWith('#')) {
    return parseHexColor(normalized) || fallback;
  }
  const match = normalized.match(/rgba?\(([^)]+)\)/i);
  if (match) {
    const [red, green, blue] = match[1]
      .split(/[,\s/]+/)
      .filter(Boolean)
      .slice(0, 3)
      .map(channel => Number.parseFloat(channel.trim()));
    if ([red, green, blue].every(channel => Number.isFinite(channel))) {
      return [red, green, blue];
    }
  }
  return fallback;
}

function mixColor(start, end, progress) {
  return start.map(
    (channel, index) => Math.round(channel + ((end[index] - channel) * progress)),
  );
}

function rgba(color, alpha) {
  const [red, green, blue] = color;
  return `rgba(${red}, ${green}, ${blue}, ${clamp(alpha)})`;
}

function getThemeColors() {
  const root = document.documentElement;
  const style = window.getComputedStyle(root);
  const accent = parseCssColor(style.getPropertyValue('--color-accent'), [239, 124, 186]);
  const accentStrong = parseCssColor(
    style.getPropertyValue('--color-accent-strong'),
    accent,
  );
  const isGradient = root.dataset.accentKind === 'gradient';
  const end = isGradient ? accentStrong : accent;
  return {
    end,
    isGradient,
    // Keep the reveal rim luminous and slightly pearlescent while allowing
    // the active accent to tint it.  Gradient themes get a little more tint
    // so both ends remain perceptible without introducing neon saturation.
    pearlEnd: mixColor(PEARL_WARM, end, isGradient ? 0.24 : 0.18),
    pearlStart: mixColor(PEARL_COOL, accent, isGradient ? 0.24 : 0.18),
    start: accent,
  };
}

function getPixelRatio(width, height) {
  const deviceRatio = Math.min(MAX_PIXEL_RATIO, window.devicePixelRatio || 1);
  const areaRatio = Math.sqrt(MAX_BACKING_PIXELS / Math.max(1, width * height));
  return Math.min(deviceRatio, areaRatio);
}

function createGeometry(width, height) {
  const isPortrait = height > width;
  const angle = (isPortrait ? 41 : 14) * (Math.PI / 180);
  const direction = {
    x: Math.cos(angle),
    y: Math.sin(angle),
  };
  const normal = {
    x: -direction.y,
    y: direction.x,
  };
  const travelRadius = Math.max(width, height) * 0.72;
  return {
    angle,
    afterglowBudget: isPortrait || width < 760 ? 5 : 10,
    center: {
      x: width * 0.5,
      y: height * 0.4,
    },
    direction,
    isPortrait,
    normal,
    particleBudget: isPortrait || width < 760 ? 32 : 64,
    travelRadius,
    travelSpeed: (travelRadius * 2) / (COMET_DURATION * (MOVEMENT_END - MOVEMENT_START)),
  };
}

function getMovementProgress(localProgress) {
  if (localProgress <= MOVEMENT_START) {
    return 0;
  }
  if (localProgress >= MOVEMENT_END) {
    return 1;
  }
  return (localProgress - MOVEMENT_START) / (MOVEMENT_END - MOVEMENT_START);
}

export default class GalleryOpeningRenderer {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.context = canvas.getContext('2d');
    this.duration = options.duration || 1900;
    this.frameId = null;
    this.geometry = null;
    this.height = 0;
    this.lastFrameTime = null;
    this.lastDrawTime = null;
    this.nextDrawTime = null;
    this.lastTrailTime = -Infinity;
    this.afterglowMotes = [];
    this.particles = [];
    this.pixelRatio = 1;
    this.frameInterval = 0;
    this.resizePending = false;
    this.spawnAccumulator = 0;
    this.spawnedParticles = 0;
    this.startTime = null;
    this.theme = getThemeColors();
    this.trail = [];
    this.veilCanvas = null;
    this.veilContext = null;
    this.veilFrameCanvas = null;
    this.veilFrameContext = null;
    this.width = 0;
    this.handleResize = this.handleResize.bind(this);
    this.renderFrame = this.renderFrame.bind(this);
    this.scheduleResize = this.scheduleResize.bind(this);
  }

  start() {
    if (!this.context) {
      return;
    }
    this.stop();
    this.theme = getThemeColors();
    this.handleResize();
    window.addEventListener('resize', this.scheduleResize, { passive: true });
    this.startTime = window.performance.now();
    this.lastFrameTime = this.startTime;
    this.lastDrawTime = this.startTime;
    this.nextDrawTime = this.frameInterval > 0
      ? this.startTime + this.frameInterval
      : null;
    this.draw(this.getCometState(0), 0);
    this.frameId = window.requestAnimationFrame(this.renderFrame);
  }

  stop() {
    if (this.frameId !== null) {
      window.cancelAnimationFrame(this.frameId);
      this.frameId = null;
    }
    window.removeEventListener('resize', this.scheduleResize);
    this.resizePending = false;
    this.startTime = null;
    this.lastFrameTime = null;
    this.lastDrawTime = null;
    this.nextDrawTime = null;
    this.lastTrailTime = -Infinity;
    this.spawnAccumulator = 0;
    this.spawnedParticles = 0;
    this.afterglowMotes = [];
    this.particles = [];
    this.trail = [];
    if (this.context && this.width && this.height) {
      this.context.clearRect(0, 0, this.width, this.height);
    }
    if (this.veilCanvas) {
      this.veilCanvas.width = 1;
      this.veilCanvas.height = 1;
    }
    if (this.veilFrameCanvas) {
      this.veilFrameCanvas.width = 1;
      this.veilFrameCanvas.height = 1;
    }
  }

  scheduleResize() {
    this.resizePending = true;
  }

  handleResize() {
    const width = this.canvas.clientWidth || window.innerWidth;
    const height = this.canvas.clientHeight || window.innerHeight;
    const pixelRatio = getPixelRatio(width, height);
    if (width === this.width
      && height === this.height
      && pixelRatio === this.pixelRatio
      && this.afterglowMotes.length) {
      return;
    }
    const previousGeometry = this.geometry;
    const previousHeight = this.height;
    const previousWidth = this.width;
    this.width = width;
    this.height = height;
    this.pixelRatio = pixelRatio;
    this.canvas.width = Math.max(1, Math.round(width * pixelRatio));
    this.canvas.height = Math.max(1, Math.round(height * pixelRatio));
    this.frameInterval = (this.canvas.width * this.canvas.height) > FRAME_PIXEL_THRESHOLD
      ? FRAME_INTERVAL
      : 0;
    if (this.frameInterval > 0 && this.lastDrawTime !== null) {
      this.nextDrawTime = this.lastDrawTime + this.frameInterval;
    } else if (this.frameInterval === 0) {
      this.nextDrawTime = null;
    }
    this.context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    this.geometry = createGeometry(width, height);
    this.afterglowMotes = this.createAfterglowMotes();
    this.rebuildVeil();
    if (!previousGeometry
      || previousGeometry.isPortrait !== this.geometry.isPortrait
      || !previousWidth
      || !previousHeight) {
      this.particles = [];
      this.spawnAccumulator = 0;
      this.spawnedParticles = 0;
      this.trail = [];
      this.lastTrailTime = -Infinity;
      return;
    }
    const scaleX = width / previousWidth;
    const scaleY = height / previousHeight;
    const sizeScale = (scaleX + scaleY) * 0.5;
    this.trail = this.trail.map((point) => {
      const sampledComet = this.getCometState(point.time);
      return Object.assign({}, point, {
        x: sampledComet.x,
        y: sampledComet.y,
      });
    });
    this.particles = this.particles.map(particle => Object.assign({}, particle, {
      length: particle.length * sizeScale,
      size: particle.size * sizeScale,
      velocityX: particle.velocityX * scaleX,
      velocityY: particle.velocityY * scaleY,
      x: particle.x * scaleX,
      y: particle.y * scaleY,
    }));
  }

  rebuildVeil() {
    if (!this.veilCanvas) {
      this.veilCanvas = document.createElement('canvas');
      this.veilContext = this.veilCanvas.getContext('2d');
    }
    if (!this.veilContext) {
      return;
    }
    this.veilCanvas.width = Math.max(1, Math.round(this.width));
    this.veilCanvas.height = Math.max(1, Math.round(this.height));
    if (this.pixelRatio >= OFFSCREEN_REVEAL_PIXEL_RATIO) {
      if (!this.veilFrameCanvas) {
        this.veilFrameCanvas = document.createElement('canvas');
        this.veilFrameContext = this.veilFrameCanvas.getContext('2d');
      }
      if (this.veilFrameContext) {
        this.veilFrameCanvas.width = this.veilCanvas.width;
        this.veilFrameCanvas.height = this.veilCanvas.height;
      }
    } else if (this.veilFrameCanvas) {
      this.veilFrameCanvas.width = 1;
      this.veilFrameCanvas.height = 1;
    }
    const { veilContext } = this;
    veilContext.setTransform(1, 0, 0, 1, 0, 0);
    veilContext.clearRect(0, 0, this.width, this.height);
    const baseAlpha = this.geometry.isPortrait || this.width < 760 ? 0.95 : 0.93;

    const baseGradient = veilContext.createLinearGradient(
      this.width * 0.08,
      0,
      this.width * 0.92,
      this.height,
    );
    baseGradient.addColorStop(0, rgba(DEEP_SPACE_TOP, baseAlpha));
    baseGradient.addColorStop(0.52, rgba(DEEP_SPACE_MIDDLE, baseAlpha));
    baseGradient.addColorStop(1, rgba(DEEP_SPACE_BOTTOM, baseAlpha));
    veilContext.fillStyle = baseGradient;
    veilContext.fillRect(0, 0, this.width, this.height);

    const themeWash = veilContext.createLinearGradient(
      0,
      this.height * 0.18,
      this.width,
      this.height * 0.74,
    );
    themeWash.addColorStop(0, rgba(this.theme.start, 0.08));
    themeWash.addColorStop(0.46, rgba(this.theme.start, 0.02));
    themeWash.addColorStop(0.7, rgba(this.theme.end, 0.035));
    themeWash.addColorStop(1, rgba(this.theme.end, 0.09));
    veilContext.fillStyle = themeWash;
    veilContext.fillRect(0, 0, this.width, this.height);

    this.drawCachedNebula(veilContext);
    this.drawCachedStars(veilContext);

    const centerX = this.width * 0.5;
    const centerY = this.height * 0.42;
    const vignetteRadius = Math.hypot(this.width, this.height) * 0.58;
    const vignette = veilContext.createRadialGradient(
      centerX,
      centerY,
      Math.min(this.width, this.height) * 0.08,
      centerX,
      centerY,
      vignetteRadius,
    );
    vignette.addColorStop(0, rgba(DEEP_SPACE_EDGE, 0));
    vignette.addColorStop(0.58, rgba(DEEP_SPACE_EDGE, 0.04));
    vignette.addColorStop(1, rgba(DEEP_SPACE_EDGE, 0.36));
    veilContext.fillStyle = vignette;
    veilContext.fillRect(0, 0, this.width, this.height);
    veilContext.setTransform(1, 0, 0, 1, 0, 0);
    veilContext.globalAlpha = 1;
    veilContext.globalCompositeOperation = 'source-over';
  }

  drawCachedNebula(targetContext) {
    const context = targetContext;
    const shortEdge = Math.min(this.width, this.height);
    const isCompact = this.geometry.isPortrait || this.width < 760;
    const clouds = [
      {
        alpha: isCompact ? 0.052 : 0.064,
        color: mixColor(NEBULA_BLUE, this.theme.start, 0.18),
        radius: shortEdge * (isCompact ? 0.36 : 0.32),
        scaleX: isCompact ? 1.15 : 1.8,
        scaleY: isCompact ? 1.2 : 0.78,
        x: this.width * (isCompact ? 0.28 : 0.22),
        y: this.height * (isCompact ? 0.24 : 0.28),
      },
      {
        alpha: isCompact ? 0.044 : 0.056,
        color: mixColor(NEBULA_VIOLET, this.theme.end, 0.2),
        radius: shortEdge * (isCompact ? 0.32 : 0.29),
        scaleX: isCompact ? 1.08 : 1.65,
        scaleY: isCompact ? 1.22 : 0.82,
        x: this.width * (isCompact ? 0.7 : 0.76),
        y: this.height * (isCompact ? 0.64 : 0.58),
      },
      {
        alpha: isCompact ? 0.03 : 0.038,
        color: mixColor(NEBULA_BLUE, NEBULA_VIOLET, 0.52),
        radius: shortEdge * (isCompact ? 0.27 : 0.24),
        scaleX: isCompact ? 1.3 : 1.9,
        scaleY: isCompact ? 0.88 : 0.58,
        x: this.width * 0.51,
        y: this.height * (isCompact ? 0.44 : 0.38),
      },
    ];

    context.save();
    for (let index = 0; index < clouds.length; index += 1) {
      const cloud = clouds[index];
      context.save();
      context.translate(cloud.x, cloud.y);
      context.rotate(seededSigned(index, 21) * 0.22);
      context.scale(cloud.scaleX, cloud.scaleY);
      const gradient = context.createRadialGradient(
        0,
        0,
        cloud.radius * 0.04,
        0,
        0,
        cloud.radius,
      );
      gradient.addColorStop(0, rgba(cloud.color, cloud.alpha));
      gradient.addColorStop(0.34, rgba(cloud.color, cloud.alpha * 0.62));
      gradient.addColorStop(0.72, rgba(cloud.color, cloud.alpha * 0.2));
      gradient.addColorStop(1, rgba(cloud.color, 0));
      context.fillStyle = gradient;
      context.beginPath();
      context.arc(0, 0, cloud.radius, 0, Math.PI * 2);
      context.fill();
      context.restore();
    }
    context.restore();
  }

  drawCachedStars(targetContext) {
    const context = targetContext;
    const isCompact = this.geometry.isPortrait || this.width < 760;
    const starBudget = isCompact ? 14 : 24;
    const shortEdge = Math.min(this.width, this.height);
    const edgePadding = Math.min(34, shortEdge * 0.055);

    context.save();
    for (let index = 0; index < starBudget; index += 1) {
      const x = edgePadding
        + (seededUnit(index, 31) * Math.max(1, this.width - (edgePadding * 2)));
      const y = edgePadding
        + (seededUnit(index, 32) * Math.max(1, this.height - (edgePadding * 2)));
      const size = (0.32 + (seededUnit(index, 33) * 0.72))
        * (isCompact ? 0.82 : 1);
      const alpha = 0.12 + (seededUnit(index, 34) * 0.2);
      const color = seededUnit(index, 35) > 0.52
        ? mixColor(DISTANT_STAR_COOL, this.theme.start, 0.12)
        : mixColor(DISTANT_STAR_WARM, this.theme.end, 0.1);
      const halo = context.createRadialGradient(x, y, 0, x, y, size * 3.2);
      halo.addColorStop(0, rgba(WHITE, alpha * 0.92));
      halo.addColorStop(0.22, rgba(color, alpha * 0.68));
      halo.addColorStop(1, rgba(color, 0));
      context.fillStyle = halo;
      context.beginPath();
      context.arc(x, y, size * 3.2, 0, Math.PI * 2);
      context.fill();

      if (size > 0.8 && index % 5 === 0) {
        const arm = size * 2.8;
        context.globalAlpha = alpha * 0.38;
        context.strokeStyle = rgba(color, 0.72);
        context.lineWidth = 0.45;
        context.beginPath();
        context.moveTo(x - arm, y);
        context.lineTo(x + arm, y);
        context.moveTo(x, y - (arm * 0.52));
        context.lineTo(x, y + (arm * 0.52));
        context.stroke();
        context.globalAlpha = 1;
      }
    }
    context.restore();
  }

  getRevealGeometry(elapsed) {
    if (elapsed >= VEIL_FADE_END) {
      return null;
    }
    const comet = this.getCometState(elapsed);
    if (comet.movementProgress <= 0) {
      return null;
    }
    const revealStart = this.getCometState(
      COMET_DELAY + (COMET_DURATION * MOVEMENT_START),
    );
    const expansion = smoothstep(VEIL_REVEAL_START, VEIL_REVEAL_END, elapsed);
    const shortEdge = Math.min(this.width, this.height);
    const minimumWidth = clamp(shortEdge * 0.055, 34, 54);
    const maximumWidth = clamp(shortEdge * 0.22, 96, 220);
    const featherWidth = clamp(shortEdge * 0.04, 20, 42);
    const revealWidth = minimumWidth
      + ((maximumWidth - minimumWidth) * expansion);
    const outerWidth = revealWidth + (featherWidth * 2);
    const headLag = (outerWidth * 0.5)
      + (this.geometry.isPortrait ? 18 : 24);
    const travelled = this.geometry.travelRadius * 2 * comet.movementProgress;
    if (travelled <= headLag) {
      return null;
    }
    return {
      comet,
      featherWidth,
      outerWidth,
      revealHead: {
        x: comet.x - (this.geometry.direction.x * headLag),
        y: comet.y - (this.geometry.direction.y * headLag),
      },
      revealStart,
    };
  }

  getCometState(elapsed) {
    const localProgress = clamp((elapsed - COMET_DELAY) / COMET_DURATION);
    const movementProgress = getMovementProgress(localProgress);
    const distance = this.geometry.travelRadius * ((movementProgress * 2) - 1);
    const entryAlpha = smoothstep(0.04, 0.18, localProgress);
    const exitAlpha = 1 - smoothstep(0.72, 1, localProgress);
    return {
      alpha: entryAlpha * exitAlpha,
      localProgress,
      movementProgress,
      x: this.geometry.center.x + (this.geometry.direction.x * distance),
      y: this.geometry.center.y + (this.geometry.direction.y * distance),
    };
  }

  createAfterglowMotes() {
    const { direction, normal } = this.geometry;
    const shortEdge = Math.min(this.width, this.height);
    const edgePadding = Math.min(42, shortEdge * 0.08);
    const alongSpan = Math.min(
      (this.width - (edgePadding * 2)) / Math.max(0.2, Math.abs(direction.x)),
      (this.height - (edgePadding * 2)) / Math.max(0.2, Math.abs(direction.y)),
    ) * 0.78;
    const lateralSpan = shortEdge * 0.24;
    const mobileScale = this.geometry.isPortrait || this.width < 760 ? 0.72 : 1;
    const motes = [];

    for (let index = 0; index < this.geometry.afterglowBudget; index += 1) {
      const along = (seededUnit(index, 1) - 0.5) * alongSpan;
      const lateral = (seededUnit(index, 2) - 0.5) * lateralSpan;
      const accentColor = mixColor(
        this.theme.start,
        this.theme.end,
        seededUnit(index, 4),
      );
      const pearlColor = mixColor(PEARL_COOL, PEARL_WARM, seededUnit(index, 8));
      const x = clamp(
        this.geometry.center.x + (direction.x * along) + (normal.x * lateral),
        edgePadding,
        this.width - edgePadding,
      );
      const y = clamp(
        this.geometry.center.y + (direction.y * along) + (normal.y * lateral),
        edgePadding,
        this.height - edgePadding,
      );
      motes.push({
        alpha: 0.2 + (seededUnit(index, 3) * 0.16),
        color: mixColor(accentColor, pearlColor, 0.62),
        delay: seededUnit(index, 5) * 52,
        driftX: (seededUnit(index, 6) - 0.5) * 16 * mobileScale,
        driftY: -(6 + (seededUnit(index, 7) * 12)) * mobileScale,
        phase: seededUnit(index, 9) * Math.PI * 2,
        radius: (6 + (seededUnit(index, 10) * 8)) * mobileScale,
        scaleX: 0.82 + (seededUnit(index, 11) * 0.44),
        scaleY: 0.84 + (seededUnit(index, 12) * 0.34),
        softness: 0.18 + (seededUnit(index, 13) * 0.18),
        x,
        y,
      });
    }

    return motes;
  }

  isNearViewport(comet) {
    const padding = Math.max(this.width, this.height) * 0.18;
    return comet.x > -padding
      && comet.x < this.width + padding
      && comet.y > -padding
      && comet.y < this.height + padding;
  }

  updateTrail(elapsed) {
    if (Number.isFinite(this.lastTrailTime)
      && elapsed - this.lastTrailTime > MAX_TRAIL_CATCHUP) {
      this.trail = this.trail.filter(
        point => elapsed - point.time < MAX_TRAIL_CATCHUP,
      );
      this.lastTrailTime = elapsed - MAX_TRAIL_CATCHUP;
    }
    const oldestSampleTime = Math.max(COMET_DELAY, elapsed - TRAIL_LIFETIME);
    let sampleTime = Number.isFinite(this.lastTrailTime)
      ? Math.max(this.lastTrailTime + TRAIL_SAMPLE_INTERVAL, oldestSampleTime)
      : Math.max(oldestSampleTime, elapsed - MAX_TRAIL_CATCHUP);
    while (sampleTime <= elapsed) {
      const sampledComet = this.getCometState(sampleTime);
      if (sampledComet.localProgress > 0) {
        this.trail.push({
          jitter: (Math.random() * 2) - 1,
          time: sampleTime,
          x: sampledComet.x,
          y: sampledComet.y,
        });
      }
      this.lastTrailTime = sampleTime;
      sampleTime += TRAIL_SAMPLE_INTERVAL;
    }
    this.trail = this.trail.filter(point => elapsed - point.time < TRAIL_LIFETIME);
  }

  spawnParticle(comet, initialAge = 0) {
    const random = Math.random();
    const glintThreshold = this.geometry.isPortrait ? 0.82 : 0.75;
    const streakThreshold = this.geometry.isPortrait ? 0.62 : 0.54;
    const particleScale = this.geometry.isPortrait ? 1 : 1.28;
    const isGlint = random > glintThreshold;
    const isStreak = !isGlint && random > streakThreshold;
    const emissionLag = this.geometry.travelSpeed * initialAge;
    const behind = 5 + (Math.random() * 52) + emissionLag;
    const lateral = (Math.random() - 0.5)
      * (this.geometry.isPortrait ? 22 : 34)
      * particleScale;
    const forwardSpeed = this.geometry.travelSpeed * (0.05 + (Math.random() * 0.13));
    const sideSpeed = (Math.random() - 0.5) * 0.11;
    const themeProgress = this.theme.isGradient ? Math.random() : 0;
    const color = Math.random() > 0.76
      ? WHITE
      : mixColor(this.theme.start, this.theme.end, themeProgress);
    let type = 'dust';
    if (isGlint) {
      type = 'glint';
    } else if (isStreak) {
      type = 'streak';
    }
    const particle = {
      age: initialAge,
      color,
      length: isStreak ? (12 + (Math.random() * 28)) * particleScale : 0,
      life: isGlint
        ? 420 + (Math.random() * 420)
        : 580 + (Math.random() * 560) + (this.geometry.isPortrait ? 0 : 90),
      phase: Math.random() * Math.PI * 2,
      size: (isGlint ? 1.8 + (Math.random() * 2.4) : 0.8 + (Math.random() * 2.2))
        * particleScale,
      type,
      velocityX: (this.geometry.direction.x * forwardSpeed)
        + (this.geometry.normal.x * sideSpeed),
      velocityY: (this.geometry.direction.y * forwardSpeed)
        + (this.geometry.normal.y * sideSpeed),
      x: comet.x - (this.geometry.direction.x * behind)
        + (this.geometry.normal.x * lateral),
      y: comet.y - (this.geometry.direction.y * behind)
        + (this.geometry.normal.y * lateral),
    };
    particle.x += particle.velocityX * initialAge;
    particle.y += particle.velocityY * initialAge;
    this.particles.push(particle);
    this.spawnedParticles += 1;
  }

  updateParticles(comet, elapsed, delta) {
    for (let index = 0; index < this.particles.length; index += 1) {
      const particle = this.particles[index];
      particle.age += delta;
      particle.x += particle.velocityX * delta;
      particle.y += particle.velocityY * delta;
    }
    this.particles = this.particles.filter(particle => particle.age < particle.life);
    const canSpawn = comet.movementProgress > 0
      && comet.movementProgress < 1
      && this.isNearViewport(comet)
      && this.spawnedParticles < this.geometry.particleBudget;
    if (canSpawn) {
      const centerEmission = Math.sin(comet.movementProgress * Math.PI);
      const baseSpawnRate = this.geometry.isPortrait ? 0.041 : 0.062;
      const spawnRate = baseSpawnRate * (0.72 + (centerEmission * 0.56));
      this.spawnAccumulator += delta * spawnRate;
      while (this.spawnAccumulator >= 1
        && this.spawnedParticles < this.geometry.particleBudget) {
        this.spawnParticle(comet, Math.random() * delta);
        this.spawnAccumulator -= 1;
      }
    }
  }

  getTrailPoint(point, elapsed, lifetime, turbulence) {
    const ageProgress = clamp((elapsed - point.time) / lifetime);
    const offset = point.jitter * turbulence * ageProgress;
    return {
      x: point.x + (this.geometry.normal.x * offset),
      y: point.y + (this.geometry.normal.y * offset),
    };
  }

  strokeTrail(elapsed, options) {
    const points = this.trail.filter(point => elapsed - point.time <= options.lifetime);
    if (points.length < 2) {
      return;
    }
    const { context } = this;
    const [firstRecord] = points;
    const lastRecord = points[points.length - 1];
    const first = this.getTrailPoint(
      firstRecord,
      elapsed,
      options.lifetime,
      options.turbulence,
    );
    const last = this.getTrailPoint(
      lastRecord,
      elapsed,
      options.lifetime,
      options.turbulence,
    );
    const gradient = context.createLinearGradient(first.x, first.y, last.x, last.y);
    const startColor = options.isWhite ? WHITE : this.theme.start;
    const endColor = options.isWhite ? WHITE : this.theme.end;
    gradient.addColorStop(0, rgba(startColor, 0));
    gradient.addColorStop(0.32, rgba(startColor, options.alpha * 0.22));
    gradient.addColorStop(0.74, rgba(endColor, options.alpha * 0.72));
    gradient.addColorStop(1, rgba(options.finishWhite ? WHITE : endColor, options.alpha));

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.filter = options.blur ? `blur(${options.blur}px)` : 'none';
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = options.width;
    context.strokeStyle = gradient;
    context.beginPath();
    context.moveTo(first.x, first.y);
    let previous = first;
    for (let index = 1; index < points.length; index += 1) {
      const current = this.getTrailPoint(
        points[index],
        elapsed,
        options.lifetime,
        options.turbulence,
      );
      const middleX = (previous.x + current.x) * 0.5;
      const middleY = (previous.y + current.y) * 0.5;
      context.quadraticCurveTo(previous.x, previous.y, middleX, middleY);
      previous = current;
    }
    context.lineTo(last.x, last.y);
    context.stroke();
    context.restore();
  }

  getCutEdgePoint(point, elapsed, options, side) {
    const trailPoint = this.getTrailPoint(
      point,
      elapsed,
      options.lifetime,
      options.turbulence,
    );
    const ageProgress = clamp((elapsed - point.time) / options.lifetime);
    const separation = options.separation * smoothstep(0, 1, ageProgress) * side;
    return {
      x: trailPoint.x + (this.geometry.normal.x * separation),
      y: trailPoint.y + (this.geometry.normal.y * separation),
    };
  }

  strokeCutEdges(elapsed, options) {
    const points = this.trail.filter(point => elapsed - point.time <= options.lifetime);
    if (points.length < 2) {
      return;
    }
    const { context } = this;
    const [firstRecord] = points;
    const lastRecord = points[points.length - 1];
    const gradient = context.createLinearGradient(
      firstRecord.x,
      firstRecord.y,
      lastRecord.x,
      lastRecord.y,
    );
    gradient.addColorStop(0, rgba(this.theme.start, 0));
    gradient.addColorStop(0.34, rgba(this.theme.start, options.alpha * 0.18));
    gradient.addColorStop(0.76, rgba(this.theme.end, options.alpha * 0.68));
    gradient.addColorStop(1, rgba(WHITE, options.alpha));

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.filter = options.blur ? `blur(${options.blur}px)` : 'none';
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = options.width;
    context.strokeStyle = gradient;
    context.beginPath();
    for (let side = -1; side <= 1; side += 2) {
      const first = this.getCutEdgePoint(firstRecord, elapsed, options, side);
      const last = this.getCutEdgePoint(lastRecord, elapsed, options, side);
      context.moveTo(first.x, first.y);
      let previous = first;
      for (let index = 1; index < points.length; index += 1) {
        const current = this.getCutEdgePoint(points[index], elapsed, options, side);
        const middleX = (previous.x + current.x) * 0.5;
        const middleY = (previous.y + current.y) * 0.5;
        context.quadraticCurveTo(previous.x, previous.y, middleX, middleY);
        previous = current;
      }
      context.lineTo(last.x, last.y);
    }
    context.stroke();
    context.restore();
  }

  strokePearlCutEdges(elapsed, options) {
    const points = this.trail.filter(point => elapsed - point.time <= options.lifetime);
    if (points.length < 2) {
      return;
    }
    const { context } = this;
    const [firstRecord] = points;
    const lastRecord = points[points.length - 1];
    const cool = this.theme.pearlStart;
    const warm = this.theme.pearlEnd;

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.filter = options.blur ? `blur(${options.blur}px)` : 'none';
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = options.width;

    for (let side = -1; side <= 1; side += 2) {
      const first = this.getCutEdgePoint(firstRecord, elapsed, options, side);
      const last = this.getCutEdgePoint(lastRecord, elapsed, options, side);
      const sideColor = side < 0 ? cool : warm;
      const counterColor = side < 0 ? warm : cool;
      const gradient = context.createLinearGradient(first.x, first.y, last.x, last.y);
      gradient.addColorStop(0, rgba(sideColor, 0));
      gradient.addColorStop(0.3, rgba(sideColor, options.alpha * 0.22));
      gradient.addColorStop(0.64, rgba(PEARL_WHITE, options.alpha * 0.78));
      gradient.addColorStop(0.86, rgba(counterColor, options.alpha * 0.52));
      gradient.addColorStop(1, rgba(PEARL_WHITE, options.alpha * 0.82));
      context.strokeStyle = gradient;
      context.beginPath();
      context.moveTo(first.x, first.y);
      let previous = first;
      for (let index = 1; index < points.length; index += 1) {
        const current = this.getCutEdgePoint(points[index], elapsed, options, side);
        const middleX = (previous.x + current.x) * 0.5;
        const middleY = (previous.y + current.y) * 0.5;
        context.quadraticCurveTo(previous.x, previous.y, middleX, middleY);
        previous = current;
      }
      context.lineTo(last.x, last.y);
      context.stroke();
    }
    context.restore();
  }

  drawTrails(elapsed) {
    const portraitScale = this.geometry.isPortrait ? 0.78 : 1;
    const lifecycleAlpha = 1 - smoothstep(this.duration - 320, this.duration, elapsed);
    this.strokeTrail(elapsed, {
      alpha: 0.42 * lifecycleAlpha,
      blur: 17,
      finishWhite: false,
      isWhite: false,
      lifetime: 1060,
      turbulence: 18,
      width: 72 * portraitScale,
    });
    this.strokeTrail(elapsed, {
      alpha: 0.68 * lifecycleAlpha,
      blur: 6,
      finishWhite: this.theme.isGradient,
      isWhite: false,
      lifetime: 760,
      turbulence: 10,
      width: 25 * portraitScale,
    });
    this.strokeTrail(elapsed, {
      alpha: 0.92 * lifecycleAlpha,
      blur: 1.8,
      finishWhite: true,
      isWhite: true,
      lifetime: 430,
      turbulence: 4,
      width: 6 * portraitScale,
    });
  }

  drawAirflow(comet, elapsed) {
    if (comet.alpha <= 0.01 || !this.isNearViewport(comet)) {
      return;
    }
    const entry = smoothstep(0.11, 0.22, comet.localProgress);
    const exit = 1 - smoothstep(0.67, 0.84, comet.localProgress);
    const breathing = 0.94 + (Math.sin(elapsed * 0.011) * 0.06);
    const alpha = comet.alpha * entry * exit * breathing;
    if (alpha <= 0.005) {
      return;
    }

    const { context } = this;
    const scale = this.geometry.isPortrait ? 0.72 : 1;
    const alphaScale = this.geometry.isPortrait ? 0.84 : 1;
    const laneCount = this.geometry.isPortrait || this.width < 760 ? 2 : 3;
    context.save();
    context.globalCompositeOperation = 'lighter';
    context.translate(comet.x, comet.y);
    context.rotate(this.geometry.angle);
    const gradient = context.createLinearGradient(-142 * scale, 0, 90 * scale, 0);
    gradient.addColorStop(0, rgba(this.theme.start, 0));
    gradient.addColorStop(0.27, rgba(this.theme.start, 0.48));
    gradient.addColorStop(0.61, rgba(WHITE, 0.9));
    gradient.addColorStop(0.84, rgba(this.theme.end, 0.54));
    gradient.addColorStop(1, rgba(this.theme.end, 0));
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.strokeStyle = gradient;
    context.shadowBlur = 4.5 * scale;
    context.shadowColor = rgba(this.theme.end, 0.48);

    for (let laneIndex = 0; laneIndex < laneCount; laneIndex += 1) {
      const lane = AIRFLOW_LANES[laneIndex];
      const lead = lane.lead * scale;
      const offset = lane.offset * scale;
      const spread = lane.spread * scale;
      const wake = lane.wake * scale;
      const lanePulse = 0.95 + (Math.sin((elapsed * 0.009) + lane.phase) * 0.05);
      context.globalAlpha = alpha * alphaScale * lane.alpha * lanePulse;
      context.lineWidth = lane.width * scale;
      context.setLineDash(lane.dash.length
        ? [lane.dash[0] * scale, lane.dash[1] * scale]
        : []);
      context.lineDashOffset = (-elapsed * 0.052 * scale) + lane.phase;

      for (let side = -1; side <= 1; side += 2) {
        context.beginPath();
        context.moveTo(-wake, side * offset * 0.58);
        context.bezierCurveTo(
          -wake * 0.52,
          side * offset * 0.68,
          -lead * 0.1,
          side * (offset + (spread * 0.86)),
          lead * 0.42,
          side * (offset + spread),
        );
        context.bezierCurveTo(
          lead * 0.72,
          side * (offset + (spread * 0.92)),
          lead * 0.94,
          side * (offset + (spread * 0.32)),
          lead,
          side * offset * 0.72,
        );
        context.stroke();
      }
    }
    context.restore();
  }

  drawCutGlow(elapsed) {
    const pulse = 0.84 + (Math.sin(elapsed * 0.014) * 0.1);
    const separation = this.geometry.isPortrait ? 14 : 18;
    this.strokeCutEdges(elapsed, {
      alpha: 0.78 * pulse,
      blur: 11,
      lifetime: 185,
      separation,
      turbulence: 1.5,
      width: this.geometry.isPortrait ? 9 : 12,
    });
    this.strokePearlCutEdges(elapsed, {
      alpha: 0.58 * pulse,
      blur: 2.6,
      lifetime: 165,
      separation: separation * 0.88,
      turbulence: 0.8,
      width: this.geometry.isPortrait ? 3.2 : 4.2,
    });
    this.strokeCutEdges(elapsed, {
      alpha: 0.96 * pulse,
      blur: 0.8,
      lifetime: 145,
      separation: separation * 0.78,
      turbulence: 0.5,
      width: this.geometry.isPortrait ? 1.4 : 1.8,
    });
  }

  drawParticle(particle, elapsed, lifecycleAlpha) {
    const { context } = this;
    const progress = clamp(particle.age / particle.life);
    const fadeIn = smoothstep(0, 0.12, progress);
    const fadeOut = 1 - smoothstep(PARTICLE_DISSIPATION_START, PARTICLE_DISSIPATION_END, progress);
    const twinkle = 0.72 + (Math.sin((elapsed * 0.013) + particle.phase) * 0.28);
    const alpha = fadeIn * fadeOut * twinkle * lifecycleAlpha;
    if (alpha <= 0.005) {
      return;
    }
    const drift = Math.sin((elapsed * 0.007) + particle.phase) * 4 * progress;
    const dissipation = smoothstep(PARTICLE_DISSIPATION_START, PARTICLE_DISSIPATION_END, progress);
    const sizeScale = 1 - (dissipation * 0.34);
    const x = particle.x + (this.geometry.normal.x * drift);
    const y = particle.y + (this.geometry.normal.y * drift);
    context.save();
    context.globalCompositeOperation = 'lighter';
    context.globalAlpha = alpha;
    context.fillStyle = rgba(particle.color, 0.92);
    context.strokeStyle = rgba(particle.color, 0.86);
    context.shadowBlur = particle.type === 'dust'
      ? particle.size * (2.8 - (dissipation * 1.2))
      : particle.size * (5.2 - (dissipation * 1.8));
    context.shadowColor = rgba(particle.color, 0.78);

    if (particle.type === 'streak') {
      context.lineCap = 'round';
      context.lineWidth = Math.max(0.7, particle.size * 0.62 * sizeScale);
      context.beginPath();
      context.moveTo(x, y);
      context.lineTo(
        x - (this.geometry.direction.x * particle.length),
        y - (this.geometry.direction.y * particle.length),
      );
      context.stroke();
    } else if (particle.type === 'glint') {
      const arm = particle.size * sizeScale * (2.6 + (twinkle * 1.8));
      context.translate(x, y);
      context.rotate(this.geometry.angle);
      context.lineWidth = 0.75;
      context.beginPath();
      context.moveTo(-arm * 2.2, 0);
      context.lineTo(arm * 2.2, 0);
      context.moveTo(0, -arm);
      context.lineTo(0, arm);
      context.stroke();
      context.beginPath();
      context.arc(0, 0, particle.size * 0.72 * sizeScale, 0, Math.PI * 2);
      context.fill();
    } else {
      context.beginPath();
      context.arc(x, y, particle.size * sizeScale, 0, Math.PI * 2);
      context.fill();
    }
    context.restore();
  }

  drawParticles(elapsed) {
    const lifecycleAlpha = 1 - smoothstep(this.duration - 360, this.duration, elapsed);
    for (let index = 0; index < this.particles.length; index += 1) {
      this.drawParticle(this.particles[index], elapsed, lifecycleAlpha);
    }
  }

  drawAfterglowBloom(lifecycleAlpha, progress) {
    const { context } = this;
    const mobileScale = this.geometry.isPortrait ? 0.78 : 1;
    const radius = Math.min(this.width, this.height) * 0.17;
    const offset = radius * (0.18 + (progress * 0.12));
    const center = {
      x: this.geometry.center.x + (this.geometry.direction.x * offset),
      y: this.geometry.center.y + (this.geometry.direction.y * offset),
    };

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.globalAlpha = lifecycleAlpha * 0.32;
    context.translate(center.x, center.y);
    context.rotate(this.geometry.angle);
    context.scale(2.2 * mobileScale, 0.62);
    const gradient = context.createRadialGradient(0, 0, 0, 0, 0, radius);
    gradient.addColorStop(0, rgba(PEARL_WHITE, 0.22));
    gradient.addColorStop(0.28, rgba(this.theme.start, 0.14));
    gradient.addColorStop(0.66, rgba(this.theme.end, 0.07));
    gradient.addColorStop(1, rgba(this.theme.end, 0));
    context.filter = `blur(${Math.max(5, radius * 0.04)}px)`;
    context.fillStyle = gradient;
    context.beginPath();
    context.arc(0, 0, radius, 0, Math.PI * 2);
    context.fill();
    context.restore();
  }

  drawAfterglowMote(mote, elapsed, start, lifecycleAlpha) {
    const { context } = this;
    const localStart = start + mote.delay;
    const progress = clamp((elapsed - localStart) / (this.duration - localStart));
    const entry = smoothstep(0, 0.2, progress);
    const drift = smoothstep(0, 1, progress);
    const twinkle = 0.9 + (Math.sin((elapsed * 0.009) + mote.phase) * 0.1);
    const alpha = lifecycleAlpha * entry * twinkle * mote.alpha;
    if (alpha <= 0.004) {
      return;
    }
    const x = mote.x + (mote.driftX * drift);
    const y = mote.y + (mote.driftY * drift);

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.globalAlpha = alpha;
    context.translate(x, y);
    context.scale(mote.scaleX, mote.scaleY);
    const gradient = context.createRadialGradient(0, 0, 0, 0, 0, mote.radius);
    gradient.addColorStop(0, rgba(PEARL_WHITE, 0.52));
    gradient.addColorStop(0.22, rgba(mote.color, 0.36));
    gradient.addColorStop(0.68, rgba(mote.color, 0.14));
    gradient.addColorStop(0.86, rgba(PEARL_WHITE, 0.18));
    gradient.addColorStop(1, rgba(mote.color, 0));
    context.filter = `blur(${mote.radius * mote.softness}px)`;
    context.fillStyle = gradient;
    context.beginPath();
    context.arc(0, 0, mote.radius, 0, Math.PI * 2);
    context.fill();
    context.restore();
  }

  drawAfterglow(elapsed) {
    const fadeStart = this.duration - AFTERGLOW_LINGER_DURATION;
    const start = fadeStart - AFTERGLOW_ENTRY_DURATION;
    if (elapsed < start) {
      return;
    }
    const entry = smoothstep(start, fadeStart, elapsed);
    const fade = 1 - smoothstep(fadeStart, this.duration, elapsed);
    const lifecycleAlpha = entry * fade;
    if (lifecycleAlpha <= 0.004) {
      return;
    }
    const progress = clamp((elapsed - start) / (this.duration - start));
    this.drawAfterglowBloom(lifecycleAlpha, progress);
    for (let index = 0; index < this.afterglowMotes.length; index += 1) {
      this.drawAfterglowMote(
        this.afterglowMotes[index],
        elapsed,
        start,
        lifecycleAlpha,
      );
    }
  }

  drawVeil(elapsed) {
    if (!this.veilCanvas || !this.veilContext) {
      return false;
    }
    const alpha = 1 - smoothstep(VEIL_FADE_START, VEIL_FADE_END, elapsed);
    if (alpha <= 0.001) {
      return false;
    }
    const { context, veilFrameContext } = this;
    const useOffscreenReveal = elapsed >= VEIL_REVEAL_START
      && this.pixelRatio >= OFFSCREEN_REVEAL_PIXEL_RATIO
      && veilFrameContext;
    if (!useOffscreenReveal) {
      context.save();
      context.globalCompositeOperation = 'copy';
      context.globalAlpha = alpha;
      context.drawImage(
        this.veilCanvas,
        0,
        0,
        this.width,
        this.height,
      );
      context.restore();
      this.drawVeilReveal(elapsed, context);
      return true;
    }

    veilFrameContext.save();
    veilFrameContext.setTransform(1, 0, 0, 1, 0, 0);
    veilFrameContext.globalCompositeOperation = 'copy';
    veilFrameContext.globalAlpha = alpha;
    veilFrameContext.drawImage(this.veilCanvas, 0, 0);
    veilFrameContext.restore();
    this.drawVeilReveal(elapsed, veilFrameContext);

    context.save();
    context.globalCompositeOperation = 'copy';
    context.globalAlpha = 1;
    context.drawImage(
      this.veilFrameCanvas,
      0,
      0,
      this.width,
      this.height,
    );
    context.restore();
    return true;
  }

  drawVeilReveal(elapsed, targetContext = this.context) {
    const reveal = this.getRevealGeometry(elapsed);
    if (!reveal) {
      return;
    }
    const {
      featherWidth,
      outerWidth,
      revealHead,
      revealStart,
    } = reveal;
    const featherStop = featherWidth / outerWidth;
    const middleX = (revealStart.x + revealHead.x) * 0.5;
    const middleY = (revealStart.y + revealHead.y) * 0.5;
    const context = targetContext;
    const featherGradient = context.createLinearGradient(
      middleX - (this.geometry.normal.x * outerWidth * 0.5),
      middleY - (this.geometry.normal.y * outerWidth * 0.5),
      middleX + (this.geometry.normal.x * outerWidth * 0.5),
      middleY + (this.geometry.normal.y * outerWidth * 0.5),
    );
    featherGradient.addColorStop(0, rgba(WHITE, 0));
    featherGradient.addColorStop(featherStop * 0.28, rgba(WHITE, 0.08));
    featherGradient.addColorStop(featherStop * 0.62, rgba(WHITE, 0.32));
    featherGradient.addColorStop(featherStop, rgba(WHITE, 1));
    featherGradient.addColorStop(1 - featherStop, rgba(WHITE, 1));
    featherGradient.addColorStop(1 - (featherStop * 0.62), rgba(WHITE, 0.32));
    featherGradient.addColorStop(1 - (featherStop * 0.28), rgba(WHITE, 0.08));
    featherGradient.addColorStop(1, rgba(WHITE, 0));

    context.save();
    context.globalCompositeOperation = 'destination-out';
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = outerWidth;
    context.strokeStyle = featherGradient;
    context.beginPath();
    context.moveTo(revealStart.x, revealStart.y);
    context.lineTo(revealHead.x, revealHead.y);
    context.stroke();
    context.restore();
  }

  drawRevealPearlEdge(elapsed) {
    const reveal = this.getRevealGeometry(elapsed);
    if (!reveal) {
      return;
    }
    const { context } = this;
    const progress = smoothstep(VEIL_REVEAL_START, VEIL_REVEAL_END, elapsed);
    const lifecycle = 1 - smoothstep(VEIL_FADE_END - 210, VEIL_FADE_END, elapsed);
    const alpha = lifecycle * (0.18 + (progress * 0.28));
    if (alpha <= 0.01) {
      return;
    }
    const { normal } = this.geometry;
    const edgeOffset = reveal.outerWidth * 0.5 - (reveal.featherWidth * 0.34);
    const start = {
      x: reveal.revealStart.x + (normal.x * edgeOffset),
      y: reveal.revealStart.y + (normal.y * edgeOffset),
    };
    const end = {
      x: reveal.revealHead.x + (normal.x * edgeOffset),
      y: reveal.revealHead.y + (normal.y * edgeOffset),
    };
    const gradient = context.createLinearGradient(start.x, start.y, end.x, end.y);
    gradient.addColorStop(0, rgba(this.theme.pearlStart, 0));
    gradient.addColorStop(0.48, rgba(PEARL_WHITE, alpha * 0.42));
    gradient.addColorStop(0.84, rgba(this.theme.pearlEnd, alpha * 0.78));
    gradient.addColorStop(1, rgba(PEARL_WHITE, alpha));
    context.save();
    context.globalCompositeOperation = 'lighter';
    context.globalAlpha = 1;
    context.lineCap = 'round';
    context.lineWidth = this.geometry.isPortrait ? 1.15 : 1.45;
    context.strokeStyle = gradient;
    context.beginPath();
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.stroke();
    context.restore();
  }

  drawBloom(comet, radius, color, alpha, blur, scaleX, scaleY) {
    const { context } = this;
    context.save();
    context.globalCompositeOperation = 'lighter';
    context.translate(comet.x, comet.y);
    context.rotate(this.geometry.angle);
    context.scale(scaleX, scaleY);
    const gradient = context.createRadialGradient(0, 0, 0, 0, 0, radius);
    gradient.addColorStop(0, rgba(color, alpha));
    gradient.addColorStop(0.3, rgba(color, alpha * 0.74));
    gradient.addColorStop(1, rgba(color, 0));
    context.filter = blur ? `blur(${blur}px)` : 'none';
    context.fillStyle = gradient;
    context.beginPath();
    context.arc(0, 0, radius, 0, Math.PI * 2);
    context.fill();
    context.restore();
  }

  drawHead(comet, elapsed) {
    if (comet.alpha <= 0.01 || !this.isNearViewport(comet)) {
      return;
    }
    const { context } = this;
    const mobileScale = this.geometry.isPortrait ? 0.76 : 1;
    const twinkle = 0.94 + (Math.sin(elapsed * 0.016) * 0.06);
    const alpha = comet.alpha * twinkle;
    const glintPulse = Math.max(
      pulseAround(comet.localProgress, 0.34, 0.065),
      pulseAround(comet.localProgress, 0.63, 0.055),
    );
    const glintScale = 0.82 + (glintPulse * 0.28);
    if (this.theme.isGradient) {
      const chromaticOffset = 2.4 * mobileScale;
      const startComet = {
        x: comet.x + (this.geometry.normal.x * chromaticOffset),
        y: comet.y + (this.geometry.normal.y * chromaticOffset),
      };
      const endComet = {
        x: comet.x - (this.geometry.normal.x * chromaticOffset),
        y: comet.y - (this.geometry.normal.y * chromaticOffset),
      };
      this.drawBloom(startComet, 62 * mobileScale, this.theme.start, alpha * 0.38, 12, 1.5, 0.82);
      this.drawBloom(endComet, 54 * mobileScale, this.theme.end, alpha * 0.42, 10, 1.45, 0.8);
    }
    this.drawBloom(comet, 92 * mobileScale, this.theme.end, alpha * 0.34, 18, 1.72, 0.72);
    this.drawBloom(comet, 46 * mobileScale, this.theme.start, alpha * 0.76, 7, 1.5, 0.78);
    this.drawBloom(comet, 18 * mobileScale, WHITE, alpha, 2, 1.22, 0.88);

    context.save();
    context.globalCompositeOperation = 'lighter';
    context.globalAlpha = alpha * (0.2 + (glintPulse * 0.8));
    context.translate(comet.x, comet.y);
    context.rotate(this.geometry.angle);
    context.strokeStyle = rgba(WHITE, 0.88);
    context.shadowBlur = 16 * mobileScale;
    context.shadowColor = rgba(this.theme.end, 0.92);
    context.lineCap = 'round';
    context.lineWidth = 1.15;
    context.beginPath();
    context.moveTo(-62 * mobileScale * glintScale, 0);
    context.lineTo(62 * mobileScale * glintScale, 0);
    context.moveTo(0, -31 * mobileScale * glintScale);
    context.lineTo(0, 31 * mobileScale * glintScale);
    context.stroke();
    context.globalAlpha = alpha;
    context.fillStyle = rgba(WHITE, 1);
    context.shadowBlur = 22 * mobileScale;
    context.shadowColor = rgba(WHITE, 0.96);
    context.beginPath();
    context.arc(0, 0, 5.8 * mobileScale, 0, Math.PI * 2);
    context.fill();
    context.restore();
  }

  draw(comet, elapsed) {
    const { context } = this;
    if (!this.drawVeil(elapsed)) {
      context.clearRect(0, 0, this.width, this.height);
    }
    this.drawTrails(elapsed);
    this.drawAirflow(comet, elapsed);
    this.drawCutGlow(elapsed);
    this.drawParticles(elapsed);
    this.drawHead(comet, elapsed);
    this.drawRevealPearlEdge(elapsed);
    this.drawAfterglow(elapsed);
  }

  renderFrame(timestamp) {
    let resized = false;
    if (this.resizePending) {
      this.resizePending = false;
      this.handleResize();
      resized = true;
    }
    const elapsed = timestamp - this.startTime;
    if (elapsed >= this.duration) {
      this.stop();
      return;
    }
    if (!resized
      && this.frameInterval > 0
      && timestamp + FRAME_EARLY_TOLERANCE < this.nextDrawTime) {
      this.frameId = window.requestAnimationFrame(this.renderFrame);
      return;
    }
    const frameDelta = Math.max(0, timestamp - this.lastFrameTime);
    const particleDelta = Math.min(MAX_PARTICLE_DELTA, frameDelta);
    const comet = this.getCometState(elapsed);
    this.updateTrail(elapsed);
    this.updateParticles(comet, elapsed, particleDelta);
    this.draw(comet, elapsed);
    this.lastFrameTime = timestamp;
    this.lastDrawTime = timestamp;
    if (this.frameInterval > 0) {
      if (resized
        || this.nextDrawTime === null
        || this.nextDrawTime + this.frameInterval <= timestamp) {
        this.nextDrawTime = timestamp + this.frameInterval;
      } else {
        this.nextDrawTime += this.frameInterval;
      }
    } else {
      this.nextDrawTime = null;
    }
    this.frameId = window.requestAnimationFrame(this.renderFrame);
  }
}
