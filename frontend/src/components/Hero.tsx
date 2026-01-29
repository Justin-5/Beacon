"use client";

import React, { useEffect, useRef, useState, FormEvent, useId } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { useRouter } from "next/navigation";

const Hero: React.FC = () => {
  const id = useId();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const containerRef = useRef<HTMLDivElement | null>(null);

  const rotation = useMotionValue(0);
  const smoothRotation = useSpring(rotation, {
    stiffness: 120,
    damping: 20,
    mass: 0.6,
  });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height * 0.25; // approximate lighthouse top

      const dx = event.clientX - centerX;
      const dy = event.clientY - centerY;

      const angleDeg = (Math.atan2(dy, dx) * 180) / Math.PI;
      rotation.set(angleDeg);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [rotation]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
          "radial-gradient(circle at top, #1f3b73 0%, #020617 45%, #020617 100%)",
        color: "#f9fafb",
        padding: "3rem 1.5rem",
        boxSizing: "border-box",
      }}
    >
      <div
        ref={containerRef}
        style={{
          position: "relative",
          maxWidth: "960px",
          width: "100%",
          textAlign: "center",
        }}
      >
        {/* Decorative stars */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.4) 0, transparent 50%)," +
              "radial-gradient(1px 1px at 80% 30%, rgba(255,255,255,0.3) 0, transparent 50%)," +
              "radial-gradient(1px 1px at 30% 80%, rgba(255,255,255,0.25) 0, transparent 50%)",
            opacity: 0.5,
            pointerEvents: "none",
          }}
        />

        {/* Lighthouse & beam */}
        <div
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "3rem",
          }}
        >
          {/* Rotating light beam */}
          <motion.div
            style={{
              position: "absolute",
              top: "10%",
              left: "50%",
              transform: "translateX(-50%)",
              transformOrigin: "50% 100%",
              pointerEvents: "none",
              rotate: smoothRotation,
            }}
          >
            <svg
              width="320"
              height="260"
              viewBox="0 0 320 260"
              style={{ overflow: "visible" }}
            >
              <defs>
                <linearGradient
                  id={`beamGradient-${id}`}
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="0%"
                >
                  <stop offset="0%" stopColor="#facc15" stopOpacity="0.85" />
                  <stop offset="60%" stopColor="#fde68a" stopOpacity="0.55" />
                  <stop offset="100%" stopColor="#fef9c3" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Triangle beam */}
              <polygon
                points="0,260 160,0 320,260"
                fill={`url(#beamGradient-${id})`}
              />
            </svg>
          </motion.div>

          {/* Lighthouse SVG */}
          <svg
            width="220"
            height="320"
            viewBox="0 0 220 320"
            aria-hidden="true"
            style={{ position: "relative", zIndex: 1 }}
          >
            <defs>
              <linearGradient
                id={`lighthouseBody-${id}`}
                x1="0%"
                y1="0%"
                x2="0%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#e5e7eb" />
                <stop offset="100%" stopColor="#9ca3af" />
              </linearGradient>
              <linearGradient
                id={`lighthouseBase-${id}`}
                x1="0%"
                y1="0%"
                x2="0%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#111827" />
                <stop offset="100%" stopColor="#020617" />
              </linearGradient>
            </defs>

            {/* Rock base */}
            <path
              d="M10 300 C 40 260, 180 260, 210 300 L 210 320 L 10 320 Z"
              fill={`url(#lighthouseBase-${id})`}
            />

            {/* Tower */}
            <polygon
              points="95,80 125,80 150,290 70,290"
              fill={`url(#lighthouseBody-${id})`}
            />

            {/* Stripes */}
            <rect x="80" y="120" width="60" height="18" fill="#1d4ed8" />
            <rect x="78" y="170" width="64" height="18" fill="#0f172a" />
            <rect x="76" y="220" width="68" height="18" fill="#1d4ed8" />

            {/* Windows */}
            <rect
              x="103"
              y="140"
              width="14"
              height="18"
              rx="3"
              fill="#0f172a"
            />
            <rect
              x="103"
              y="190"
              width="14"
              height="18"
              rx="3"
              fill="#0f172a"
            />
            <rect
              x="103"
              y="240"
              width="14"
              height="18"
              rx="3"
              fill="#0f172a"
            />

            {/* Lantern room */}
            <rect x="88" y="55" width="44" height="28" rx="6" fill="#0f172a" />
            <rect
              x="92"
              y="60"
              width="36"
              height="18"
              rx="4"
              fill="#facc15"
              opacity={0.9}
            />
            {/* Lantern roof */}
            <polygon
              points="110,30 80,55 140,55"
              fill="#020617"
              stroke="#0f172a"
              strokeWidth="2"
            />
            {/* Rail */}
            <rect x="80" y="82" width="60" height="6" rx="3" fill="#020617" />
          </svg>
        </div>

        {/* Text content */}
        <div
          style={{
            position: "relative",
            zIndex: 2,
            maxWidth: "640px",
            margin: "0 auto",
          }}
        >
          <h1
            style={{
              fontSize: "3rem",
              lineHeight: 1.1,
              fontWeight: 800,
              letterSpacing: "-0.04em",
              marginBottom: "0.75rem",
            }}
          >
            Beacon
          </h1>
          <p
            style={{
              fontSize: "1.15rem",
              lineHeight: 1.6,
              color: "rgba(226,232,240,0.9)",
              marginBottom: "2rem",
            }}
          >
            Illuminating the path to service.
          </p>

          {/* Search bar */}
          <form
            onSubmit={handleSubmit}
            style={{
              display: "flex",
              maxWidth: "520px",
              margin: "0 auto",
              backgroundColor: "rgba(15,23,42,0.9)",
              borderRadius: "9999px",
              border: "1px solid rgba(148,163,184,0.5)",
              padding: "0.35rem 0.4rem 0.35rem 1.25rem",
              boxShadow:
                "0 18px 45px rgba(15,23,42,0.85), 0 0 40px rgba(250,204,21,0.2)",
              backdropFilter: "blur(10px)",
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search opportunities near you..."
              aria-label="Search opportunities"
              style={{
                flex: 1,
                border: "none",
                outline: "none",
                background: "transparent",
                color: "#e5e7eb",
                fontSize: "1rem",
                padding: "0.6rem 0.5rem",
              }}
            />
            <button
              type="submit"
              style={{
                borderRadius: "9999px",
                padding: "0.55rem 1.3rem",
                border: "none",
                cursor: "pointer",
                background:
                  "linear-gradient(135deg, #facc15 0%, #f97316 40%, #ea580c 100%)",
                color: "#0f172a",
                fontWeight: 600,
                fontSize: "0.95rem",
                boxShadow: "0 10px 25px rgba(250,204,21,0.25)",
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
                whiteSpace: "nowrap",
              }}
            >
              Search
              <span aria-hidden="true">↗</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Hero;
