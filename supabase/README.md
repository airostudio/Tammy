# Supabase migrations

## Applying `migrations/20260813000000_enable_row_level_security.sql`

This is a one-time setup step for your Supabase project - it isn't run
automatically by the FastAPI backend or the Next.js frontend.

**Easiest path (Supabase Dashboard):** open your project's SQL Editor,
paste the contents of the migration file, and run it.

**With the Supabase CLI:** `supabase db push` (after `supabase link`ing
this repo to your project).

## What it does and why it's needed

The app's tables are created by the FastAPI backend (SQLAlchemy's
`Base.metadata.create_all()`), not through the Supabase dashboard, so they
start with Postgres's default: Row Level Security **off**. Every Supabase
project exposes a REST API (PostgREST) by default, reachable with the
public `anon` key that's embedded in the Next.js frontend
(`NEXT_PUBLIC_SUPABASE_ANON_KEY`) - visible to anyone who opens their
browser's network tab. Without RLS, that key alone would let anyone read
and write every row directly through Supabase's API, completely bypassing
the FastAPI backend's `require_admin` check.

This migration enables RLS on every table and adds a policy allowing any
**authenticated** Supabase user (i.e. staff who can sign in to the app)
full access, while the public `anon` role gets none. `calendar_connections`
(which holds OAuth access/refresh tokens) gets no policies at all, so it's
reachable only through the FastAPI backend's direct database connection,
never through the public API - not even for authenticated users.

The FastAPI backend itself is unaffected either way: it connects via
`DATABASE_URL` as the table owner, and RLS never applies to a table's
owner.

Verified against a real local Postgres instance (with roles/grants
matching Supabase's defaults) before being added here: the owner role sees
everything, `anon` sees and can write nothing, `authenticated` can read
and write the normal tables but sees nothing in `calendar_connections`.
