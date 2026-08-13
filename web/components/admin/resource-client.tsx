"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { DataTable } from "@/components/admin/data-table";
import { ResourceFormModal } from "@/components/admin/resource-form-modal";
import type { ResourceConfig } from "@/lib/admin/types";

export function ResourceClient<T extends { id: string }>({ config }: { config: ResourceConfig<T> }) {
  const [rows, setRows] = useState<T[] | null>(null);
  const [error, setError] = useState(false);
  const [modal, setModal] = useState<{ mode: "create" | "edit"; row: T | null } | null>(null);

  const load = useCallback(async () => {
    try {
      const response = await apiFetch(config.endpoint);
      if (!response.ok) throw new Error("Failed to load");
      setRows(await response.json());
      setError(false);
    } catch {
      setError(true);
    }
  }, [config.endpoint]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <div className="mb-4.5 flex items-center justify-between">
        <h2 className="text-xl font-semibold">{config.label}</h2>
        <div className="flex gap-2.5">
          <button
            onClick={load}
            className="rounded-md border-[1.5px] border-line-strong px-4.5 py-2 text-[13.5px] font-semibold hover:border-ink"
          >
            Refresh
          </button>
          <button
            onClick={() => setModal({ mode: "create", row: null })}
            className="rounded-md bg-teal px-4.5 py-2 text-[13.5px] font-semibold text-surface hover:bg-teal-deep"
          >
            + New
          </button>
        </div>
      </div>

      {rows === null ? (
        <p className="py-10 text-center text-ink-faint">
          {error ? "Could not load this data. Try refreshing." : "Loading…"}
        </p>
      ) : (
        <DataTable config={config} rows={rows} onEdit={(row) => setModal({ mode: "edit", row })} onActionComplete={load} />
      )}

      {modal && (
        <ResourceFormModal
          config={config}
          mode={modal.mode}
          row={modal.row}
          onClose={() => setModal(null)}
          onSaved={() => {
            setModal(null);
            load();
          }}
        />
      )}
    </div>
  );
}
