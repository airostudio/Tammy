"use client";

import { ResourceClient } from "@/components/admin/resource-client";
import { messagesConfig } from "@/lib/admin/resources";

export default function MessagesPage() {
  return <ResourceClient config={messagesConfig} />;
}
