import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
}

export type FieldType = "text" | "textarea" | "select" | "datetime-local" | "number" | "email" | "list";

export interface FieldConfig {
  key: string;
  label: string;
  type: FieldType;
  required?: boolean;
  options?: string[];
  default?: string | number;
}

export interface RowAction<T> {
  label: string;
  danger?: boolean;
  isEdit?: boolean;
  confirm?: string;
  show?: (row: T) => boolean;
  run?: (row: T) => Promise<void>;
}

export interface ResourceConfig<T extends { id: string }> {
  key: string;
  label: string;
  singular: string;
  endpoint: string; // e.g. "/api/appointments/" - trailing slash matches the FastAPI routes
  needsUserId?: boolean;
  columns: Column<T>[];
  fields: FieldConfig[];
  actions: RowAction<T>[];
}
