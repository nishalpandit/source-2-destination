/* ==========================================================================
   Source 2 Destination — Modals, Confirmation Dialogs & Slide-Over Drawers
   File: assets/js/modals.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function ensureConfirmModal() {
    let backdrop = document.getElementById('s2d-confirm-backdrop');
    if (backdrop) return backdrop;

    backdrop = document.createElement('div');
    backdrop.id = 's2d-confirm-backdrop';
    backdrop.className = 's2d-modal-backdrop';
    backdrop.setAttribute('role', 'dialog');
    backdrop.setAttribute('aria-modal', 'true');
    backdrop.innerHTML = `
      <div class="s2d-modal-dialog modal-sm">
        <div class="s2d-modal-header">
          <div style="display:flex;align-items:center;gap:10px;">
            <span id="s2d-confirm-icon-wrap" class="kpi-icon rose" style="width:34px;height:34px;">
              <i data-lucide="alert-triangle" id="s2d-confirm-icon"></i>
            </span>
            <h3 class="s2d-card-title" id="s2d-confirm-title">Confirm Action</h3>
          </div>
          <button type="button" class="btn-s2d btn-s2d-ghost btn-icon-s2d" data-confirm-cancel aria-label="Close modal">
            <i data-lucide="x"></i>
          </button>
        </div>
        <div class="s2d-modal-body">
          <div class="mono-code mb-2" id="s2d-confirm-record" style="display:inline-block;padding:3px 8px;background:#F1F5F9;border-radius:5px;color:#0F172A;font-weight:600;"></div>
          <p id="s2d-confirm-message" class="text-secondary-s2d mb-3" style="font-size:0.84rem;line-height:1.55;"></p>
          <div class="s2d-callout amber" style="padding:10px 12px;font-size:0.76rem;">
            <i data-lucide="shield-alert" style="width:16px;height:16px;margin-top:1px;"></i>
            <span><strong>Demo Simulation:</strong> This state change applies to in-memory demonstration records and will reset on page refresh until connected to the Django REST API.</span>
          </div>
        </div>
        <div class="s2d-modal-footer">
          <button type="button" class="btn-s2d btn-s2d-secondary" data-confirm-cancel>Cancel</button>
          <button type="button" class="btn-s2d btn-s2d-danger" id="s2d-confirm-accept">Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(backdrop);
    if (window.lucide) window.lucide.createIcons({ nodes: [backdrop] });
    return backdrop;
  }

  function confirm(options) {
    const opts = options || {};
    const backdrop = ensureConfirmModal();
    const titleEl = backdrop.querySelector('#s2d-confirm-title');
    const recordEl = backdrop.querySelector('#s2d-confirm-record');
    const msgEl = backdrop.querySelector('#s2d-confirm-message');
    const acceptBtn = backdrop.querySelector('#s2d-confirm-accept');
    const iconWrap = backdrop.querySelector('#s2d-confirm-icon-wrap');

    titleEl.textContent = opts.title || 'Confirm Status Change';
    recordEl.textContent = opts.recordLabel || 'Selected Record';
    recordEl.style.display = opts.recordLabel ? 'inline-block' : 'none';
    msgEl.textContent = opts.message || 'Are you sure you want to proceed with this administrative action?';
    acceptBtn.textContent = opts.confirmLabel || 'Confirm Action';

    const variant = opts.variant || 'danger'; // danger | success | primary
    acceptBtn.className = 'btn-s2d ' + (
      variant === 'success' ? 'btn-s2d-success' :
      variant === 'primary' ? 'btn-s2d-primary' : 'btn-s2d-danger'
    );
    iconWrap.className = 'kpi-icon ' + (
      variant === 'success' ? 'emerald' :
      variant === 'primary' ? '' : 'rose'
    );

    backdrop.classList.add('show');

    return new Promise((resolve) => {
      const cleanup = () => {
        backdrop.classList.remove('show');
        acceptBtn.removeEventListener('click', onAccept);
        cancelBtns.forEach((b) => b.removeEventListener('click', onCancel));
        backdrop.removeEventListener('click', onBackdrop);
      };
      const onAccept = () => { cleanup(); resolve(true); };
      const onCancel = () => { cleanup(); resolve(false); };
      const onBackdrop = (e) => { if (e.target === backdrop) onCancel(); };

      const cancelBtns = backdrop.querySelectorAll('[data-confirm-cancel]');
      acceptBtn.addEventListener('click', onAccept);
      cancelBtns.forEach((b) => b.addEventListener('click', onCancel));
      backdrop.addEventListener('click', onBackdrop);
    });
  }

  function openById(modalId) {
    const el = document.getElementById(modalId);
    if (!el) return;
    el.classList.add('show');
  }

  function closeById(modalId) {
    const el = document.getElementById(modalId);
    if (!el) return;
    el.classList.remove('show');
  }

  function ensureDrawer() {
    let backdrop = document.getElementById('s2d-inspector-drawer');
    if (backdrop) return backdrop;

    backdrop = document.createElement('div');
    backdrop.id = 's2d-inspector-drawer';
    backdrop.className = 's2d-drawer-backdrop';
    backdrop.innerHTML = `
      <aside class="s2d-drawer" role="dialog" aria-label="Record Details">
        <div class="s2d-modal-header">
          <div>
            <div class="page-eyebrow" id="s2d-drawer-eyebrow" style="margin-bottom:2px;">RECORD INSPECTOR</div>
            <h3 class="s2d-card-title" id="s2d-drawer-title">Details</h3>
          </div>
          <button type="button" class="btn-s2d btn-s2d-ghost btn-icon-s2d" data-drawer-close aria-label="Close panel">
            <i data-lucide="x"></i>
          </button>
        </div>
        <div class="s2d-drawer-body" id="s2d-drawer-body"></div>
        <div class="s2d-modal-footer" id="s2d-drawer-footer">
          <button type="button" class="btn-s2d btn-s2d-secondary" data-drawer-close>Close</button>
        </div>
      </aside>
    `;
    document.body.appendChild(backdrop);
    if (window.lucide) window.lucide.createIcons({ nodes: [backdrop] });

    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop || e.target.closest('[data-drawer-close]')) {
        backdrop.classList.remove('show');
      }
    });
    return backdrop;
  }

  function openDrawer(options) {
    const opts = options || {};
    const backdrop = ensureDrawer();
    backdrop.querySelector('#s2d-drawer-eyebrow').textContent = opts.eyebrow || 'RECORD DETAILS';
    backdrop.querySelector('#s2d-drawer-title').textContent = opts.title || 'Record Summary';
    const bodyEl = backdrop.querySelector('#s2d-drawer-body');
    bodyEl.innerHTML = opts.html || '';
    const footerEl = backdrop.querySelector('#s2d-drawer-footer');
    if (opts.footerHtml) {
      footerEl.innerHTML = opts.footerHtml;
    } else {
      footerEl.innerHTML = `<button type="button" class="btn-s2d btn-s2d-secondary" data-drawer-close>Close Inspector</button>`;
    }
    if (window.lucide) window.lucide.createIcons({ nodes: [backdrop] });
    backdrop.classList.add('show');
  }

  // Declarative modal triggers [data-modal-open="id"] and [data-modal-close]
  function bindDeclarativeModals() {
    document.addEventListener('click', (e) => {
      const opener = e.target.closest('[data-modal-open]');
      if (opener) {
        e.preventDefault();
        openById(opener.getAttribute('data-modal-open'));
        return;
      }
      const closer = e.target.closest('[data-modal-close]');
      if (closer) {
        e.preventDefault();
        const parentModal = closer.closest('.s2d-modal-backdrop');
        if (parentModal) parentModal.classList.remove('show');
      }
      if (e.target.classList && e.target.classList.contains('s2d-modal-backdrop') && e.target.id !== 's2d-confirm-backdrop') {
        e.target.classList.remove('show');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.s2d-modal-backdrop.show, .s2d-drawer-backdrop.show').forEach((el) => {
          if (el.id !== 's2d-confirm-backdrop') el.classList.remove('show');
        });
      }
    });
  }

  window.S2DModal = { confirm, openById, closeById, openDrawer, bindDeclarativeModals };
})(window, document);
