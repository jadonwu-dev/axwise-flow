import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

/**
 * Analyze API route - proxies to Python backend
 */
export async function POST(request: NextRequest) {
  try {
    // Check environment
    const isProduction = process.env.NODE_ENV === 'production';
    const enableClerkValidation = process.env.NEXT_PUBLIC_ENABLE_CLERK_...=***REMOVED*** 'true';

    console.log('🔄 [ANALYZE] Environment check:', {
      isProduction,
      enableClerkValidation,
      envVar: process.env.NEXT_PUBLIC_ENABLE_CLERK_VALIDATION,
      nodeEnv: process.env.NODE_ENV
    });

    let userId: string | null = null;
    let token: string | null = null;

    if (isProduction || enableClerkValidation) {
      // Get authentication from Clerk
      const authResult = await auth();
      userId = authResult.userId;

      // Try to get a fresh token with retry logic
      try {
        token = await authResult.getToken({ skipCache: true });

        // If token is still null, try one more time
        if (!token) {
          console.warn('🔄 [ANALYZE] First token attempt failed, retrying...');
          await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
          token = await authResult.getToken({ skipCache: true });
        }
      } catch (tokenError) {
        console.error('🔄 [ANALYZE] Token retrieval error:', tokenError);
      }

      if (!userId) {
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }

      if (!token) {
        console.error('🔄 [ANALYZE] No auth token available after retry');
        return NextResponse.json(
          { error: 'Authentication token not available' },
          { status: 401 }
        );
      }

      console.log('🔄 [ANALYZE] Using Clerk authentication with fresh token');
      console.log('🔄 [ANALYZE] Token format check:', {
        tokenLength: token?.length || 0,
        tokenParts: token?.split('.').length || 0,
        tokenStart: token?.substring(0, 50) || 'null',
        tokenType: typeof token
      });
    } else {
      // Development mode: use development user
      userId = 'testuser123';
      token = 'DEV_TOKEN_REDACTED';
      console.log('🔄 [ANALYZE] Using development mode authentication');
    }

    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Get the request body
    const body = await request.json();

    // Forward the request to the Python backend with retry logic for auth failures
    let response = await fetch(`${backendUrl}/api/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    // If we get a 401, try to refresh the token and retry once
    if (response.status === 401 && (isProduction || enableClerkValidation)) {
      console.warn('🔄 [ANALYZE] Got 401, attempting token refresh and retry...');

      try {
        const authResult = await auth();
        const freshToken = await authResult.getToken({ skipCache: true });

        if (freshToken) {
          console.log('🔄 [ANALYZE] Retrying with fresh token');
          response = await fetch(`${backendUrl}/api/analyze`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${freshToken}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
          });
        }
      } catch (retryError) {
        console.error('🔄 [ANALYZE] Token refresh retry failed:', retryError);
      }
    }

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Analyze API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
