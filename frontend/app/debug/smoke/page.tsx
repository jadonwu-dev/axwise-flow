"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SignedIn, SignedOut, SignInButton } from "@clerk/nextjs";

type Check = {
  name: string;
  status: "PENDING" | "PASS" | "FAIL";
  info?: string;
};

export default function SmokeTestPage() {
  const searchParams = useSearchParams();
  const targetSessionId = useMemo(() => searchParams.get("session") || "", [searchParams]);

  const [checks, setChecks] = useState<Check[]>([
    { name: "GET /api/research/sessions (list)", status: "PENDING" },
    { name: "GET /api/research/sessions/[id] (detail)", status: "PENDING" },
    { name: "GET /api/research/sessions/[id]/questionnaire", status: "PENDING" },
  ]);

  useEffect(() => {
    let mounted = true;

    async function run() {
      const update = (i: number, data: Partial<Check>) =>
        setChecks((prev) => {
          const next = [...prev];
          next[i] = { ...next[i], ...data } as Check;
          return next;
        });

      // 1) Sessions list via proxy (should be 200 when signed in)
      try {
        const r = await fetch(`/api/research/sessions?limit=5`, { cache: "no-store" });
        if (!mounted) return;
        if (r.ok) {
          const arr = await r.json();
          update(0, { status: "PASS", info: `count=${Array.isArray(arr) ? arr.length : "?"}` });
        } else {
          const t = await r.text();
          update(0, { status: "FAIL", info: `${r.status} ${t?.slice(0, 160)}` });
        }
      } catch (e: any) {
        update(0, { status: "FAIL", info: e?.message || String(e) });
      }

      // If no target session specified, we end here
      if (!targetSessionId) {
        update(1, { status: "PASS", info: "skipped (no session param)" });
        update(2, { status: "PASS", info: "skipped (no session param)" });
        return;
      }

      // 2) Session detail
      try {
        const r = await fetch(`/api/research/sessions/${encodeURIComponent(targetSessionId)}`, { cache: "no-store" });
        if (!mounted) return;
        if (r.ok) {
          const data = await r.json();
          update(1, { status: "PASS", info: `questions_generated=${String(!!data?.questions_generated)}` });
        } else {
          const t = await r.text();
          update(1, { status: "FAIL", info: `${r.status} ${t?.slice(0, 160)}` });
        }
      } catch (e: any) {
        update(1, { status: "FAIL", info: e?.message || String(e) });
      }

      // 3) Questionnaire
      try {
        const r = await fetch(`/api/research/sessions/${encodeURIComponent(targetSessionId)}/questionnaire`, { cache: "no-store" });
        if (!mounted) return;
        if (r.ok) {
          const data = await r.json();
          const hasQ = !!data?.questionnaire;
          update(2, { status: hasQ ? "PASS" : "FAIL", info: hasQ ? "questionnaire present" : "missing questionnaire" });
        } else {
          const t = await r.text();
          update(2, { status: "FAIL", info: `${r.status} ${t?.slice(0, 160)}` });
        }
      } catch (e: any) {
        update(2, { status: "FAIL", info: e?.message || String(e) });
      }
    }

    run();
    return () => {
      mounted = false;
    };
  }, [targetSessionId]);

  return (
    <div style={{ maxWidth: 720, margin: "32px auto", padding: 16 }}>
      <h1>Smoke Test: Research Sessions Proxy & Questionnaire</h1>
      <p>Use query param <code>?session=&lt;session_id&gt;</code> to test a specific session (e.g., local_…)</p>

      <SignedOut>
        <div style={{ margin: "16px 0", padding: 12, border: "1px solid #f0c36d", background: "#fff8e1" }}>
          <strong>Not signed in.</strong> The proxy requires an authenticated Clerk session.
          <div style={{ marginTop: 8 }}>
            <SignInButton mode="modal">
              <button style={{ padding: "8px 12px", border: "1px solid #ccc", borderRadius: 6 }}>Sign in</button>
            </SignInButton>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div style={{ marginTop: 16 }}>
          {checks.map((c, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: 8, borderBottom: "1px solid #eee" }}>
              <span style={{ width: 14 }}>{c.status === "PASS" ? "✅" : c.status === "FAIL" ? "❌" : "⏳"}</span>
              <div>
                <div><strong>{c.name}</strong></div>
                {c.info ? <div style={{ color: "#666" }}>{c.info}</div> : null}
              </div>
            </div>
          ))}
        </div>
      </SignedIn>
    </div>
  );
}

