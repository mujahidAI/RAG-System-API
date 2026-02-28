/**
 * Sidebar - Navigation sidebar with links to Chat, Ingest, and Evaluate pages.
 */

import { NavLink } from 'react-router-dom';

export function Sidebar() {
  const navItems = [
    { path: '/', label: 'Chat', icon: '💬' },
    { path: '/ingest', label: 'Ingest', icon: '📁' },
    { path: '/evaluate', label: 'Evaluate', icon: '📊' },
  ];

  return (
    <aside className="w-60 bg-sidebar text-white h-screen flex flex-col fixed left-0 top-0">
      {/* Logo / App Name */}
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold">RAG System</h1>
        <p className="text-gray-400 text-sm mt-1">Question Answering</p>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`
                }
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <p className="text-gray-500 text-xs text-center">
          v1.0.0
        </p>
      </div>
    </aside>
  );
}
