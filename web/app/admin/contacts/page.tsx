"use client";

import { ResourceClient } from "@/components/admin/resource-client";
import { contactsConfig } from "@/lib/admin/resources";

export default function ContactsPage() {
  return <ResourceClient config={contactsConfig} />;
}
