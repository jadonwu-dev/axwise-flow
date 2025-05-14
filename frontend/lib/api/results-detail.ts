/**
 * Detailed results retrieval methods for the API client
 */

import { apiCore } from './core';
import { DetailedAnalysisResult, SentimentOverview } from './types';

/**
 * Calculate sentiment overview from sentiment data
 */
function calculateSentimentOverview(scores: number[]): SentimentOverview {
  if (!scores || scores.length === 0) {
    return { positive: 0.33, neutral: 0.34, negative: 0.33 };
  }

  const counts = scores.reduce((acc: { positive: number, neutral: number, negative: number }, score: number) => {
    if (score >= 0.2) acc.positive++;
    else if (score <= -0.2) acc.negative++;
    else acc.neutral++;
    return acc;
  }, { positive: 0, neutral: 0, negative: 0 });

  const total = scores.length;
  return {
    positive: counts.positive / total,
    neutral: counts.neutral / total,
    negative: counts.negative / total
  };
}

/**
 * Get analysis result by ID
 * 
 * @param id The ID of the analysis to retrieve
 * @returns A promise that resolves to the detailed analysis result
 */
export async function getAnalysisById(id: string): Promise<DetailedAnalysisResult> {
  try {
    const response = await apiCore.getClient().get(`/api/results/${id}`, {
      timeout: 120000 // 120 seconds timeout for fetching potentially large results
    });
    console.log('API response data (raw):', JSON.stringify(response.data, null, 2));

    if (!response.data.results) {
      throw new Error('Invalid API response: missing results');
    }

    const results = response.data.results;

    // Add specific logging for sentimentStatements
    console.log('SentimentStatements from API (direct):',
               results.sentimentStatements ?
               JSON.stringify(results.sentimentStatements, null, 2) :
               'MISSING');

    // Check if results.sentimentStatements exists directly
    console.log('Raw sentimentStatements from API:',
               results.sentimentStatements ?
               JSON.stringify(results.sentimentStatements, null, 2) :
               'MISSING');

    // Make sure sentimentStatements are properly extracted and preserved
    if (results.sentimentStatements) {
      console.log("Found sentiment statements in API response:", JSON.stringify(results.sentimentStatements, null, 2));
    } else {
      console.warn("No sentiment statements found in API response");
    }

    // Log sentiment data structure to help with debugging
    if (Array.isArray(results.sentiment)) {
      console.log(`Sentiment array found with ${results.sentiment.length} items`);
      if (results.sentiment.length > 0) {
        console.log("Sample sentiment item:", JSON.stringify(results.sentiment[0], null, 2));
      }
    } else {
      console.warn("Sentiment is not an array:", typeof results.sentiment);
      // Handle case where sentiment is an object instead of an array
      if (results.sentiment && typeof results.sentiment === 'object') {
        // Convert object structure to expected format if needed
        const sentimentData = results.sentiment;

        // Initialize sentimentStatements if not present or malformed
        if (!results.sentimentStatements ||
            typeof results.sentimentStatements !== 'object' ||
            !results.sentimentStatements.positive ||
            !results.sentimentStatements.neutral ||
            !results.sentimentStatements.negative) {

          results.sentimentStatements = {
            positive: [],
            neutral: [],
            negative: []
          };

          // If the sentiment object has statement data in a different format, extract it
          if (sentimentData.statements) {
            // Process statements if available
            const statements = sentimentData.statements || {};

            if (Array.isArray(statements.positive)) {
              results.sentimentStatements.positive = statements.positive;
            }
            if (Array.isArray(statements.neutral)) {
              results.sentimentStatements.neutral = statements.neutral;
            }
            if (Array.isArray(statements.negative)) {
              results.sentimentStatements.negative = statements.negative;
            }
          }
        }
      }
    }

    // Ensure we have the required fields
    if (!Array.isArray(results.sentiment)) {
      // Convert sentiment object to array if necessary
      if (results.sentiment && typeof results.sentiment === 'object') {
        // Keep object format but ensure it has the necessary properties
        // Don't override if it's already properly structured
      } else {
        results.sentiment = [];
      }
    }

    // Ensure themes have statements if they exist as supporting_quotes or examples
    if (Array.isArray(results.themes)) {
      results.themes = results.themes.map((theme: {
        statements?: string[];
        supporting_quotes?: string[];
        examples?: string[];
        quotes?: string[];
        sentiment_distribution?: { positive: number; neutral: number; negative: number };
        [key: string]: any;
      }) => {
        // Initialize statements array if it doesn't exist
        if (!theme.statements || !Array.isArray(theme.statements)) {
          theme.statements = [];
        }

        // Check for supporting_quotes field (API might return this format)
        if (theme.supporting_quotes && Array.isArray(theme.supporting_quotes) && theme.supporting_quotes.length > 0) {
          theme.statements = [...theme.statements, ...theme.supporting_quotes];
        }

        // examples field has been removed

        // Check for quotes field (another possible format)
        if (theme.quotes && Array.isArray(theme.quotes) && theme.quotes.length > 0 && theme.statements.length === 0) {
          theme.statements = [...theme.statements, ...theme.quotes];
        }

        // Ensure sentiment_distribution exists
        if (!theme.sentiment_distribution) {
          // Calculate a default sentiment distribution based on the theme's sentiment score
          const sentimentScore = theme.sentiment || 0;
          if (sentimentScore >= 0.3) {
            theme.sentiment_distribution = { positive: 0.7, neutral: 0.2, negative: 0.1 };
          } else if (sentimentScore <= -0.3) {
            theme.sentiment_distribution = { positive: 0.1, neutral: 0.2, negative: 0.7 };
          } else {
            theme.sentiment_distribution = { positive: 0.2, neutral: 0.6, negative: 0.2 };
          }
          console.log(`Added default sentiment distribution for theme: ${theme.name}`);
        }

        return theme;
      });
    }

    // Calculate sentimentOverview if missing
    if (!results.sentimentOverview) {
      const scores = results.sentiment
        .map((s: { score: number }) => s.score)
        .filter((score: number) => typeof score === 'number');
      results.sentimentOverview = calculateSentimentOverview(scores);
    }

    // Validate sentimentOverview
    if (!results.sentimentOverview ||
        typeof results.sentimentOverview.positive !== 'number' ||
        typeof results.sentimentOverview.neutral !== 'number' ||
        typeof results.sentimentOverview.negative !== 'number') {
      results.sentimentOverview = {
        positive: 0.33,
        neutral: 0.34,
        negative: 0.33
      };
    }

    // IMPORTANT: This is where we need to handle the raw sentiment data vs. sentimentStatements
    // Check if we need to initialize sentimentStatements structure
    if (!results.sentimentStatements ||
        !results.sentimentStatements.positive ||
        !results.sentimentStatements.neutral ||
        !results.sentimentStatements.negative) {

      console.log("Initializing sentimentStatements structure");

      // Initialize with empty arrays if needed
      if (!results.sentimentStatements) {
      results.sentimentStatements = {
        positive: [],
        neutral: [],
        negative: []
      };
      }

      // Ensure all arrays exist
      if (!Array.isArray(results.sentimentStatements.positive)) results.sentimentStatements.positive = [];
      if (!Array.isArray(results.sentimentStatements.neutral)) results.sentimentStatements.neutral = [];
      if (!Array.isArray(results.sentimentStatements.negative)) results.sentimentStatements.negative = [];
    }

    // Check for raw sentiment data to combine with sentimentStatements
    // This handles the case where sentiment contains the raw arrays directly
    if (results.sentiment && typeof results.sentiment === 'object') {
      const sentimentObj = results.sentiment;

      // Check if sentiment has direct positive/neutral/negative arrays
      if (Array.isArray(sentimentObj.positive)) {
        console.log(`Found ${sentimentObj.positive.length} positive statements in sentiment object`);

        // Only merge if there are actually statements
        if (sentimentObj.positive.length > 0) {
          // Merge unique statements from sentiment.positive into sentimentStatements.positive
          sentimentObj.positive.forEach((statement: string) => {
            if (!results.sentimentStatements.positive.includes(statement)) {
              results.sentimentStatements.positive.push(statement);
            }
          });
        }
      }

      if (Array.isArray(sentimentObj.neutral)) {
        console.log(`Found ${sentimentObj.neutral.length} neutral statements in sentiment object`);

        // Only merge if there are actually statements
        if (sentimentObj.neutral.length > 0) {
          // Merge unique statements from sentiment.neutral into sentimentStatements.neutral
          sentimentObj.neutral.forEach((statement: string) => {
            if (!results.sentimentStatements.neutral.includes(statement)) {
              results.sentimentStatements.neutral.push(statement);
            }
          });
        }
      }

      if (Array.isArray(sentimentObj.negative)) {
        console.log(`Found ${sentimentObj.negative.length} negative statements in sentiment object`);

        // Only merge if there are actually statements
        if (sentimentObj.negative.length > 0) {
          // Merge unique statements from sentiment.negative into sentimentStatements.negative
          sentimentObj.negative.forEach((statement: string) => {
            if (!results.sentimentStatements.negative.includes(statement)) {
              results.sentimentStatements.negative.push(statement);
            }
          });
        }
      }

      // Check for raw supporting_statements
      if (sentimentObj.supporting_statements && typeof sentimentObj.supporting_statements === 'object') {
        const supportingStmts = sentimentObj.supporting_statements;

        if (Array.isArray(supportingStmts.positive) && supportingStmts.positive.length > 0) {
          // Merge unique statements from supporting_statements.positive
          supportingStmts.positive.forEach((statement: string) => {
            if (!results.sentimentStatements.positive.includes(statement)) {
              results.sentimentStatements.positive.push(statement);
            }
          });
        }

        if (Array.isArray(supportingStmts.neutral) && supportingStmts.neutral.length > 0) {
          // Merge unique statements from supporting_statements.neutral
          supportingStmts.neutral.forEach((statement: string) => {
            if (!results.sentimentStatements.neutral.includes(statement)) {
              results.sentimentStatements.neutral.push(statement);
            }
          });
        }

        if (Array.isArray(supportingStmts.negative) && supportingStmts.negative.length > 0) {
          // Merge unique statements from supporting_statements.negative
          supportingStmts.negative.forEach((statement: string) => {
            if (!results.sentimentStatements.negative.includes(statement)) {
              results.sentimentStatements.negative.push(statement);
            }
          });
        }
      }

      // Log combined results
      console.log('Combined sentiment statements:', {
          positive: results.sentimentStatements.positive.length,
          neutral: results.sentimentStatements.neutral.length,
          negative: results.sentimentStatements.negative.length
      });
    } else {
      if (process.env.NODE_ENV === 'development') {
        console.log('Using provided sentimentStatements without merging:', {
          positive: results.sentimentStatements.positive?.length || 0,
          neutral: results.sentimentStatements.neutral?.length || 0,
          negative: results.sentimentStatements.negative?.length || 0
        });
      }
    }

    // Removed synthetic statement generation to only show actual statements from interviews

    // Ensure other required fields
    if (!Array.isArray(results.themes)) results.themes = [];
    if (!Array.isArray(results.patterns)) results.patterns = [];
    if (!results.id) results.id = id;
    if (!results.status) results.status = 'completed';
    if (!results.createdAt) results.createdAt = new Date().toISOString();
    if (!results.fileName) results.fileName = 'Unknown File';

    // IMPORTANT: Extract sentimentStatements to top-level of returned object
    // This ensures it's available directly on the analysis object
    const finalResult = {
      ...results,
      // Extract sentimentStatements to top level if available
      sentimentStatements: results.sentimentStatements ||
                          (results.sentiment && results.sentiment.sentimentStatements) ||
                          {positive: [], neutral: [], negative: []}
    };

    console.log('Processed analysis data:', finalResult);
    return finalResult;

  } catch (error: any) {
    console.error('API error:', error);
    throw new Error(`Failed to fetch analysis: ${error.message}`);
  }
}
