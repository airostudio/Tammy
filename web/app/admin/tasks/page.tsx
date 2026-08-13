"use client";

import { ResourceClient } from "@/components/admin/resource-client";
import { tasksConfig } from "@/lib/admin/resources";

export default function TasksPage() {
  return <ResourceClient config={tasksConfig} />;
}
