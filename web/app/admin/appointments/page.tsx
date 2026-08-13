"use client";

import { ResourceClient } from "@/components/admin/resource-client";
import { appointmentsConfig } from "@/lib/admin/resources";

export default function AppointmentsPage() {
  return <ResourceClient config={appointmentsConfig} />;
}
