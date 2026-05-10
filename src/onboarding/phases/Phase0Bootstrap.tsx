// C-OB01 — Phase 0: Bootstrap
// Silent environment check. No UI rendered.
// Detects platform, GPU, disk space, network, locale, accessibility preferences.

import { useEffect } from 'react';
import { useOnboardingStore } from '../store/onboardingStore';
import type { SystemCapabilities } from '../types';

interface Phase0BootstrapProps {
  onComplete: () => void;
}

export function Phase0Bootstrap({ onComplete }: Phase0BootstrapProps) {
  const setSystem = useOnboardingStore((s) => s.setSystem);

  useEffect(() => {
    async function runBootstrap() {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const prefersHighContrast = window.matchMedia('(forced-colors: active)').matches;
      const hasScreenReader = document.querySelector('[aria-live]') !== null;

      let platform: SystemCapabilities['platform'] = 'unknown';
      let hasGpu = false;
      let diskSpaceGb = 0;
      let isOnline = navigator.onLine;
      const locale = navigator.language || 'en-US';

      // Try Tauri system info
      try {
        const { invoke } = await import('@tauri-apps/api/core');
        const caps = await invoke<SystemCapabilities>('check_system_capabilities');
        Object.assign(
          { platform, hasGpu, diskSpaceGb },
          { platform: caps.platform, hasGpu: caps.hasGpu, diskSpaceGb: caps.diskSpaceGb }
        );
        platform = caps.platform;
        hasGpu = caps.hasGpu;
        diskSpaceGb = caps.diskSpaceGb;
        isOnline = caps.isOnline;
      } catch {
        // Browser env — use navigator APIs
        const ua = navigator.userAgent.toLowerCase();
        if (ua.includes('win')) platform = 'windows';
        else if (ua.includes('mac')) platform = 'macos';
        else if (ua.includes('linux')) platform = 'linux';

        // Basic GPU check via WebGL
        try {
          const canvas = document.createElement('canvas');
          const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
          hasGpu = gl !== null;
        } catch {
          hasGpu = false;
        }
      }

      const capabilities: SystemCapabilities = {
        platform,
        hasGpu,
        diskSpaceGb,
        isOnline,
        locale,
        prefersReducedMotion,
        prefersHighContrast,
        hasScreenReader,
      };

      setSystem(capabilities);
      onComplete();
    }

    runBootstrap();
  }, [setSystem, onComplete]);

  // Phase 0 renders no UI — it is invisible
  return null;
}
