"use client";

import { ResourceClient } from "@/components/admin/resource-client";
import { visitorsConfig } from "@/lib/admin/resources";

export default function VisitorsPage() {
  return <ResourceClient config={visitorsConfig} />;
}
