import { AdminHeader } from "@/components/admin/admin-header";

// Auth enforcement happens in proxy.ts (redirects to /login if there's no
// Supabase session) - this layout is just the shell.
export default function AdminLayout({ children }: LayoutProps<"/admin">) {
  return (
    <div className="flex min-h-screen flex-col bg-surface-sunken">
      <AdminHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-7 py-7">{children}</main>
    </div>
  );
}
