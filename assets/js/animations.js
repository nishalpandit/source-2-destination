/* ==========================================================================
   Source 2 Destination — Restrained GSAP Micro-Interactions & Tab Controller
   File: assets/js/animations.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function initAnimations() {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced || !window.gsap) return;

    const kpiCards = document.querySelectorAll('.kpi-card');
    if (kpiCards.length) {
      window.gsap.fromTo(
        kpiCards,
        { opacity: 0, y: 8 },
        { opacity: 1, y: 0, duration: 0.24, stagger: 0.025, ease: 'power2.out', clearProps: 'transform,opacity' }
      );
    }

    const mainCards = document.querySelectorAll('.s2d-card, .chart-card, .table-card, .auth-card');
    if (mainCards.length && mainCards.length <= 16) {
      window.gsap.fromTo(
        mainCards,
        { opacity: 0, y: 6 },
        { opacity: 1, y: 0, duration: 0.26, stagger: 0.03, ease: 'power2.out', clearProps: 'transform,opacity' }
      );
    }
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
