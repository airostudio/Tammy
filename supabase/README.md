# Supabase migrations

Two files, meant to be run in order - either is a one-time setup step for
your Supabase project, not something the FastAPI backend or Next.js
frontend runs automatically.

1. **`20260813000000_initial_schema.sql`** - every table, primary key,
   index, and foreign key the backend needs. Generated directly from the
   FastAPI backend's actual SQLAlchemy models (via `Base.metadata.create_all()`
   against a real local Postgres instance, then `pg_dump --schema-only`),
   not hand-written, so it's guaranteed accurate. Safe to run on a brand
   new project even if you've never started the backend - you no longer
   need to boot the FastAPI app first just to get tables created.
2. **`20260813000001_enable_row_level_security.sql`** - locks the tables
   down. See that file's header for the full reasoning; short version:
   without this, the public `anon` key embedded in the Next.js frontend
   would let anyone read and write every row directly through Supabase's
   REST API, bypassing the backend's auth entirely.

## Applying them

**Easiest path (Supabase Dashboard):** open your project's SQL Editor,
paste each file's contents in order, and run it.

**With the Supabase CLI:** `supabase db push` (after `supabase link`ing
this repo to your project) applies every file in `migrations/` in
filename order automatically.

## What the RLS migration does and why it's needed

The app's tables can be created either by the FastAPI backend
(SQLAlchemy's `Base.metadata.create_all()`, which happens automatically
on first boot) or by the schema migration above - either way, they start
with Postgres's default: Row Level Security **off**. Every Supabase
project exposes a REST API (PostgREST) by default, reachable with the
public `anon` key that's embedded in the Next.js frontend
(`NEXT_PUBLIC_SUPABASE_ANON_KEY`) - visible to anyone who opens their
browser's network tab. Without RLS, that key alone would let anyone read
and write every row directly through Supabase's API, completely bypassing
the FastAPI backend's `require_admin` check.

The RLS migration enables RLS on every table and adds a policy allowing
any **authenticated** Supabase user (i.e. staff who can sign in to the
app) full access, while the public `anon` role gets none.
`calendar_connections` (which holds OAuth access/refresh tokens) gets no
policies at all, so it's reachable only through the FastAPI backend's
direct database connection, never through the public API - not even for
authenticated users.

The FastAPI backend itself is unaffected either way: it connects via
`DATABASE_URL` as the table owner, and RLS never applies to a table's
owner.

Both files were verified against a real local Postgres instance (with
roles/grants matching Supabase's defaults) before being added here, run
in order against a genuinely empty database: all 8 tables come up from
the schema file alone, and after the RLS file the owner role sees
everything, `anon` sees and can write nothing, and `authenticated` can
read and write the normal tables but sees nothing in
`calendar_connections`.
