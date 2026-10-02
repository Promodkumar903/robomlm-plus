import React, { useMemo, useState } from "react";

import AppShell from "../src/components/AppShell";
import PageHeader from "../src/components/PageHeader";
import StatusBadge from "../src/components/StatusBadge";

import "./memory.css";

type MemoryScope =
  | "USER"
  | "BOT"
  | "TRADE"
  | "DECISION"
  | "INTELLIGENCE"
  | "OPPORTUNITY"
  | "EVIDENCE"
  | "LEARNING"
  | "SEARCH";

export default function MemoryPage() {
  const [scope, setScope] =
    useState<MemoryScope>("BOT");

  const [searchText, setSearchText] =
    useState("");

  const memoryScopes = useMemo(
    () => [
      "USER",
      "BOT",
      "TRADE",
      "DECISION",
      "INTELLIGENCE",
      "OPPORTUNITY",
      "EVIDENCE",
      "LEARNING",
      "SEARCH"
    ],
    []
  );

  return (
    <AppShell>
      <div className="memory-page">

        <PageHeader
          title="Memory"
          subtitle="ROBOMLM Intelligence Memory Center"
        />

        <div className="memory-topbar">

          <div className="memory-search">

            <input
              type="text"
              placeholder="Search memory..."
              value={searchText}
              onChange={(e) =>
                setSearchText(e.target.value)
              }
            />

          </div>

          <StatusBadge
            status={scope}
          />

        </div>

        <div className="memory-scope-grid">

          {memoryScopes.map((item) => (
            <button
              key={item}
              className={
                scope === item
                  ? "scope-btn active"
                  : "scope-btn"
              }
              onClick={() =>
                setScope(item as MemoryScope)
              }
            >
              {item}
            </button>
          ))}

        </div>

        <section className="memory-section">

          <h2>Memory Sources</h2>

          <div className="memory-card-grid">

            <div className="memory-card">
              AUTOROBOMLM
            </div>

            <div className="memory-card">
              AUTOROBOMLM+
            </div>

            <div className="memory-card">
              Buyer
            </div>

            <div className="memory-card">
              HTF Trading
            </div>

            <div className="memory-card">
              Scalper Trading
            </div>

            <div className="memory-card">
              Research
            </div>

          </div>

        </section>

        <section className="memory-section">

          <h2>Memory Timeline</h2>

          <div className="timeline-placeholder">

            Backend Memory Timeline Feed

          </div>

        </section>

        <section className="memory-section">

          <h2>Memory Viewer</h2>

          <div className="viewer-placeholder">

            Selected Memory Record

          </div>

        </section>

        <section className="memory-section">

          <h2>Evidence Links</h2>

          <div className="viewer-placeholder">

            Evidence / References /
            Opportunity Links

          </div>

        </section>

        <section className="memory-section">

          <h2>Decision Memory</h2>

          <div className="viewer-placeholder">

            Historical Decisions

          </div>

        </section>

        <section className="memory-section">

          <h2>Learning Memory</h2>

          <div className="viewer-placeholder">

            Learning Records

          </div>

        </section>

        <section className="memory-section">

          <h2>Search Memory</h2>

          <div className="viewer-placeholder">

            Search History Feed

          </div>

        </section>

      </div>
    </AppShell>
  );
}