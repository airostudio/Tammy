"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { DEFAULT_USER_ID } from "@/lib/admin/resources";
import type { ResourceConfig } from "@/lib/admin/types";

function toDatetimeLocal(value: unknown): string {
  if (!value || typeof value !== "string") return "";
  const date = new Date(value);
  if (isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

interface ResourceFormModalProps<T extends { id: string }> {
  config: ResourceConfig<T>;
  mode: "create" | "edit";
  row: T | null;
  onClose: () => void;
  onSaved: () => void;
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join("; ");
    }
    if (data.detail) return data.detail;
  } catch {
    // fall through
  }
  return "Could not save. Please check the fields and try again.";
}

export function ResourceFormModal<T extends { id: string }>({
  config,
  mode,
  row,
  onClose,
  onSaved,
}: ResourceFormModalProps<T>) {
  const initialValues = Object.fromEntries(
    config.fields.map((field) => {
      const raw = row ? (row as Record<string, unknown>)[field.key] : field.default;
      if (field.type === "list") return [field.key, Array.isArray(raw) ? raw.join(", ") : (raw ?? "")];
      if (field.type === "datetime-local") return [field.key, toDatetimeLocal(raw)];
      return [field.key, raw ?? ""];
    }),
  );

  const [values, setValues] = useState<Record<string, string>>(initialValues as Record<string, string>);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function setField(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);

    const body: Record<string, unknown> = {};
    for (const field of config.fields) {
      const raw = values[field.key];
      if (field.type === "number") {
        body[field.key] = raw === "" ? null : Number(raw);
      } else if (field.type === "list") {
        body[field.key] = raw
          ? raw.split(",").map((s) => s.trim()).filter(Boolean)
          : [];
      } else {
        body[field.key] = raw === "" ? null : raw;
      }
    }
    if (mode === "create" && config.needsUserId) {
      body.user_id = DEFAULT_USER_ID;
    }

    try {
      const path = mode === "create" ? config.endpoint : `${config.endpoint}${row!.id}`;
      const response = await apiFetch(path, {
        method: mode === "create" ? "POST" : "PUT",
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        setError(await parseErrorMessage(response));
        return;
      }

      onSaved();
    } catch {
      setError("Could not reach the server. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-100 flex items-start justify-center overflow-y-auto bg-ink/45 p-6 py-15"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-xl rounded-2xl bg-surface shadow-xl">
        <div className="flex items-center justify-between border-b border-line px-6 py-5">
          <h3 className="text-lg font-semibold">
            {mode === "create" ? `New ${config.singular}` : `Edit ${config.singular}`}
          </h3>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="p-1 text-2xl leading-none text-ink-faint hover:text-ink"
          >
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="flex max-h-[60vh] flex-col gap-4 overflow-y-auto px-6 pt-5 pb-1">
            {config.fields.map((field) => (
              <div key={field.key}>
                <label htmlFor={`field_${field.key}`} className="mb-1.5 block text-[13px] font-semibold text-ink-soft">
                  {field.label}
                </label>
                {field.type === "textarea" ? (
                  <textarea
                    id={`field_${field.key}`}
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(e) => setField(field.key, e.target.value)}
                    className="min-h-[72px] w-full rounded-md border-[1.5px] border-line-strong bg-paper px-3.5 py-2.5 text-[14.5px] focus:border-teal focus:outline-none"
                  />
                ) : field.type === "select" ? (
                  <select
                    id={`field_${field.key}`}
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(e) => setField(field.key, e.target.value)}
                    className="w-full rounded-md border-[1.5px] border-line-strong bg-paper px-3.5 py-2.5 text-[14.5px] focus:border-teal focus:outline-none"
                  >
                    {field.options?.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id={`field_${field.key}`}
                    type={field.type === "list" ? "text" : field.type}
                    required={field.required}
                    value={values[field.key] ?? ""}
                    onChange={(e) => setField(field.key, e.target.value)}
                    className="w-full rounded-md border-[1.5px] border-line-strong bg-paper px-3.5 py-2.5 text-[14.5px] focus:border-teal focus:outline-none"
                  />
                )}
              </div>
            ))}
          </div>

          {error && <p className="px-6 pt-3 text-[13.5px] text-red-600">{error}</p>}

          <div className="flex justify-end gap-2.5 px-6 py-5">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border-[1.5px] border-line-strong px-5 py-2.5 text-sm font-semibold hover:border-ink"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-md bg-teal px-5 py-2.5 text-sm font-semibold text-surface hover:bg-teal-deep disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
