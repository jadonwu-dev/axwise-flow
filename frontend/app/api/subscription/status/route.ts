import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

async function getToken(): Promise<string | null> {
  try {
    // Get the authentication context from Clerk
    const { userId, getToken } = await auth();

    if (!userId) {
      console.log('No authenticated user found');
      return null;
    }

    // Get the JWT token from Clerk
    const token = await getToken();

    if (!token) {
      console.log('No JWT token available from Clerk');
      return null;
    }

    return token;
  } catch (error) {
    console.error('Error getting Clerk token:', error);
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log('Subscription Status API route called');

    // Get the auth token
    const token = await getToken();

    if (!token) {
      console.log('Subscription Status API: No authentication token available');
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    console.log('Subscription Status API: Using Clerk JWT token');
    console.log('Proxying to backend:', `${backendUrl}/api/subscription/status`);

    // Forward the request to the Python backend
    const response = await fetch(`${backendUrl}/api/subscription/status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

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
