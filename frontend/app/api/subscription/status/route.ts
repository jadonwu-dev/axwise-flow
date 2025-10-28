import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

async function getToken(): Promise<string> {
  // OSS mode: always use development token
  const token = process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN || 'DEV_TOKEN_REDACTED';
  console.log('Subscription Status API: Using development token');
  return token;
}

export async function GET(request: NextRequest) {
  try {
    console.log('Subscription Status API route called');

    // Get the auth token
    const token = await getToken();

    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    console.log('Subscription Status API: Using development token');
    console.log('Proxying to backend:', `${backendUrl}/api/subscription/status`);

    // Forward the request to the Python backend
    const response = await fetch(`${backendUrl}/api/subscription/status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    // OSS fallback: if backend route is not present, return a default "free" plan
    if (response.status === 404) {
      console.warn('Subscription Status API: Backend route not found - returning OSS default');
      return NextResponse.json({ tier: 'free', status: 'inactive' });
    }

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Subscription Status API: Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Subscription Status API: Backend response successful');

    return NextResponse.json(data);
  } catch (error) {
    console.error('Subscription Status API: Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
