/**
 * Layout - Main layout wrapper with sidebar and content area.
 * Includes backend status badge in the top-right corner.
 */

import { Sidebar } from './Sidebar';
import { StatusBadge } from './StatusBadge';
import { useBackendStatus } from '../hooks/useBackendStatus';

export function Layout({ children }) {
  const { status } = useBackendStatus();

  return (
    <div className="flex min-h-screen bg-main">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <main className="flex-1 ml-60 p-6">
        {/* Status Badge */}
        <div className="fixed top-4 right-6 z-10">
          <StatusBadge status={status} />
        </div>

        {/* Page Content */}
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
