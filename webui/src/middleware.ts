import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that don't require authentication
const publicRoutes = ['/login', '/api/auth', '/_next', '/favicon.ico'];

// Routes that should be accessible without auth in development
const devAccessibleRoutes = ['/'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip middleware for public routes
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Skip middleware for static files
  if (pathname.includes('.')) {
    return NextResponse.next();
  }

  // In development, allow all access for now
  // In production, you'd check for auth token here
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    return NextResponse.next();
  }

  // Check for API key in cookies or headers
  const apiKey = request.cookies.get('api_key')?.value || 
                 request.headers.get('X-API-Key');

  if (!apiKey) {
    // For API routes, return 401
    if (pathname.startsWith('/api/')) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // For page routes, redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Add API key to request headers for downstream use
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('X-API-Key', apiKey);

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};

