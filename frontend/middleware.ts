import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// No-op middleware: all routes pass through without Clerk validation
export function middleware(_req: NextRequest) {
  return NextResponse.next();
}

// Keep the matcher to avoid running on static assets unnecessarily
export const config = {
  matcher: [
    '/((?!_next|onepager-presentation|workshop-designthinking|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
