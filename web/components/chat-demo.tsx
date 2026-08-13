"use client";

import { useRef, useState } from "react";
import type { ChatResponse } from "@/lib/types";

type Message = { role: "user" | "assistant"; text: string };

const EXAMPLE_QUERIES = [
  "Schedule a meeting tomorrow at 2pm",
  "What can you help me with?",
  "Create a task to review proposal",
  "Show my calendar for today",
  "Check in a visitor",
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export function ChatDemo() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Hi, I'm Tammy. I can help with scheduling appointments, managing tasks, finding contacts, checking in visitors, and handling messages. Try asking something like “Schedule a meeting tomorrow at 2pm”.",
    },
  ]);
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>(EXAMPLE_QUERIES);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);
    scrollToBottom();

    try {
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      if (!response.ok) throw new Error("Request failed");
      const data: ChatResponse = await response.json();

      setMessages((prev) => [...prev, { role: "assistant", text: data.response }]);
      setSuggestions(data.suggestions ?? []);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "I'm having trouble connecting to the server. Please make sure the API is running.",
        },
      ]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  }

  return (
    <div className="mx-auto max-w-2xl overflow-hidden rounded-2xl border border-line bg-surface shadow-lg">
      <div className="flex items-center gap-2.5 border-b border-line bg-surface-sunken px-5.5 py-4">
        <span className="flex h-6.5 w-6.5 items-center justify-center rounded-full bg-teal font-serif text-[13px] italic text-surface">
          T
        </span>
        <span className="text-[14.5px] font-semibold">Tammy</span>
        <span className="ml-auto flex items-center gap-1.5 text-[12.5px] text-teal-deep">
          <span className="h-1.75 w-1.75 rounded-full bg-teal" />
          Online
        </span>
      </div>

      <div ref={scrollRef} className="h-[380px] space-y-4.5 overflow-y-auto bg-paper p-5.5">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : ""}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4.5 py-3 text-[14.5px] ${
                m.role === "user"
                  ? "rounded-br-sm bg-teal text-surface"
                  : "rounded-bl-sm border border-line bg-surface"
              }`}
            >
              <strong
                className={`mb-1.5 block text-[12.5px] font-semibold tracking-wide uppercase ${
                  m.role === "user" ? "text-teal-tint" : "text-teal-deep"
                }`}
              >
                {m.role === "user" ? "You" : "Tammy"}
              </strong>
              <span className="whitespace-pre-line">{m.text}</span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex">
            <div className="max-w-[80%] rounded-xl rounded-bl-sm border border-line bg-surface px-4.5 py-3 text-[14.5px]">
              <strong className="mb-1.5 block text-[12.5px] font-semibold tracking-wide text-teal-deep uppercase">
                Tammy
              </strong>
              <span className="tracking-widest text-ink-faint">●●●</span>
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage(input);
        }}
        className="flex gap-2.5 border-t border-line bg-surface px-5 py-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message... (e.g., 'Schedule a meeting tomorrow at 2pm')"
          disabled={loading}
          className="flex-1 rounded-md border-[1.5px] border-line-strong bg-paper px-4 py-3 text-[14.5px] text-ink focus:border-teal focus:outline-none disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-teal px-6.5 py-3 text-[14.5px] font-semibold text-surface transition-colors hover:bg-teal-deep disabled:opacity-50"
        >
          Send
        </button>
      </form>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2 border-t border-line bg-surface px-5 py-3.5 pb-4.5">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="rounded-full border border-line bg-surface-sunken px-3.5 py-1.75 text-[13px] transition-colors hover:border-teal hover:bg-teal-tint hover:text-teal-deep"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
