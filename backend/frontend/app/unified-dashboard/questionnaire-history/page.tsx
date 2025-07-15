"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

/**
 * Redirect page for the old questionnaire-history route.
 * This page has been consolidated into research-chat-history.
 */
export default function QuestionnaireHistoryRedirect() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check if there's a session parameter for individual questionnaire viewing
    const sessionParam = searchParams.get("session");

    if (sessionParam) {
      // Redirect to individual questionnaire detail page
      router.replace(`/unified-dashboard/questionnaire/${sessionParam}`);
    } else {
      // Redirect to research-chat-history with questionnaires tab
      router.replace(
        "/unified-dashboard/research-chat-history?tab=questionnaires"
      );
    }
  }, [router, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-lg font-semibold mb-2">Redirecting...</h2>
        <p className="text-muted-foreground">
          Questionnaire history has been moved to Research Chat History.
        </p>
      </div>
    </div>
  );
}
