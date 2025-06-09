import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

/**
 * History API route - proxies to Python backend with proper authentication
 * - Development: Uses development token when Clerk validation is disabled
 * - Production: Requires Clerk authentication and forwards JWT token
 */
export async function GET(request: NextRequest) {
  try {
    console.log('History API route called');

    // Check environment
    const isProduction = process.env.NODE_ENV === 'production';
    const enableClerkValidation = true; // Force enable Clerk validation for testing

    console.log('History API: Environment check:', {
      isProduction,
      enableClerkValidation,
      envVar: process.env.NEXT_PUBLIC_ENABLE_CLERK_VALIDATION,
      nodeEnv: process.env.NODE_ENV
    });

    let authToken: string;

    if (isProduction || enableClerkValidation) {
      // Production or Clerk validation enabled: require proper authentication
      const { userId, getToken } = await auth();

      if (!userId) {
        console.log('History API: No authenticated user');
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }

      // Get the auth token from Clerk with retry logic
      let token;
      try {
        token = await getToken({ skipCache: true });

        // If token is still null, try one more time
        if (!token) {
          console.warn('History API: First token attempt failed, retrying...');
          await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
          token = await getToken({ skipCache: true });
        }
      } catch (tokenError) {
        console.error('History API: Token retrieval error:', tokenError);
      }

      if (!token) {
        console.log('History API: No auth token available after retry');
        return NextResponse.json(
          { error: 'Authentication token not available' },
          { status: 401 }
        );
      }

      authToken = token;
      console.log('History API: Using Clerk JWT token for authenticated user:', userId);
    } else {
      // Development mode: use development token
      authToken = 'dev_test_token_DEV_TOKEN_REDACTED';
      console.log('History API: Using development token (development mode only)');
    }

    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Get query parameters
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();

    console.log('Proxying to backend:', `${backendUrl}/api/analyses${queryString ? `?${queryString}` : ''}`);

    // Forward the request to the Python backend with appropriate token
    const response = await fetch(`${backendUrl}/api/analyses${queryString ? `?${queryString}` : ''}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', response.status, errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend response successful, returning', data.length, 'analyses');

    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });

  } catch (error) {
    console.error('History API error:', error);
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
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
