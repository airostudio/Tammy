// ENDCOM.NET admin dashboard - data-driven table + create/edit forms over the
// existing appointments/tasks/contacts/visitors/messages API, gated by the
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
    const newButton = document.getElementById('newButton');
    const logoutButton = document.getElementById('logoutButton');

    const modalOverlay = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const modalFields = document.getElementById('modalFields');
    const modalForm = document.getElementById('modalForm');
    const modalError = document.getElementById('modalError');
    const modalClose = document.getElementById('modalClose');
    const modalCancel = document.getElementById('modalCancel');
    const modalSave = document.getElementById('modalSave');

    // Every record the assistant/admin creates without a real per-user login
    // attaches to this fixed single-tenant user (see app/utils/default_user.py).
    const DEFAULT_USER_ID = 'system';

    function formatDateTime(value) {
        if (!value) return '—';
        const date = new Date(value);
        if (isNaN(date.getTime())) return value;
        return date.toLocaleString(undefined, {
            month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
        });
    }

    function toDatetimeLocal(value) {
        if (!value) return '';
        const date = new Date(value);
        if (isNaN(date.getTime())) return '';
        const pad = (n) => String(n).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
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

    // Each resource: where to fetch/save it, which columns the table shows,
    // which row-level actions are available, and which fields the
    // create/edit form should render. needsUserId is true for the resources
    // that are scoped to a user_id foreign key (there's no per-admin login,
    // so new records attach to the shared DEFAULT_USER_ID).
    const RESOURCES = {
        appointments: {
            label: 'Appointments',
            singular: 'appointment',
            endpoint: '/api/appointments/',
            needsUserId: true,
            columns: [
                { key: 'title', label: 'Title' },
                { key: 'start_time', label: 'Start', format: formatDateTime },
                { key: 'duration_minutes', label: 'Duration', format: (v) => (v ? `${v} min` : '—') },
                { key: 'location', label: 'Location' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
            ],
            actions: [
                { label: 'Edit', isEdit: true },
                { label: 'Delete', danger: true, confirm: 'Delete this appointment?', run: (row) => del(`/api/appointments/${row.id}`) },
            ],
            fields: [
                { key: 'title', label: 'Title', type: 'text', required: true },
                { key: 'description', label: 'Description', type: 'textarea' },
                { key: 'location', label: 'Location', type: 'text' },
                { key: 'start_time', label: 'Start time', type: 'datetime-local', required: true },
                { key: 'duration_minutes', label: 'Duration (minutes)', type: 'number', default: 60 },
                { key: 'attendees', label: 'Attendees (comma-separated)', type: 'list' },
                { key: 'meeting_url', label: 'Meeting URL', type: 'text' },
                { key: 'conference_room', label: 'Conference room', type: 'text' },
            ],
        },
        tasks: {
            label: 'Tasks',
            singular: 'task',
            endpoint: '/api/tasks/',
            needsUserId: true,
            columns: [
                { key: 'title', label: 'Title' },
                { key: 'priority', label: 'Priority', format: statusPill, raw: true },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
                { key: 'due_date', label: 'Due', format: formatDateTime },
            ],
            actions: [
                { label: 'Edit', isEdit: true },
                {
                    label: 'Complete', show: (row) => row.status !== 'completed',
                    run: (row) => post(`/api/tasks/${row.id}/complete`),
                },
                { label: 'Delete', danger: true, confirm: 'Delete this task?', run: (row) => del(`/api/tasks/${row.id}`) },
            ],
            fields: [
                { key: 'title', label: 'Title', type: 'text', required: true },
                { key: 'description', label: 'Description', type: 'textarea' },
                { key: 'priority', label: 'Priority', type: 'select', options: ['low', 'medium', 'high', 'urgent'], default: 'medium' },
                { key: 'due_date', label: 'Due date', type: 'datetime-local' },
                { key: 'project', label: 'Project', type: 'text' },
                { key: 'category', label: 'Category', type: 'text' },
            ],
        },
        contacts: {
            label: 'Contacts',
            singular: 'contact',
            endpoint: '/api/contacts/',
            needsUserId: true,
            columns: [
                { key: 'full_name', label: 'Name' },
                { key: 'company', label: 'Company' },
                { key: 'email', label: 'Email' },
                { key: 'phone_number', label: 'Phone' },
            ],
            actions: [
                { label: 'Edit', isEdit: true },
                { label: 'Delete', danger: true, confirm: 'Delete this contact?', run: (row) => del(`/api/contacts/${row.id}`) },
            ],
            fields: [
                { key: 'first_name', label: 'First name', type: 'text', required: true },
                { key: 'last_name', label: 'Last name', type: 'text', required: true },
                { key: 'email', label: 'Email', type: 'email' },
                { key: 'phone_number', label: 'Phone', type: 'text' },
                { key: 'mobile_number', label: 'Mobile', type: 'text' },
                { key: 'company', label: 'Company', type: 'text' },
                { key: 'job_title', label: 'Job title', type: 'text' },
                { key: 'relationship_type', label: 'Relationship', type: 'text' },
                { key: 'priority', label: 'Priority', type: 'select', options: ['low', 'normal', 'high'], default: 'normal' },
                { key: 'notes', label: 'Notes', type: 'textarea' },
            ],
        },
        visitors: {
            label: 'Visitors',
            singular: 'visitor',
            endpoint: '/api/visitors/',
            columns: [
                { key: 'full_name', label: 'Name' },
                { key: 'host_name', label: 'Host' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
                { key: 'check_in_time', label: 'Checked in', format: formatDateTime },
            ],
            actions: [
                { label: 'Edit', isEdit: true },
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
            fields: [
                { key: 'full_name', label: 'Visitor name', type: 'text', required: true },
                { key: 'host_name', label: 'Host', type: 'text', required: true },
                { key: 'company', label: 'Company', type: 'text' },
                { key: 'email', label: 'Email', type: 'email' },
                { key: 'phone_number', label: 'Phone', type: 'text' },
                { key: 'visit_type', label: 'Visit type', type: 'select', options: ['in_person', 'call', 'video_call'], default: 'in_person' },
                { key: 'purpose', label: 'Purpose', type: 'textarea' },
                { key: 'scheduled_time', label: 'Scheduled time', type: 'datetime-local' },
                { key: 'location', label: 'Location', type: 'text' },
            ],
        },
        messages: {
            label: 'Messages',
            singular: 'message',
            endpoint: '/api/messages/',
            columns: [
                { key: 'message_type', label: 'Type' },
                { key: 'from_email', label: 'From', format: (v, row) => v || row.from_phone || row.from_name || '—' },
                { key: 'subject', label: 'Subject', format: (v, row) => v || row.snippet || '—' },
                { key: 'status', label: 'Status', format: statusPill, raw: true },
            ],
            actions: [
                { label: 'Edit', isEdit: true },
                { label: 'Delete', danger: true, confirm: 'Delete this message?', run: (row) => del(`/api/messages/${row.id}`) },
            ],
            fields: [
                { key: 'message_type', label: 'Type', type: 'select', options: ['email', 'sms', 'call', 'chat', 'note'], required: true, default: 'email' },
                { key: 'direction', label: 'Direction', type: 'select', options: ['inbound', 'outbound'], required: true, default: 'inbound' },
                { key: 'from_name', label: 'From name', type: 'text' },
                { key: 'from_email', label: 'From email', type: 'email' },
                { key: 'from_phone', label: 'From phone', type: 'text' },
                { key: 'to_email', label: 'To email', type: 'email' },
                { key: 'subject', label: 'Subject', type: 'text' },
                { key: 'body', label: 'Body', type: 'textarea' },
                { key: 'priority', label: 'Priority', type: 'select', options: ['low', 'normal', 'high', 'urgent'], default: 'normal' },
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

    async function responseErrorMessage(response) {
        try {
            const data = await response.json();
            if (Array.isArray(data.detail)) {
                return data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
            }
            if (data.detail) return data.detail;
        } catch (err) {
            // fall through to generic message
        }
        return 'Could not save. Please check the fields and try again.';
    }

    // "calendar" isn't a data table like the others - it's a settings panel
    // (feed URL + connected-calendar status), so it's kept out of RESOURCES
    // and handled as a special tab.
    const SPECIAL_TABS = { calendar: 'Calendar' };

    function renderTabs() {
        tabsEl.innerHTML = '';
        const allTabs = Object.assign({}, RESOURCES, SPECIAL_TABS);
        Object.keys(allTabs).forEach((key) => {
            const btn = document.createElement('button');
            btn.className = 'admin-tab' + (key === activeTab ? ' active' : '');
            btn.textContent = RESOURCES[key] ? RESOURCES[key].label : SPECIAL_TABS[key];
            btn.onclick = () => {
                activeTab = key;
                renderTabs();
                loadActiveTab();
            };
            tabsEl.appendChild(btn);
        });
        newButton.hidden = activeTab === 'calendar';
    }

    function loadActiveTab() {
        if (activeTab === 'calendar') {
            loadCalendarPanel();
        } else {
            loadPanel();
        }
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

                if (action.isEdit) {
                    openModal('edit', activeTab, row);
                    return;
                }

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

    // --- Calendar settings panel -----------------------------------------

    const CALENDAR_PROVIDERS = [
        { key: 'google', label: 'Google Calendar' },
        { key: 'microsoft', label: 'Microsoft 365 / Outlook' },
    ];

    async function loadCalendarPanel() {
        panelTitle.textContent = 'Calendar';
        panelBody.innerHTML = '<p class="admin-empty">Loading…</p>';

        try {
            const [feedResponse, connectionsResponse] = await Promise.all([
                apiFetch('/api/calendar/feed-url'),
                apiFetch('/api/calendar/connections'),
            ]);
            if (!feedResponse.ok || !connectionsResponse.ok) throw new Error('Failed to load');

            const feedData = await feedResponse.json();
            const connections = await connectionsResponse.json();
            renderCalendarPanel(feedData, connections);
        } catch (err) {
            if (err.message !== 'Not authenticated') {
                panelBody.innerHTML = '<p class="admin-empty">Could not load calendar settings. Try refreshing.</p>';
            }
        }
    }

    function renderCalendarPanel(feedData, connections) {
        const feedUrl = window.location.origin + feedData.path;
        const byProvider = {};
        connections.forEach((c) => { byProvider[c.provider] = c; });

        panelBody.innerHTML = '';

        const feedSection = document.createElement('div');
        feedSection.className = 'admin-calendar-section';
        feedSection.innerHTML = `
            <h3>Subscribe by URL (iCal)</h3>
            <p class="admin-calendar-hint">Any calendar app can subscribe to this URL to see your appointments - no account connection needed.</p>
        `;
        const feedRow = document.createElement('div');
        feedRow.className = 'admin-feed-row';
        const feedInput = document.createElement('input');
        feedInput.type = 'text';
        feedInput.readOnly = true;
        feedInput.value = feedUrl;
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-secondary';
        copyBtn.type = 'button';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(feedUrl).then(() => {
                const original = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => { copyBtn.textContent = original; }, 1500);
            });
        });
        feedRow.appendChild(feedInput);
        feedRow.appendChild(copyBtn);
        feedSection.appendChild(feedRow);
        panelBody.appendChild(feedSection);

        const connectSection = document.createElement('div');
        connectSection.className = 'admin-calendar-section';
        const heading = document.createElement('h3');
        heading.textContent = 'Connected calendars';
        const hint = document.createElement('p');
        hint.className = 'admin-calendar-hint';
        hint.textContent = 'Connect Google Calendar or Microsoft 365 to have new appointments pushed there automatically.';
        connectSection.appendChild(heading);
        connectSection.appendChild(hint);

        CALENDAR_PROVIDERS.forEach(({ key, label }) => {
            const connection = byProvider[key];
            const card = document.createElement('div');
            card.className = 'admin-calendar-card';

            const info = document.createElement('div');
            const title = document.createElement('div');
            title.className = 'admin-calendar-card-title';
            title.textContent = label;
            info.appendChild(title);

            const status = document.createElement('span');
            status.className = 'admin-pill' + (connection ? '' : ' is-muted');
            status.textContent = connection
                ? `Connected${connection.account_email ? ' as ' + connection.account_email : ''}`
                : 'Not connected';
            info.appendChild(status);
            card.appendChild(info);

            if (connection) {
                const disconnectBtn = document.createElement('button');
                disconnectBtn.className = 'admin-action-btn is-danger';
                disconnectBtn.type = 'button';
                disconnectBtn.textContent = 'Disconnect';
                disconnectBtn.addEventListener('click', async () => {
                    if (!window.confirm(`Disconnect ${label}?`)) return;
                    disconnectBtn.disabled = true;
                    try {
                        await apiFetch(`/api/calendar/connections/${key}`, { method: 'DELETE' });
                        loadCalendarPanel();
                    } catch (err) {
                        disconnectBtn.disabled = false;
                        window.alert('Could not disconnect. Please try again.');
                    }
                });
                card.appendChild(disconnectBtn);
            } else {
                const connectLink = document.createElement('a');
                connectLink.className = 'btn btn-secondary';
                connectLink.href = `/api/calendar/oauth/${key}/connect`;
                connectLink.textContent = 'Connect';
                card.appendChild(connectLink);
            }

            connectSection.appendChild(card);
        });

        panelBody.appendChild(connectSection);
    }

    // --- Create/edit modal ---------------------------------------------

    let modalMode = null; // 'create' | 'edit'
    let modalRow = null;
    let modalResourceKey = null;

    function buildFieldElement(field, value) {
        const wrapper = document.createElement('div');
        wrapper.className = 'admin-field';

        const label = document.createElement('label');
        label.setAttribute('for', `field_${field.key}`);
        label.textContent = field.label;
        wrapper.appendChild(label);

        let input;
        if (field.type === 'textarea') {
            input = document.createElement('textarea');
            input.value = value == null ? '' : value;
        } else if (field.type === 'select') {
            input = document.createElement('select');
            field.options.forEach((opt) => {
                const optionEl = document.createElement('option');
                optionEl.value = opt;
                optionEl.textContent = opt.replace(/_/g, ' ');
                if (opt === value) optionEl.selected = true;
                input.appendChild(optionEl);
            });
        } else {
            input = document.createElement('input');
            if (field.type === 'datetime-local') {
                input.type = 'datetime-local';
                input.value = toDatetimeLocal(value);
            } else if (field.type === 'number') {
                input.type = 'number';
                input.value = value == null ? '' : value;
            } else if (field.type === 'email') {
                input.type = 'email';
                input.value = value == null ? '' : value;
            } else if (field.type === 'list') {
                input.type = 'text';
                input.value = Array.isArray(value) ? value.join(', ') : (value == null ? '' : value);
            } else {
                input.type = 'text';
                input.value = value == null ? '' : value;
            }
        }

        input.id = `field_${field.key}`;
        input.name = field.key;
        if (field.required) input.required = true;

        wrapper.appendChild(input);
        return wrapper;
    }

    function openModal(mode, resourceKey, row) {
        modalMode = mode;
        modalRow = row || null;
        modalResourceKey = resourceKey;

        const resource = RESOURCES[resourceKey];
        const noun = resource.singular || resource.label;
        modalTitle.textContent = mode === 'create' ? `New ${noun}` : `Edit ${noun}`;
        modalError.hidden = true;
        modalFields.innerHTML = '';

        resource.fields.forEach((field) => {
            const value = row ? row[field.key] : field.default;
            modalFields.appendChild(buildFieldElement(field, value));
        });

        modalOverlay.hidden = false;
    }

    function closeModal() {
        modalOverlay.hidden = true;
        modalMode = null;
        modalRow = null;
        modalResourceKey = null;
    }

    modalClose.addEventListener('click', closeModal);
    modalCancel.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    newButton.addEventListener('click', () => openModal('create', activeTab, null));

    modalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        modalError.hidden = true;

        const resource = RESOURCES[modalResourceKey];
        const formData = new FormData(modalForm);
        const body = {};

        resource.fields.forEach((field) => {
            const raw = formData.get(field.key);
            if (field.type === 'number') {
                body[field.key] = raw === '' || raw === null ? null : Number(raw);
            } else if (field.type === 'list') {
                body[field.key] = raw ? String(raw).split(',').map((s) => s.trim()).filter(Boolean) : [];
            } else {
                body[field.key] = raw === '' ? null : raw;
            }
        });

        if (modalMode === 'create' && resource.needsUserId) {
            body.user_id = DEFAULT_USER_ID;
        }

        modalSave.disabled = true;

        try {
            const path = modalMode === 'create'
                ? resource.endpoint
                : `${resource.endpoint}${modalRow.id}`;
            const response = await apiFetch(path, {
                method: modalMode === 'create' ? 'POST' : 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                modalError.textContent = await responseErrorMessage(response);
                modalError.hidden = false;
                return;
            }

            closeModal();
            loadPanel();
        } catch (err) {
            if (err.message !== 'Not authenticated') {
                modalError.textContent = 'Could not reach the server. Please try again.';
                modalError.hidden = false;
            }
        } finally {
            modalSave.disabled = false;
        }
    });

    // --- Login / session -------------------------------------------------

    function showLogin() {
        dashboard.hidden = true;
        loginScreen.hidden = false;
        closeModal();
    }

    function showDashboard() {
        loginScreen.hidden = true;
        dashboard.hidden = false;
        // The OAuth callback redirects back to /admin#calendar so the user
        // lands back on the tab they started from.
        if (window.location.hash === '#calendar') {
            activeTab = 'calendar';
        }
        renderTabs();
        loadActiveTab();
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

    refreshButton.addEventListener('click', loadActiveTab);

    checkSession();
})();
