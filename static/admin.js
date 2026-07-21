// Tammy admin dashboard - data-driven table renderer over the existing
// appointments/tasks/contacts/visitors/messages API, gated by the
// admin session cookie (see app/api/admin.py, app/api/deps.py).

(function () {
    const loginScreen = document.getElementById('loginScreen');
    const loginForm = document.getElementById('loginForm');
    const loginPassword = document.getElementById('loginPassword');
    const loginButton = document.getElementById('loginButton');
    const loginError = document.getElementById('loginError');

    const dashboard = document.getElementById('dashboard');
    const tabsEl = document.getElementById('tabs');
    const panelTitle = document.getElementById('panelTitle');
    const panelBody = document.getElementById('panelBody');
    const refreshButton = document.getElementById('refreshButton');
    const logoutButton = document.getElementById('logoutButton');

    function formatDateTime(value) {
        if (!value) return '—';
        const date = new Date(value);
        if (isNaN(date.getTime())) return value;
        return date.toLocaleString(undefined, {
            month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
        });
    }

    function pill(value, tone) {
        if (!value) return '';
        const cls = tone === 'muted' ? ' is-muted' : tone === 'warning' ? ' is-warning' : '';
        return `<span class="admin-pill${cls}">${escapeHtml(value.replace(/_/g, ' '))}</span>`;
    }

    function statusPill(value) {
        const muted = ['completed', 'checked_out', 'archived', 'cancelled', 'read'];
        const warning = ['no_show', 'urgent', 'flagged'];
        if (muted.includes(value)) return pill(value, 'muted');
        if (warning.includes(value)) return pill(value, 'warning');
        return pill(value);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text == null ? '' : String(text);
        return div.innerHTML;
    }

    // Each resource: where to fetch the list from, which columns to show,
    // and which row-level actions are available (shown conditionally).
    const RESOURCES = {
        appointments: {
            label: 'Appointments',
            endpoint: '/api/appointments/',
            columns: [
                { key: 'title', label: 'Title' },
                { key: 'start_time', label: 'Start', format: formatDateTime },
                { key: 'duration_minutes', label: 'Duration', format: (v) => (v ? `${v} min` : '—') },
                { key: 'location', label: 'Location' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
            ],
            actions: [
                { label: 'Delete', danger: true, confirm: 'Delete this appointment?', run: (row) => del(`/api/appointments/${row.id}`) },
            ],
        },
        tasks: {
            label: 'Tasks',
            endpoint: '/api/tasks/',
            columns: [
                { key: 'title', label: 'Title' },
                { key: 'priority', label: 'Priority', format: statusPill, raw: true },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
                { key: 'due_date', label: 'Due', format: formatDateTime },
            ],
            actions: [
                {
                    label: 'Complete', show: (row) => row.status !== 'completed',
                    run: (row) => post(`/api/tasks/${row.id}/complete`),
                },
                { label: 'Delete', danger: true, confirm: 'Delete this task?', run: (row) => del(`/api/tasks/${row.id}`) },
            ],
        },
        contacts: {
            label: 'Contacts',
            endpoint: '/api/contacts/',
            columns: [
                { key: 'full_name', label: 'Name' },
                { key: 'company', label: 'Company' },
                { key: 'email', label: 'Email' },
                { key: 'phone_number', label: 'Phone' },
            ],
            actions: [
                { label: 'Delete', danger: true, confirm: 'Delete this contact?', run: (row) => del(`/api/contacts/${row.id}`) },
            ],
        },
        visitors: {
            label: 'Visitors',
            endpoint: '/api/visitors/',
            columns: [
                { key: 'full_name', label: 'Name' },
                { key: 'host_name', label: 'Host' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
                { key: 'check_in_time', label: 'Checked in', format: formatDateTime },
            ],
            actions: [
                {
                    label: 'Check in', show: (row) => row.status === 'scheduled',
                    run: (row) => post(`/api/visitors/${row.id}/check-in`),
                },
                {
                    label: 'Check out', show: (row) => row.status === 'checked_in',
                    run: (row) => post(`/api/visitors/${row.id}/check-out`),
                },
                { label: 'Delete', danger: true, confirm: 'Delete this visitor record?', run: (row) => del(`/api/visitors/${row.id}`) },
            ],
        },
        messages: {
            label: 'Messages',
            endpoint: '/api/messages/',
            columns: [
                { key: 'message_type', label: 'Type' },
                { key: 'from_email', label: 'From', format: (v, row) => v || row.from_phone || row.from_name || '—' },
                { key: 'subject', label: 'Subject', format: (v, row) => v || row.snippet || '—' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
            ],
            actions: [
                { label: 'Delete', danger: true, confirm: 'Delete this message?', run: (row) => del(`/api/messages/${row.id}`) },
            ],
        },
    };

    let activeTab = 'appointments';

    async function apiFetch(path, options) {
        const response = await fetch(path, Object.assign({ credentials: 'same-origin' }, options));
        if (response.status === 401) {
            showLogin();
            throw new Error('Not authenticated');
        }
        return response;
    }

    async function post(path) {
        const response = await apiFetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        if (!response.ok) throw new Error('Request failed');
        return response;
    }

    async function del(path) {
        const response = await apiFetch(path, { method: 'DELETE' });
        if (!response.ok && response.status !== 204) throw new Error('Request failed');
        return response;
    }

    function renderTabs() {
        tabsEl.innerHTML = '';
        Object.keys(RESOURCES).forEach((key) => {
            const btn = document.createElement('button');
            btn.className = 'admin-tab' + (key === activeTab ? ' active' : '');
            btn.textContent = RESOURCES[key].label;
            btn.onclick = () => {
                activeTab = key;
                renderTabs();
                loadPanel();
            };
            tabsEl.appendChild(btn);
        });
    }

    async function loadPanel() {
        const resource = RESOURCES[activeTab];
        panelTitle.textContent = resource.label;
        panelBody.innerHTML = '<p class="admin-empty">Loading…</p>';

        try {
            const response = await apiFetch(resource.endpoint);
            if (!response.ok) throw new Error('Failed to load');
            const rows = await response.json();
            renderTable(resource, rows);
        } catch (err) {
            if (err.message !== 'Not authenticated') {
                panelBody.innerHTML = '<p class="admin-empty">Could not load this data. Try refreshing.</p>';
            }
        }
    }

    function renderTable(resource, rows) {
        if (!rows.length) {
            panelBody.innerHTML = `<p class="admin-empty">No ${resource.label.toLowerCase()} yet.</p>`;
            return;
        }

        const headCells = resource.columns.map((c) => `<th>${escapeHtml(c.label)}</th>`).join('');
        const bodyRows = rows.map((row) => {
            const cells = resource.columns.map((col) => {
                const value = row[col.key];
                const formatted = col.format ? col.format(value, row) : escapeHtml(value);
                return `<td>${col.raw ? formatted : escapeHtml(formatted)}</td>`;
            }).join('');

            const actions = (resource.actions || [])
                .filter((a) => !a.show || a.show(row))
                .map((a, i) => `<button class="admin-action-btn${a.danger ? ' is-danger' : ''}" data-row="${row.id}" data-action="${i}">${escapeHtml(a.label)}</button>`)
                .join('');

            return `<tr>${cells}<td><div class="admin-row-actions">${actions}</div></td></tr>`;
        }).join('');

        panelBody.innerHTML = `
            <div class="admin-table-wrap">
                <table class="admin-table">
                    <thead><tr>${headCells}<th></th></tr></thead>
                    <tbody>${bodyRows}</tbody>
                </table>
            </div>
        `;

        panelBody.querySelectorAll('.admin-action-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const row = rows.find((r) => String(r.id) === btn.dataset.row);
                const action = resource.actions[Number(btn.dataset.action)];
                if (action.confirm && !window.confirm(action.confirm)) return;

                btn.disabled = true;
                try {
                    await action.run(row);
                    loadPanel();
                } catch (err) {
                    btn.disabled = false;
                    window.alert('That action failed. Please try again.');
                }
            });
        });
    }

    function showLogin() {
        dashboard.hidden = true;
        loginScreen.hidden = false;
    }

    function showDashboard() {
        loginScreen.hidden = true;
        dashboard.hidden = false;
        renderTabs();
        loadPanel();
    }

    async function checkSession() {
        try {
            const response = await fetch('/api/admin/me', { credentials: 'same-origin' });
            if (response.ok) {
                showDashboard();
            } else {
                showLogin();
            }
        } catch (err) {
            showLogin();
        }
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.hidden = true;
        loginButton.disabled = true;

        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: loginPassword.value }),
            });

            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                loginError.textContent = data.detail || 'Incorrect password.';
                loginError.hidden = false;
                return;
            }

            loginPassword.value = '';
            showDashboard();
        } catch (err) {
            loginError.textContent = 'Could not reach the server. Please try again.';
            loginError.hidden = false;
        } finally {
            loginButton.disabled = false;
        }
    });

    logoutButton.addEventListener('click', async () => {
        await fetch('/api/admin/logout', { method: 'POST', credentials: 'same-origin' });
        showLogin();
    });

    refreshButton.addEventListener('click', loadPanel);

    checkSession();
})();
