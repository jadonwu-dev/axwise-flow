import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

/**
 * API route to serve the onepager presentation HTML file
 * This is a workaround for Firebase App Hosting not serving static files correctly
 */
export async function GET(request: NextRequest) {
  try {
    // Read the HTML file from the public directory
    const filePath = join(process.cwd(), 'public', 'onepager-presentation', 'index.html');
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
    console.error('Error serving onepager presentation:', error);
    return new NextResponse('Onepager presentation not found', { 
      status: 404,
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  }
}
