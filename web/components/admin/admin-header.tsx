"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import logo from "@/public/endcom-logo.webp";
import { createClient } from "@/lib/supabase/client";

const NAV_ITEMS = [
  { href: "/admin/appointments", label: "Appointments" },
  { href: "/admin/tasks", label: "Tasks" },
  { href: "/admin/contacts", label: "Contacts" },
  { href: "/admin/visitors", label: "Visitors" },
  { href: "/admin/messages", label: "Messages" },
  { href: "/admin/calendar", label: "Calendar" },
];

export function AdminHeader() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <>
      <header className="flex items-center gap-5 border-b border-line bg-surface px-7 py-4">
        <Link href="/admin" className="flex items-center gap-2">
          <Image
            src={logo}
            alt="ENDCOM.NET"
            className="h-[72px] w-auto rounded-lg bg-black/70 p-1.5"
            priority
          />
          <span className="text-sm font-medium text-ink-soft">Admin</span>
        </Link>
        <Link href="/" className="ml-auto text-sm text-ink-soft hover:text-teal-deep">
          View site
        </Link>
        <button
          onClick={handleSignOut}
          className="rounded-md border-[1.5px] border-line-strong px-4.5 py-2 text-sm font-semibold hover:border-ink"
        >
          Sign out
        </button>
      </header>

      <nav className="flex gap-1 overflow-x-auto border-b border-line bg-surface px-7">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`border-b-2 px-4 py-3.5 text-[14.5px] font-medium whitespace-nowrap ${
                active ? "border-teal font-semibold text-teal-deep" : "border-transparent text-ink-soft hover:text-ink"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </>
  );
}
