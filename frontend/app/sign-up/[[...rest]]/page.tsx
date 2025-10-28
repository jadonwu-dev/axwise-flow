'use client';

import Link from 'next/link';

export default function SignUpPage(): JSX.Element {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-6 text-center">
        <h1 className="text-3xl font-bold">Sign Up Disabled</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Authentication is removed in OSS mode. You can use the app without creating an account.
        </p>
        <Link
          href="/unified-dashboard"
          className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
