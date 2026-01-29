"use client";

import React, { useEffect, useState } from "react";
import { SignedIn, SignedOut, SignInButton, useUser } from "@clerk/nextjs";
import { Loader2 } from "lucide-react";
import { getSavedRoles } from "@/lib/api";
import { ChatDrawer, type ChatOpportunity } from "@/components/ChatDrawer";
import { OpportunityCard } from "@/components/OpportunityCard";

type SavedOpportunity = ChatOpportunity;

export default function DashboardPage() {
  const { user, isLoaded, isSignedIn } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [opportunities, setOpportunities] = useState<SavedOpportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] =
    useState<SavedOpportunity | null>(null);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn || !user?.id) {
      setIsLoading(false);
      return;
    }

    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    getSavedRoles(user.id)
      .then((roles: SavedOpportunity[]) => {
        if (isCancelled) return;
        const mapped: SavedOpportunity[] = roles.map(
          (role: SavedOpportunity) => ({
            ...role,
          }),
        );
        setOpportunities(mapped);
      })
      .catch((err: any) => {
        if (isCancelled) return;
        setError(err?.message ?? "Failed to load saved opportunities.");
      })
      .finally(() => {
        if (isCancelled) return;
        setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id]);

  const handleChatOpen = (opportunity: SavedOpportunity) => {
    setSelectedOpportunity(opportunity);
  };

  const handleChatClose = () => {
    setSelectedOpportunity(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-50">
      <SignedIn>
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 pb-8 pt-20 sm:px-6 lg:px-8">
          {/* Header */}
          <header className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-teal-400/80">
                Dashboard
              </p>
              <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-slate-50">
                My Saved Opportunities
              </h1>
              <p className="mt-1 text-sm text-slate-400">
                Revisit roles you&apos;ve starred and keep your path to service
                within reach.
              </p>
            </div>
          </header>

          {/* Content */}
          <main className="flex-1">
            {isLoading && (
              <div className="flex h-48 items-center justify-center">
                <div className="flex items-center gap-3 rounded-full border border-slate-800 bg-slate-950/80 px-4 py-2 shadow-[0_18px_45px_rgba(15,23,42,0.9)]">
                  <Loader2 className="h-4 w-4 animate-spin text-teal-400" />
                  <span className="text-sm text-slate-200">
                    Gathering your saved roles…
                  </span>
                </div>
              </div>
            )}

            {!isLoading && error && (
              <div className="mt-8 rounded-2xl border border-red-500/40 bg-red-950/40 px-4 py-3 text-sm text-red-100">
                {error}
              </div>
            )}

            {!isLoading && !error && opportunities.length === 0 && (
              <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-950/70 px-6 py-6 text-sm text-slate-200">
                <p className="font-semibold text-slate-100 mb-1">
                  You haven&apos;t saved any roles yet.
                </p>
                <p>
                  Explore opportunities on the search page and tap the heart
                  icon to save roles that resonate with you.
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
                    isSaved
                  />
                ))}
              </div>
            )}
          </main>
        </div>
      </SignedIn>

      <SignedOut>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-50">
          <div className="max-w-md rounded-2xl border border-slate-800 bg-slate-950/80 px-6 py-8 text-center shadow-[0_18px_45px_rgba(15,23,42,0.9)]">
            <h1 className="text-2xl font-bold mb-2">
              Sign in to view saved roles
            </h1>
            <p className="text-sm text-slate-300">
              Your personal dashboard keeps track of every opportunity you save
              with Beacon. Please sign in to access your list.
            </p>
            <SignInButton mode="modal">
              <button className="mt-4 rounded-lg bg-teal-500 px-4 py-2 text-sm font-medium text-white hover:bg-teal-600">
                Sign In
              </button>
            </SignInButton>
          </div>
        </div>
      </SignedOut>

      {/* Contextual Chat Drawer */}
      <ChatDrawer
        isOpen={!!selectedOpportunity}
        opportunity={selectedOpportunity}
        onClose={handleChatClose}
      />
    </div>
  );
}
