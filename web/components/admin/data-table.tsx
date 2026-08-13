"use client";

import type { ResourceConfig } from "@/lib/admin/types";

interface DataTableProps<T extends { id: string }> {
  config: ResourceConfig<T>;
  rows: T[];
  onEdit: (row: T) => void;
  onActionComplete: () => void;
}

export function DataTable<T extends { id: string }>({ config, rows, onEdit, onActionComplete }: DataTableProps<T>) {
  if (rows.length === 0) {
    return <p className="py-10 text-center text-ink-faint">No {config.label.toLowerCase()} yet.</p>;
  }

  async function runAction(row: T, action: (typeof config.actions)[number]) {
    if (action.isEdit) {
      onEdit(row);
      return;
    }
    if (action.confirm && !window.confirm(action.confirm)) return;
    try {
      await action.run?.(row);
      onActionComplete();
    } catch {
      window.alert("That action failed. Please try again.");
    }
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-surface">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            {config.columns.map((col) => (
              <th
                key={col.key}
                className="border-b border-line px-4.5 py-3 text-left text-[12.5px] font-normal tracking-wide text-ink-faint uppercase whitespace-nowrap"
              >
                {col.label}
              </th>
            ))}
            <th className="border-b border-line px-4.5 py-3" />
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="group hover:bg-surface-sunken">
              {config.columns.map((col) => (
                <td key={col.key} className="border-b border-line px-4.5 py-3.5 group-last:border-b-0">
                  {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? "")}
                </td>
              ))}
              <td className="border-b border-line px-4.5 py-3.5 group-last:border-b-0">
                <div className="flex justify-end gap-2">
                  {config.actions
                    .filter((a) => !a.show || a.show(row))
                    .map((action) => (
                      <button
                        key={action.label}
                        onClick={() => runAction(row, action)}
                        className={`rounded-md border px-3.5 py-1.5 text-[12.5px] transition-colors ${
                          action.danger
                            ? "border-line-strong hover:border-red-600 hover:text-red-600"
                            : "border-line-strong hover:border-teal hover:text-teal-deep"
                        }`}
                      >
                        {action.label}
                      </button>
                    ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
