-- Full schema for a brand-new Supabase project - every table, primary key,
-- index, and foreign key the ENDCOM.NET backend needs.
--
-- Generated from the FastAPI backend's actual SQLAlchemy models (via
-- `Base.metadata.create_all()` against a real local Postgres instance,
-- then `pg_dump --schema-only`), not hand-written - so this is guaranteed
-- to match app/models/*.py exactly at the time it was generated. If the
-- backend gains a new model or column later, this file won't retroactively
-- pick it up on its own (the backend's own startup already handles that
-- for you via app/database.py's init_db()/_add_missing_columns) - re-run
-- the same generation process if you want this file to stay a fully
-- accurate from-empty snapshot.
--
-- To apply: paste this file into the Supabase Dashboard's SQL Editor and
-- run it, or `supabase db push` if you're using the Supabase CLI. Run
-- 20260813000001_enable_row_level_security.sql right after it - a fresh
-- Supabase project needs both to be safe to expose (see that file's
-- header for why).
--
-- Safe to re-run: every statement is idempotent (CREATE TABLE/INDEX IF
-- NOT EXISTS) except the ADD CONSTRAINT statements for primary/foreign
-- keys, which will error with "already exists" on a second run against a
-- database that already has them - that's intentional, it means nothing
-- to do here rather than silently reapplying.

CREATE TABLE IF NOT EXISTS public.appointments (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    location character varying,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    duration_minutes integer NOT NULL,
    all_day boolean,
    attendees json,
    meeting_url character varying,
    conference_room character varying,
    status character varying,
    is_reminder_sent boolean,
    external_calendar_provider character varying,
    external_calendar_event_id character varying,
    is_recurring boolean,
    recurrence_rule character varying,
    created_by character varying,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.calendar_connections (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    provider character varying NOT NULL,
    access_token character varying NOT NULL,
    refresh_token character varying,
    token_expires_at timestamp without time zone,
    external_calendar_id character varying,
    external_account_email character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.contacts (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    full_name character varying NOT NULL,
    nickname character varying,
    email character varying,
    phone_number character varying,
    mobile_number character varying,
    company character varying,
    job_title character varying,
    department character varying,
    address text,
    city character varying,
    state character varying,
    country character varying,
    postal_code character varying,
    birthday date,
    anniversary date,
    linkedin_url character varying,
    twitter_handle character varying,
    website character varying,
    relationship_type character varying,
    priority character varying,
    notes text,
    tags json,
    custom_fields json,
    is_favorite boolean,
    last_contacted timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.documents (
    id character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    file_name character varying NOT NULL,
    file_path character varying NOT NULL,
    file_type character varying NOT NULL,
    mime_type character varying NOT NULL,
    file_size integer NOT NULL,
    category character varying,
    tags json,
    owner_id character varying,
    created_by character varying,
    department character varying,
    is_public boolean,
    shared_with json,
    access_level character varying,
    version character varying,
    previous_version_id character varying,
    is_latest_version boolean,
    status character varying,
    extracted_text text,
    summary text,
    keywords json,
    download_count integer,
    last_accessed timestamp without time zone,
    expires_at timestamp without time zone,
    storage_provider character varying,
    external_url character varying,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.messages (
    id character varying NOT NULL,
    message_type character varying NOT NULL,
    direction character varying NOT NULL,
    from_name character varying,
    from_email character varying,
    from_phone character varying,
    to_name character varying,
    to_email character varying,
    to_phone character varying,
    subject character varying,
    body text,
    snippet character varying,
    status character varying,
    priority character varying,
    is_flagged boolean,
    is_spam boolean,
    thread_id character varying,
    in_reply_to character varying,
    sent_at timestamp without time zone,
    received_at timestamp without time zone,
    read_at timestamp without time zone,
    has_attachments boolean,
    attachments json,
    sentiment character varying,
    category character varying,
    requires_action boolean,
    action_type character varying,
    ai_draft_reply text,
    tags json,
    labels json,
    external_id character varying,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.tasks (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    priority character varying,
    status character varying,
    due_date timestamp without time zone,
    start_date timestamp without time zone,
    completed_at timestamp without time zone,
    estimated_hours integer,
    actual_hours integer,
    project character varying,
    category character varying,
    tags json,
    assigned_to character varying,
    assigned_by character varying,
    depends_on json,
    blocks json,
    reminder_date timestamp without time zone,
    is_reminder_sent boolean,
    follow_up_date timestamp without time zone,
    parent_task_id character varying,
    has_subtasks boolean,
    progress_percentage integer,
    notes text,
    attachments json,
    is_recurring boolean,
    recurrence_rule character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.users (
    id character varying NOT NULL,
    email character varying NOT NULL,
    username character varying NOT NULL,
    full_name character varying NOT NULL,
    hashed_password character varying NOT NULL,
    is_active boolean,
    is_superuser boolean,
    timezone character varying,
    phone_number character varying,
    job_title character varying,
    department character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

CREATE TABLE IF NOT EXISTS public.visitors (
    id character varying NOT NULL,
    full_name character varying NOT NULL,
    company character varying,
    email character varying,
    phone_number character varying,
    visit_type character varying,
    purpose text,
    host_name character varying NOT NULL,
    host_department character varying,
    scheduled_time timestamp without time zone,
    check_in_time timestamp without time zone,
    check_out_time timestamp without time zone,
    status character varying,
    location character varying,
    conference_room character varying,
    parking_spot character varying,
    badge_number character varying,
    id_verified boolean,
    nda_signed boolean,
    call_duration_minutes character varying,
    call_notes text,
    notes text,
    photo_url character varying,
    host_notified boolean,
    notification_sent_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

-- Primary keys

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.calendar_connections
    ADD CONSTRAINT calendar_connections_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.visitors
    ADD CONSTRAINT visitors_pkey PRIMARY KEY (id);

-- Indexes

CREATE INDEX IF NOT EXISTS ix_appointments_id ON public.appointments USING btree (id);
CREATE INDEX IF NOT EXISTS ix_appointments_start_time ON public.appointments USING btree (start_time);

CREATE INDEX IF NOT EXISTS ix_calendar_connections_id ON public.calendar_connections USING btree (id);
CREATE INDEX IF NOT EXISTS ix_calendar_connections_user_id ON public.calendar_connections USING btree (user_id);

CREATE INDEX IF NOT EXISTS ix_contacts_company ON public.contacts USING btree (company);
CREATE INDEX IF NOT EXISTS ix_contacts_email ON public.contacts USING btree (email);
CREATE INDEX IF NOT EXISTS ix_contacts_full_name ON public.contacts USING btree (full_name);
CREATE INDEX IF NOT EXISTS ix_contacts_id ON public.contacts USING btree (id);

CREATE INDEX IF NOT EXISTS ix_documents_category ON public.documents USING btree (category);
CREATE INDEX IF NOT EXISTS ix_documents_id ON public.documents USING btree (id);
CREATE INDEX IF NOT EXISTS ix_documents_title ON public.documents USING btree (title);

CREATE INDEX IF NOT EXISTS ix_messages_from_email ON public.messages USING btree (from_email);
CREATE INDEX IF NOT EXISTS ix_messages_id ON public.messages USING btree (id);
CREATE INDEX IF NOT EXISTS ix_messages_message_type ON public.messages USING btree (message_type);
CREATE INDEX IF NOT EXISTS ix_messages_status ON public.messages USING btree (status);
CREATE INDEX IF NOT EXISTS ix_messages_thread_id ON public.messages USING btree (thread_id);
CREATE INDEX IF NOT EXISTS ix_messages_to_email ON public.messages USING btree (to_email);

CREATE INDEX IF NOT EXISTS ix_tasks_due_date ON public.tasks USING btree (due_date);
CREATE INDEX IF NOT EXISTS ix_tasks_id ON public.tasks USING btree (id);
CREATE INDEX IF NOT EXISTS ix_tasks_project ON public.tasks USING btree (project);
CREATE INDEX IF NOT EXISTS ix_tasks_status ON public.tasks USING btree (status);
CREATE INDEX IF NOT EXISTS ix_tasks_title ON public.tasks USING btree (title);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON public.users USING btree (email);
CREATE INDEX IF NOT EXISTS ix_users_id ON public.users USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON public.users USING btree (username);

CREATE INDEX IF NOT EXISTS ix_visitors_full_name ON public.visitors USING btree (full_name);
CREATE INDEX IF NOT EXISTS ix_visitors_id ON public.visitors USING btree (id);
CREATE INDEX IF NOT EXISTS ix_visitors_status ON public.visitors USING btree (status);

-- Foreign keys

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.calendar_connections
    ADD CONSTRAINT calendar_connections_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_parent_task_id_fkey FOREIGN KEY (parent_task_id) REFERENCES public.tasks(id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
