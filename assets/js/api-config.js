/* ==========================================================================
   Source 2 Destination — Centralized Django REST Framework (DRF) API Config
   File: assets/js/api-config.js
   ==========================================================================
   NOTE ON ARCHITECTURE:
   - Centralizes all future Django REST API v1 endpoints in one configuration map.
   - Does NOT execute fake network calls or mock servers.
   - Uses strictly ephemeral in-memory state during UI demonstration mode.
   - Backend security & RBAC remain the authoritative enforcement boundary.
   ========================================================================== */

(function (window) {
  'use strict';

  const API_CONFIG = {
    mode: 'DEMO_IN_MEMORY', // Switch to 'LIVE_DRF_API' when connecting Django backend
    baseUrl: '/api/v1',
    timeoutMs: 15000,
    currencySymbol: '$',
    currencyCode: 'USD',
    paginationDefaults: {
      pageParam: 'page',
      pageSizeParam: 'page_size',
      searchParam: 'search',
      orderingParam: 'ordering',
      defaultPageSize: 10
    },

    endpoints: {
      auth: {
        login: '/api/v1/auth/token/',
        logout: '/api/v1/auth/logout/',
        passwordForgot: '/api/v1/auth/password/reset/',
        passwordResetConfirm: '/api/v1/auth/password/reset/confirm/',
        currentUser: '/api/v1/auth/me/'
      },
      superAdmin: {
        overviewMetrics: '/api/v1/super-admin/analytics/overview/',
        schools: '/api/v1/super-admin/schools/',
        schoolDetail: (id) => `/api/v1/super-admin/schools/${encodeURIComponent(id)}/`,
        schoolAdmins: '/api/v1/super-admin/school-admins/',
        validityRecords: '/api/v1/super-admin/validity/records/',
        validityRules: '/api/v1/super-admin/validity/rules/',
        rechargePlans: '/api/v1/super-admin/recharges/plans/',
        rechargeHistory: '/api/v1/super-admin/recharges/history/',
        callingDuration: '/api/v1/super-admin/calling-config/duration/',
        callingSchedules: '/api/v1/super-admin/calling-config/schedules/',
        callHistory: '/api/v1/super-admin/calls/history/',
        schoolReports: '/api/v1/super-admin/reports/schools/',
        subscriptions: '/api/v1/super-admin/subscriptions/',
        subscriptionPlans: '/api/v1/super-admin/subscriptions/plans/',
        payments: '/api/v1/super-admin/payments/transactions/',
        devices: '/api/v1/super-admin/devices/',
        roles: '/api/v1/super-admin/iam/roles/',
        permissionsMatrix: '/api/v1/super-admin/iam/permissions/',
        settings: '/api/v1/super-admin/settings/',
        notifications: '/api/v1/super-admin/notifications/',
        auditLogs: '/api/v1/super-admin/audit-logs/'
      },
      franchise: {
        overviewMetrics: '/api/v1/franchise/analytics/overview/',
        schools: '/api/v1/franchise/schools/',
        students: '/api/v1/franchise/students/',
        bulkStudentImport: '/api/v1/franchise/students/bulk-import/',
        classes: '/api/v1/franchise/academics/classes/',
        validity: '/api/v1/franchise/validity/',
        recharges: '/api/v1/franchise/recharges/',
        callingDuration: '/api/v1/franchise/calling-config/duration/',
        callingSchedules: '/api/v1/franchise/calling-config/schedules/',
        callHistory: '/api/v1/franchise/calls/history/',
        reports: '/api/v1/franchise/reports/',
        commissions: '/api/v1/franchise/commissions/',
        transactions: '/api/v1/franchise/transactions/',
        profileSettings: '/api/v1/franchise/settings/profile/'
      },
      schoolAdmin: {
        overviewMetrics: '/api/v1/school-admin/analytics/overview/',
        students: '/api/v1/school-admin/students/',
        bulkStudentImport: '/api/v1/school-admin/students/bulk-import/',
        classes: '/api/v1/school-admin/academics/classes/',
        sections: '/api/v1/school-admin/academics/sections/',
        guardians: '/api/v1/school-admin/guardians/',
        studentCodes: '/api/v1/school-admin/student-codes/',
        requestServerCode: '/api/v1/school-admin/student-codes/issue/',
        studentStatus: '/api/v1/school-admin/students/status-transitions/',
        callingSchedules: '/api/v1/school-admin/calling-config/schedules/',
        callingDuration: '/api/v1/school-admin/calling-config/duration/',
        validity: '/api/v1/school-admin/validity/',
        recharges: '/api/v1/school-admin/recharges/',
        callHistory: '/api/v1/school-admin/calls/history/',
        studentReports: '/api/v1/school-admin/reports/students/',
        classReports: '/api/v1/school-admin/reports/classes/',
        deviceAssignments: '/api/v1/school-admin/devices/assignments/',
        hostelWardens: '/api/v1/school-admin/wardens/',
        profileSettings: '/api/v1/school-admin/settings/profile/'
      }
    }
  };

  /**
   * Formats DRF pagination query parameters for future server-side tables.
   */
  function buildDrfQueryParams(state) {
    const params = new URLSearchParams();
    if (state.page) params.set(API_CONFIG.paginationDefaults.pageParam, String(state.page));
    if (state.pageSize) params.set(API_CONFIG.paginationDefaults.pageSizeParam, String(state.pageSize));
    if (state.search) params.set(API_CONFIG.paginationDefaults.searchParam, state.search.trim());
    if (state.sortField) {
      const prefix = state.sortDir === 'desc' ? '-' : '';
      params.set(API_CONFIG.paginationDefaults.orderingParam, `${prefix}${state.sortField}`);
    }
    if (state.filters) {
      Object.entries(state.filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '' && v !== 'all') {
          params.set(k, String(v));
        }
      });
    }
    return params.toString();
  }

  /**
   * Maps standard Django REST Framework serializer error payloads
   * (e.g. { "email": ["Enter a valid email address."], "non_field_errors": [...] })
   * directly onto form elements with [data-drf-error="<field_name>"].
   */
  function applyDrfFieldErrors(formEl, errorPayload) {
    if (!formEl || !errorPayload) return;
    formEl.querySelectorAll('[data-drf-error]').forEach((slot) => {
      slot.textContent = '';
      slot.classList.remove('show');
    });
    Object.entries(errorPayload).forEach(([field, messages]) => {
      const text = Array.isArray(messages) ? messages.join(' ') : String(messages);
      const slot = formEl.querySelector(`[data-drf-error="${field}"]`);
      const input = formEl.querySelector(`[name="${field}"]`);
      if (slot) {
        slot.textContent = text;
        slot.classList.add('show');
      }
      if (input) {
        input.classList.add('is-invalid');
      }
    });
  }

  function formatCurrency(amount) {
    const num = Number(amount || 0);
    return API_CONFIG.currencySymbol + num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function formatNumber(num) {
    return Number(num || 0).toLocaleString('en-US');
  }

  window.S2DApiConfig = {
    config: API_CONFIG,
    buildDrfQueryParams,
    applyDrfFieldErrors,
    formatCurrency,
    formatNumber
  };
})(window);
