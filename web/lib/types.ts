// Mirrors the FastAPI response schemas in app/schemas/*.py

export interface Appointment {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  location: string | null;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  all_day: boolean;
  attendees: string[];
  meeting_url: string | null;
  conference_room: string | null;
  status: string;
  external_calendar_provider?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  priority: string;
  status: string;
  due_date: string | null;
  project: string | null;
  category: string | null;
  tags: string[];
  assigned_to: string | null;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface Contact {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string | null;
  phone_number: string | null;
  mobile_number: string | null;
  company: string | null;
  job_title: string | null;
  relationship_type: string | null;
  priority: string;
  notes: string | null;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface Visitor {
  id: string;
  full_name: string;
  company: string | null;
  email: string | null;
  phone_number: string | null;
  visit_type: string;
  purpose: string | null;
  host_name: string;
  status: string;
  scheduled_time: string | null;
  check_in_time: string | null;
  check_out_time: string | null;
  location: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  message_type: string;
  direction: string;
  from_name: string | null;
  from_email: string | null;
  from_phone: string | null;
  to_email: string | null;
  subject: string | null;
  body: string | null;
  snippet?: string | null;
  status: string;
  priority: string;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

export interface CalendarConnection {
  provider: string;
  account_email: string | null;
  connected_at: string;
}

export interface ChatResponse {
  response: string;
  intent: string | null;
  entities: Record<string, unknown> | null;
  actions: Array<{ type: string; data: Record<string, unknown> }> | null;
  confidence: number | null;
  suggestions: string[] | null;
  timestamp: string;
}
