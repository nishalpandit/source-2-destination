/* ==========================================================================
   Source 2 Destination — Role-Aware Navigation Blueprints & Global Search
   File: assets/js/navigation.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  const ROLE_NAVIGATION = {
    'super-admin': {
      roleLabel: 'Super Admin',
      portalTitle: 'Global Governance',
      homeRoute: 'super-admin/dashboard.html',
      settingsRoute: 'super-admin/settings/general.html',
      notificationsRoute: 'super-admin/settings/notifications.html',
      groups: [
        {
          label: 'Executive Command',
          items: [
            { id: 'sa-dashboard', label: 'Dashboard Overview', icon: 'layout-dashboard', href: 'super-admin/dashboard.html' }
          ]
        },
        {
          label: 'Institutions & Access',
          items: [
            {
              id: 'sa-schools', label: 'School Management', icon: 'building-2',
              children: [
                { label: 'School Directory', href: 'super-admin/schools/list.html' },
                { label: 'Add New School', href: 'super-admin/schools/add.html' },
                { label: 'Edit School Record', href: 'super-admin/schools/edit.html' },
                { label: 'School 360° Details', href: 'super-admin/schools/details.html' }
              ]
            },
            {
              id: 'sa-school-admins', label: 'School Administrators', icon: 'user-cog',
              children: [
                { label: 'Administrator List', href: 'super-admin/school-admins/list.html' },
                { label: 'Add School Admin', href: 'super-admin/school-admins/add.html' },
                { label: 'Edit School Admin', href: 'super-admin/school-admins/edit.html' },
                { label: 'Admin Profile & Logs', href: 'super-admin/school-admins/details.html' }
              ]
            }
          ]
        },
        {
          label: 'Calling Policy & Credits',
          items: [
            {
              id: 'sa-validity', label: 'Calling Validity', icon: 'calendar-check-2',
              children: [
                { label: 'Validity Records & Alerts', href: 'super-admin/validity/overview.html' },
                { label: 'Global Validity Rules', href: 'super-admin/validity/rules.html' }
              ]
            },
            {
              id: 'sa-recharges', label: 'Recharge Management', icon: 'zap',
              children: [
                { label: 'Plans & Credit Allocation', href: 'super-admin/recharges/overview.html' },
                { label: 'Create / Edit Plan', href: 'super-admin/recharges/create-plan.html' },
                { label: 'Recharge Ledger', href: 'super-admin/recharges/history.html' }
              ]
            },
            { id: 'sa-duration', label: 'Calling Duration Caps', icon: 'timer', href: 'super-admin/calling-duration/index.html' },
            { id: 'sa-schedules', label: 'Calling Schedules', icon: 'clock-4', href: 'super-admin/calling-schedules/index.html' },
            { id: 'sa-call-history', label: 'Global Call History', icon: 'phone-call', href: 'super-admin/call-history/index.html' }
          ]
        },
        {
          label: 'Billing & Fleet',
          items: [
            {
              id: 'sa-subscriptions', label: 'Subscriptions', icon: 'layers',
              children: [
                { label: 'Plans & School Status', href: 'super-admin/subscriptions/overview.html' },
                { label: 'Create / Assign Plan', href: 'super-admin/subscriptions/create.html' }
              ]
            },
            {
              id: 'sa-payments', label: 'Payments & Ledger', icon: 'credit-card',
              children: [
                { label: 'Transaction Overview', href: 'super-admin/payments/overview.html' },
                { label: 'Payment Receipt Detail', href: 'super-admin/payments/details.html' }
              ]
            },
            {
              id: 'sa-devices', label: 'Device Fleet (MDM)', icon: 'tablet-smartphone',
              children: [
                { label: 'Device Registry & Compliance', href: 'super-admin/devices/list.html' },
                { label: 'Register & Assign Device', href: 'super-admin/devices/register.html' },
                { label: 'Device Telemetry Details', href: 'super-admin/devices/details.html' }
              ]
            },
            { id: 'sa-reports', label: 'School-wise Reports', icon: 'bar-chart-3', href: 'super-admin/reports/index.html' }
          ]
        },
        {
          label: 'Governance & System',
          items: [
            {
              id: 'sa-roles', label: 'Roles & Permissions', icon: 'shield-check',
              children: [
                { label: 'Roles & Permission Matrix', href: 'super-admin/roles-permissions/list.html' },
                { label: 'Create / Edit Role', href: 'super-admin/roles-permissions/create.html' }
              ]
            },
            {
              id: 'sa-settings', label: 'Settings & Audit', icon: 'settings',
              children: [
                { label: 'General & Admin Settings', href: 'super-admin/settings/general.html' },
                { label: 'Notification Templates', href: 'super-admin/settings/notifications.html' },
                { label: 'Audit Activity Log', href: 'super-admin/settings/audit-logs.html' }
              ]
            }
          ]
        }
      ]
    },

    'franchise': {
      roleLabel: 'Franchise Partner',
      portalTitle: 'Territory Operations',
      homeRoute: 'franchise/dashboard.html',
      settingsRoute: 'franchise/settings/index.html',
      notificationsRoute: 'franchise/settings/index.html',
      groups: [
        {
          label: 'Partner Overview',
          items: [
            { id: 'fr-dashboard', label: 'Franchise Dashboard', icon: 'layout-dashboard', href: 'franchise/dashboard.html' }
          ]
        },
        {
          label: 'Campus & Student Ops',
          items: [
            {
              id: 'fr-schools', label: 'Assigned Schools', icon: 'building-2',
              children: [
                { label: 'Assigned School List', href: 'franchise/schools/list.html' },
                { label: 'Onboard School', href: 'franchise/schools/add.html' },
                { label: 'Edit School Record', href: 'franchise/schools/edit.html' },
                { label: 'School Details', href: 'franchise/schools/details.html' }
              ]
            },
            {
              id: 'fr-students', label: 'Student Directory', icon: 'users',
              children: [
                { label: 'Student List', href: 'franchise/students/list.html' },
                { label: 'Add Student', href: 'franchise/students/add.html' },
                { label: 'Edit Student', href: 'franchise/students/edit.html' },
                { label: 'Student Profile', href: 'franchise/students/details.html' }
              ]
            },
            { id: 'fr-bulk', label: 'Bulk Student Upload', icon: 'file-spreadsheet', href: 'franchise/bulk-upload/index.html' },
            { id: 'fr-classes', label: 'Classes & Sections', icon: 'book-open', href: 'franchise/classes/index.html' }
          ]
        },
        {
          label: 'Calling & Validity',
          items: [
            { id: 'fr-validity', label: 'Student Validity', icon: 'calendar-clock', href: 'franchise/validity/index.html' },
            { id: 'fr-recharges', label: 'Recharge Management', icon: 'zap', href: 'franchise/recharges/index.html' },
            { id: 'fr-duration', label: 'Calling Duration', icon: 'timer', href: 'franchise/calling-duration/index.html' },
            { id: 'fr-schedules', label: 'Calling Schedules', icon: 'clock-4', href: 'franchise/calling-schedules/index.html' },
            { id: 'fr-calls', label: 'Call History', icon: 'phone-call', href: 'franchise/call-history/index.html' }
          ]
        },
        {
          label: 'Commercials & Analytics',
          items: [
            { id: 'fr-commissions', label: 'Revenue & Commissions', icon: 'coins', href: 'franchise/commissions/index.html' },
            { id: 'fr-transactions', label: 'Payment & Transactions', icon: 'receipt', href: 'franchise/transactions/index.html' },
            { id: 'fr-reports', label: 'School & Student Reports', icon: 'bar-chart-3', href: 'franchise/reports/index.html' },
            { id: 'fr-settings', label: 'Profile & Settings', icon: 'settings', href: 'franchise/settings/index.html' }
          ]
        }
      ]
    },

    'school-admin': {
      roleLabel: 'School Admin',
      portalTitle: 'Campus & Hostel Ops',
      homeRoute: 'school-admin/dashboard.html',
      settingsRoute: 'school-admin/settings/index.html',
      notificationsRoute: 'school-admin/settings/index.html',
      groups: [
        {
          label: 'Campus Command',
          items: [
            { id: 'sa2-dashboard', label: 'School Dashboard', icon: 'layout-dashboard', href: 'school-admin/dashboard.html' }
          ]
        },
        {
          label: 'Students & Families',
          items: [
            {
              id: 'sa2-students', label: 'Student Management', icon: 'graduation-cap',
              children: [
                { label: 'Student Directory', href: 'school-admin/students/list.html' },
                { label: 'Enroll Student', href: 'school-admin/students/add.html' },
                { label: 'Edit Student', href: 'school-admin/students/edit.html' },
                { label: 'Student 360° Details', href: 'school-admin/students/details.html' }
              ]
            },
            { id: 'sa2-bulk', label: 'Bulk Student Upload', icon: 'file-spreadsheet', href: 'school-admin/bulk-upload/index.html' },
            {
              id: 'sa2-classes', label: 'Classes & Sections', icon: 'layout-grid',
              children: [
                { label: 'Manage Classes', href: 'school-admin/classes/list.html' },
                { label: 'Manage Sections', href: 'school-admin/classes/sections.html' }
              ]
            },
            {
              id: 'sa2-guardians', label: 'Parents & Guardians', icon: 'heart-handshake',
              children: [
                { label: 'Guardian & Whitelist', href: 'school-admin/guardians/list.html' },
                { label: 'Add Guardian', href: 'school-admin/guardians/add.html' },
                { label: 'Edit Guardian', href: 'school-admin/guardians/edit.html' },
                { label: 'Guardian Details', href: 'school-admin/guardians/details.html' }
              ]
            },
            { id: 'sa2-codes', label: 'Student Unique Codes', icon: 'key-round', href: 'school-admin/student-codes/index.html' },
            { id: 'sa2-status', label: 'Activation & Status', icon: 'user-check', href: 'school-admin/student-status/index.html' }
          ]
        },
        {
          label: 'Calling Rules & Credits',
          items: [
            { id: 'sa2-schedules', label: 'Calling Schedules', icon: 'calendar-range', href: 'school-admin/calling-schedules/index.html' },
            { id: 'sa2-duration', label: 'Calling Duration', icon: 'timer', href: 'school-admin/calling-duration/index.html' },
            { id: 'sa2-validity', label: 'Student Validity', icon: 'calendar-check-2', href: 'school-admin/validity/index.html' },
            {
              id: 'sa2-recharges', label: 'Recharge Desk', icon: 'zap',
              children: [
                { label: 'Overview & History', href: 'school-admin/recharges/overview.html' },
                { label: 'Recharge Student Account', href: 'school-admin/recharges/student-recharge.html' }
              ]
            },
            { id: 'sa2-calls', label: 'Campus Call History', icon: 'phone-call', href: 'school-admin/call-history/index.html' }
          ]
        },
        {
          label: 'Hostel & Reporting',
          items: [
            {
              id: 'sa2-devices', label: 'Device Assignments', icon: 'tablet-smartphone',
              children: [
                { label: 'Booth & Device List', href: 'school-admin/device-assignments/list.html' },
                { label: 'Assign Device', href: 'school-admin/device-assignments/assign.html' }
              ]
            },
            {
              id: 'sa2-wardens', label: 'Hostel Wardens', icon: 'badge-check',
              children: [
                { label: 'Warden Directory', href: 'school-admin/hostel-wardens/list.html' },
                { label: 'Add Warden', href: 'school-admin/hostel-wardens/add.html' },
                { label: 'Edit Warden', href: 'school-admin/hostel-wardens/edit.html' },
                { label: 'Warden Details', href: 'school-admin/hostel-wardens/details.html' }
              ]
            },
            { id: 'sa2-student-reports', label: 'Student-wise Reports', icon: 'file-bar-chart', href: 'school-admin/student-reports/index.html' },
            { id: 'sa2-class-reports', label: 'Class-wise Reports', icon: 'pie-chart', href: 'school-admin/class-reports/index.html' },
            { id: 'sa2-settings', label: 'Profile & Settings', icon: 'settings', href: 'school-admin/settings/index.html' }
          ]
        }
      ]
    }
  };

  function getRootPrefix() {
    const bodyPrefix = document.body.getAttribute('data-root');
    if (bodyPrefix !== null) return bodyPrefix;
    return '../';
  }

  function resolveHref(relPath) {
    const prefix = getRootPrefix();
    return prefix + relPath;
  }

  function getCurrentRouteKey() {
    const explicit = document.body.getAttribute('data-route');
    if (explicit) return explicit;
    const path = window.location.pathname;
    const match = path.match(/((?:super-admin|franchise|school-admin|auth)\/.+\.html)$/);
    return match ? match[1] : 'index.html';
  }

  function flattenRoutes(role) {
    const cfg = ROLE_NAVIGATION[role];
    if (!cfg) return [];
    const list = [];
    cfg.groups.forEach((g) => {
      g.items.forEach((item) => {
        if (item.href) {
          list.push({ label: item.label, group: g.label, href: item.href, icon: item.icon });
        }
        if (item.children) {
          item.children.forEach((ch) => {
            list.push({ label: `${item.label} — ${ch.label}`, group: g.label, href: ch.href, icon: item.icon });
          });
        }
      });
    });
    return list;
  }

  function initGlobalCommandSearch(role) {
    let modal = document.getElementById('s2d-cmd-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 's2d-cmd-modal';
      modal.className = 's2d-modal-backdrop';
      modal.innerHTML = `
        <div class="s2d-modal-dialog" style="max-width:580px;align-self:flex-start;margin-top:7vh;">
          <div style="padding:14px 18px;border-bottom:1px solid var(--s2d-border);display:flex;align-items:center;gap:10px;">
            <i data-lucide="search" style="color:var(--s2d-text-muted);"></i>
            <input type="text" id="s2d-cmd-input" placeholder="Jump to module, student, school, or setting..." style="flex:1;border:none;outline:none;font-size:0.9rem;color:var(--s2d-heading);background:transparent;" autocomplete="off">
            <span class="topbar-kbd">ESC</span>
          </div>
          <div id="s2d-cmd-results" style="max-height:360px;overflow-y:auto;padding:8px;"></div>
          <div style="padding:9px 16px;border-top:1px solid var(--s2d-border);background:var(--s2d-surface-subtle);font-size:0.73rem;color:var(--s2d-text-secondary);display:flex;justify-content:space-between;border-radius:0 0 16px 16px;">
            <span>Role-scoped quick navigation (${(ROLE_NAVIGATION[role] && ROLE_NAVIGATION[role].roleLabel) || 'Portal'})</span>
            <span>Enter to navigate</span>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
      if (window.lucide) window.lucide.createIcons({ nodes: [modal] });
    }

    const input = modal.querySelector('#s2d-cmd-input');
    const resultsBox = modal.querySelector('#s2d-cmd-results');
    const routes = flattenRoutes(role);

    function renderResults(q) {
      const term = (q || '').toLowerCase().trim();
      const filtered = routes.filter((r) => !term || r.label.toLowerCase().includes(term) || r.group.toLowerCase().includes(term)).slice(0, 12);

      if (!filtered.length) {
        resultsBox.innerHTML = `<div style="padding:28px;text-align:center;color:var(--s2d-text-secondary);font-size:0.82rem;">No matching modules found for "${window.S2DNotify.escapeHtml(q)}".</div>`;
        return;
      }

      resultsBox.innerHTML = filtered.map((r, idx) => `
        <a href="${resolveHref(r.href)}" class="s2d-dropdown-item ${idx === 0 ? 'cmd-first' : ''}" style="padding:9px 12px;justify-content:space-between;">
          <span style="display:flex;align-items:center;gap:10px;">
            <i data-lucide="${r.icon || 'arrow-right'}" style="width:16px;height:16px;color:var(--s2d-primary);"></i>
            <span>${window.S2DNotify.escapeHtml(r.label)}</span>
          </span>
          <span style="font-size:0.71rem;color:var(--s2d-text-muted);">${window.S2DNotify.escapeHtml(r.group)}</span>
        </a>
      `).join('');
      if (window.lucide) window.lucide.createIcons({ nodes: [resultsBox] });
    }

    const openCmd = () => {
      modal.classList.add('show');
      input.value = '';
      renderResults('');
      setTimeout(() => input.focus(), 40);
    };

    document.querySelectorAll('[data-open-cmd-search]').forEach((btn) => {
      btn.addEventListener('click', openCmd);
    });

    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCmd();
      }
    });

    input.addEventListener('input', () => renderResults(input.value));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const first = resultsBox.querySelector('a');
        if (first) window.location.href = first.getAttribute('href');
      }
    });
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('show');
    });
  }

  window.S2DNavigation = {
    ROLE_NAVIGATION,
    getRootPrefix,
    resolveHref,
    getCurrentRouteKey,
    initGlobalCommandSearch
  };
})(window, document);
