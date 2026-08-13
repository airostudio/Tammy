import { apiFetch } from "@/lib/api";
import { formatDateTime, Pill } from "@/lib/admin/format";
import type { Appointment, Contact, Message, Task, Visitor } from "@/lib/types";
import type { ResourceConfig } from "@/lib/admin/types";

// Every record the assistant/admin creates without a real per-user login
// attaches to this fixed single-tenant user (see app/utils/default_user.py
// on the backend).
export const DEFAULT_USER_ID = "system";

async function post(path: string) {
  const response = await apiFetch(path, { method: "POST" });
  if (!response.ok) throw new Error("Request failed");
}

async function del(path: string) {
  const response = await apiFetch(path, { method: "DELETE" });
  if (!response.ok && response.status !== 204) throw new Error("Request failed");
}

export const appointmentsConfig: ResourceConfig<Appointment> = {
  key: "appointments",
  label: "Appointments",
  singular: "appointment",
  endpoint: "/api/appointments/",
  needsUserId: true,
  columns: [
    { key: "title", label: "Title" },
    { key: "start_time", label: "Start", render: (r) => formatDateTime(r.start_time) },
    { key: "duration_minutes", label: "Duration", render: (r) => `${r.duration_minutes} min` },
    { key: "location", label: "Location" },
    { key: "status", label: "Status", render: (r) => <Pill value={r.status} /> },
  ],
  fields: [
    { key: "title", label: "Title", type: "text", required: true },
    { key: "description", label: "Description", type: "textarea" },
    { key: "location", label: "Location", type: "text" },
    { key: "start_time", label: "Start time", type: "datetime-local", required: true },
    { key: "duration_minutes", label: "Duration (minutes)", type: "number", default: 60 },
    { key: "attendees", label: "Attendees (comma-separated)", type: "list" },
    { key: "meeting_url", label: "Meeting URL", type: "text" },
    { key: "conference_room", label: "Conference room", type: "text" },
  ],
  actions: [
    { label: "Edit", isEdit: true },
    {
      label: "Delete",
      danger: true,
      confirm: "Delete this appointment?",
      run: (row) => del(`/api/appointments/${row.id}`),
    },
  ],
};

export const tasksConfig: ResourceConfig<Task> = {
  key: "tasks",
  label: "Tasks",
  singular: "task",
  endpoint: "/api/tasks/",
  needsUserId: true,
  columns: [
    { key: "title", label: "Title" },
    { key: "priority", label: "Priority", render: (r) => <Pill value={r.priority} /> },
    { key: "status", label: "Status", render: (r) => <Pill value={r.status} /> },
    { key: "due_date", label: "Due", render: (r) => formatDateTime(r.due_date) },
  ],
  fields: [
    { key: "title", label: "Title", type: "text", required: true },
    { key: "description", label: "Description", type: "textarea" },
    { key: "priority", label: "Priority", type: "select", options: ["low", "medium", "high", "urgent"], default: "medium" },
    { key: "due_date", label: "Due date", type: "datetime-local" },
    { key: "project", label: "Project", type: "text" },
    { key: "category", label: "Category", type: "text" },
  ],
  actions: [
    { label: "Edit", isEdit: true },
    {
      label: "Complete",
      show: (row) => row.status !== "completed",
      run: (row) => post(`/api/tasks/${row.id}/complete`),
    },
    { label: "Delete", danger: true, confirm: "Delete this task?", run: (row) => del(`/api/tasks/${row.id}`) },
  ],
};

export const contactsConfig: ResourceConfig<Contact> = {
  key: "contacts",
  label: "Contacts",
  singular: "contact",
  endpoint: "/api/contacts/",
  needsUserId: true,
  columns: [
    { key: "full_name", label: "Name" },
    { key: "company", label: "Company" },
    { key: "email", label: "Email" },
    { key: "phone_number", label: "Phone" },
  ],
  fields: [
    { key: "first_name", label: "First name", type: "text", required: true },
    { key: "last_name", label: "Last name", type: "text", required: true },
    { key: "email", label: "Email", type: "email" },
    { key: "phone_number", label: "Phone", type: "text" },
    { key: "mobile_number", label: "Mobile", type: "text" },
    { key: "company", label: "Company", type: "text" },
    { key: "job_title", label: "Job title", type: "text" },
    { key: "relationship_type", label: "Relationship", type: "text" },
    { key: "priority", label: "Priority", type: "select", options: ["low", "normal", "high"], default: "normal" },
    { key: "notes", label: "Notes", type: "textarea" },
  ],
  actions: [
    { label: "Edit", isEdit: true },
    { label: "Delete", danger: true, confirm: "Delete this contact?", run: (row) => del(`/api/contacts/${row.id}`) },
  ],
};

export const visitorsConfig: ResourceConfig<Visitor> = {
  key: "visitors",
  label: "Visitors",
  singular: "visitor",
  endpoint: "/api/visitors/",
  columns: [
    { key: "full_name", label: "Name" },
    { key: "host_name", label: "Host" },
    { key: "status", label: "Status", render: (r) => <Pill value={r.status} /> },
    { key: "check_in_time", label: "Checked in", render: (r) => formatDateTime(r.check_in_time) },
  ],
  fields: [
    { key: "full_name", label: "Visitor name", type: "text", required: true },
    { key: "host_name", label: "Host", type: "text", required: true },
    { key: "company", label: "Company", type: "text" },
    { key: "email", label: "Email", type: "email" },
    { key: "phone_number", label: "Phone", type: "text" },
    { key: "visit_type", label: "Visit type", type: "select", options: ["in_person", "call", "video_call"], default: "in_person" },
    { key: "purpose", label: "Purpose", type: "textarea" },
    { key: "scheduled_time", label: "Scheduled time", type: "datetime-local" },
    { key: "location", label: "Location", type: "text" },
  ],
  actions: [
    { label: "Edit", isEdit: true },
    {
      label: "Check in",
      show: (row) => row.status === "scheduled",
      run: (row) => post(`/api/visitors/${row.id}/check-in`),
    },
    {
      label: "Check out",
      show: (row) => row.status === "checked_in",
      run: (row) => post(`/api/visitors/${row.id}/check-out`),
    },
    {
      label: "Delete",
      danger: true,
      confirm: "Delete this visitor record?",
      run: (row) => del(`/api/visitors/${row.id}`),
    },
  ],
};

export const messagesConfig: ResourceConfig<Message> = {
  key: "messages",
  label: "Messages",
  singular: "message",
  endpoint: "/api/messages/",
  columns: [
    { key: "message_type", label: "Type" },
    { key: "from_email", label: "From", render: (r) => r.from_email || r.from_phone || r.from_name || "—" },
    { key: "subject", label: "Subject", render: (r) => r.subject || r.snippet || "—" },
    { key: "status", label: "Status", render: (r) => <Pill value={r.status} /> },
  ],
  fields: [
    { key: "message_type", label: "Type", type: "select", options: ["email", "sms", "call", "chat", "note"], required: true, default: "email" },
    { key: "direction", label: "Direction", type: "select", options: ["inbound", "outbound"], required: true, default: "inbound" },
    { key: "from_name", label: "From name", type: "text" },
    { key: "from_email", label: "From email", type: "email" },
    { key: "from_phone", label: "From phone", type: "text" },
    { key: "to_email", label: "To email", type: "email" },
    { key: "subject", label: "Subject", type: "text" },
    { key: "body", label: "Body", type: "textarea" },
    { key: "priority", label: "Priority", type: "select", options: ["low", "normal", "high", "urgent"], default: "normal" },
  ],
  actions: [
    { label: "Edit", isEdit: true },
    { label: "Delete", danger: true, confirm: "Delete this message?", run: (row) => del(`/api/messages/${row.id}`) },
  ],
};
