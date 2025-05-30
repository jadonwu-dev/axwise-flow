import { NextRequest, NextResponse } from 'next/server';

async function getToken(): Promise<string> {
  // In development mode, use a development token
  if (process.env.NODE_ENV === 'development') {
    return 'DEV_TOKEN_REDACTED';
  }
  
  // In production, this would get the actual Clerk JWT token
  // For now, return development token
  return 'DEV_TOKEN_REDACTED';
}

export async function GET(request: NextRequest) {
  try {
    console.log('Subscription Status API route called');
    
    // Get the auth token
    const token = await getToken();
    
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    console.log('Subscription Status API: Using development token (development mode only)');
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
