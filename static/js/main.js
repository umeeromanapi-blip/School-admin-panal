/**
 * School Management Admin Panel — Client Interactions & REST API Fetch Integration
 * Connects frontend forms, buttons, and tables to Django REST Framework APIs.
 */

// Helper to retrieve CSRF token for Fetch requests
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  if (cookieValue) return decodeURIComponent(cookieValue);

  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : '';
}

// Helper to display modern toast alerts dynamically
function showToast(message, type = 'success') {
  let wrapper = document.getElementById('toast-wrapper');
  if (!wrapper) {
    wrapper = document.createElement('div');
    wrapper.id = 'toast-wrapper';
    wrapper.className = 'toast-container';
    document.body.appendChild(wrapper);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type === 'error' ? 'danger' : type}`;
  toast.setAttribute('role', 'alert');

  let iconSvg = '';
  if (type === 'success') {
    iconSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
  } else if (type === 'error' || type === 'danger') {
    iconSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/></svg>';
  } else {
    iconSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
  }

  toast.innerHTML = `
    <div class="toast-icon">${iconSvg}</div>
    <div class="toast-body">${message}</div>
    <button class="toast-close" aria-label="Dismiss">&times;</button>
  `;

  wrapper.appendChild(toast);

  const timer = setTimeout(() => {
    dismissToast(toast);
  }, 4500);

  const closeBtn = toast.querySelector('.toast-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      clearTimeout(timer);
      dismissToast(toast);
    });
  }
}

function dismissToast(toast) {
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(100%)';
  setTimeout(() => {
    toast.remove();
  }, 300);
}

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-dismiss existing server-rendered toasts
  const existingToasts = document.querySelectorAll('.toast');
  existingToasts.forEach(toast => {
    const timer = setTimeout(() => {
      dismissToast(toast);
    }, 5000);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(timer);
        dismissToast(toast);
      });
    }
  });

  // 2. Client-side Instant Filter for Student Directory Table
  const clientSearchInput = document.getElementById('client-filter-input');
  const studentRows = document.querySelectorAll('.student-table-row');

  if (clientSearchInput && studentRows.length > 0) {
    clientSearchInput.addEventListener('input', (e) => {
      const filterVal = e.target.value.toLowerCase().trim();
      let matchCount = 0;

      studentRows.forEach(row => {
        const textContent = row.textContent.toLowerCase();
        if (textContent.includes(filterVal)) {
          row.style.display = '';
          matchCount++;
        } else {
          row.style.display = 'none';
        }
      });

      const countDisplay = document.getElementById('visible-count-display');
      if (countDisplay) {
        countDisplay.textContent = filterVal ? `Showing ${matchCount} matching` : '';
      }
    });
  }

  // 3. Dynamic Form Live Badge Preview
  const nameInput = document.getElementById('id_student_name');
  const admInput = document.getElementById('id_admission_number');
  const classInput = document.getElementById('id_student_class');
  const contactInput = document.getElementById('id_contact_number');

  const previewName = document.getElementById('preview-student-name');
  const previewAdm = document.getElementById('preview-admission-number');
  const previewClass = document.getElementById('preview-student-class');
  const previewContact = document.getElementById('preview-contact-number');
  const previewAvatar = document.getElementById('preview-avatar');

  function updatePreview() {
    if (!previewName) return;
    const name = nameInput?.value.trim() || 'Student Name';
    const adm = admInput?.value.trim() || 'ADM-XXX';
    const sClass = classInput?.value.trim() || 'Class --';
    const contact = contactInput?.value.trim() || '0300-------';

    previewName.textContent = name;
    previewAdm.textContent = adm.toUpperCase();
    previewClass.textContent = sClass;
    previewContact.textContent = contact;

    if (previewAvatar) {
      const initials = name.split(' ').map(p => p[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'ST';
      previewAvatar.textContent = initials;
    }
  }

  if (nameInput) {
    nameInput.addEventListener('input', updatePreview);
    admInput?.addEventListener('input', updatePreview);
    classInput?.addEventListener('input', updatePreview);
    contactInput?.addEventListener('input', updatePreview);
    updatePreview();
  }

  // 4. Mobile sidebar toggle
  const mobileToggle = document.getElementById('mobile-sidebar-toggle');
  const sidebar = document.querySelector('.app-sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // ========================================================
  // 5. REST API: Student Create & Update via Fetch API
  // ========================================================
  const studentMainForm = document.getElementById('student-main-form');
  if (studentMainForm) {
    studentMainForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const studentId = studentMainForm.dataset.studentId;
      const actionMode = studentMainForm.dataset.actionMode;
      const submitBtn = document.getElementById('btn-submit-student');
      const submitLabel = document.getElementById('btn-submit-label');
      const originalBtnText = submitLabel ? submitLabel.textContent : 'Save';

      // Clear previous error messages & styles
      ['student_name', 'admission_number', 'student_class', 'contact_number'].forEach(field => {
        const errEl = document.getElementById(`api-error-${field}`);
        if (errEl) {
          errEl.textContent = '';
          errEl.style.display = 'none';
        }
        const inputEl = document.getElementById(`id_${field}`);
        if (inputEl) {
          inputEl.style.borderColor = '';
        }
      });

      const payload = {
        student_name: nameInput ? nameInput.value.trim() : '',
        admission_number: admInput ? admInput.value.trim().toUpperCase() : '',
        student_class: classInput ? classInput.value.trim() : '',
        contact_number: contactInput ? contactInput.value.trim() : '',
      };

      const isUpdate = (actionMode === 'update' && studentId);
      const apiUrl = isUpdate ? `/api/students/${studentId}/` : '/api/students/';
      const apiMethod = isUpdate ? 'PUT' : 'POST';

      if (submitBtn) {
        submitBtn.disabled = true;
        if (submitLabel) submitLabel.textContent = 'Saving via REST API...';
      }

      try {
        const response = await fetch(apiUrl, {
          method: apiMethod,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (response.ok) {
          showToast(
            isUpdate
              ? `Student "${data.student_name}" updated successfully via REST API!`
              : `Student "${data.student_name}" (${data.admission_number}) registered successfully via REST API!`,
            'success'
          );
          setTimeout(() => {
            window.location.href = '/students/';
          }, 600);
        } else if (response.status === 400) {
          const errors = data.errors || data;
          let firstErrorField = null;

          Object.keys(errors).forEach(field => {
            const errBox = document.getElementById(`api-error-${field}`);
            const inputField = document.getElementById(`id_${field}`);
            const msg = Array.isArray(errors[field]) ? errors[field].join(' ') : errors[field];

            if (errBox) {
              errBox.textContent = msg;
              errBox.style.display = 'block';
            }
            if (inputField) {
              inputField.style.borderColor = '#ef4444';
              if (!firstErrorField) firstErrorField = inputField;
            }
          });

          if (firstErrorField) firstErrorField.focus();
          showToast('Please review the highlighted validation errors.', 'error');
        } else {
          showToast(data.detail || 'Server encountered an unexpected error.', 'error');
        }
      } catch (err) {
        console.error('REST API Error:', err);
        showToast('Network error: Unable to reach the Django REST API.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          if (submitLabel) submitLabel.textContent = originalBtnText;
        }
      }
    });
  }

  // ========================================================
  // 6. REST API: Instant Student Delete via Fetch API
  // ========================================================
  const deleteButtons = document.querySelectorAll('.btn-icon-delete');
  deleteButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const studentId = btn.dataset.studentId;
      const studentName = btn.dataset.studentName || 'this student';
      if (!studentId) return; // Allow normal link navigation if no data attribute

      e.preventDefault();

      const confirmed = window.confirm(
        `Are you sure you want to permanently delete student "${studentName}" via REST API?\n\nThis operation will delete the record from SQLite database immediately.`
      );

      if (!confirmed) return;

      try {
        const response = await fetch(`/api/students/${studentId}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Accept': 'application/json',
          },
        });

        if (response.status === 204 || response.ok) {
          const row = document.getElementById(`student-row-${studentId}`);
          if (row) {
            row.style.transition = 'all 0.35s ease';
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            setTimeout(() => {
              row.remove();
              showToast(`Student "${studentName}" deleted successfully via REST API.`, 'success');
            }, 350);
          } else {
            showToast(`Student "${studentName}" deleted successfully.`, 'success');
          }
        } else {
          showToast('Could not delete student record from server.', 'error');
        }
      } catch (err) {
        console.error('Delete API Error:', err);
        showToast('Network error occurred while calling delete API.', 'error');
      }
    });
  });

  // ========================================================
  // 7. REST API: Student Confirm Delete Page via Fetch API
  // ========================================================
  const confirmDeleteForm = document.getElementById('delete-student-form');
  if (confirmDeleteForm) {
    confirmDeleteForm.addEventListener('submit', async (e) => {
      const studentId = confirmDeleteForm.dataset.studentId;
      if (!studentId) return;

      e.preventDefault();
      const confirmBtn = document.getElementById('btn-confirm-delete');
      if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span>Deleting via API...</span>';
      }

      try {
        const response = await fetch(`/api/students/${studentId}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Accept': 'application/json',
          },
        });

        if (response.status === 204 || response.ok) {
          showToast('Student record permanently deleted via REST API.', 'success');
          setTimeout(() => {
            window.location.href = '/students/';
          }, 500);
        } else {
          showToast('Failed to delete student record.', 'error');
          if (confirmBtn) confirmBtn.disabled = false;
        }
      } catch (err) {
        console.error('Delete API Error:', err);
        showToast('Network error occurred during API deletion.', 'error');
        if (confirmBtn) confirmBtn.disabled = false;
      }
    });
  }

  // ========================================================
  // 8. REST API: Live Dashboard Sync via Fetch API
  // ========================================================
  const syncBtn = document.getElementById('btn-api-sync-dashboard');
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      const syncIcon = document.getElementById('sync-icon');
      const syncText = document.getElementById('sync-text');

      if (syncIcon) syncIcon.style.animation = 'spin 1s linear infinite';
      if (syncText) syncText.textContent = 'Syncing...';

      try {
        const response = await fetch('/api/dashboard/stats/', {
          headers: {
            'Accept': 'application/json',
          },
        });

        if (response.ok) {
          const stats = await response.json();
          const totalCounter = document.getElementById('total-student-count');
          if (totalCounter) {
            totalCounter.textContent = stats.total_students;
            totalCounter.style.transform = 'scale(1.1)';
            setTimeout(() => {
              totalCounter.style.transform = 'scale(1)';
            }, 250);
          }
          showToast(`Dashboard refreshed via REST API! Total active students: ${stats.total_students}`, 'success');
        } else {
          showToast('Failed to sync dashboard metrics.', 'error');
        }
      } catch (err) {
        console.error('Sync API Error:', err);
        showToast('Could not fetch real-time stats from API.', 'error');
      } finally {
        if (syncIcon) syncIcon.style.animation = '';
        if (syncText) syncText.textContent = 'Live API Sync';
      }
    });
  }
});
