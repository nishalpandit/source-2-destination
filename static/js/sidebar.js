/* ==========================================================================
   Source 2 Destination — Shared Sidebar & Top Navigation Bar Controller
   File: assets/js/sidebar.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function getUserProfile(role) {
    const ctx = (window.S2D_DEMO && window.S2D_DEMO.currentContext) || {};
    if (role === 'franchise') return ctx.franchise || { fullName: 'Vikramaditya Singhania', initials: 'VS', email: 'v.singhania@northedunet.in', roleLabel: 'Franchise Partner' };
    if (role === 'school-admin') return ctx.schoolAdmin || { fullName: 'Dr. Ramesh Chandra Sharma', initials: 'RS', email: 'principal@doonvalley.edu.in', roleLabel: 'School Administrator' };
    return ctx.superAdmin || { fullName: 'Aarav Singhal', initials: 'AS', email: 'aarav.singhal@source2destination.in', roleLabel: 'Super Administrator' };
  }

  function renderSidebarAndTopbar() {
    const role = document.body.getAttribute('data-role');
    if (!role || !window.S2DNavigation.ROLE_NAVIGATION[role]) return;

    const navCfg = window.S2DNavigation.ROLE_NAVIGATION[role];
    const currentRoute = window.S2DNavigation.getCurrentRouteKey();
    const resolveHref = window.S2DNavigation.resolveHref;
    const user = getUserProfile(role);

    const sidebarMount = document.getElementById('app-sidebar');
    const topbarMount = document.getElementById('app-topbar');

    if (sidebarMount) {
      let groupsHtml = '';
      navCfg.groups.forEach((group) => {
        let itemsHtml = '';
        group.items.forEach((item) => {
          if (item.children && item.children.length) {
            const hasActiveChild = item.children.some((ch) => ch.href === currentRoute);
            const subHtml = item.children.map((ch) => {
              const isAct = ch.href === currentRoute;
              return `<a href="${resolveHref(ch.href)}" class="sidebar-sublink ${isAct ? 'active' : ''}">${ch.label}</a>`;
            }).join('');

            itemsHtml += `
              <div class="nav-item-box ${hasActiveChild ? 'open' : ''}">
                <button type="button" class="sidebar-parent-btn ${hasActiveChild ? 'active-parent' : ''}" aria-expanded="${hasActiveChild ? 'true' : 'false'}">
                  <span class="sidebar-link-icon"><i data-lucide="${item.icon}"></i></span>
                  <span class="sidebar-link-label">${item.label}</span>
                  <i data-lucide="chevron-right" class="sidebar-chevron"></i>
                </button>
                <div class="sidebar-tooltip">${item.label}</div>
                <div class="sidebar-submenu">${subHtml}</div>
              </div>
            `;
          } else {
            const isAct = item.href === currentRoute;
            itemsHtml += `
              <div class="nav-item-box">
                <a href="${resolveHref(item.href)}" class="sidebar-link ${isAct ? 'active' : ''}">
                  <span class="sidebar-link-icon"><i data-lucide="${item.icon}"></i></span>
                  <span class="sidebar-link-label">${item.label}</span>
                </a>
                <div class="sidebar-tooltip">${item.label}</div>
              </div>
            `;
          }
        });

        groupsHtml += `
          <div class="sidebar-group">
            <div class="sidebar-group-label">${group.label}</div>
            ${itemsHtml}
          </div>
        `;
      });

      sidebarMount.innerHTML = `
        <div class="sidebar-brand">
          <a href="${resolveHref(navCfg.homeRoute)}" class="sidebar-brand-link" title="Source 2 Destination">
            <img src="${resolveHref('assets/images/logo.svg')}" alt="Source 2 Destination Logo" class="sidebar-brand-logo">
            <div class="sidebar-brand-text">
              <span class="sidebar-brand-name">Source 2 Destination</span>
              <span class="sidebar-brand-role">${navCfg.roleLabel}</span>
            </div>
          </a>
          <button type="button" class="btn-s2d btn-s2d-ghost btn-icon-s2d d-lg-none sidebar-close-mobile" data-sidebar-close aria-label="Close navigation">
            <i data-lucide="x"></i>
          </button>
        </div>

        <nav class="sidebar-nav-scroll" aria-label="${navCfg.roleLabel} Navigation">
          ${groupsHtml}
        </nav>

        <div class="sidebar-footer">
          <div class="sidebar-user-card">
            <div class="sidebar-user-avatar">${user.initials}</div>
            <div class="sidebar-user-meta">
              <div class="sidebar-user-name">${user.fullName}</div>
              <div class="sidebar-user-email">${user.email}</div>
            </div>
            <a href="${resolveHref('auth/login.html')}" class="sidebar-logout-btn" title="Sign out">
              <i data-lucide="log-out" style="width:16px;height:16px;"></i>
            </a>
          </div>
        </div>
      `;
    }

    if (topbarMount) {
      const pageSection = document.body.getAttribute('data-section') || navCfg.portalTitle;
      const pageTitle = document.body.getAttribute('data-page-title') || document.title.split('—')[0].trim();
      const notifs = (window.S2D_DEMO && window.S2D_DEMO.notifications) || [];
      const unreadCount = notifs.filter((n) => n.unread).length;

      topbarMount.innerHTML = `
        <div class="topbar-left">
          <button type="button" class="topbar-toggle-btn" id="sidebar-toggle-btn" aria-label="Toggle sidebar navigation" title="Toggle sidebar">
            <i data-lucide="panel-left"></i>
          </button>
          <nav class="topbar-breadcrumb" aria-label="Breadcrumb">
            <a href="${resolveHref(navCfg.homeRoute)}">${navCfg.roleLabel}</a>
            <span class="crumb-sep">/</span>
            <span class="d-none d-sm-inline">${pageSection}</span>
            <span class="crumb-sep d-none d-sm-inline">/</span>
            <span class="crumb-current">${pageTitle}</span>
          </nav>
        </div>

        <div class="topbar-right">
          <div class="demo-mode-pill" style="background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.25);color:#065f46;" title="Source 2 Destination Cloud Portal — System Active & Secure">
            <span class="demo-mode-dot" style="background:#10b981;"></span>
            <span>Campus Portal <span class="demo-label-extended">· Live System</span></span>
          </div>

          <button type="button" class="topbar-search-btn" data-open-cmd-search aria-label="Search modules">
            <span style="display:inline-flex;align-items:center;gap:7px;">
              <i data-lucide="search" style="width:15px;height:15px;"></i>
              <span class="search-btn-label">Quick search...</span>
            </span>
            <span class="topbar-kbd">⌘K</span>
          </button>

          <!-- Role Environment Switcher for Seamless Demo Inspection -->
          <div style="position:relative;" class="s2d-dropdown-host">
            <button type="button" class="btn-s2d btn-s2d-secondary btn-sm-s2d" data-dropdown-toggle title="Switch Role Portal (Demo Preview)">
              <i data-lucide="layers-3" style="width:15px;height:15px;color:var(--s2d-primary);"></i>
              <span class="d-none d-md-inline">${navCfg.roleLabel}</span>
              <i data-lucide="chevron-down" style="width:14px;height:14px;"></i>
            </button>
            <div class="s2d-dropdown-menu" style="min-width:235px;">
              <div style="padding:6px 10px;font-size:0.69rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:var(--s2d-text-muted);">Switch Portal Environment</div>
              <a href="${resolveHref('super-admin/dashboard.html')}" class="s2d-dropdown-item">
                <i data-lucide="shield" style="width:15px;height:15px;color:#4F46E5;"></i>
                <span>Super Admin Portal</span>
              </a>
              <a href="${resolveHref('franchise/dashboard.html')}" class="s2d-dropdown-item">
                <i data-lucide="network" style="width:15px;height:15px;color:#0D9488;"></i>
                <span>Franchise Partner Portal</span>
              </a>
              <a href="${resolveHref('school-admin/dashboard.html')}" class="s2d-dropdown-item">
                <i data-lucide="school" style="width:15px;height:15px;color:#0284C7;"></i>
                <span>School Admin Portal</span>
              </a>
              <div class="s2d-dropdown-divider"></div>
              <a href="${resolveHref('index.html')}" class="s2d-dropdown-item">
                <i data-lucide="compass" style="width:15px;height:15px;"></i>
                <span>Platform Launcher Hub</span>
              </a>
            </div>
          </div>

          <!-- Notification Bell -->
          <div style="position:relative;" class="s2d-dropdown-host">
            <button type="button" class="topbar-icon-btn" data-dropdown-toggle aria-label="Notifications">
              <i data-lucide="bell" style="width:17px;height:17px;"></i>
              ${unreadCount > 0 ? '<span class="notif-dot" id="topbar-notif-dot"></span>' : ''}
            </button>
            <div class="s2d-dropdown-menu" style="min-width:330px;padding:0;">
              <div style="padding:12px 15px;border-bottom:1px solid var(--s2d-border);display:flex;align-items:center;justify-content:space-between;">
                <span style="font-weight:600;font-size:0.84rem;color:var(--s2d-heading);">Notifications</span>
                <button type="button" id="mark-all-read-btn" style="border:none;background:transparent;color:var(--s2d-primary);font-size:0.75rem;font-weight:600;cursor:pointer;">Mark all read</button>
              </div>
              <div style="max-height:280px;overflow-y:auto;" id="topbar-notif-list">
                ${notifs.map((n) => `
                  <div style="padding:11px 15px;border-bottom:1px solid var(--s2d-border);background:${n.unread ? '#F8FAFF' : '#FFFFFF'};">
                    <div style="display:flex;justify-content:space-between;gap:8px;margin-bottom:2px;">
                      <span style="font-size:0.79rem;font-weight:600;color:var(--s2d-heading);">${n.title}</span>
                      <span style="font-size:0.69rem;color:var(--s2d-text-muted);white-space:nowrap;">${n.time}</span>
                    </div>
                    <div style="font-size:0.75rem;color:var(--s2d-text-secondary);line-height:1.4;">${n.desc}</div>
                  </div>
                `).join('')}
              </div>
              <div style="padding:9px 14px;text-align:center;background:var(--s2d-surface-subtle);border-radius:0 0 10px 10px;">
                <a href="${resolveHref(navCfg.notificationsRoute)}" style="font-size:0.77rem;font-weight:600;">View notification settings & history</a>
              </div>
            </div>
          </div>

          <!-- User Avatar Profile Dropdown -->
          <div style="position:relative;" class="s2d-dropdown-host">
            <button type="button" class="topbar-icon-btn" data-dropdown-toggle aria-label="Account menu" style="width:auto;padding:0 8px;gap:7px;">
              <span class="avatar-sm" style="width:26px;height:26px;font-size:0.7rem;border-radius:6px;">${user.initials}</span>
              <i data-lucide="chevron-down" style="width:14px;height:14px;"></i>
            </button>
            <div class="s2d-dropdown-menu" style="min-width:230px;">
              <div style="padding:8px 10px;border-bottom:1px solid var(--s2d-border);margin-bottom:4px;">
                <div style="font-weight:600;font-size:0.82rem;color:var(--s2d-heading);">${user.fullName}</div>
                <div style="font-size:0.73rem;color:var(--s2d-text-secondary);">${user.roleLabel}</div>
              </div>
              <a href="${resolveHref(navCfg.settingsRoute)}" class="s2d-dropdown-item">
                <i data-lucide="user" style="width:15px;height:15px;"></i>
                <span>Profile & Preferences</span>
              </a>
              <a href="${resolveHref(navCfg.homeRoute)}" class="s2d-dropdown-item">
                <i data-lucide="activity" style="width:15px;height:15px;"></i>
                <span>Operational Overview</span>
              </a>
              <div class="s2d-dropdown-divider"></div>
              <a href="${resolveHref('auth/login.html')}" class="s2d-dropdown-item danger">
                <i data-lucide="log-out" style="width:15px;height:15px;"></i>
                <span>Sign Out</span>
              </a>
            </div>
          </div>
        </div>
      `;
    }

    // Ensure mobile off-canvas backdrop exists
    let backdrop = document.getElementById('sidebar-mobile-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'sidebar-mobile-backdrop';
      backdrop.className = 'sidebar-backdrop';
      document.body.appendChild(backdrop);
    }

    bindSidebarEvents(backdrop);
    window.S2DNavigation.initGlobalCommandSearch(role);
  }

  function bindSidebarEvents(backdrop) {
    const toggleBtn = document.getElementById('sidebar-toggle-btn');

    const closeMobile = () => {
      document.body.classList.remove('mobile-sidebar-open');
      backdrop.classList.remove('show');
    };

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        if (window.innerWidth < 992) {
          const isOpen = document.body.classList.toggle('mobile-sidebar-open');
          backdrop.classList.toggle('show', isOpen);
        } else {
          document.body.classList.toggle('sidebar-collapsed');
          setTimeout(() => window.dispatchEvent(new Event('resize')), 260);
        }
      });
    }

    backdrop.addEventListener('click', closeMobile);
    document.querySelectorAll('[data-sidebar-close]').forEach((b) => b.addEventListener('click', closeMobile));

    // Accordion parent submenu toggles
    document.querySelectorAll('.sidebar-parent-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (window.innerWidth >= 992 && document.body.classList.contains('sidebar-collapsed')) {
          document.body.classList.remove('sidebar-collapsed');
          btn.closest('.nav-item-box').classList.add('open');
          return;
        }
        const box = btn.closest('.nav-item-box');
        const nowOpen = box.classList.toggle('open');
        btn.setAttribute('aria-expanded', nowOpen ? 'true' : 'false');
      });
    });

    // Topbar dropdowns
    document.querySelectorAll('.s2d-dropdown-host [data-dropdown-toggle]').forEach((trigger) => {
      trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const menu = trigger.parentElement.querySelector('.s2d-dropdown-menu');
        const wasOpen = menu.classList.contains('show');
        document.querySelectorAll('.s2d-dropdown-menu.show').forEach((m) => m.classList.remove('show'));
        if (!wasOpen) menu.classList.add('show');
      });
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.s2d-dropdown-host') && !e.target.closest('.row-action-cell')) {
        document.querySelectorAll('.s2d-dropdown-menu.show').forEach((m) => m.classList.remove('show'));
      }
    });

    const markReadBtn = document.getElementById('mark-all-read-btn');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (window.S2D_DEMO && window.S2D_DEMO.notifications) {
          window.S2D_DEMO.notifications.forEach((n) => { n.unread = false; });
        }
        const dot = document.getElementById('topbar-notif-dot');
        if (dot) dot.remove();
        document.querySelectorAll('#topbar-notif-list > div').forEach((el) => {
          el.style.background = '#FFFFFF';
        });
        window.S2DNotify.show({ title: 'Notifications Marked Read', description: 'All unread alerts cleared in session memory.', type: 'success' });
      });
    }
  }

  window.S2DSidebar = { renderSidebarAndTopbar };
})(window, document);
