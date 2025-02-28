import { clerkMiddleware } from '@clerk/nextjs/server';

// Export Clerk's middleware
export default clerkMiddleware();

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