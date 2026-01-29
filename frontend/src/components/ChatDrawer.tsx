"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { X, Send } from "lucide-react";
import { chatWithRole } from "@/lib/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type ChatOpportunity = {
  id?: string;
  title: string;
  organization: string;
  location: string;
  summary: string;
  url: string;
  full_text?: string;
};

type ChatDrawerProps = {
  isOpen: boolean;
  onClose: () => void;
  opportunity: ChatOpportunity | null;
};

export function ChatDrawer({ isOpen, onClose, opportunity }: ChatDrawerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Reset conversation when a new opportunity is selected or drawer closes
    setMessages([]);
    setInput("");
    setIsLoading(false);
  }, [opportunity?.id, isOpen]);

  const headerTitle = useMemo(
    () => opportunity?.title ?? "Contextual Chat",
    [opportunity?.title],
  );

  const handleSend = useCallback(
    async (evt?: React.FormEvent) => {
      evt?.preventDefault();
      if (!opportunity || !input.trim() || isLoading) return;

      const content = input.trim();
      setInput("");

      const userMessage: ChatMessage = {
        id: `${Date.now()}-user`,
        role: "user",
        content,
      };

      const nextMessages = [...messages, userMessage];
      setMessages(nextMessages);
      setIsLoading(true);

      const historyPayload = nextMessages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      try {
        const response = await chatWithRole(
          opportunity.id ?? "",
          opportunity.full_text ?? opportunity.summary ?? "",
          content,
          historyPayload,
        );

        const botMessage: ChatMessage = {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          content: response.answer,
        };
        setMessages((prev) => [...prev, botMessage]);
      } catch (error: any) {
        const errorMessage: ChatMessage = {
          id: `${Date.now()}-error`,
          role: "assistant",
          content:
            error?.message ??
            "Sorry, something went wrong while fetching a response.",
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [input, isLoading, messages, opportunity],
  );

  if (!isOpen || !opportunity) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="relative z-50 flex h-full w-full max-w-md flex-col bg-slate-950/95 text-slate-50 border-l border-slate-800 shadow-[0_0_40px_rgba(8,47,73,0.8)]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3 bg-slate-950/90">
          <div className="flex flex-col">
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-400/80">
              Contextual Chat
            </span>
            <h2 className="text-sm font-medium text-slate-100 line-clamp-2">
              {headerTitle}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-700/80 bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:text-slate-50 hover:border-teal-500 transition-colors"
            aria-label="Close chat"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
          {messages.length === 0 && (
            <div className="rounded-2xl border border-dashed border-slate-700/80 bg-slate-900/60 px-4 py-3 text-xs text-slate-300">
              <p className="font-medium text-slate-100 mb-1">
                Ask Beacon about this opportunity
              </p>
              <p>
                Get clarity on time commitment, responsibilities, requirements,
                and more — grounded in the role&apos;s details.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm shadow-sm ${
                  msg.role === "user"
                    ? "bg-teal-500 text-slate-950 rounded-br-none"
                    : "bg-slate-900/90 text-slate-50 border border-slate-800 rounded-bl-none"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-teal-400" />
              Beacon is thinking…
            </div>
          )}
        </div>

        {/* Input */}
        <form
          onSubmit={handleSend}
          className="border-t border-slate-800 bg-slate-950/95 px-3 py-3"
        >
          <div className="flex items-end gap-2 rounded-2xl border border-slate-800 bg-slate-900/80 px-3 py-2 focus-within:border-teal-500 focus-within:ring-1 focus-within:ring-teal-500/70">
            <textarea
              rows={2}
              className="flex-1 resize-none bg-transparent text-sm text-slate-100 placeholder:text-slate-500 outline-none border-none"
              placeholder="Ask a question about this role…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="inline-flex items-center justify-center rounded-full bg-teal-500 px-3 py-2 text-xs font-semibold text-slate-950 shadow-md hover:bg-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="mr-1 h-3 w-3" />
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
