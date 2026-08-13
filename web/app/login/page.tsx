"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const supabase = createClient();
    const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });

    if (signInError) {
      setError(signInError.message);
      setLoading(false);
      return;
    }

    router.push(searchParams.get("next") || "/admin");
    router.refresh();
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm flex flex-col items-center gap-3.5 rounded-2xl border border-line bg-surface p-10 text-center shadow-xl"
      >
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-teal font-serif text-xl italic text-surface">
          T
        </span>
        <h1 className="font-serif text-2xl italic font-semibold">Tammy Admin</h1>
        <p className="mb-2 text-sm text-ink-soft">Sign in to view the front desk data.</p>

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          autoComplete="email"
          required
          className="w-full rounded-md border-[1.5px] border-line-strong bg-paper px-4 py-3 text-sm text-ink focus:border-teal focus:outline-none"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          autoComplete="current-password"
          required
          className="w-full rounded-md border-[1.5px] border-line-strong bg-paper px-4 py-3 text-sm text-ink focus:border-teal focus:outline-none"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-teal px-7 py-3.5 text-[15.5px] font-semibold text-surface transition-colors hover:bg-teal-deep disabled:opacity-50"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>

        {error && <p className="text-[13.5px] text-red-600">{error}</p>}
      </form>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
