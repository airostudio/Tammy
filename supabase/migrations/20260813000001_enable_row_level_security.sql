-- Enable Row Level Security on every table and restrict access to
-- authenticated Supabase users only.
--
-- Run this AFTER 20260813000000_initial_schema.sql - it assumes every
-- table already exists.
--
-- Why this matters: these tables were created by the FastAPI backend's
-- SQLAlchemy models (Base.metadata.create_all()), not through the Supabase
-- dashboard, so Postgres's default applies - RLS is OFF. Supabase's
-- PostgREST API is enabled by default for every project and is reachable
-- with just the anon key, which is a PUBLIC, client-embeddable key (it's
-- sitting in the Next.js frontend's NEXT_PUBLIC_SUPABASE_ANON_KEY, visible
-- to anyone who opens the browser's network tab). Without RLS, that anon
-- key alone would let anyone read and write every row directly via
-- Supabase's REST API, completely bypassing the FastAPI backend's
-- require_admin auth check.
--
-- The FastAPI backend itself is UNAFFECTED by any of this: it connects via
-- DATABASE_URL as the table owner (Postgres's "postgres" role on a
-- Supabase project), and RLS never applies to a table's owner. These
-- policies only gate access through Supabase's PostgREST API / supabase-js
-- client (the anon/authenticated roles) - e.g. if the Next.js frontend
-- ever reads data directly via Realtime subscriptions instead of going
-- through the FastAPI backend for everything.
--
-- This app is single-tenant (one admin/staff team manages all of
-- ENDCOM.NET's data - appointments/tasks/contacts/etc. all belong to a
-- single fixed "system" user, not a real per-customer owner), so the
-- policy is simple:
-- any authenticated Supabase user (i.e. anyone who can sign in - meaning
-- staff you've added to the Supabase project) can do anything; the public
-- anon role can do nothing. If this ever needs to become multi-tenant,
-- replace `true` below with a real ownership check.
--
-- calendar_connections holds OAuth access/refresh tokens and gets NO
-- policies at all (not even for authenticated) - with RLS enabled and zero
-- policies, every role is denied by default, so those tokens are only ever
-- reachable through the FastAPI backend's direct, RLS-bypassing connection.
--
-- To apply: paste this file into the Supabase Dashboard's SQL Editor and
-- run it, or `supabase db push` if you're using the Supabase CLI.

alter table if exists users enable row level security;
alter table if exists appointments enable row level security;
alter table if exists contacts enable row level security;
alter table if exists tasks enable row level security;
alter table if exists visitors enable row level security;
alter table if exists messages enable row level security;
alter table if exists documents enable row level security;
alter table if exists calendar_connections enable row level security;

drop policy if exists "Authenticated users can manage users" on users;
create policy "Authenticated users can manage users" on users
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage appointments" on appointments;
create policy "Authenticated users can manage appointments" on appointments
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage contacts" on contacts;
create policy "Authenticated users can manage contacts" on contacts
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage tasks" on tasks;
create policy "Authenticated users can manage tasks" on tasks
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage visitors" on visitors;
create policy "Authenticated users can manage visitors" on visitors
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage messages" on messages;
create policy "Authenticated users can manage messages" on messages
  for all to authenticated using (true) with check (true);

drop policy if exists "Authenticated users can manage documents" on documents;
create policy "Authenticated users can manage documents" on documents
  for all to authenticated using (true) with check (true);

-- calendar_connections intentionally has no policies - see comment above.
