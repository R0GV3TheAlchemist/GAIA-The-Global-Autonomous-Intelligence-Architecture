/**
 * src/lib/fieldParticles.ts
 * GAIA-OS — Ambient Field Particle Engine
 * Issue #68 Phase 6
 *
 * Implements a Three.js-based alignment-reactive particle field.
 * Renders particles as a BufferGeometry Points mesh with a custom
 * ShaderMaterial for soft circular sprites (no texture atlas needed).
 *
 * Particle behaviour per tier:
 *   minimal  — sparse, barely drifting, cool slate
 *   core     — gentle swell, amber warmth
 *   standard — steady field, sovereign violet
 *   full     — coherent lattice forming, Schumann teal
 *   vibrant  — dense radiant field, solar gold
 *
 * Connection lines are drawn as a second LineSegments mesh; pairs
 * within CONNECTION_DIST[tier] draw a faint edge, simulating a
 * biometric coherence network.
 *
 * Usage:
 *   const fp = new FieldParticles(canvasEl);
 *   fp.setTier('full');
 *   // call fp.dispose() on component unmount
 */

import * as THREE from 'three';
import gsap       from 'gsap';
import type { AlignmentTier } from '../hooks/useAlignment';

// ---------------------------------------------------------------------------
// Types + config
// ---------------------------------------------------------------------------

export interface TierParticleConfig {
  count:          number;   // number of particles
  speed:          number;   // base drift speed multiplier
  connectionDist: number;   // max distance for connection lines
  particleSize:   number;   // gl_PointSize in shader
  opacity:        number;   // Points mesh opacity
  color:          string;   // hex colour
  lineOpacity:    number;   // connection line opacity
}

export const TIER_PARTICLE_CONFIG: Record<AlignmentTier, TierParticleConfig> = {
  minimal: {
    count:          300,
    speed:          0.06,
    connectionDist: 0,      // no connections at minimal
    particleSize:   2.2,
    opacity:        0.28,
    color:          '#4a4a6a',
    lineOpacity:    0,
  },
  core: {
    count:          600,
    speed:          0.12,
    connectionDist: 0.18,
    particleSize:   2.5,
    opacity:        0.38,
    color:          '#f9a825',
    lineOpacity:    0.06,
  },
  standard: {
    count:          900,
    speed:          0.20,
    connectionDist: 0.22,
    particleSize:   2.8,
    opacity:        0.48,
    color:          '#a78bfa',
    lineOpacity:    0.09,
  },
  full: {
    count:          1400,
    speed:          0.30,
    connectionDist: 0.28,
    particleSize:   3.0,
    opacity:        0.60,
    color:          '#52c7b8',
    lineOpacity:    0.13,
  },
  vibrant: {
    count:          2000,
    speed:          0.45,
    connectionDist: 0.34,
    particleSize:   3.2,
    opacity:        0.72,
    color:          '#f9d342',
    lineOpacity:    0.18,
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Parse a CSS hex colour string to a THREE.Color. */
export function parseHexColor(hex: string): THREE.Color {
  return new THREE.Color(hex);
}

/**
 * Read --crystal-primary from the live computed style.
 * Falls back to the standard-tier hex if the token is unavailable.
 */
function getLiveColor(): string {
  if (typeof document === 'undefined') return '#a78bfa';
  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue('--crystal-primary')
    .trim();
  return raw || '#a78bfa';
}

function prefersReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}

// ---------------------------------------------------------------------------
// Shaders
// Soft circular sprite — no texture needed
// ---------------------------------------------------------------------------

const VERT_SHADER = /* glsl */`
  uniform float uSize;
  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize  = uSize * (300.0 / -mvPosition.z);
    gl_Position   = projectionMatrix * mvPosition;
  }
`;

const FRAG_SHADER = /* glsl */`
  uniform vec3  uColor;
  uniform float uOpacity;
  void main() {
    // Soft circular disc
    float d = length(gl_PointCoord - vec2(0.5));
    if (d > 0.5) discard;
    float alpha = smoothstep(0.5, 0.2, d) * uOpacity;
    gl_FragColor = vec4(uColor, alpha);
  }
`;

// ---------------------------------------------------------------------------
// FieldParticles
// ---------------------------------------------------------------------------

export class FieldParticles {
  private canvas:    HTMLCanvasElement;
  private renderer: THREE.WebGLRenderer;
  private scene:    THREE.Scene;
  private camera:   THREE.PerspectiveCamera;
  private rafId:    number | null = null;

  private points:   THREE.Points | null       = null;
  private lines:    THREE.LineSegments | null  = null;

  private positions:  Float32Array = new Float32Array(0);
  private velocities: Float32Array = new Float32Array(0);
  private phases:     Float32Array = new Float32Array(0);

  private currentTier: AlignmentTier = 'standard';
  private clock = new THREE.Clock();

  // Page Visibility pause
  private _visibilityHandler: () => void;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      alpha:     true,
      antialias: false,   // off for performance — particles don't need MSAA
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);

    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
    this.camera.position.z = 3;

    // Resize observer
    const ro = new ResizeObserver(() => this._onResize());
    ro.observe(canvas.parentElement ?? document.body);
    this._onResize();

    // Page Visibility API — pause when hidden
    this._visibilityHandler = () => {
      if (document.hidden) {
        this._stopLoop();
      } else {
        this._startLoop();
      }
    };
    document.addEventListener('visibilitychange', this._visibilityHandler);
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /** Set or change the alignment tier. Crossfades the particle field. */
  setTier(tier: AlignmentTier): void {
    if (tier === this.currentTier && this.points) return;
    this.currentTier = tier;
    this._buildField(tier);
    if (!this.rafId) this._startLoop();
  }

  /** Clean up all Three.js resources. */
  dispose(): void {
    this._stopLoop();
    document.removeEventListener('visibilitychange', this._visibilityHandler);
    this._clearMeshes();
    this.renderer.dispose();
  }

  // ---------------------------------------------------------------------------
  // Private — field construction
  // ---------------------------------------------------------------------------

  private _buildField(tier: AlignmentTier): void {
    const cfg   = TIER_PARTICLE_CONFIG[tier];
    const count = cfg.count;
    const color = parseHexColor(getLiveColor());  // live token

    // ── 1. Positions, velocities, phases ──
    const pos   = new Float32Array(count * 3);
    const vel   = new Float32Array(count * 3);
    const phase = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      // Spread particles in a sphere of radius 2
      const theta = Math.random() * Math.PI * 2;
      const phi   = Math.acos(2 * Math.random() - 1);
      const r     = 1.5 + Math.random() * 0.8;
      pos[i3]     = r * Math.sin(phi) * Math.cos(theta);
      pos[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i3 + 2] = r * Math.cos(phi);

      // Random drift velocity
      vel[i3]     = (Math.random() - 0.5) * 0.001;
      vel[i3 + 1] = (Math.random() - 0.5) * 0.001;
      vel[i3 + 2] = (Math.random() - 0.5) * 0.0005;

      phase[i] = Math.random() * Math.PI * 2;
    }

    this.positions  = pos;
    this.velocities = vel;
    this.phases     = phase;

    // ── 2. Build Points geometry ──
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uColor:   { value: color },
        uSize:    { value: cfg.particleSize },
        uOpacity: { value: 0 },            // start transparent for fade-in
      },
      vertexShader:   VERT_SHADER,
      fragmentShader: FRAG_SHADER,
      transparent:    true,
      depthWrite:     false,
      blending:       THREE.AdditiveBlending,
    });

    const newPoints = new THREE.Points(geo, mat);

    // ── 3. Connection lines ──
    let newLines: THREE.LineSegments | null = null;
    if (cfg.connectionDist > 0 && cfg.count <= 1400) {
      // Only compute connections for smaller counts (O(n²) guard)
      const linePairs: number[] = [];
      const distSq = cfg.connectionDist * cfg.connectionDist;
      for (let i = 0; i < count; i++) {
        for (let j = i + 1; j < count; j++) {
          const dx = pos[i*3]   - pos[j*3];
          const dy = pos[i*3+1] - pos[j*3+1];
          const dz = pos[i*3+2] - pos[j*3+2];
          if (dx*dx + dy*dy + dz*dz < distSq) {
            linePairs.push(
              pos[i*3], pos[i*3+1], pos[i*3+2],
              pos[j*3], pos[j*3+1], pos[j*3+2],
            );
          }
        }
      }
      if (linePairs.length > 0) {
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute('position',
          new THREE.BufferAttribute(new Float32Array(linePairs), 3));
        const lineMat = new THREE.LineBasicMaterial({
          color,
          transparent: true,
          opacity:     0,
          depthWrite:  false,
          blending:    THREE.AdditiveBlending,
        });
        newLines = new THREE.LineSegments(lineGeo, lineMat);
      }
    }

    // ── 4. Crossfade: fade out old, fade in new ──
    const oldPoints = this.points;
    const oldLines  = this.lines;

    // Add new meshes
    this.scene.add(newPoints);
    if (newLines) this.scene.add(newLines);
    this.points = newPoints;
    this.lines  = newLines;

    if (prefersReducedMotion()) {
      // Instant swap
      (mat.uniforms['uOpacity'].value) = cfg.opacity;
      if (newLines) (newLines.material as THREE.LineBasicMaterial).opacity = cfg.lineOpacity;
      if (oldPoints) { this.scene.remove(oldPoints); oldPoints.geometry.dispose(); (oldPoints.material as THREE.Material).dispose(); }
      if (oldLines)  { this.scene.remove(oldLines);  oldLines.geometry.dispose();  (oldLines.material  as THREE.Material).dispose(); }
    } else {
      // GSAP crossfade over 1.5s
      gsap.to(mat.uniforms['uOpacity'], { value: cfg.opacity, duration: 1.5, ease: 'power2.inOut' });
      if (newLines) {
        const lm = newLines.material as THREE.LineBasicMaterial;
        gsap.to(lm, { opacity: cfg.lineOpacity, duration: 1.5, ease: 'power2.inOut' });
      }
      if (oldPoints) {
        const om = oldPoints.material as THREE.ShaderMaterial;
        gsap.to(om.uniforms['uOpacity'], {
          value: 0, duration: 0.8, ease: 'power2.in',
          onComplete: () => {
            this.scene.remove(oldPoints);
            oldPoints.geometry.dispose();
            om.dispose();
          },
        });
      }
      if (oldLines) {
        const lm = oldLines.material as THREE.LineBasicMaterial;
        gsap.to(lm, {
          opacity: 0, duration: 0.8, ease: 'power2.in',
          onComplete: () => {
            this.scene.remove(oldLines!);
            oldLines!.geometry.dispose();
            lm.dispose();
          },
        });
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Private — animation loop
  // ---------------------------------------------------------------------------

  private _startLoop(): void {
    if (this.rafId) return;
    this.clock.start();
    const loop = () => {
      this.rafId = requestAnimationFrame(loop);
      this._tick();
    };
    loop();
  }

  private _stopLoop(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  private _tick(): void {
    const t   = this.clock.getElapsedTime();
    const cfg = TIER_PARTICLE_CONFIG[this.currentTier];
    const pos = this.positions;
    const vel = this.velocities;
    const ph  = this.phases;
    const count = cfg.count;
    const geo = this.points?.geometry;
    if (!geo) return;

    const posAttr = geo.attributes['position'] as THREE.BufferAttribute;

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      // Lissajous drift: sinusoidal displacement in each axis
      const wave = Math.sin(t * cfg.speed + ph[i]) * 0.002;
      pos[i3]     += vel[i3]     + wave;
      pos[i3 + 1] += vel[i3 + 1] + Math.cos(t * cfg.speed * 0.7 + ph[i]) * 0.002;
      pos[i3 + 2] += vel[i3 + 2];

      // Soft boundary: particles beyond radius 2.5 reverse velocity
      const r2 = pos[i3]*pos[i3] + pos[i3+1]*pos[i3+1] + pos[i3+2]*pos[i3+2];
      if (r2 > 6.25) {  // 2.5^2
        vel[i3]     *= -0.8;
        vel[i3 + 1] *= -0.8;
        vel[i3 + 2] *= -0.8;
      }
    }

    posAttr.needsUpdate = true;

    // Slow camera rotation for depth parallax
    if (this.scene.children.length > 0) {
      this.scene.rotation.y = t * 0.025;
      this.scene.rotation.x = Math.sin(t * 0.012) * 0.12;
    }

    this.renderer.render(this.scene, this.camera);
  }

  private _onResize(): void {
    const el = this.canvas.parentElement ?? document.body;
    const w  = el.clientWidth  || window.innerWidth;
    const h  = el.clientHeight || window.innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  private _clearMeshes(): void {
    [this.points, this.lines].forEach(mesh => {
      if (!mesh) return;
      this.scene.remove(mesh);
      mesh.geometry.dispose();
      (mesh.material as THREE.Material).dispose();
    });
    this.points = null;
    this.lines  = null;
  }
}
