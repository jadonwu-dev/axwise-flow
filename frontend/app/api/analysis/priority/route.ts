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
    console.log('Priority Insights API route called');
    
    // Get the auth token
    const token = await getToken();
    
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    console.log('Priority Insights API: Using development token (development mode only)');
    console.log('Proxying to backend:', `${backendUrl}/api/analysis/priority${queryString ? `?${queryString}` : ''}`);
    
    // Forward the request to the Python backend
    const response = await fetch(`${backendUrl}/api/analysis/priority${queryString ? `?${queryString}` : ''}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Priority Insights API: Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Priority Insights API: Backend response successful');
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Priority Insights API: Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
