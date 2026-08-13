import Link from "next/link";
import { ChatDemo } from "@/components/chat-demo";
import { CopyButton } from "@/components/copy-button";
import {
  CalendarIcon,
  CheckCircleIcon,
  CheckIcon,
  ClockIcon,
  DoorIcon,
  MailIcon,
  ShieldIcon,
  SparkleIcon,
  UsersIcon,
} from "@/components/icons";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://your-domain.com";

const FEATURES = [
  {
    icon: CalendarIcon,
    title: "Calendar management",
    body: "Schedules appointments, checks availability, sends reminders, and resolves conflicts automatically.",
  },
  {
    icon: CheckCircleIcon,
    title: "Task coordination",
    body: "Creates tasks, sets priorities, tracks deadlines, and keeps projects moving without the nagging.",
  },
  {
    icon: UsersIcon,
    title: "Contact management",
    body: "Keeps a living directory of contacts, relationships, and the small details worth remembering.",
  },
  {
    icon: DoorIcon,
    title: "Visitor tracking",
    body: "Checks visitors in, prints a badge, logs the visit, and notifies the right host the moment they arrive.",
  },
  {
    icon: MailIcon,
    title: "Communication",
    body: "Filters and prioritises messages, drafts responses, and handles the routine inquiries on its own.",
  },
  {
    icon: SparkleIcon,
    title: "Natural conversation",
    body: "Understands plain-language requests and stays aware of context across a conversation.",
  },
];

const DESK_LOG = [
  {
    icon: CalendarIcon,
    title: "Booked: Priya & J. Alvarez",
    sub: "Product review, moved to 2:00 PM",
    time: "Just now",
  },
  {
    icon: DoorIcon,
    title: "Visitor checked in",
    sub: "D. Okafor for the 10 o'clock, badge #114",
    time: "8:57 AM",
  },
  {
    icon: MailIcon,
    title: "3 messages triaged",
    sub: "1 flagged for follow-up today",
    time: "8:30 AM",
  },
];

export default function Home() {
  return (
    <>
      {/* Nav */}
      <nav className="sticky top-0 z-40 border-b border-line bg-paper/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
          <Link href="#" className="flex items-center gap-2.5 text-[22px] font-semibold">
            <span className="flex h-8.5 w-8.5 items-center justify-center rounded-full bg-teal font-serif text-lg italic text-surface">
              E
            </span>
            <span className="font-serif italic">ENDCOM.NET</span>
          </Link>
          <ul className="hidden items-center gap-7 md:flex">
            <li>
              <a href="#features" className="text-[15px] font-medium text-ink-soft hover:text-ink">
                What she does
              </a>
            </li>
            <li>
              <a href="#chat" className="text-[15px] font-medium text-ink-soft hover:text-ink">
                Try the demo
              </a>
            </li>
            <li>
              <a href="#api" className="text-[15px] font-medium text-ink-soft hover:text-ink">
                Integrations
              </a>
            </li>
            <li>
              <Link href="/login" className="text-[15px] font-medium text-ink-soft hover:text-ink">
                Admin
              </Link>
            </li>
          </ul>
          <a
            href="#chat"
            className="rounded-md bg-teal px-5 py-2.5 text-[15px] font-semibold text-surface transition-colors hover:bg-teal-deep"
          >
            Talk to Tammy
          </a>
        </div>
      </nav>

      <main id="main">
        {/* Hero */}
        <section className="py-16 md:py-22">
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 md:grid-cols-[1.05fr_0.95fr] md:gap-16">
            <div>
              <span className="mb-5.5 inline-flex items-center gap-2 rounded-full bg-teal-tint px-3.5 py-1.75 text-[13px] font-semibold tracking-wide text-teal-deep uppercase">
                Virtual front desk, staffed 24/7
              </span>
              <h1 className="mb-5.5 text-[clamp(2.25rem,4.4vw,3.25rem)] leading-[1.12] font-semibold text-balance">
                A receptionist and executive assistant who{" "}
                <em className="font-serif text-teal-deep not-italic italic">never misses a call</em>
              </h1>
              <p className="mb-9 max-w-[46ch] text-lg text-ink-soft">
                Tammy answers your phones, books meetings, greets visitors, and keeps your inbox in
                order - so your team can focus on the work instead of the front desk.
              </p>
              <div className="flex flex-wrap gap-4">
                <a
                  href="#chat"
                  className="rounded-md bg-teal px-7 py-3.5 text-[15.5px] font-semibold text-surface transition-colors hover:bg-teal-deep"
                >
                  Try the chat demo
                </a>
                <a
                  href={`${API_URL}/docs`}
                  className="rounded-md border-[1.5px] border-line-strong px-7 py-3.5 text-[15.5px] font-semibold transition-colors hover:border-ink"
                >
                  Read the API docs
                </a>
              </div>
              <div className="mt-10 flex flex-wrap gap-7">
                <span className="flex items-center gap-2 text-[13.5px] text-ink-faint">
                  <CheckIcon className="h-4 w-4 text-teal-deep" />
                  No calls to voicemail
                </span>
                <span className="flex items-center gap-2 text-[13.5px] text-ink-faint">
                  <ClockIcon className="h-4 w-4 text-teal-deep" />
                  Live in minutes
                </span>
                <span className="flex items-center gap-2 text-[13.5px] text-ink-faint">
                  <ShieldIcon className="h-4 w-4 text-teal-deep" />
                  Your data, your control
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-line bg-surface p-7 shadow-xl">
              <div className="mb-4.5 flex items-center justify-between text-xs tracking-wide text-ink-faint uppercase">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-teal" />
                  Front desk - today
                </span>
                <span>9:12 AM</span>
              </div>
              {DESK_LOG.map((item, i) => (
                <div
                  key={item.title}
                  className={`flex gap-3.5 py-3.5 ${i > 0 ? "border-t border-line" : ""}`}
                >
                  <item.icon className="mt-0.5 h-5 w-5 shrink-0 text-teal-deep" />
                  <div>
                    <div className="mb-0.5 text-[15px] font-semibold">{item.title}</div>
                    <div className="text-[13.5px] text-ink-soft">{item.sub}</div>
                  </div>
                  <div className="ml-auto shrink-0 text-[13px] whitespace-nowrap text-ink-faint">
                    {item.time}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-y border-line bg-surface-sunken py-22">
          <div className="mx-auto max-w-6xl px-6">
            <div className="mx-auto mb-12 max-w-xl text-center">
              <span className="mb-3 block text-[13px] font-semibold tracking-wide text-brass uppercase">
                What Tammy handles
              </span>
              <h2 className="mb-3.5 text-[clamp(1.75rem,3vw,2.25rem)] font-semibold text-balance">
                Everything a front desk and an EA juggle, in one place
              </h2>
              <p className="text-[16.5px] text-ink-soft">
                Built for teams who want the polish of a full-time assistant without the overhead.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {FEATURES.map((f) => (
                <div
                  key={f.title}
                  className="rounded-xl border border-line bg-surface p-7.5 transition-all hover:-translate-y-0.75 hover:border-line-strong hover:shadow-md"
                >
                  <div className="mb-5 flex h-11.5 w-11.5 items-center justify-center rounded-full bg-teal-tint text-teal-deep">
                    <f.icon className="h-5.5 w-5.5" />
                  </div>
                  <h3 className="mb-2.5 text-lg font-semibold">{f.title}</h3>
                  <p className="text-[14.5px] text-ink-soft">{f.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Chat demo */}
        <section id="chat" className="py-22">
          <div className="mx-auto max-w-6xl px-6">
            <div className="mx-auto mb-12 max-w-xl text-center">
              <span className="mb-3 block text-[13px] font-semibold tracking-wide text-brass uppercase">
                See it in action
              </span>
              <h2 className="mb-3.5 text-[clamp(1.75rem,3vw,2.25rem)] font-semibold">Try Tammy now</h2>
              <p className="text-[16.5px] text-ink-soft">
                Chat with Tammy using plain language, just like you would with a real assistant.
              </p>
            </div>
            <ChatDemo />
          </div>
        </section>

        {/* API examples */}
        <section id="api" className="py-22">
          <div className="mx-auto max-w-6xl px-6">
            <div className="mx-auto mb-12 max-w-xl text-center">
              <span className="mb-3 block text-[13px] font-semibold tracking-wide text-brass uppercase">
                For developers
              </span>
              <h2 className="mb-3.5 text-[clamp(1.75rem,3vw,2.25rem)] font-semibold">
                Integrate ENDCOM.NET into your own tools
              </h2>
              <p className="text-[16.5px] text-ink-soft">
                A straightforward REST API - bring ENDCOM.NET into whatever your team already uses.
              </p>
            </div>

            <div className="mx-auto mb-10 grid max-w-2xl gap-5">
              {[
                {
                  label: "Chat with Tammy",
                  code: `curl -X POST ${API_URL}/api/chat \\\n  -H "Content-Type: application/json" \\\n  -d '{"message": "Schedule a meeting tomorrow at 2pm"}'`,
                },
                {
                  label: "Create an appointment",
                  code: `curl -X POST ${API_URL}/api/appointments \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "user_id": "user123",\n    "title": "Team Meeting",\n    "start_time": "2025-11-15T14:00:00",\n    "duration_minutes": 60\n  }'`,
                },
              ].map((block) => (
                <div key={block.label} className="overflow-hidden rounded-xl border border-line bg-surface">
                  <div className="flex items-center justify-between border-b border-line bg-surface-sunken px-4.5 py-3 text-[13.5px] font-semibold">
                    <span>{block.label}</span>
                    <CopyButton text={block.code} />
                  </div>
                  <pre className="overflow-x-auto px-5 py-4.5">
                    <code className="font-mono text-[13.5px] leading-relaxed text-ink-soft">{block.code}</code>
                  </pre>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap justify-center gap-3.5">
              <a
                href={`${API_URL}/docs`}
                className="rounded-md border border-line px-5.5 py-2.75 text-[14.5px] font-medium transition-all hover:-translate-y-0.5 hover:border-teal"
              >
                Full API documentation
              </a>
              <a
                href={`${API_URL}/redoc`}
                className="rounded-md border border-line px-5.5 py-2.75 text-[14.5px] font-medium transition-all hover:-translate-y-0.5 hover:border-teal"
              >
                ReDoc reference
              </a>
              <a
                href={`${API_URL}/health`}
                className="rounded-md border border-line px-5.5 py-2.75 text-[14.5px] font-medium transition-all hover:-translate-y-0.5 hover:border-teal"
              >
                Health check
              </a>
            </div>
          </div>
        </section>

        {/* Tech stack */}
        <section className="py-22">
          <div className="mx-auto max-w-6xl px-6 text-center">
            <span className="mb-3 block text-[13px] font-semibold tracking-wide text-brass uppercase">
              Under the hood
            </span>
            <h2 className="mb-10 text-[clamp(1.75rem,3vw,2.25rem)] font-semibold">
              Built on a modern, reliable stack
            </h2>
            <div className="mx-auto flex max-w-3xl flex-wrap justify-center gap-3">
              {["Next.js", "FastAPI", "Supabase", "Python 3.11+", "SQLAlchemy", "RESTful API", "Docker"].map(
                (t) => (
                  <span
                    key={t}
                    className="rounded-full border border-line bg-surface px-4.5 py-2.25 text-[13.5px] font-medium text-ink-soft"
                  >
                    {t}
                  </span>
                ),
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-line py-10">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6">
          <p className="text-sm text-ink-faint">
            &copy; {new Date().getFullYear()} ENDCOM.NET. Open source under the MIT License.
          </p>
          <div className="flex gap-6">
            <a
              href="https://github.com/airostudio/Tammy"
              className="text-sm text-ink-soft transition-colors hover:text-teal-deep"
            >
              GitHub
            </a>
            <a href={`${API_URL}/docs`} className="text-sm text-ink-soft transition-colors hover:text-teal-deep">
              Documentation
            </a>
            <Link href="/login" className="text-sm text-ink-soft transition-colors hover:text-teal-deep">
              Admin
            </Link>
          </div>
        </div>
      </footer>
    </>
  );
}
