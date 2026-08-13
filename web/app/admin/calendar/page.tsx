"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { CalendarConnection } from "@/lib/types";

const PROVIDERS = [
  { key: "google", label: "Google Calendar" },
  { key: "microsoft", label: "Microsoft 365 / Outlook" },
];

export default function CalendarSettingsPage() {
  const [feedUrl, setFeedUrl] = useState<string | null>(null);
  const [connections, setConnections] = useState<CalendarConnection[] | null>(null);
  const [copied, setCopied] = useState(false);
  const [connecting, setConnecting] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [feedResponse, connectionsResponse] = await Promise.all([
      apiFetch("/api/calendar/feed-url"),
      apiFetch("/api/calendar/connections"),
    ]);
    if (feedResponse.ok) {
      const data = await feedResponse.json();
      setFeedUrl(`${process.env.NEXT_PUBLIC_API_URL}${data.path}`);
    }
    if (connectionsResponse.ok) {
      setConnections(await connectionsResponse.json());
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleConnect(provider: string) {
    setConnecting(provider);
    try {
      // A plain <a href> can't carry our Bearer token cross-origin, so we
      // fetch the authorize URL (with the token attached) and redirect
      // ourselves - see the Accept: application/json handling in
      // app/api/calendar.py's start_oauth_connect.
      const response = await apiFetch(`/api/calendar/oauth/${provider}/connect`, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) throw new Error("Failed to start connection");
      const data = await response.json();
      window.location.href = data.authorize_url;
    } catch {
      window.alert("Could not start the connection. Please try again.");
      setConnecting(null);
    }
  }

  async function handleDisconnect(provider: string, label: string) {
    if (!window.confirm(`Disconnect ${label}?`)) return;
    try {
      await apiFetch(`/api/calendar/connections/${provider}`, { method: "DELETE" });
      load();
    } catch {
      window.alert("Could not disconnect. Please try again.");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <h2 className="text-xl font-semibold">Calendar</h2>

      <div className="rounded-xl border border-line bg-surface p-6">
        <h3 className="mb-1.5 text-base font-semibold">Subscribe by URL (iCal)</h3>
        <p className="mb-4 text-[13.5px] text-ink-soft">
          Any calendar app can subscribe to this URL to see your appointments - no account connection needed.
        </p>
        <div className="flex gap-2.5">
          <input
            readOnly
            value={feedUrl ?? "Loading…"}
            className="flex-1 rounded-md border-[1.5px] border-line-strong bg-paper px-3.5 py-2.5 font-mono text-[13.5px]"
          />
          <button
            disabled={!feedUrl}
            onClick={() => {
              if (!feedUrl) return;
              navigator.clipboard.writeText(feedUrl);
              setCopied(true);
              setTimeout(() => setCopied(false), 1500);
            }}
            className="rounded-md border-[1.5px] border-line-strong px-5 py-2.5 text-sm font-semibold hover:border-ink disabled:opacity-50"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-line bg-surface p-6">
        <h3 className="mb-1.5 text-base font-semibold">Connected calendars</h3>
        <p className="mb-1 text-[13.5px] text-ink-soft">
          Connect Google Calendar or Microsoft 365 to have new appointments pushed there automatically.
        </p>

        {PROVIDERS.map(({ key, label }) => {
          const connection = connections?.find((c) => c.provider === key);
          return (
            <div key={key} className="flex items-center justify-between gap-4 border-t border-line py-4 first:border-t-0">
              <div>
                <div className="mb-1.5 text-[14.5px] font-semibold">{label}</div>
                <span
                  className={`inline-block rounded-full px-3 py-1 text-[12.5px] font-semibold ${
                    connection ? "bg-teal-tint text-teal-deep" : "bg-surface-sunken text-ink-faint"
                  }`}
                >
                  {connection ? `Connected${connection.account_email ? ` as ${connection.account_email}` : ""}` : "Not connected"}
                </span>
              </div>
              {connection ? (
                <button
                  onClick={() => handleDisconnect(key, label)}
                  className="rounded-md border-[1.5px] border-line-strong px-4.5 py-2 text-[13.5px] font-semibold hover:border-red-600 hover:text-red-600"
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={() => handleConnect(key)}
                  disabled={connecting === key}
                  className="rounded-md border-[1.5px] border-line-strong px-4.5 py-2 text-[13.5px] font-semibold hover:border-ink disabled:opacity-50"
                >
                  {connecting === key ? "Connecting…" : "Connect"}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
