/* ==========================================================================
   Source 2 Destination — Enterprise Toast & Notification System
   File: assets/js/notifications.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function ensureStack() {
    let stack = document.getElementById('s2d-toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 's2d-toast-stack';
      stack.className = 's2d-toast-stack';
      stack.setAttribute('aria-live', 'polite');
      document.body.appendChild(stack);
    }
    return stack;
  }

  function show(options) {
    const opts = typeof options === 'string' ? { title: options } : (options || {});
    const title = opts.title || 'Action Simulated';
    const description = opts.description || 'Updated in temporary demonstration memory (resets on page refresh).';
    const type = opts.type || 'info'; // success | warning | danger | info
    const duration = opts.duration || 4200;

    const iconMap = {
      success: { icon: 'check-circle-2', color: '#10B981' },
      warning: { icon: 'alert-triangle', color: '#F59E0B' },
      danger:  { icon: 'alert-octagon',  color: '#EF4444' },
      info:    { icon: 'info',           color: '#818CF8' }
    };
    const meta = iconMap[type] || iconMap.info;

    const stack = ensureStack();
    const toast = document.createElement('div');
    toast.className = 's2d-toast';
    toast.innerHTML = `
      <span style="color:${meta.color};display:inline-flex;margin-top:2px;">
        <i data-lucide="${meta.icon}"></i>
      </span>
      <div style="flex:1;min-width:0;">
        <div class="s2d-toast-title">${escapeHtml(title)}</div>
        <div class="s2d-toast-desc">${escapeHtml(description)}</div>
      </div>
      <button type="button" aria-label="Dismiss notification" style="background:transparent;border:none;color:#94A3B8;cursor:pointer;padding:2px;">
        <i data-lucide="x" style="width:15px;height:15px;"></i>
      </button>
    `;

    stack.appendChild(toast);
    if (window.lucide) window.lucide.createIcons({ nodes: [toast] });

    const closeBtn = toast.querySelector('button');
    const removeToast = () => {
      if (!toast.parentNode) return;
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(6px)';
      toast.style.transition = 'opacity 160ms ease, transform 160ms ease';
      setTimeout(() => toast.remove(), 170);
    };

    closeBtn.addEventListener('click', removeToast);
    setTimeout(removeToast, duration);
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  window.S2DNotify = { show, escapeHtml };
})(window, document);
