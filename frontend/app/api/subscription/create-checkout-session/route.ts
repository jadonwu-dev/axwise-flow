import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

async function getToken(): Promise<string> {
  // OSS mode: return development token
  return process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN || 'DEV_TOKEN_REDACTED';
}

export async function POST(request: NextRequest) {
  try {
    console.log('Create Checkout Session API route called');

    // Get the auth token
    const token = await getToken();

    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Get request body
    const body = await request.json();

    console.log('Create Checkout Session API: Using authentication token');
    console.log('Proxying to backend:', `${backendUrl}/api/subscription/create-checkout-session`);

    // Forward the request to the Python backend
    const response = await fetch(`${backendUrl}/api/subscription/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Create Checkout Session API: Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Create Checkout Session API: Backend response successful');

    return NextResponse.json(data);
  } catch (error) {
    console.error('Create Checkout Session API: Error:', error);

    // Handle authentication errors specifically
    if (error instanceof Error && error.message.includes('Authentication')) {
      return NextResponse.json(
        { error: 'Authentication required. Please sign in and try again.' },
        { status: 401 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
