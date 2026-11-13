/* ==========================================================================
   Source 2 Destination — Enterprise Forms, Validation, Bulk Upload & Schedules
   File: assets/js/forms.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  function validateField(input) {
    const val = (input.value || '').trim();
    const isReq = input.hasAttribute('required') || input.dataset.required === 'true';
    const type = input.getAttribute('type') || '';
    let errorMsg = '';

    if (isReq && !val) {
      errorMsg = 'This field is required.';
    } else if (val && type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
      errorMsg = 'Enter a valid institutional email address.';
    } else if (val && input.dataset.validatePhone === 'true' && val.replace(/\D/g, '').length < 10) {
      errorMsg = 'Enter a valid 10+ digit authorized telephone number.';
    } else if (val && type === 'number') {
      const num = Number(val);
      if (input.min !== '' && num < Number(input.min)) errorMsg = `Minimum allowed value is ${input.min}.`;
      if (input.max !== '' && num > Number(input.max)) errorMsg = `Maximum allowed ceiling is ${input.max}.`;
    } else if (input.dataset.matchTarget) {
      const other = document.querySelector(input.dataset.matchTarget);
      if (other && val !== other.value) errorMsg = 'Confirmation password does not match.';
    }

    const fieldBox = input.closest('.s2d-field') || input.parentElement;
    let errEl = fieldBox ? fieldBox.querySelector('.field-error') : null;
    if (!errEl && fieldBox) {
      errEl = document.createElement('div');
      errEl.className = 'field-error';
      fieldBox.appendChild(errEl);
    }

    if (errorMsg) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      if (errEl) {
        errEl.textContent = errorMsg;
        errEl.classList.add('show');
      }
      return false;
    } else {
      input.classList.remove('is-invalid');
      if (val) input.classList.add('is-valid');
      if (errEl) {
        errEl.textContent = '';
        errEl.classList.remove('show');
      }
      return true;
    }
  }

  function initForms() {
    // Phone input live formatting helper
    document.querySelectorAll('[data-validate-phone="true"]').forEach((inp) => {
      inp.addEventListener('blur', () => validateField(inp));
    });

    // Password visibility toggles
    document.querySelectorAll('[data-toggle-password]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetSelector = btn.getAttribute('data-toggle-password');
        const inp = document.querySelector(targetSelector);
        if (!inp) return;
        const nextType = inp.type === 'password' ? 'text' : 'password';
        inp.type = nextType;
        btn.innerHTML = `<i data-lucide="${nextType === 'password' ? 'eye' : 'eye-off'}" style="width:16px;height:16px;"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [btn] });
      });
    });

    // Password strength meter on reset-password
    const strengthInput = document.querySelector('[data-password-strength]');
    if (strengthInput) {
      const bar = document.getElementById('pwd-strength-bar');
      const label = document.getElementById('pwd-strength-label');
      strengthInput.addEventListener('input', () => {
        const v = strengthInput.value;
        let score = 0;
        if (v.length >= 8) score += 25;
        if (/[A-Z]/.test(v)) score += 25;
        if (/[0-9]/.test(v)) score += 25;
        if (/[^A-Za-z0-9]/.test(v)) score += 25;
        if (bar) {
          bar.style.width = `${score}%`;
          bar.className = 's2d-progress-bar ' + (score < 50 ? 'rose' : score < 75 ? 'amber' : 'emerald');
        }
        if (label) {
          label.textContent = score === 0 ? 'Enter a strong password' : score < 50 ? 'Weak — add uppercase, digits & symbols' : score < 100 ? 'Good — meets baseline policy' : 'Strong enterprise password';
        }
      });
    }

    // Standard S2D managed forms
    document.querySelectorAll('form[data-s2d-form]').forEach((form) => {
      let isDirty = false;
      const unsavedBadge = form.querySelector('.unsaved-indicator') || document.querySelector('.unsaved-indicator');

      form.querySelectorAll('input, select, textarea').forEach((el) => {
        el.addEventListener('input', () => {
          isDirty = true;
          if (unsavedBadge) unsavedBadge.classList.add('show');
          if (el.classList.contains('is-invalid')) validateField(el);
        });
        el.addEventListener('blur', () => {
          if (el.hasAttribute('required') || el.value) validateField(el);
        });
      });

      window.addEventListener('beforeunload', (e) => {
        if (isDirty && form.dataset.warnUnsaved === 'true') {
          e.preventDefault();
          e.returnValue = '';
        }
      });

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        let allValid = true;
        form.querySelectorAll('input, select, textarea').forEach((el) => {
          if (!validateField(el)) allValid = false;
        });

        if (!allValid) {
          window.S2DNotify.show({
            title: 'Validation Check Required',
            description: 'Please review the highlighted fields before submitting.',
            type: 'danger'
          });
          const firstInvalid = form.querySelector('.is-invalid');
          if (firstInvalid) firstInvalid.focus();
          return;
        }

        isDirty = false;
        if (unsavedBadge) unsavedBadge.classList.remove('show');

        const redirectTarget = form.getAttribute('data-redirect');
        const successTitle = form.getAttribute('data-success-title') || 'Record Saved (Demo Simulation)';
        const successDesc = form.getAttribute('data-success-desc') || 'Validated payload prepared for Django REST API and applied to session memory.';

        const submitBtn = form.querySelector('[type="submit"]');
        const origHtml = submitBtn ? submitBtn.innerHTML : '';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `<span>Processing...</span>`;
        }

        const submitAction = async () => {
          if (form.hasAttribute('action') && form.getAttribute('action') !== '#' && !form.getAttribute('action').startsWith('javascript:')) {
            try {
              const formData = new FormData(form);
              await fetch(form.action, {
                method: form.getAttribute('method') || 'POST',
                body: formData
              });
              if (window.S2DActiveTables) {
                Object.values(window.S2DActiveTables).forEach(t => t && t.refresh && t.refresh());
              }
            } catch (err) {
              console.warn("Form server submit:", err);
            }
          }
        };

        setTimeout(async () => {
          await submitAction();

          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = origHtml;
            if (window.lucide) window.lucide.createIcons({ nodes: [submitBtn] });
          }

          // Close parent modal if inside modal
          const parentModal = form.closest('.s2d-modal-backdrop');
          if (parentModal) parentModal.classList.remove('show');

          window.S2DNotify.show({
            title: successTitle,
            description: successDesc,
            type: 'success'
          });

          if (redirectTarget) {
            setTimeout(() => {
              window.location.href = redirectTarget;
            }, 650);
          }
        }, 280);
      });
    });
  }

  /* ==================== BULK EXCEL / CSV UPLOAD EXPERIENCE ==================== */
  function initBulkUploadWizard() {
    const zone = document.getElementById('bulk-upload-dropzone');
    if (!zone) return;

    const fileInput = document.getElementById('bulk-file-input');
    const sampleBtn = document.getElementById('download-sample-template');
    const simulateBtn = document.getElementById('simulate-sample-validation');
    const previewSection = document.getElementById('bulk-validation-preview');
    const confirmImportBtn = document.getElementById('confirm-bulk-import-btn');
    const fileBadge = document.getElementById('uploaded-filename-badge');

    const sampleRows = [
      { row: 2, name: ' Evelyn Montgomery', code: 'AUTO-SERVER', school: 'Oakridge Residential Academy', grade: 'Grade 9', section: 'Section A', fatherPhone: '+1 (555) 890-1101', motherPhone: '+1 (555) 890-1102', status: 'Valid', issue: 'Ready for import' },
      { row: 3, name: 'Sebastian Cross', code: 'AUTO-SERVER', school: 'Oakridge Residential Academy', grade: 'Grade 10', section: 'Section B', fatherPhone: '+1 (555) 890-2240', motherPhone: '+1 (555) 890-2241', status: 'Valid', issue: 'Ready for import' },
      { row: 4, name: 'Liam Hawthorne', code: 'S2D-OAK-8841', school: 'Oakridge Residential Academy', grade: 'Grade 10', section: 'Section A', fatherPhone: '+1 (555) 801-2210', motherPhone: '+1 (555) 801-2211', status: 'Duplicate', issue: 'Duplicate student + primary phone already exists (STU-4001)' },
      { row: 5, name: 'Nora Lindqvist', code: 'AUTO-SERVER', school: 'Oakridge Residential Academy', grade: 'Grade 11', section: 'Section C', fatherPhone: '555-99', motherPhone: '', status: 'Error', issue: 'Invalid E.164 guardian phone number format' },
      { row: 6, name: 'Julian Ashford', code: 'AUTO-SERVER', school: 'Oakridge Residential Academy', grade: 'Grade 8', section: 'Section A', fatherPhone: '+1 (555) 890-4418', motherPhone: '+1 (555) 890-4419', status: 'Valid', issue: 'Ready for import' }
    ];

    function renderPreview(fileName) {
      if (!previewSection) return;
      previewSection.style.display = 'block';
      if (fileBadge) fileBadge.textContent = fileName;
      const tbody = document.getElementById('bulk-preview-tbody');
      if (tbody) {
        tbody.innerHTML = sampleRows.map((r) => {
          const badgeCls = r.status === 'Valid' ? 's2d-badge-success' : r.status === 'Duplicate' ? 's2d-badge-warning' : 's2d-badge-danger';
          return `
            <tr>
              <td class="mono-code">#${r.row}</td>
              <td class="cell-primary">${r.name}</td>
              <td>${r.grade} · ${r.section}</td>
              <td class="mono-code">${r.fatherPhone}</td>
              <td><span class="s2d-badge ${badgeCls}">${r.status}</span></td>
              <td class="text-secondary-s2d">${r.issue}</td>
            </tr>
          `;
        }).join('');
      }
      window.S2DNotify.show({
        title: 'Spreadsheet Parsed for Preview',
        description: `${fileName}: 3 valid records, 1 duplicate warning, 1 phone validation error.`,
        type: 'info'
      });
    }

    zone.addEventListener('click', () => fileInput && fileInput.click());
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('dragover');
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) renderPreview(file.name);
    });

    if (fileInput) {
      fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files[0]) renderPreview(fileInput.files[0].name);
      });
    }

    if (simulateBtn) {
      simulateBtn.addEventListener('click', () => renderPreview('oakridge_term1_students_sample.xlsx'));
    }

    if (sampleBtn) {
      sampleBtn.addEventListener('click', () => {
        const csv = [
          'student_full_name,class_grade,section,hostel_wing,father_name,father_authorized_phone,mother_name,mother_authorized_phone,validity_plan_code',
          '"Evelyn Montgomery","Grade 9","Section A","East Gables Rm 104","Arthur Montgomery","+15558901101","claire Montgomery","+15558901102","RPL-02"',
          '"Sebastian Cross","Grade 10","Section B","North Hall Rm 212","Edward Cross","+15558902240","Hannah Cross","+15558902241","RPL-03"'
        ].join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 's2d_bulk_student_upload_template.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        window.S2DNotify.show({ title: 'Sample Template Downloaded', description: 's2d_bulk_student_upload_template.csv saved.', type: 'success' });
      });
    }

    if (confirmImportBtn) {
      confirmImportBtn.addEventListener('click', async () => {
        const ok = await window.S2DModal.confirm({
          title: 'Import 3 Validated Student Records?',
          recordLabel: '3 Valid · 2 Skipped (Duplicate/Error)',
          message: 'Valid rows will be staged in session memory. Duplicate and invalid rows will be excluded pending correction.',
          confirmLabel: 'Confirm Import (3 Students)',
          variant: 'primary'
        });
        if (ok) {
          window.S2DNotify.show({
            title: 'Bulk Import Simulated',
            description: '3 validated student accounts added to temporary session memory; server-side unique codes queued for DRF API.',
            type: 'success'
          });
        }
      });
    }
  }

  /* ==================== INTERACTIVE WEEKLY SCHEDULE MATRIX ==================== */
  function initScheduleMatrices() {
    document.querySelectorAll('[data-schedule-matrix]').forEach((grid) => {
      grid.addEventListener('click', (e) => {
        const cell = e.target.closest('.schedule-cell');
        if (!cell) return;
        if (cell.classList.contains('allowed')) {
          cell.classList.remove('allowed');
          cell.classList.add('restricted');
          cell.textContent = 'Restricted';
        } else if (cell.classList.contains('restricted')) {
          cell.classList.remove('restricted');
          cell.classList.add('override');
          cell.textContent = 'Supervised';
        } else {
          cell.classList.remove('override');
          cell.classList.add('allowed');
          cell.textContent = 'Allowed';
        }
      });
    });
  }

  window.S2DForms = { initForms, validateField, initBulkUploadWizard, initScheduleMatrices };
})(window, document);
