"use client";

import React from "react";
import { ExternalLink, Heart, MapPin, MessageCircle } from "lucide-react";
import type { ChatOpportunity } from "./ChatDrawer";

type OpportunityCardProps = {
  opportunity: ChatOpportunity;
  onChatClick?: (opportunity: ChatOpportunity) => void;
  isSaved?: boolean;
  onSave?: (opportunity: ChatOpportunity) => void;
};

export function OpportunityCard({
  opportunity,
  onChatClick,
  isSaved,
  onSave,
}: OpportunityCardProps) {
  const handleApply = () => {
    if (!opportunity.url) return;
    window.open(opportunity.url, "_blank", "noopener,noreferrer");
  };

  const handleChat = () => {
    onChatClick?.(opportunity);
  };

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSave?.(opportunity);
  };

  return (
    <div className="relative flex h-full flex-col rounded-2xl border border-slate-800/90 bg-slate-950/80 p-4 shadow-[0_18px_45px_rgba(15,23,42,0.9)] transition-all hover:-translate-y-1 hover:border-teal-500/70 hover:shadow-[0_25px_60px_rgba(45,212,191,0.35)]">
      {/* Save button */}
      <button
        type="button"
        onClick={handleSave}
        className="absolute right-3 top-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-800 bg-slate-900/80 text-slate-400 hover:border-teal-500 hover:bg-slate-900 hover:text-teal-300 transition-colors"
        aria-label={isSaved ? "Unsave opportunity" : "Save opportunity"}
      >
        <Heart
          className={`h-4 w-4 ${
            isSaved ? "fill-teal-500 text-teal-500" : "text-slate-400"
          }`}
        />
      </button>

      <div className="flex-1 space-y-2 pr-6">
        <h3 className="text-lg font-semibold text-slate-50 line-clamp-2">
          {opportunity.title}
        </h3>
        <p className="text-sm font-medium text-teal-300">
          {opportunity.organization}
        </p>
        {opportunity.location && (
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <MapPin className="h-3.5 w-3.5 text-teal-400" />
            <span>{opportunity.location}</span>
          </div>
        )}
        <p className="text-sm text-slate-300 line-clamp-4">
          {opportunity.summary}
        </p>
      </div>

      <div className="mt-4 flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={handleApply}
          className="inline-flex flex-1 items-center justify-center gap-1 rounded-full border border-teal-500/70 bg-teal-500/10 px-3 py-2 text-xs font-semibold text-teal-200 hover:bg-teal-500/20 hover:border-teal-400 transition-colors"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          Apply Now
        </button>
        <button
          type="button"
          onClick={handleChat}
          className="inline-flex flex-1 items-center justify-center gap-1 rounded-full bg-slate-900/90 px-3 py-2 text-xs font-semibold text-slate-100 border border-slate-700 hover:border-teal-500 hover:bg-slate-900/60 transition-colors"
        >
          <MessageCircle className="h-3.5 w-3.5 text-teal-400" />
          Ask Beacon
        </button>
      </div>
    </div>
  );
}
