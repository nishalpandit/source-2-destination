/* ==========================================================================
   Source 2 Destination — Master Page Orchestrator & Module Table Definitions
   File: assets/js/app.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function fmtMoney(v) {
    return window.S2DApiConfig ? window.S2DApiConfig.formatCurrency(v) : '₹' + Number(v || 0).toFixed(2);
  }

  function badge(v) {
    return window.S2DTables.statusBadge(v);
  }

  function getQueryParam(key) {
    return new URLSearchParams(window.location.search).get(key);
  }

  async function toggleRecordStatus(row, refreshFn, activeLabel, suspendedLabel) {
    const actWord = activeLabel || 'Active';
    const susWord = suspendedLabel || 'Suspended';
    const isCurrentlyActive = String(row.status).toLowerCase() === actWord.toLowerCase();
    const nextStatus = isCurrentlyActive ? susWord : actWord;

    const ok = await window.S2DModal.confirm({
      title: `${isCurrentlyActive ? 'Deactivate / Suspend' : 'Activate'} Record?`,
      recordLabel: `${row.id} · ${row.name || row.studentName || row.deviceName || row.school || row.code}`,
      message: isCurrentlyActive
        ? `Changing status to "${nextStatus}" immediately restricts associated calling privileges in demonstration memory.`
        : `Restoring status to "${nextStatus}" re-enables authorized operations within configured schedules.`,
      confirmLabel: isCurrentlyActive ? `Set ${nextStatus}` : `Activate Now`,
      variant: isCurrentlyActive ? 'danger' : 'success'
    });

    if (ok) {
      row.status = nextStatus;
      const recId = row.id || row.code;
      if (refreshFn) refreshFn();
      window.S2DNotify.show({
        title: `Status Updated to ${nextStatus}`,
        description: `${recId || 'Record'} marked ${nextStatus}.`,
        type: 'success'
      });
    }
  }

  function openCallInspector(row) {
    window.S2DModal.openDrawer({
      eyebrow: 'CALL SESSION RECORD · ' + row.id,
      title: `${row.studentName} → ${row.guardianName}`,
      html: `
        <div class="s2d-callout indigo mb-3">
          <i data-lucide="phone-call"></i>
          <div><strong>Authorized Whitelist Session</strong><br>Dialed via restricted Android Kiosk App without exposing raw dialer.</div>
        </div>
        <div class="kv-grid mb-4">
          <div><div class="kv-item-label">Session ID</div><div class="kv-item-value mono-code">${row.id}</div></div>
          <div><div class="kv-item-label">Call Status</div><div class="kv-item-value">${badge(row.status)}</div></div>
          <div><div class="kv-item-label">Student</div><div class="kv-item-value">${row.studentName} (${row.studentCode})</div></div>
          <div><div class="kv-item-label">Campus</div><div class="kv-item-value">${row.school}</div></div>
          <div><div class="kv-item-label">Authorized Destination</div><div class="kv-item-value mono-code">${row.authorizedNumber}</div></div>
          <div><div class="kv-item-label">Start Timestamp</div><div class="kv-item-value mono-code">${row.startTime}</div></div>
          <div><div class="kv-item-label">Call Duration</div><div class="kv-item-value mono-code">${row.duration}</div></div>
          <div><div class="kv-item-label">Credits Deducted</div><div class="kv-item-value">${row.minutesUsed} mins (Rem: ${row.remainingAfter}m)</div></div>
          <div><div class="kv-item-label">Terminal Device</div><div class="kv-item-value mono-code">${row.device}</div></div>
          <div><div class="kv-item-label">Termination Cause</div><div class="kv-item-value">${row.disconnectReason}</div></div>
        </div>
      `
    });
  }

  function openTransactionInspector(row) {
    window.S2DModal.openDrawer({
      eyebrow: 'FINANCIAL LEDGER · ' + row.id,
      title: `${fmtMoney(row.amount)} — ${row.category}`,
      html: `
        <div class="kv-grid mb-4">
          <div><div class="kv-item-label">Transaction ID</div><div class="kv-item-value mono-code">${row.id}</div></div>
          <div><div class="kv-item-label">Settlement Status</div><div class="kv-item-value">${badge(row.status)}</div></div>
          <div><div class="kv-item-label">Institution</div><div class="kv-item-value">${row.entity}</div></div>
          <div><div class="kv-item-label">Franchise Partner</div><div class="kv-item-value">${row.franchise}</div></div>
          <div><div class="kv-item-label">Gateway Reference</div><div class="kv-item-value mono-code">${row.reference}</div></div>
          <div><div class="kv-item-label">Payment Instrument</div><div class="kv-item-value">${row.method}</div></div>
          <div><div class="kv-item-label">Timestamp</div><div class="kv-item-value mono-code">${row.date}</div></div>
          <div><div class="kv-item-label">Gross Amount</div><div class="kv-item-value">${fmtMoney(row.amount)}</div></div>
        </div>
        <div class="s2d-card" style="background:var(--s2d-surface-subtle);">
          <div class="s2d-card-body" style="padding:14px;">
            <div style="font-weight:600;margin-bottom:6px;">Django REST Webhook Readiness</div>
            <div class="text-secondary-s2d" style="font-size:0.78rem;">Idempotency key & signed webhook verification will be validated server-side via <code>/api/v1/super-admin/payments/transactions/</code>.</div>
          </div>
        </div>
      `
    });
  }

  /* ==================== DECLARATIVE TABLE REGISTRY ==================== */
  function initDeclarativeTables() {
    const D = window.S2D_DEMO;
    if (!D || !window.S2DTables) return;
    const T = window.S2DTables.EnterpriseTable;
    const href = window.S2DNavigation.resolveHref;

    const specs = {
      /* --- SUPER ADMIN TABLES --- */
      'sa-schools-table': () => ({
        data: D.schools,
        searchPlaceholder: 'Search school name, code, city, or admin...',
        filters: [
          { key: 'franchise', label: 'Franchise', options: ['North India EduNet Partners', 'Western Scholastic Network', 'Southern Campus Connect', 'Central Heartland Edutech'] },
          { key: 'subscriptionStatus', label: 'Subscription', options: ['Active', 'Expiring', 'Expired'] },
          { key: 'status', label: 'Status', options: ['Active', 'Suspended'] }
        ],
        exportFilename: 'super-admin-schools.csv',
        columns: [
          { key: 'name', label: 'School Identity', render: (r) => `<a href="${href('super-admin/schools/details.html')}?id=${r.id || r.code}" class="cell-primary">${r.name}</a><span class="cell-sub mono-code">${r.id || r.code} · ${r.city}</span>` },
          { key: 'franchise', label: 'Assigned Franchise' },
          { key: 'adminName', label: 'Primary Admin', render: (r) => `<span class="cell-primary" style="font-weight:500;">${r.adminName}</span><span class="cell-sub">${r.adminEmail}</span>` },
          { key: 'students', label: 'Students', render: (r) => `<strong>${r.activeStudents ?? 0}</strong> <span class="text-secondary-s2d">/ ${r.students ?? r.studentSeats ?? 0}</span>` },
          { key: 'subscriptionStatus', label: 'Subscription', render: (r) => `${badge(r.subscriptionStatus)}<span class="cell-sub">${r.subscriptionPlan}</span>` },
          { key: 'status', label: 'Account', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'View 360° Details', icon: 'eye', href: `${href('super-admin/schools/details.html')}?id=${r.id || r.code}` },
          { label: 'Edit School', icon: 'pencil', href: `${href('super-admin/schools/edit.html')}?id=${r.id || r.code}` },
          { divider: true },
          { label: r.status === 'Active' ? 'Suspend School' : 'Activate School', icon: 'power', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Suspended') }
        ]
      }),

      'sa-school-admins-table': () => ({
        data: D.schoolAdmins,
        searchPlaceholder: 'Search administrator name, email, or school...',
        filters: [
          { key: 'status', label: 'Status', options: ['Active', 'Inactive'] },
          { key: 'mfaEnabled', label: 'MFA', options: ['Enabled', 'Pending', 'Disabled'] }
        ],
        exportFilename: 'school-administrators.csv',
        columns: [
          { key: 'name', label: 'Administrator', render: (r) => `<a href="${href('super-admin/school-admins/details.html')}?id=${r.id}" class="cell-primary">${r.name}</a><span class="cell-sub">${r.email}</span>` },
          { key: 'school', label: 'Assigned School', render: (r) => `${r.school}<span class="cell-sub mono-code">${r.schoolId}</span>` },
          { key: 'designation', label: 'Designation' },
          { key: 'mfaEnabled', label: '2FA / MFA', render: (r) => badge(r.mfaEnabled) },
          { key: 'lastLogin', label: 'Last Active', render: (r) => `<span class="mono-code">${r.lastLogin}</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'View Admin Profile', icon: 'eye', href: `${href('super-admin/school-admins/details.html')}?id=${r.id}` },
          { label: 'Edit Assignment', icon: 'pencil', href: `${href('super-admin/school-admins/edit.html')}?id=${r.id}` },
          { divider: true },
          { label: r.status === 'Active' ? 'Deactivate Admin' : 'Activate Admin', icon: 'user-x', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Inactive') }
        ]
      }),

      'sa-validity-table': () => ({
        data: D.students,
        searchPlaceholder: 'Search student, code, or school...',
        filters: [
          { key: 'validityStatus', label: 'Validity', options: ['Active', 'Expiring', 'Expired'] },
          { key: 'school', label: 'School', options: ['Doon Valley Residential Academy', 'Mayo International Boarding School', 'Scindia Residential Campus', 'Bishop Cotton Boys School & Hostel', 'Sahyadri International Residential School'] }
        ],
        dateFilterKey: 'validityExpiry',
        exportFilename: 'student-validity-records.csv',
        columns: [
          { key: 'name', label: 'Student', render: (r) => `<span class="cell-primary">${r.name}</span><span class="cell-sub mono-code">${r.studentCode}</span>` },
          { key: 'school', label: 'School' },
          { key: 'validityStart', label: 'Activated On', render: (r) => `<span class="mono-code">${r.validityStart}</span>` },
          { key: 'validityExpiry', label: 'Expiry Date', render: (r) => `<span class="mono-code">${r.validityExpiry}</span>` },
          { key: 'remainingMinutes', label: 'Rem. Credits', render: (r) => `<span class="mono-code">${r.remainingMinutes} mins</span>` },
          { key: 'validityStatus', label: 'Validity Status', render: (r) => badge(r.validityStatus) }
        ],
        rowActions: (r) => [
          {
            label: 'Extend Validity (+90d)', icon: 'calendar-plus',
            onClick: async (row, refresh) => {
              const ok = await window.S2DModal.confirm({
                title: 'Extend Student Calling Validity?',
                recordLabel: `${row.studentCode} · ${row.name}`,
                message: 'Extends account validity window by 90 days and marks validity status Active in demonstration memory.',
                confirmLabel: 'Extend +90 Days',
                variant: 'primary'
              });
              if (ok) {
                row.validityExpiry = '2027-08-30';
                row.validityStatus = 'Active';
                row.status = 'Active';
                refresh();
                window.S2DNotify.show({ title: 'Validity Extended', description: `${row.name} extended through 2027-08-30.`, type: 'success' });
              }
            }
          }
        ]
      }),

      'sa-recharge-history-table': () => ({
        data: D.recharges,
        searchPlaceholder: 'Search recharge ID, student, plan, or school...',
        filters: [
          { key: 'status', label: 'Status', options: ['Successful', 'Pending', 'Failed'] },
          { key: 'planName', label: 'Plan', options: ['Starter Monthly Pack', 'Standard Term Calling Pack', 'Full Academic Year Pack', 'Senior Scholar Extended Pack'] }
        ],
        dateFilterKey: 'date',
        exportFilename: 'recharge-history.csv',
        columns: [
          { key: 'id', label: 'Recharge ID', render: (r) => `<span class="mono-code cell-primary">${r.id}</span><span class="cell-sub mono-code">${r.date}</span>` },
          { key: 'studentName', label: 'Student', render: (r) => `<span class="cell-primary">${r.studentName}</span><span class="cell-sub mono-code">${r.studentCode}</span>` },
          { key: 'school', label: 'School' },
          { key: 'planName', label: 'Plan & Credits', render: (r) => `${r.planName}<span class="cell-sub">+${r.minutesAdded} mins · ${r.validityDays}d</span>` },
          { key: 'amount', label: 'Amount', render: (r) => `<strong class="mono-code">${fmtMoney(r.amount)}</strong>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          {
            label: 'Inspect Allocation', icon: 'file-text',
            onClick: (row) => window.S2DModal.openDrawer({
              eyebrow: 'RECHARGE RECORD · ' + row.id,
              title: `${row.studentName} — ${row.planName}`,
              html: `<div class="kv-grid">
                <div><div class="kv-item-label">Recharge ID</div><div class="kv-item-value mono-code">${row.id}</div></div>
                <div><div class="kv-item-label">Status</div><div class="kv-item-value">${badge(row.status)}</div></div>
                <div><div class="kv-item-label">Student</div><div class="kv-item-value">${row.studentName} (${row.studentCode})</div></div>
                <div><div class="kv-item-label">Campus</div><div class="kv-item-value">${row.school}</div></div>
                <div><div class="kv-item-label">Credits Added</div><div class="kv-item-value">+${row.minutesAdded} minutes</div></div>
                <div><div class="kv-item-label">Payment Mode</div><div class="kv-item-value">${row.paymentMode}</div></div>
                <div><div class="kv-item-label">Amount Paid</div><div class="kv-item-value">${fmtMoney(row.amount)}</div></div>
                <div><div class="kv-item-label">Timestamp</div><div class="kv-item-value mono-code">${row.date}</div></div>
              </div>`
            })
          }
        ]
      }),

      'global-call-history-table': () => ({
        data: D.callHistory,
        searchPlaceholder: 'Search student, guardian number, school, or call ID...',
        filters: [
          { key: 'school', label: 'School', options: ['Doon Valley Residential Academy', 'Mayo International Boarding School', 'Scindia Residential Campus', 'Bishop Cotton Boys School & Hostel', 'Sahyadri International Residential School'] },
          { key: 'status', label: 'Call Status', options: ['Completed', 'Missed', 'Restricted'] }
        ],
        dateFilterKey: 'dateOnly',
        exportFilename: 'call-history-logs.csv',
        columns: [
          { key: 'studentName', label: 'Student', render: (r) => `<span class="cell-primary">${r.studentName}</span><span class="cell-sub mono-code">${r.studentCode}</span>` },
          { key: 'school', label: 'School' },
          { key: 'authorizedNumber', label: 'Authorized Guardian', render: (r) => `<span class="mono-code">${r.authorizedNumber}</span><span class="cell-sub">${r.guardianName}</span>` },
          { key: 'startTime', label: 'Start Time', render: (r) => `<span class="mono-code">${r.startTime}</span>` },
          { key: 'duration', label: 'Duration / Usage', render: (r) => `<span class="mono-code">${r.duration}</span><span class="cell-sub">-${r.minutesUsed}m credit</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'View Call Details', icon: 'phone-forwarded', onClick: (row) => openCallInspector(row) }
        ]
      }),

      'sa-subscriptions-table': () => ({
        data: D.subscriptions,
        searchPlaceholder: 'Search school, subscription ID, or plan...',
        filters: [
          { key: 'status', label: 'Status', options: ['Active', 'Expiring', 'Expired'] },
          { key: 'planName', label: 'Plan', options: ['Enterprise Boarding Annual', 'Campus Growth Annual', 'Standard Hostel Quarterly'] }
        ],
        dateFilterKey: 'expiryDate',
        exportFilename: 'school-subscriptions.csv',
        columns: [
          { key: 'school', label: 'Subscribed School', render: (r) => `<span class="cell-primary">${r.school}</span><span class="cell-sub mono-code">${r.id} · ${r.franchise}</span>` },
          { key: 'planName', label: 'Subscription Plan', render: (r) => `${r.planName}<span class="cell-sub">${r.studentSeats} students · ${r.deviceSeats} devices</span>` },
          { key: 'amount', label: 'Contract Value', render: (r) => `<strong class="mono-code">${fmtMoney(r.amount)}</strong>` },
          { key: 'expiryDate', label: 'Renewal Date', render: (r) => `<span class="mono-code">${r.expiryDate}</span><span class="cell-sub">${r.autoRenew}</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'Edit Subscription', icon: 'pencil', href: `${href('super-admin/subscriptions/create.html')}?id=${r.id}` },
          {
            label: 'Simulate Renewal (+1 Yr)', icon: 'refresh-cw',
            onClick: (row, refresh) => {
              row.status = 'Active';
              row.expiryDate = '2027-11-24';
              refresh();
              window.S2DNotify.show({ title: 'Subscription Renewed (Demo)', description: `${row.school} renewed through ${row.expiryDate}.`, type: 'success' });
            }
          }
        ]
      }),

      'sa-payments-table': () => ({
        data: D.transactions,
        searchPlaceholder: 'Search transaction ID, gateway ref, or institution...',
        filters: [
          { key: 'status', label: 'Payment Status', options: ['Successful', 'Pending', 'Failed', 'Refunded'] },
          { key: 'category', label: 'Category', options: ['Student Recharge', 'Annual Subscription', 'Bulk Credit Allocation', 'Subscription Renewal'] }
        ],
        dateFilterKey: 'date',
        exportFilename: 'financial-transactions.csv',
        columns: [
          { key: 'id', label: 'Transaction', render: (r) => `<a href="${href('super-admin/payments/details.html')}?id=${r.id}" class="cell-primary mono-code">${r.id}</a><span class="cell-sub mono-code">${r.date}</span>` },
          { key: 'entity', label: 'Institution & Partner', render: (r) => `${r.entity}<span class="cell-sub">${r.franchise}</span>` },
          { key: 'category', label: 'Category' },
          { key: 'method', label: 'Method / Ref', render: (r) => `${r.method}<span class="cell-sub mono-code">${r.reference}</span>` },
          { key: 'amount', label: 'Amount', render: (r) => `<strong class="mono-code">${fmtMoney(r.amount)}</strong>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'Quick Inspect', icon: 'panel-right', onClick: (row) => openTransactionInspector(row) },
          { label: 'Full Receipt Page', icon: 'receipt', href: `${href('super-admin/payments/details.html')}?id=${r.id}` }
        ]
      }),

      'sa-devices-table': () => ({
        data: D.devices,
        searchPlaceholder: 'Search device ID, serial, IMEI, or school...',
        filters: [
          { key: 'onlineStatus', label: 'Connectivity', options: ['Online', 'Offline'] },
          { key: 'kioskCompliance', label: 'Compliance', options: ['Compliant', 'Policy Update Pending', 'Non-Compliant (Tamper Alert)'] },
          { key: 'status', label: 'State', options: ['Active', 'Available', 'Blocked'] }
        ],
        exportFilename: 'android-enterprise-devices.csv',
        columns: [
          { key: 'deviceName', label: 'Device Identity', render: (r) => `<a href="${href('super-admin/devices/details.html')}?id=${r.id}" class="cell-primary">${r.deviceName}</a><span class="cell-sub mono-code">${r.id} · SN: ${r.serialNumber}</span>` },
          { key: 'school', label: 'Assigned Campus', render: (r) => `${r.school}<span class="cell-sub">${r.wingLocation}</span>` },
          { key: 'enrollmentStatus', label: 'AE Enrollment', render: (r) => badge(r.enrollmentStatus) },
          { key: 'kioskCompliance', label: 'Kiosk Policy', render: (r) => badge(r.kioskCompliance) },
          { key: 'onlineStatus', label: 'Telemetry', render: (r) => `${badge(r.onlineStatus)}<span class="cell-sub">${r.lastHeartbeat}</span>` },
          { key: 'status', label: 'Access', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'Device Telemetry', icon: 'cpu', href: `${href('super-admin/devices/details.html')}?id=${r.id}` },
          { label: 'Reassign Campus', icon: 'arrow-left-right', href: `${href('super-admin/devices/register.html')}?id=${r.id}` },
          { divider: true },
          { label: r.status === 'Blocked' ? 'Unblock Terminal' : 'Block Terminal', icon: 'shield-ban', danger: r.status !== 'Blocked', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Blocked') }
        ]
      }),

      'sa-audit-table': () => ({
        data: D.auditLogs,
        selectable: false,
        searchPlaceholder: 'Search actor, module, action, or IP address...',
        filters: [
          { key: 'severity', label: 'Severity', options: ['Info', 'Warning', 'Critical'] },
          { key: 'module', label: 'Module', options: ['Calling Duration', 'Guardian Whitelist', 'Device Compliance', 'Recharge Allocation', 'School Status'] }
        ],
        exportFilename: 'enterprise-audit-logs.csv',
        columns: [
          { key: 'timestamp', label: 'Timestamp (UTC)', render: (r) => `<span class="mono-code">${r.timestamp}</span>` },
          { key: 'actor', label: 'Actor / Principal', render: (r) => `<span class="cell-primary">${r.actor}</span>` },
          { key: 'module', label: 'Module' },
          { key: 'action', label: 'Event Summary', render: (r) => `${r.action}<span class="cell-sub">${r.target}</span>` },
          { key: 'ipAddress', label: 'Origin IP', render: (r) => `<span class="mono-code">${r.ipAddress}</span>` },
          { key: 'severity', label: 'Severity', render: (r) => badge(r.severity) }
        ]
      }),

      /* --- FRANCHISE TABLES (SCOPED TO FRN-101) --- */
      'fr-schools-table': () => ({
        data: D.schools.filter((s) => s.franchiseId === 'FRN-101'),
        searchPlaceholder: 'Search assigned school name, city, or admin...',
        filters: [
          { key: 'subscriptionStatus', label: 'Subscription', options: ['Active', 'Expiring', 'Expired'] },
          { key: 'status', label: 'Status', options: ['Active', 'Suspended'] }
        ],
        exportFilename: 'franchise-assigned-schools.csv',
        columns: [
          { key: 'name', label: 'Assigned School', render: (r) => `<a href="${href('franchise/schools/details.html')}?id=${r.id || r.code}" class="cell-primary">${r.name}</a><span class="cell-sub mono-code">${r.id || r.code} · Territory Allocated</span>` },
          { key: 'city', label: 'Location' },
          { key: 'adminName', label: 'Campus Admin', render: (r) => `${r.adminName}<span class="cell-sub">${r.adminEmail}</span>` },
          { key: 'students', label: 'Students', render: (r) => `<strong>${r.activeStudents ?? 0}</strong> / ${r.students ?? r.studentSeats ?? 0}` },
          { key: 'callingMinutes', label: 'Monthly Usage', render: (r) => `<span class="mono-code">${(r.callingMinutes || (r.activeStudents || 0) * 45).toLocaleString()} mins</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'School Details', icon: 'eye', href: `${href('franchise/schools/details.html')}?id=${r.id || r.code}` },
          { label: 'Edit Campus Info', icon: 'pencil', href: `${href('franchise/schools/edit.html')}?id=${r.id || r.code}` }
        ]
      }),

      'fr-students-table': () => {
        const urlParams = new URLSearchParams(window.location.search);
        const schoolCode = urlParams.get('id') || '';
        return {
          data: D.students.filter((s) => s.franchiseId === 'FRN-101' && (!schoolCode || s.schoolId === schoolCode)),
          searchPlaceholder: 'Search student name, calling code, or guardian...',
          filters: [
            { key: 'school', label: 'Assigned School', options: ['Doon Valley Residential Academy', 'Mayo International Boarding School', 'Scindia Residential Campus'] },
            { key: 'className', label: 'Class', options: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'] },
            { key: 'status', label: 'Status', options: ['Active', 'Inactive'] }
          ],
          exportFilename: 'franchise-students.csv',
          columns: [
            { key: 'name', label: 'Student', render: (r) => `<a href="${href('franchise/students/details.html')}?id=${r.id || r.code}" class="cell-primary">${r.name}</a><span class="cell-sub mono-code">${r.studentCode || r.code}</span>` },
            { key: 'school', label: 'Assigned School' },
            { key: 'className', label: 'Class & Section', render: (r) => `${r.className} · ${r.section}` },
            { key: 'primaryPhone', label: 'Primary Guardian', render: (r) => `<span class="mono-code">${r.primaryPhone}</span><span class="cell-sub">${r.guardianName}</span>` },
            { key: 'remainingMinutes', label: 'Credits', render: (r) => `<span class="mono-code">${r.remainingMinutes} mins</span>` },
            { key: 'status', label: 'Status', render: (r) => badge(r.status) }
          ],
          rowActions: (r) => [
            { label: 'Student Profile', icon: 'user', href: `${href('franchise/students/details.html')}?id=${r.id || r.code}` },
            { label: 'Edit Student', icon: 'pencil', href: `${href('franchise/students/edit.html')}?id=${r.id || r.code}` },
            { divider: true },
            { label: r.status === 'Active' ? 'Deactivate Student' : 'Activate Student', icon: 'power', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Inactive') }
          ]
        };
      },

      'fr-commissions-table': () => ({
        data: D.commissions,
        selectable: false,
        searchPlaceholder: 'Search school, billing period, or commission ID...',
        filters: [
          { key: 'status', label: 'Payout Status', options: ['Successful', 'Pending'] },
          { key: 'school', label: 'School', options: ['Doon Valley Residential Academy', 'Mayo International Boarding School', 'Scindia Residential Campus'] }
        ],
        exportFilename: 'franchise-commission-ledger.csv',
        columns: [
          { key: 'id', label: 'Entry ID', render: (r) => `<span class="mono-code cell-primary">${r.id}</span>` },
          { key: 'period', label: 'Settlement Period' },
          { key: 'school', label: 'Assigned School', render: (r) => `<span class="cell-primary">${r.school}</span><span class="cell-sub">${r.sourceType}</span>` },
          { key: 'grossAmount', label: 'Gross Volume', render: (r) => `<span class="mono-code">${fmtMoney(r.grossAmount)}</span>` },
          { key: 'commissionEarned', label: 'Partner Commission', render: (r) => `<strong class="mono-code text-brand">${fmtMoney(r.commissionEarned)}</strong> <span class="text-secondary-s2d">(${r.rate})</span>` },
          { key: 'status', label: 'Settlement', render: (r) => `${badge(r.status)}<span class="cell-sub mono-code">Payout: ${r.payoutDate}</span>` }
        ],
        rowActions: (r) => [
          {
            label: 'Commission Breakdown', icon: 'coins',
            onClick: (row) => window.S2DModal.openDrawer({
              eyebrow: 'COMMISSION STATEMENT · ' + row.id,
              title: `${row.school} (${row.period})`,
              html: `<div class="kv-grid">
                <div><div class="kv-item-label">Ledger ID</div><div class="kv-item-value mono-code">${row.id}</div></div>
                <div><div class="kv-item-label">Settlement Status</div><div class="kv-item-value">${badge(row.status)}</div></div>
                <div><div class="kv-item-label">Gross Eligible Volume</div><div class="kv-item-value">${fmtMoney(row.grossAmount)}</div></div>
                <div><div class="kv-item-label">Contracted Tier Rate</div><div class="kv-item-value">${row.rate}</div></div>
                <div><div class="kv-item-label">Earned Commission</div><div class="kv-item-value text-brand">${fmtMoney(row.commissionEarned)}</div></div>
                <div><div class="kv-item-label">Scheduled Payout Date</div><div class="kv-item-value mono-code">${row.payoutDate}</div></div>
              </div>`
            })
          }
        ]
      }),

      /* --- SCHOOL ADMIN TABLES (SCOPED TO OAKRIDGE SCH-1001 OR CURRENT SCHOOL) --- */
      'sch-students-table': () => {
        const urlParams = new URLSearchParams(window.location.search);
        const schoolCode = urlParams.get('id') || urlParams.get('school_code') || 'SCH-1001';
        return {
          data: D.students.filter((s) => s.schoolId === schoolCode),
          searchPlaceholder: 'Search student name, calling code, room, or guardian...',
          filters: [
            { key: 'className', label: 'Class', options: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'] },
            { key: 'section', label: 'Section', options: ['Section A', 'Section B', 'Section C'] },
            { key: 'status', label: 'Account', options: ['Active', 'Inactive'] }
          ],
          exportFilename: `${schoolCode}-students.csv`,
          columns: [
            { key: 'name', label: 'Student', render: (r) => `<a href="${href('school-admin/students/details.html')}?id=${r.id || r.code}" class="cell-primary">${r.name}</a><span class="cell-sub">${r.hostelWing}</span>` },
            { key: 'studentCode', label: 'Calling Code', render: (r) => `<span class="mono-code" style="padding:3px 7px;background:#EEF2FF;color:#3730A3;border-radius:5px;font-weight:600;">${r.studentCode || r.code}</span>` },
            { key: 'className', label: 'Class / Sec', render: (r) => `${r.className}<span class="cell-sub">${r.section}</span>` },
            { key: 'guardianName', label: 'Authorized Guardian', render: (r) => `${r.guardianName} (${r.guardianRelation})<span class="cell-sub mono-code">${r.primaryPhone}</span>` },
            { key: 'remainingMinutes', label: 'Credits & Validity', render: (r) => `<strong>${r.remainingMinutes}m</strong> left<span class="cell-sub">Exp: ${r.validityExpiry}</span>` },
            { key: 'status', label: 'Status', render: (r) => badge(r.status) }
          ],
          rowActions: (r) => [
            { label: 'View 360° Profile', icon: 'eye', href: `${href('school-admin/students/details.html')}?id=${r.id || r.code}` },
            { label: 'Edit Student', icon: 'pencil', href: `${href('school-admin/students/edit.html')}?id=${r.id || r.code}` },
            { label: 'Recharge Credits', icon: 'zap', href: `${href('school-admin/recharges/student-recharge.html')}?student=${r.id || r.code}` },
            { divider: true },
            { label: r.status === 'Active' ? 'Deactivate Account' : 'Activate Account', icon: 'power', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Inactive') }
          ]
        };
      },

      'sch-classes-table': () => {
        return {
          data: D.classes,
          searchPlaceholder: 'Search class grade or faculty supervisor...',
          exportFilename: 'school-classes.csv',
          columns: [
            { key: 'className', label: 'Class Grade', render: (r) => `<span class="cell-primary">${r.className}</span><span class="cell-sub mono-code">${r.id}</span>` },
            { key: 'supervisor', label: 'Grade Coordinator' },
            { key: 'sectionsCount', label: 'Sections' },
            { key: 'studentsCount', label: 'Enrolled / Active', render: (r) => `<strong>${r.activeAccounts ?? 0}</strong> / ${r.studentsCount ?? 0} students` },
            { key: 'defaultDailyMinutes', label: 'Daily Call Cap', render: (r) => `<span class="mono-code">${r.defaultDailyMinutes} mins/day</span>` },
            { key: 'scheduleGroup', label: 'Schedule Policy' },
            { key: 'status', label: 'Status', render: (r) => badge(r.status) }
          ],
          rowActions: (r) => [
            { label: 'View Sections', icon: 'layout-list', href: `${href('school-admin/classes/sections.html')}?class=${encodeURIComponent(r.className || r.id)}` },
            {
              label: r.status === 'Active' ? 'Archive Class' : 'Activate Class', icon: r.status === 'Active' ? 'archive' : 'power', danger: r.status === 'Active',
              onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Archived')
            }
          ]
        };
      },

      'sch-sections-table': () => {
        return {
          data: D.sections,
          searchPlaceholder: 'Search section, class, advisor, or hostel wing...',
          filters: [
            { key: 'className', label: 'Class', options: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'] }
          ],
          exportFilename: 'school-sections.csv',
          columns: [
            { key: 'sectionName', label: 'Section', render: (r) => `<span class="cell-primary">${r.className} — ${r.sectionName}</span><span class="cell-sub mono-code">${r.id}</span>` },
            { key: 'roomWing', label: 'Hostel Wing Mapping' },
            { key: 'advisor', label: 'Section Advisor' },
            { key: 'studentsCount', label: 'Students', render: (r) => `${r.activeCallers ?? 0} active / ${r.studentsCount ?? 0}` },
            { key: 'assignedBooth', label: 'Primary Calling Booth' },
            { key: 'status', label: 'Status', render: (r) => badge(r.status) }
          ],
          rowActions: (r) => [
            { label: r.status === 'Active' ? 'Archive Section' : 'Activate Section', icon: r.status === 'Active' ? 'archive' : 'power', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Archived') }
          ]
        };
      },

      'sch-guardians-table': () => {
        return {
          data: D.guardians,
          searchPlaceholder: 'Search guardian name, student, or authorized phone...',
          filters: [
            { key: 'relation', label: 'Relation', options: ['Father', 'Mother', 'Legal Guardian'] },
            { key: 'status', label: 'Status', options: ['Active', 'Inactive'] }
          ],
          exportFilename: 'authorized-guardians.csv',
          columns: [
            { key: 'name', label: 'Guardian Identity', render: (r) => `<a href="${href('school-admin/guardians/details.html')}?id=${r.id || r.code}" class="cell-primary">${r.name}</a><span class="cell-sub">${r.relation} · ${r.email}</span>` },
            { key: 'studentName', label: 'Linked Student', render: (r) => `<span class="cell-primary">${r.studentName}</span><span class="cell-sub">${r.className}</span>` },
            { key: 'fatherPhone', label: 'Father Phone', render: (r) => `<span class="mono-code">${r.fatherPhone}</span>` },
            { key: 'motherPhone', label: 'Mother Phone', render: (r) => `<span class="mono-code">${r.motherPhone}</span>` },
            { key: 'verification', label: 'Whitelist & KYC', render: (r) => `${badge(r.verification)}<span class="cell-sub">${r.whitelistStatus}</span>` },
            { key: 'status', label: 'Status', render: (r) => badge(r.status) }
          ],
          rowActions: (r) => [
            { label: 'Guardian Details', icon: 'eye', href: `${href('school-admin/guardians/details.html')}?id=${r.id || r.code}` },
            { label: 'Edit Authorized Numbers', icon: 'phone', href: `${href('school-admin/guardians/edit.html')}?id=${r.id || r.code}` },
            { divider: true },
            { label: r.status === 'Active' ? 'Revoke Authorization' : 'Restore Authorization', icon: 'shield-off', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Inactive') }
          ]
        };
      },

      'sch-codes-table': () => ({
        data: D.studentCodes,
        searchPlaceholder: 'Search unique code or student name...',
        filters: [
          { key: 'status', label: 'Code Status', options: ['Active', 'Suspended', 'Pending'] }
        ],
        exportFilename: 'student-calling-codes.csv',
        columns: [
          { key: 'code', label: 'Unique Calling Code', render: (r) => `<span class="mono-code" style="padding:3px 8px;background:#EEF2FF;color:#3730A3;border-radius:5px;font-weight:600;">${r.code}</span>` },
          { key: 'studentName', label: 'Assigned Student', render: (r) => `<span class="cell-primary">${r.studentName}</span><span class="cell-sub">${r.className}</span>` },
          { key: 'issuedBy', label: 'Authority' },
          { key: 'issuedAt', label: 'Issued Timestamp', render: (r) => `<span class="mono-code">${r.issuedAt}</span>` },
          { key: 'lastUsed', label: 'Last Booth Login', render: (r) => `<span class="mono-code">${r.lastUsed}</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          {
            label: 'Inspect Code Security', icon: 'key-round',
            onClick: (row) => window.S2DModal.openDrawer({
              eyebrow: 'STUDENT CALLING CODE · ' + row.id,
              title: `${row.code} (${row.studentName})`,
              html: `<div class="s2d-callout indigo mb-3"><i data-lucide="lock"></i><div><strong>Backend Cryptographic Issuance</strong><br>Codes are generated exclusively by the Django server to guarantee collision-free entropy across campuses.</div></div>
              <div class="kv-grid">
                <div><div class="kv-item-label">Assigned Student</div><div class="kv-item-value">${row.studentName}</div></div>
                <div><div class="kv-item-label">Authentication Policy</div><div class="kv-item-value">${row.pinPolicy}</div></div>
                <div><div class="kv-item-label">Issued At</div><div class="kv-item-value mono-code">${row.issuedAt}</div></div>
                <div><div class="kv-item-label">Current Status</div><div class="kv-item-value">${badge(row.status)}</div></div>
              </div>`
            })
          },
          { label: r.status === 'Active' ? 'Suspend Code' : 'Activate Code', icon: 'ban', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Suspended') }
        ]
      }),

      'sch-devices-table': () => ({
        data: D.devices.filter((d) => d.schoolId === 'SCH-1001'),
        searchPlaceholder: 'Search booth name, device ID, or hostel wing...',
        filters: [
          { key: 'onlineStatus', label: 'Connectivity', options: ['Online', 'Offline'] },
          { key: 'status', label: 'Assignment', options: ['Active', 'Available'] }
        ],
        exportFilename: 'doon-valley-calling-devices.csv',
        columns: [
          { key: 'deviceName', label: 'Hostel Booth / Device', render: (r) => `<span class="cell-primary">${r.deviceName}</span><span class="cell-sub mono-code">${r.id} · ${r.model}</span>` },
          { key: 'wingLocation', label: 'Hostel Location' },
          { key: 'assignedMode', label: 'Assignment Scope' },
          { key: 'enrollmentStatus', label: 'Enrollment', render: (r) => badge(r.enrollmentStatus) },
          { key: 'onlineStatus', label: 'Heartbeat', render: (r) => `${badge(r.onlineStatus)}<span class="cell-sub">${r.lastHeartbeat}</span>` },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'Configure Assignment', icon: 'link', href: `${href('school-admin/device-assignments/assign.html')}?device=${r.id}` }
        ]
      }),

      'sch-wardens-table': () => ({
        data: D.wardens,
        searchPlaceholder: 'Search warden name, email, or hostel block...',
        filters: [
          { key: 'status', label: 'Status', options: ['Active', 'Inactive'] }
        ],
        exportFilename: 'hostel-wardens.csv',
        columns: [
          { key: 'name', label: 'Hostel Warden', render: (r) => `<a href="${href('school-admin/hostel-wardens/details.html')}?id=${r.id}" class="cell-primary">${r.name}</a><span class="cell-sub">${r.email}</span>` },
          { key: 'hostelWing', label: 'Assigned Hostel Wing' },
          { key: 'shiftHours', label: 'Duty Shift', render: (r) => `<span class="mono-code">${r.shiftHours}</span>` },
          { key: 'supervisedStudents', label: 'Supervision Scope', render: (r) => `${r.supervisedStudents} students · ${r.supervisedDevices} booths` },
          { key: 'emergencyOverride', label: 'Override Privilege', render: (r) => badge(r.emergencyOverride) },
          { key: 'status', label: 'Status', render: (r) => badge(r.status) }
        ],
        rowActions: (r) => [
          { label: 'Warden Details', icon: 'eye', href: `${href('school-admin/hostel-wardens/details.html')}?id=${r.id}` },
          { label: 'Edit Warden', icon: 'pencil', href: `${href('school-admin/hostel-wardens/edit.html')}?id=${r.id}` },
          { divider: true },
          { label: r.status === 'Active' ? 'Mark Inactive' : 'Activate Warden', icon: 'user-check', danger: r.status === 'Active', onClick: (row, refresh) => toggleRecordStatus(row, refresh, 'Active', 'Inactive') }
        ]
      })
    };

    window.S2DActiveTables = window.S2DActiveTables || {};
    document.querySelectorAll('[data-s2d-table]').forEach((el) => {
      const key = el.getAttribute('data-s2d-table');
      const factory = specs[key];
      if (!factory) return;
      const cfg = factory();
      cfg.mount = el;
      window.S2DActiveTables[key] = new T(cfg);
    });
  }

  /* ==================== DYNAMIC ?id= HYDRATION FOR DETAIL & EDIT PAGES ==================== */
  function hydrateDynamicRecordBindings() {
    const D = window.S2D_DEMO;
    if (!D) return;
    const recordId = getQueryParam('id') || getQueryParam('student') || getQueryParam('device');
    if (!recordId) return;

    const allCollections = [
      ...D.schools, ...D.schoolAdmins, ...D.students,
      ...D.guardians, ...D.wardens, ...D.devices,
      ...D.transactions, ...D.subscriptions
    ];
    const found = allCollections.find((item) => item.id === recordId);
    if (!found) return;

    document.querySelectorAll('[data-bind-field]').forEach((el) => {
      const key = el.getAttribute('data-bind-field');
      if (found[key] !== undefined) {
        if (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA') {
          el.value = found[key];
        } else {
          el.textContent = found[key];
        }
      }
    });
  }

  /* ==================== AUTH ROLE LAUNCHER ==================== */
  function initAuthLoginFlow() {
    const loginForm = document.getElementById('s2d-auth-login-form');
    if (!loginForm) return;

    const roleSelect = document.getElementById('login-demo-role');
    const emailInput = document.getElementById('login-email');

    const rootPrefix = document.body.hasAttribute('data-root') ? document.body.getAttribute('data-root') : '../';
    const demoPresets = {
      'super-admin': { email: 'aarav.singhal@source2destination.in', target: `${rootPrefix}super-admin/dashboard.html` },
      'franchise':   { email: 'v.singhania@northedunet.in', target: `${rootPrefix}franchise/dashboard.html` },
      'school-admin':{ email: 'principal@doonvalley.edu.in', target: `${rootPrefix}school-admin/dashboard.html` }
    };

    if (roleSelect) {
      roleSelect.addEventListener('change', () => {
        const preset = demoPresets[roleSelect.value];
        if (preset && emailInput) {
          emailInput.value = preset.email;
          loginForm.setAttribute('data-redirect', preset.target);
        }
      });
    }

    document.querySelectorAll('[data-quick-role-fill]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const r = btn.getAttribute('data-quick-role-fill');
        if (roleSelect) {
          roleSelect.value = r;
          roleSelect.dispatchEvent(new Event('change'));
        }
      });
    });
  }

  /* ==================== INTERACTIVE ACTION BUTTONS ==================== */
  function initInteractiveTriggers() {
    document.querySelectorAll('[data-demo-action]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const actionTitle = btn.getAttribute('data-demo-action');
        const confirmPrompt = btn.getAttribute('data-confirm-prompt');
        if (confirmPrompt) {
          const ok = await window.S2DModal.confirm({
            title: actionTitle,
            recordLabel: btn.getAttribute('data-record-label') || 'Active Selection',
            message: confirmPrompt,
            confirmLabel: 'Proceed',
            variant: btn.classList.contains('btn-s2d-danger') || btn.classList.contains('btn-s2d-danger-outline') ? 'danger' : 'primary'
          });
          if (!ok) return;
        }
        window.S2DNotify.show({
          title: actionTitle,
          description: btn.getAttribute('data-demo-desc') || 'Action simulated in session memory. Ready for Django REST endpoint integration.',
          type: 'success'
        });
      });
    });

    // Server-side Student Code Issuance Request simulation
    const issueCodeBtn = document.getElementById('request-server-code-btn');
    if (issueCodeBtn) {
      issueCodeBtn.addEventListener('click', () => {
        const previewOut = document.getElementById('server-code-request-status');
        if (previewOut) {
          previewOut.style.display = 'flex';
        }
        window.S2DNotify.show({
          title: 'Server Code Issuance Queued',
          description: 'POST /api/v1/school-admin/student-codes/issue/ payload validated. Production entropy is strictly server-generated.',
          type: 'info'
        });
      });
    }
  }

  /* ==================== BOOTSTRAP APPLICATION ==================== */
  document.addEventListener('DOMContentLoaded', () => {
    if (window.S2DSidebar) window.S2DSidebar.renderSidebarAndTopbar();
    if (window.lucide) window.lucide.createIcons();
    if (window.S2DModal) window.S2DModal.bindDeclarativeModals();
    if (window.S2DAnimations) {
      window.S2DAnimations.initTabs();
      window.S2DAnimations.initAnimations();
    }
    initDeclarativeTables();
    hydrateDynamicRecordBindings();
    initAuthLoginFlow();
    if (window.S2DForms) {
      window.S2DForms.initForms();
      window.S2DForms.initBulkUploadWizard();
      window.S2DForms.initScheduleMatrices();
    }
    if (window.S2DCharts) window.S2DCharts.mountCharts();
    initInteractiveTriggers();
  });
})(window, document);
