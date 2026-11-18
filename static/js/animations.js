/* ==========================================================================
   Source 2 Destination — Restrained GSAP Micro-Interactions & Tab Controller
   File: assets/js/animations.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function initAnimations() {
    // Card entrance/hover animations intentionally disabled for clean, static dashboard UX
  }

  function initTabs() {
    document.querySelectorAll('[data-s2d-tabs]').forEach((tabBar) => {
      const scopeId = tabBar.getAttribute('data-s2d-tabs');
      const buttons = tabBar.querySelectorAll('[data-tab-target]');

      buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
          const targetId = btn.getAttribute('data-tab-target');
          buttons.forEach((b) => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
          });
          btn.classList.add('active');
          btn.setAttribute('aria-selected', 'true');

          const container = scopeId ? document.getElementById(scopeId) : tabBar.parentElement;
          const panels = container
            ? container.querySelectorAll(':scope > .s2d-tab-panel, .s2d-tab-panel[data-tab-group="' + scopeId + '"]')
            : document.querySelectorAll('.s2d-tab-panel');

          panels.forEach((panel) => {
            panel.classList.toggle('active', panel.id === targetId);
          });

          // Trigger resize so ApexCharts inside newly revealed tabs size properly
          setTimeout(() => window.dispatchEvent(new Event('resize')), 40);
        });
      });
    });
  }

  window.S2DAnimations = { initAnimations, initTabs };
})(window, document);
