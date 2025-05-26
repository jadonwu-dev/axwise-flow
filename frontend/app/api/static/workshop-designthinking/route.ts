import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

/**
 * API route to serve the workshop design thinking HTML file
 * This is a workaround for Firebase App Hosting not serving static files correctly
 */
export async function GET(request: NextRequest) {
  try {
    // Read the HTML file from the public directory
    const filePath = join(process.cwd(), 'public', 'workshop-designthinking', 'index.html');
    const htmlContent = await readFile(filePath, 'utf-8');
    
    // Return the HTML content with proper headers
    return new NextResponse(htmlContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=3600', // Cache for 1 hour
      },
    });
  } catch (error) {
    console.error('Error serving workshop design thinking:', error);
    return new NextResponse('Workshop design thinking page not found', { 
      status: 404,
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  }
}
