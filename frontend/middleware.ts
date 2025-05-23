import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { clerkMiddleware } from '@clerk/nextjs/server';

// Public routes that don't require authentication
const publicRoutes = [
  '/',
  '/sign-in',
  '/sign-up',
  '/pricing',
  '/contact',
  '/privacy-policy',
  '/terms-of-service',
  '/impressum'
];

// Create a middleware function that conditionally applies Clerk middleware
const middleware = (req: NextRequest): NextResponse => {
  // Check if Clerk is configured
  const isClerkConfigured = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== 'your_clerk_publishable_key_here';

  // Skip authentication during static site generation or if Clerk is not configured
  const isFirebaseBot = req.headers.get('user-agent')?.includes('Firebase') || false;
  if (!isClerkConfigured || (process.env.NODE_ENV === 'production' && isFirebaseBot)) {
    console.warn('Bypassing authentication for static site generation or Firebase deployment');
    return NextResponse.next();
  }

  // Check if the current path is a public route
  const url = new URL(req.url);
  if (publicRoutes.includes(url.pathname)) {
    return NextResponse.next();
  }

  // Apply Clerk middleware for protected routes
  try {
    // @ts-expect-error - clerkMiddleware expects different parameters in different versions
    return clerkMiddleware()(req);
  } catch (error) {
    console.error('Error in Clerk middleware:', error);
    return NextResponse.next();
  }
};

export default middleware;

// Configure matcher with simpler pattern that doesn't use capturing groups
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next (Next.js internals)
     * - public (public files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next|public|favicon.ico).*)',
  ],
};
