import { createClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

/**
 * Fetch wrapper for the existing FastAPI backend. Attaches the current
 * Supabase session's access token as a Bearer token - the backend verifies
 * it directly (see app/api/deps.py) rather than requiring a cookie-based
 * session of its own, so this works fine cross-origin against a backend
 * deployed as a separate Vercel project.
 */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  return fetch(`${API_URL}${path}`, { ...options, headers });
}
