import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    console.log('Proxying research sessions request to backend');
    console.log('API_BASE_URL:', API_BASE_URL);
    
    const response = await fetch(`${API_BASE_URL}/api/research/sessions`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend responded with ${response.status}: ${response.statusText}`, errorText);
      
      // If the backend endpoint doesn't exist, return empty array for now
      if (response.status === 404) {
        console.log('Backend sessions endpoint not found, returning empty array');
        return NextResponse.json([], {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
        });
      }
      
      return NextResponse.json(
        { error: 'Failed to fetch research sessions', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Successfully fetched research sessions:', Array.isArray(data) ? data.length : 'non-array response');
    
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Error fetching research sessions:', error);
    
    // For now, return mock data so the page works
    const mockSessions = [
      {
        id: 'session-1',
        title: 'API service for legacy source systems',
        created_at: new Date().toISOString(),
        question_count: 34,
        stakeholder_count: 5,
        has_questionnaire: true,
        questionnaire_exported: false,
        message_count: 12,
        last_message_at: new Date().toISOString()
      },
      {
        id: 'session-2', 
        title: 'Mobile app user onboarding research',
        created_at: new Date(Date.now() - 86400000).toISOString(), // Yesterday
        question_count: 28,
        stakeholder_count: 3,
        has_questionnaire: true,
        questionnaire_exported: true,
        message_count: 8,
        last_message_at: new Date(Date.now() - 86400000).toISOString()
      }
    ];
    
    console.log('Returning mock data due to error:', error instanceof Error ? error.message : 'Unknown error');
    
    return NextResponse.json(mockSessions, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS', 
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }
}

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
