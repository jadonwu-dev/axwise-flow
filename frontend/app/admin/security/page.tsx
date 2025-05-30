'use client';

import React from 'react';
import { useAuth } from '@clerk/nextjs';

// Simple placeholder for admin security dashboard
// This would be replaced with actual security monitoring in production

export default function SecurityDashboard(): JSX.Element {
  const { userId } = useAuth();

  if (!userId) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Security Dashboard</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          You must be logged in to access this page.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Security Dashboard</h1>
      <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
        Security monitoring dashboard placeholder. This would be replaced with actual security monitoring in production.
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Security Alerts</h3>
          <p className="text-gray-600">No alerts at this time</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Security Logs</h3>
          <p className="text-gray-600">No logs available</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Dependency Scans</h3>
          <p className="text-gray-600">No scans completed</p>
        </div>
      </div>
    </div>
  );
}
