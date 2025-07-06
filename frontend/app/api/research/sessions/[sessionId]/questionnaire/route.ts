import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params;
    
    console.log(`🔍 [API] Fetching questionnaire for session: ${sessionId}`);
    
    // Forward the request to the Python backend
    const backendUrl = `${API_BASE_URL}/api/research/sessions/${sessionId}/questionnaire`;
    
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ [API] Backend error for session ${sessionId}:`, response.status, errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ [API] Successfully fetched questionnaire for session: ${sessionId}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ [API] Error fetching questionnaire:', error);
    return NextResponse.json(
      { error: 'Failed to fetch questionnaire' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params;
    const body = await request.json();
    
    console.log(`💾 [API] Saving questionnaire for session: ${sessionId}`);
    
    // Forward the request to the Python backend
    const backendUrl = `${API_BASE_URL}/api/research/sessions/${sessionId}/questionnaire`;
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ [API] Backend error saving questionnaire for session ${sessionId}:`, response.status, errorText);
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ [API] Successfully saved questionnaire for session: ${sessionId}`);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ [API] Error saving questionnaire:', error);
    return NextResponse.json(
      { error: 'Failed to save questionnaire' },
      { status: 500 }
    );
  }
}
