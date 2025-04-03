'use server';

/**
 * Server Actions for Upload and Analysis
 *
 * These actions replace Zustand state management by handling
 * form submissions server-side.
 */

import { apiClient } from '@/lib/apiClient';
import type { DetailedAnalysisResult, UploadResponse, AnalysisResponse } from '@/types/api';
 // Rem-addd UploadResponse, AnalysisResponse
import { cookies } from 'next/headers';

/**
 * Upload Action
 * Handles file uploads using server action
 */
export async function uploadAction(formData: FormData): Promise<{ success: true; uploadResponse: UploadResponse } | { success: false; error: string }> {
  try {
    const file = formData.get('file') as File;
    const isTextFile = formData.get('isTextFile') === 'true';

    if (!file) {
      return {
        success: false,
        error: 'No file provided'
      };
    }

    // Get auth token from cookie
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;

    if (!authToken) {
      return {
        success: false,
        error: 'Not authenticated'
      };
    }

    // Set the token on the API client
    apiClient.setAuthToken(authToken);

    const uploadResponse = await apiClient.uploadData(file, isTextFile);

    return {
      success: true,
      uploadResponse
    };
  } catch (error) {
    console.error('Upload error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown upload error'
    };
  }
}

/**
 * Analyze Action
 * Handles starting analysis using server action
 */
export async function analyzeAction(
  dataId: number,
  isTextFile: boolean,
  llmProvider: 'openai' | 'gemini' = 'gemini'
): Promise<{ success: true; analysisResponse: AnalysisResponse } | { success: false; error: string }> {
  try {
    // Get auth token from cookie
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;

    if (!authToken) {
      return {
        success: false,
        error: 'Not authenticated'
      };
    }

    // Set the token on the API client
    apiClient.setAuthToken(authToken);

    const analysisResponse = await apiClient.analyzeData(dataId, llmProvider, undefined, isTextFile);

    return {
      success: true,
      analysisResponse
    };
  } catch (error) {
    console.error('Analysis error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown analysis error'
    };
  }
}

/**
 * Redirect after successful analysis
 * Helper function to generate URL for redirection
 */
export async function getRedirectUrl(analysisId: string): Promise<string> {
  // --- START LOGGING ---
  console.log(`[Server Action - getRedirectUrl] Called with analysisId: ${analysisId}`);
  if (!analysisId) {
    console.error("[Server Action - getRedirectUrl] Received null or empty analysisId!");
    // Consider throwing an error or returning a default URL
    throw new Error("Cannot generate redirect URL without a valid analysis ID.");
  }
  // --- END LOGGING ---

  // Add timestamp to prevent caching issues
  const timestamp = Date.now();
  const url = `/unified-dashboard/visualize?analysisId=${analysisId}&visualizationTab=themes&timestamp=${timestamp}`;
  console.log(`[Server Action - getRedirectUrl] Generated URL: ${url}`);
  return url;
}

/**
 * Server-side analysis data fetcher
 * Fetches analysis data using server component
 */
export async function getServerSideAnalysis(analysisId: string): Promise<DetailedAnalysisResult | null> {
  if (!analysisId) {
      console.log("[getServerSideAnalysis] Received null or empty analysisId."); // DEBUG LOG
      return null;
  }
  console.log(`[getServerSideAnalysis] Received analysisId: ${analysisId}`); // DEBUG LOG

  try {
    // Get auth token from cookie
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;

    if (!authToken) {
      console.error('[getServerSideAnalysis] No auth token available for server fetch');
      return null;
    }

    // Set the token on the API client
    apiClient.setAuthToken(authToken);

    // Fetch analysis data
    console.log(`[getServerSideAnalysis] Calling apiClient.getAnalysisById with ID: ${analysisId}`); // DEBUG LOG
    const analysisData = await apiClient.getAnalysisById(analysisId);
    console.log(`[getServerSideAnalysis] Fetched data for ${analysisId}:`, analysisData ? `Status: ${analysisData.status}, Themes: ${analysisData.themes?.length}` : 'null'); // DEBUG LOG
    return analysisData;
  } catch (error) {
    console.error(`[getServerSideAnalysis] Error fetching analysis data server-side for ID ${analysisId}:`, error); // DEBUG LOG
    return null;
  }
}

/**
 * Get the latest completed analysis for the current user
 * This is used to display the most recent analysis on the dashboard
 */
export async function getLatestCompletedAnalysis(): Promise<DetailedAnalysisResult | null> {
  try {
    // Get auth token from cookie
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;

    if (!authToken) {
      console.error('[getLatestCompletedAnalysis] No auth token available');
      return null;
    }

    // Set the token on the API client
    apiClient.setAuthToken(authToken);

    try {
      // First attempt: Try to get from history API
      // Fetch the first page with only one result, sorted by date descending
      const response = await apiClient.getAnalysisHistory(0, 1);

      // Check if we have any completed analyses
      if (response.items && response.items.length > 0 && response.items[0].status === 'completed') {
        console.log(`[getLatestCompletedAnalysis] Found latest analysis from history: ${response.items[0].id}`);
        return response.items[0];
      }
    } catch (historyError) {
      console.error('[getLatestCompletedAnalysis] Error fetching analysis history:', historyError);
      // Continue to fallback method if history API fails
    }

    // Fallback: If history API fails or returns no results, try to get the analysis ID from URL or localStorage
    // This is a temporary solution until the history API is fixed
    try {
      // Check if we have a recent analysis ID in localStorage
      if (typeof window !== 'undefined') {
        const recentAnalysisId = localStorage.getItem('recentAnalysisId');
        if (recentAnalysisId) {
          console.log(`[getLatestCompletedAnalysis] Trying to fetch recent analysis from localStorage: ${recentAnalysisId}`);
          const analysisData = await apiClient.getAnalysisById(recentAnalysisId);
          if (analysisData && analysisData.status === 'completed') {
            console.log(`[getLatestCompletedAnalysis] Successfully fetched analysis: ${recentAnalysisId}`);
            return analysisData;
          }
        }
      }
    } catch (fallbackError) {
      console.error('[getLatestCompletedAnalysis] Fallback error:', fallbackError);
    }

    console.log('[getLatestCompletedAnalysis] No completed analyses found');
    return null;
  } catch (error) {
    console.error('[getLatestCompletedAnalysis] Error:', error);
    return null;
  }
}

/**
 * Fetch analysis history from the database
 */
export async function fetchAnalysisHistory(page: number = 1, pageSize: number = 10) {
  try {
    // Get auth token from cookie
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;

    if (!authToken) {
      return {
        success: false,
        error: 'Not authenticated',
        items: [],
        totalItems: 0,
        currentPage: page
      };
    }

    // Set the token on the API client
    apiClient.setAuthToken(authToken);

    // Set up pagination parameters
    const skip = (page - 1) * pageSize;

    // Call API to fetch history data
    // NOTE: Assumes apiClient.getAnalysisHistory exists and takes (skip, limit)
    // Also assumes the response format matches { items: [], totalCount: number }
    const response = await apiClient.getAnalysisHistory(skip, pageSize);

    return {
      success: true,
      items: response.items || [],
      totalItems: response.totalCount || 0,
      currentPage: page
    };
  } catch (error) {
    console.error('Error fetching analysis history:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error fetching history',
      items: [],
      totalItems: 0,
      currentPage: page
    };
  }
}
