"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { searchOpportunities, saveRole } from "@/lib/api";
import { ChatDrawer, type ChatOpportunity } from "@/components/ChatDrawer";
import { OpportunityCard } from "@/components/OpportunityCard";
import { useUser } from "@clerk/nextjs";

type SearchOpportunity = ChatOpportunity;

export default function SearchPage() {
  const { user, isSignedIn } = useUser();
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [opportunities, setOpportunities] = useState<SearchOpportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] =
    useState<SearchOpportunity | null>(null);
  const [savedUrls, setSavedUrls] = useState<Set<string>>(new Set());

  const hasQuery = useMemo(() => query.trim().length > 0, [query]);

  useEffect(() => {
    if (!hasQuery) {
      setOpportunities([]);
      return;
    }

    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    searchOpportunities(query)
      .then((res) => {
        if (isCancelled) return;
        const mapped: SearchOpportunity[] = res.opportunities.map((opp) => ({
          ...opp,
        }));
        setOpportunities(mapped);
      })
      .catch((err: any) => {
        if (isCancelled) return;
        setError(err?.message ?? "Failed to load opportunities.");
      })
      .finally(() => {
        if (isCancelled) return;
        setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [hasQuery, query]);

  const handleChatOpen = (opportunity: SearchOpportunity) => {
    setSelectedOpportunity(opportunity);
  };

  const handleChatClose = () => {
    setSelectedOpportunity(null);
  };

  const handleSave = async (opportunity: SearchOpportunity) => {
    if (!isSignedIn || !user?.id) {
      window.alert("Please sign in to save.");
      return;
    }

    try {
      await saveRole(user.id, {
        title: opportunity.title,
        organization: opportunity.organization,
        location: opportunity.location,
        summary: opportunity.summary,
        url: opportunity.url,
        full_text: opportunity.full_text ?? undefined,
      });

      setSavedUrls((prev) => new Set(prev).add(opportunity.url));
      window.alert("Role Saved!");
    } catch (err: any) {
      window.alert(err?.message ?? "Failed to save role.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 pb-8 pt-20 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-teal-400/80">
              Results
            </p>
            <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-slate-50">
              Search results
            </h1>
            {hasQuery && (
              <p className="mt-1 text-sm text-slate-400">
                Showing opportunities for{" "}
                <span className="font-semibold text-teal-300">
                  “{query.trim()}”
                </span>
                .
              </p>
            )}
            {!hasQuery && (
              <p className="mt-1 text-sm text-slate-400">
                Add a query in the search bar on the home page to discover
                curated volunteering opportunities.
              </p>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1">
          {isLoading && (
            <div className="flex h-48 items-center justify-center">
              <div className="flex items-center gap-3 rounded-full border border-slate-800 bg-slate-950/80 px-4 py-2 shadow-[0_18px_45px_rgba(15,23,42,0.9)]">
                <Loader2 className="h-4 w-4 animate-spin text-teal-400" />
                <span className="text-sm text-slate-200">
                  Beacon is mapping opportunities…
                </span>
              </div>
            </div>
          )}

          {!isLoading && error && (
            <div className="mt-8 rounded-2xl border border-red-500/40 bg-red-950/40 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          )}

          {!isLoading && !error && hasQuery && opportunities.length === 0 && (
            <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-950/70 px-6 py-6 text-sm text-slate-200">
              <p className="font-semibold text-slate-100 mb-1">
                No matches just yet.
              </p>
              <p>
                Try broadening your search terms, adjusting your location, or
                exploring different types of service. Beacon will keep looking
                for meaningful ways to help you give back.
              </p>
            </div>
          )}

          {!isLoading && !error && opportunities.length > 0 && (
            <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {opportunities.map((opportunity, index) => (
                <OpportunityCard
                  key={`${opportunity.id ?? opportunity.url}-${index}`}
                  opportunity={opportunity}
                  onChatClick={handleChatOpen}
                  onSave={handleSave}
                  isSaved={savedUrls.has(opportunity.url)}
                />
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Contextual Chat Drawer */}
      <ChatDrawer
        isOpen={!!selectedOpportunity}
        opportunity={selectedOpportunity}
        onClose={handleChatClose}
      />
    </div>
  );
}
