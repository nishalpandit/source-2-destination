/* ==========================================================================
   Source 2 Destination — Reusable Enterprise Data Table Engine
   File: assets/js/tables.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function statusBadge(status) {
    const val = String(status || 'Unknown');
    const lower = val.toLowerCase();
    let cls = 's2d-badge-neutral';
    if (['active', 'successful', 'completed', 'online', 'compliant', 'enrolled (ae dedicated)', 'kyc verified', 'authorized', 'enabled'].some((k) => lower.includes(k))) {
      cls = 's2d-badge-success';
    } else if (['expiring', 'pending', 'warning', 'policy update pending', 'manual invoice', 'emergency only'].some((k) => lower.includes(k))) {
      cls = 's2d-badge-warning';
    } else if (['expired', 'suspended', 'failed', 'blocked', 'offline', 'restricted', 'critical', 'non-compliant', 'missed'].some((k) => lower.includes(k))) {
      cls = 's2d-badge-danger';
    } else if (['refunded', 'available', 'info', 'court letter'].some((k) => lower.includes(k))) {
      cls = 's2d-badge-info';
    }
    return `<span class="s2d-badge ${cls}">${window.S2DNotify.escapeHtml(val)}</span>`;
  }

  class EnterpriseTable {
    constructor(config) {
      this.mount = typeof config.mount === 'string' ? document.querySelector(config.mount) : config.mount;
      if (!this.mount) return;

      this.id = config.id || 's2d-tbl-' + Math.random().toString(36).slice(2, 7);
      this.columns = config.columns || [];
      this.rawData = Array.isArray(config.data) ? config.data : [];
      this.searchPlaceholder = config.searchPlaceholder || 'Search records...';
      this.searchKeys = config.searchKeys || this.columns.map((c) => c.key).filter(Boolean);
      this.filtersConfig = config.filters || []; // [{ key, label, options: ['Active','Suspended'] }]
      this.dateFilterKey = config.dateFilterKey || null;
      this.selectable = config.selectable !== false;
      this.bulkActions = config.bulkActions || [
        { label: 'Activate Selected', action: 'activate' },
        { label: 'Suspend Selected', action: 'suspend' }
      ];
      this.rowActions = config.rowActions || null; // fn(row) => [{ label, icon, href, onClick, danger }]
      this.exportFilename = config.exportFilename || 's2d-export.csv';

      this.state = {
        search: '',
        filters: {},
        dateFrom: '',
        dateTo: '',
        sortField: config.defaultSort || '',
        sortDir: config.defaultSortDir || 'asc',
        page: 1,
        pageSize: config.pageSize || 8,
        selectedIds: new Set(),
        loading: false
      };

      this.renderShell();
      this.renderRows();
    }

    setData(newData) {
      this.rawData = Array.isArray(newData) ? newData : [];
      this.state.page = 1;
      this.renderRows();
    }

    getFilteredData() {
      const q = this.state.search.toLowerCase().trim();
      let items = this.rawData.filter((row) => {
        if (q) {
          const hit = this.searchKeys.some((k) => String(row[k] ?? '').toLowerCase().includes(q));
          if (!hit) return false;
        }
        for (const [fk, fv] of Object.entries(this.state.filters)) {
          if (fv && fv !== 'all') {
            if (String(row[fk] ?? '').toLowerCase() !== String(fv).toLowerCase()) return false;
          }
        }
        if (this.dateFilterKey && (this.state.dateFrom || this.state.dateTo)) {
          const rawDate = String(row[this.dateFilterKey] || '').slice(0, 10);
          if (this.state.dateFrom && rawDate < this.state.dateFrom) return false;
          if (this.state.dateTo && rawDate > this.state.dateTo) return false;
        }
        return true;
      });

      if (this.state.sortField) {
        const key = this.state.sortField;
        const mul = this.state.sortDir === 'desc' ? -1 : 1;
        items = [...items].sort((a, b) => {
          const va = a[key];
          const vb = b[key];
          if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * mul;
          const na = parseFloat(String(va).replace(/[^0-9.-]+/g, ''));
          const nb = parseFloat(String(vb).replace(/[^0-9.-]+/g, ''));
          if (!isNaN(na) && !isNaN(nb) && String(va).match(/^\$?-?\d/)) return (na - nb) * mul;
          return String(va ?? '').localeCompare(String(vb ?? '')) * mul;
        });
      }
      return items;
    }

    renderShell() {
      const filtersHtml = this.filtersConfig.map((f) => `
        <select class="table-filter-select" data-filter-key="${f.key}" aria-label="${f.label}">
          <option value="all">${f.label}: All</option>
          ${f.options.map((opt) => `<option value="${opt}">${opt}</option>`).join('')}
        </select>
      `).join('');

      const dateHtml = this.dateFilterKey ? `
        <input type="date" class="table-date-input" data-date-from aria-label="Start date" title="From Date">
        <input type="date" class="table-date-input" data-date-to aria-label="End date" title="To Date">
      ` : '';

      const bulkBtnsHtml = this.bulkActions.map((b) => `
        <button type="button" class="btn-s2d btn-s2d-secondary btn-xs-s2d" data-bulk-act="${b.action}">${b.label}</button>
      `).join('');

      this.mount.innerHTML = `
        <div class="table-card">
          <div class="table-toolbar">
            <div class="table-toolbar-filters">
              <div class="table-search-wrap">
                <i data-lucide="search" class="search-icon"></i>
                <input type="search" class="table-search-input" placeholder="${this.searchPlaceholder}" aria-label="${this.searchPlaceholder}">
              </div>
              ${filtersHtml}
              ${dateHtml}
              <button type="button" class="btn-s2d btn-s2d-ghost btn-sm-s2d" data-tbl-clear title="Reset search & filters">
                <i data-lucide="rotate-ccw" style="width:14px;height:14px;"></i>
                <span>Clear</span>
              </button>
            </div>
            <div class="table-toolbar-actions">
              <button type="button" class="btn-s2d btn-s2d-secondary btn-sm-s2d" data-tbl-refresh title="Refresh dataset">
                <i data-lucide="refresh-cw" style="width:14px;height:14px;"></i>
                <span class="d-none d-sm-inline">Refresh</span>
              </button>
              <button type="button" class="btn-s2d btn-s2d-secondary btn-sm-s2d" data-tbl-export title="Export filtered records to CSV">
                <i data-lucide="download" style="width:14px;height:14px;"></i>
                <span>Export CSV</span>
              </button>
            </div>
          </div>

          <div class="bulk-action-bar" data-bulk-bar>
            <div><strong data-selected-count>0</strong> records selected</div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              ${bulkBtnsHtml}
              <button type="button" class="btn-s2d btn-s2d-ghost btn-xs-s2d" data-bulk-clear>Clear Selection</button>
            </div>
          </div>

          <div class="s2d-table-wrap">
            <table class="s2d-table">
              <thead>
                <tr data-tbl-head></tr>
              </thead>
              <tbody data-tbl-body></tbody>
            </table>
          </div>

          <div class="table-pagination">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
              <span data-tbl-summary>Showing 0 records</span>
              <select class="table-filter-select" data-tbl-pagesize style="height:29px;font-size:0.75rem;padding:0 22px 0 8px;" aria-label="Rows per page">
                <option value="8" ${this.state.pageSize === 8 ? 'selected' : ''}>8 / page</option>
                <option value="15" ${this.state.pageSize === 15 ? 'selected' : ''}>15 / page</option>
                <option value="25" ${this.state.pageSize === 25 ? 'selected' : ''}>25 / page</option>
              </select>
            </div>
            <div class="pagination-controls" data-tbl-pager></div>
          </div>
        </div>
      `;

      if (window.lucide) window.lucide.createIcons({ nodes: [this.mount] });
      this.bindShellEvents();
    }

    renderHeader() {
      const headTr = this.mount.querySelector('[data-tbl-head]');
      let html = '';
      if (this.selectable) {
        html += `<th style="width:40px;"><input type="checkbox" class="s2d-checkbox" data-select-all aria-label="Select all visible rows"></th>`;
      }
      this.columns.forEach((col) => {
        const sortable = col.sortable !== false && col.key;
        const isSorted = this.state.sortField === col.key;
        const sortCls = isSorted ? (this.state.sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc') : '';
        const iconName = isSorted ? (this.state.sortDir === 'asc' ? 'arrow-up' : 'arrow-down') : 'arrow-up-down';
        html += `
          <th class="${sortable ? 'sortable' : ''} ${sortCls}" ${sortable ? `data-sort-col="${col.key}"` : ''}>
            ${col.label}
            ${sortable ? `<span class="sort-indicator"><i data-lucide="${iconName}" style="width:12px;height:12px;"></i></span>` : ''}
          </th>
        `;
      });
      if (this.rowActions) {
        html += `<th style="text-align:right;width:60px;">Actions</th>`;
      }
      headTr.innerHTML = html;
      if (window.lucide) window.lucide.createIcons({ nodes: [headTr] });

      headTr.querySelectorAll('[data-sort-col]').forEach((th) => {
        th.addEventListener('click', () => {
          const colKey = th.getAttribute('data-sort-col');
          if (this.state.sortField === colKey) {
            this.state.sortDir = this.state.sortDir === 'asc' ? 'desc' : 'asc';
          } else {
            this.state.sortField = colKey;
            this.state.sortDir = 'asc';
          }
          this.renderRows();
        });
      });

      const selectAll = headTr.querySelector('[data-select-all]');
      if (selectAll) {
        selectAll.addEventListener('change', () => {
          const pageRows = this.getCurrentPageSlice().pageItems;
          pageRows.forEach((r) => {
            if (selectAll.checked) this.state.selectedIds.add(r.id);
            else this.state.selectedIds.delete(r.id);
          });
          this.renderRows();
        });
      }
    }

    getCurrentPageSlice() {
      const filtered = this.getFilteredData();
      const total = filtered.length;
      const totalPages = Math.max(1, Math.ceil(total / this.state.pageSize));
      if (this.state.page > totalPages) this.state.page = totalPages;
      const startIdx = (this.state.page - 1) * this.state.pageSize;
      const pageItems = filtered.slice(startIdx, startIdx + this.state.pageSize);
      return { filtered, total, totalPages, startIdx, pageItems };
    }

    renderRows() {
      this.renderHeader();
      const tbody = this.mount.querySelector('[data-tbl-body]');
      const summaryEl = this.mount.querySelector('[data-tbl-summary]');
      const pagerEl = this.mount.querySelector('[data-tbl-pager]');
      const bulkBar = this.mount.querySelector('[data-bulk-bar]');
      const selCountEl = this.mount.querySelector('[data-selected-count]');

      const colCount = this.columns.length + (this.selectable ? 1 : 0) + (this.rowActions ? 1 : 0);

      if (this.state.loading) {
        tbody.innerHTML = Array.from({ length: 5 }).map(() => `
          <tr>${Array.from({ length: colCount }).map(() => `<td><div class="skeleton-bar" style="width:${60 + Math.floor(Math.random() * 35)}%;"></div></td>`).join('')}</tr>
        `).join('');
        return;
      }

      const { total, totalPages, startIdx, pageItems } = this.getCurrentPageSlice();

      // Update bulk toolbar
      selCountEl.textContent = String(this.state.selectedIds.size);
      bulkBar.classList.toggle('show', this.state.selectedIds.size > 0);

      if (!pageItems.length) {
        tbody.innerHTML = `
          <tr>
            <td colspan="${colCount}">
              <div class="table-empty-state">
                <div class="table-empty-icon"><i data-lucide="inbox"></i></div>
                <div style="font-weight:600;color:var(--s2d-heading);margin-bottom:4px;">No matching records found</div>
                <div style="font-size:0.8rem;color:var(--s2d-text-secondary);margin-bottom:14px;">Adjust your search query or active filter criteria to view records.</div>
                <button type="button" class="btn-s2d btn-s2d-secondary btn-sm-s2d" data-empty-reset>Reset All Filters</button>
              </div>
            </td>
          </tr>
        `;
        summaryEl.textContent = 'Showing 0 of 0 records';
        pagerEl.innerHTML = '';
        if (window.lucide) window.lucide.createIcons({ nodes: [tbody] });
        const rst = tbody.querySelector('[data-empty-reset]');
        if (rst) rst.addEventListener('click', () => this.clearAllFilters());
        return;
      }

      tbody.innerHTML = pageItems.map((row, rowIndex) => {
        const isChecked = this.state.selectedIds.has(row.id);
        let cells = '';
        if (this.selectable) {
          cells += `<td><input type="checkbox" class="s2d-checkbox" data-row-check="${row.id}" ${isChecked ? 'checked' : ''} aria-label="Select row ${row.id}"></td>`;
        }
        this.columns.forEach((col) => {
          const val = col.render ? col.render(row) : window.S2DNotify.escapeHtml(row[col.key] ?? '—');
          cells += `<td>${val}</td>`;
        });
        if (this.rowActions) {
          const actions = this.rowActions(row) || [];
          const menuItems = actions.map((act, aIdx) => {
            if (act.divider) return `<div class="s2d-dropdown-divider"></div>`;
            if (act.href) {
              return `<a href="${act.href}" class="s2d-dropdown-item ${act.danger ? 'danger' : ''}">
                <i data-lucide="${act.icon || 'arrow-up-right'}" style="width:14px;height:14px;"></i>
                <span>${act.label}</span>
              </a>`;
            }
            return `<button type="button" class="s2d-dropdown-item ${act.danger ? 'danger' : ''}" data-row-act-idx="${rowIndex}:${aIdx}">
              <i data-lucide="${act.icon || 'sliders'}" style="width:14px;height:14px;"></i>
              <span>${act.label}</span>
            </button>`;
          }).join('');

          cells += `
            <td class="row-action-cell">
              <button type="button" class="row-action-btn" data-row-menu-btn aria-label="Row actions">
                <i data-lucide="more-horizontal" style="width:16px;height:16px;"></i>
              </button>
              <div class="s2d-dropdown-menu" style="min-width:185px;right:12px;">
                ${menuItems}
              </div>
            </td>
          `;
        }
        return `<tr class="${isChecked ? 'row-selected' : ''}">${cells}</tr>`;
      }).join('');

      // Summary & Pager
      const endIdx = Math.min(startIdx + pageItems.length, total);
      summaryEl.textContent = `Showing ${startIdx + 1}–${endIdx} of ${total} records`;

      let pagerHtml = `<button type="button" class="page-btn" data-page-go="${this.state.page - 1}" ${this.state.page <= 1 ? 'disabled' : ''}>Prev</button>`;
      for (let p = 1; p <= totalPages; p++) {
        pagerHtml += `<button type="button" class="page-btn ${p === this.state.page ? 'active' : ''}" data-page-go="${p}">${p}</button>`;
      }
      pagerHtml += `<button type="button" class="page-btn" data-page-go="${this.state.page + 1}" ${this.state.page >= totalPages ? 'disabled' : ''}>Next</button>`;
      pagerEl.innerHTML = pagerHtml;

      if (window.lucide) window.lucide.createIcons({ nodes: [tbody] });

      // Row checkbox listeners
      tbody.querySelectorAll('[data-row-check]').forEach((cb) => {
        cb.addEventListener('change', () => {
          const rid = cb.getAttribute('data-row-check');
          if (cb.checked) this.state.selectedIds.add(rid);
          else this.state.selectedIds.delete(rid);
          this.renderRows();
        });
      });

      // Row action dropdown triggers
      tbody.querySelectorAll('[data-row-menu-btn]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const menu = btn.nextElementSibling;
          const wasOpen = menu.classList.contains('show');
          document.querySelectorAll('.s2d-dropdown-menu.show').forEach((m) => m.classList.remove('show'));
          if (!wasOpen) menu.classList.add('show');
        });
      });

      // Row action callbacks
      tbody.querySelectorAll('[data-row-act-idx]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          document.querySelectorAll('.s2d-dropdown-menu.show').forEach((m) => m.classList.remove('show'));
          const [rIdx, aIdx] = btn.getAttribute('data-row-act-idx').split(':').map(Number);
          const targetRow = pageItems[rIdx];
          const acts = this.rowActions(targetRow);
          if (acts && acts[aIdx] && typeof acts[aIdx].onClick === 'function') {
            acts[aIdx].onClick(targetRow, () => this.renderRows());
          }
        });
      });

      // Pagination buttons
      pagerEl.querySelectorAll('[data-page-go]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const nextP = Number(btn.getAttribute('data-page-go'));
          if (nextP >= 1 && nextP <= totalPages) {
            this.state.page = nextP;
            this.renderRows();
          }
        });
      });
    }

    clearAllFilters() {
      this.state.search = '';
      this.state.filters = {};
      this.state.dateFrom = '';
      this.state.dateTo = '';
      this.state.page = 1;
      const sInput = this.mount.querySelector('.table-search-input');
      if (sInput) sInput.value = '';
      this.mount.querySelectorAll('.table-filter-select[data-filter-key]').forEach((s) => { s.value = 'all'; });
      this.mount.querySelectorAll('.table-date-input').forEach((d) => { d.value = ''; });
      this.renderRows();
    }

    bindShellEvents() {
      const searchInput = this.mount.querySelector('.table-search-input');
      searchInput.addEventListener('input', () => {
        this.state.search = searchInput.value;
        this.state.page = 1;
        this.renderRows();
      });

      this.mount.querySelectorAll('[data-filter-key]').forEach((sel) => {
        sel.addEventListener('change', () => {
          this.state.filters[sel.getAttribute('data-filter-key')] = sel.value;
          this.state.page = 1;
          this.renderRows();
        });
      });

      const fromDate = this.mount.querySelector('[data-date-from]');
      const toDate = this.mount.querySelector('[data-date-to]');
      if (fromDate) fromDate.addEventListener('change', () => { this.state.dateFrom = fromDate.value; this.state.page = 1; this.renderRows(); });
      if (toDate) toDate.addEventListener('change', () => { this.state.dateTo = toDate.value; this.state.page = 1; this.renderRows(); });

      const clearBtn = this.mount.querySelector('[data-tbl-clear]');
      clearBtn.addEventListener('click', () => this.clearAllFilters());

      const refreshBtn = this.mount.querySelector('[data-tbl-refresh]');
      refreshBtn.addEventListener('click', () => {
        this.state.loading = true;
        this.renderRows();
        setTimeout(() => {
          this.state.loading = false;
          this.renderRows();
          window.S2DNotify.show({ title: 'Dataset Refreshed', description: 'Synchronized with current in-memory demonstration state.', type: 'info', duration: 2600 });
        }, 320);
      });

      const exportBtn = this.mount.querySelector('[data-tbl-export]');
      exportBtn.addEventListener('click', () => this.exportCsv());

      const pageSizeSel = this.mount.querySelector('[data-tbl-pagesize]');
      pageSizeSel.addEventListener('change', () => {
        this.state.pageSize = Number(pageSizeSel.value);
        this.state.page = 1;
        this.renderRows();
      });

      const bulkClear = this.mount.querySelector('[data-bulk-clear]');
      if (bulkClear) {
        bulkClear.addEventListener('click', () => {
          this.state.selectedIds.clear();
          this.renderRows();
        });
      }

      this.mount.querySelectorAll('[data-bulk-act]').forEach((btn) => {
        btn.addEventListener('click', async () => {
          const act = btn.getAttribute('data-bulk-act');
          const count = this.state.selectedIds.size;
          const ok = await window.S2DModal.confirm({
            title: `${act === 'activate' ? 'Activate' : 'Suspend'} ${count} Selected Record(s)?`,
            recordLabel: `${count} records selected`,
            message: `This batch action will update status in session memory for all ${count} selected records.`,
            confirmLabel: act === 'activate' ? 'Activate Selected' : 'Suspend Selected',
            variant: act === 'activate' ? 'success' : 'danger'
          });
          if (!ok) return;
          this.rawData.forEach((r) => {
            if (this.state.selectedIds.has(r.id) && 'status' in r) {
              r.status = act === 'activate' ? 'Active' : 'Suspended';
            }
          });
          this.state.selectedIds.clear();
          this.renderRows();
          window.S2DNotify.show({ title: 'Batch Status Updated', description: `Applied "${act}" to ${count} record(s) in demo memory.`, type: 'success' });
        });
      });
    }

    exportCsv() {
      const rows = this.getFilteredData();
      const exportCols = this.columns.filter((c) => c.key);
      if (!exportCols.length) return;

      const header = exportCols.map((c) => `"${c.label.replace(/"/g, '""')}"`).join(',');
      const lines = rows.map((r) => exportCols.map((c) => `"${String(r[c.key] ?? '').replace(/"/g, '""')}"`).join(','));
      const csv = [header, ...lines].join('\n');

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = this.exportFilename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      window.S2DNotify.show({
        title: 'CSV Export Generated',
        description: `Exported ${rows.length} filtered record(s) to ${this.exportFilename}.`,
        type: 'success'
      });
    }
  }

  window.S2DTables = { EnterpriseTable, statusBadge };
})(window, document);
