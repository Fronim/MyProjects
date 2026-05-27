import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Home, Folder, PlusCircle, Terminal } from 'lucide-react';

export default function Layout() {
  const navLinkClass = ({ isActive }) => `
    flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium
    ${isActive
      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
      : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'}
  `;

  return (
    <div className="flex h-screen w-screen bg-zinc-950 text-zinc-50 overflow-hidden font-sans">

      <aside className="w-64 border-r border-zinc-800 bg-zinc-900 flex flex-col justify-between p-5 shrink-0">
        <div className="flex flex-col gap-8">
          {/* Логотип системи */}
          <div className="flex items-center gap-2 px-2">
            <Terminal className="h-6 w-6 text-indigo-500" />
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
              ML TRACKER
            </span>
          </div>

          <nav className="flex flex-col gap-2">
            <NavLink to="/" className={navLinkClass}>
              <Home className="h-5 w-5" />
              <span>Dashboard</span>
            </NavLink>

            <NavLink to="/projects" className={navLinkClass}>
              <Folder className="h-5 w-5" />
              <span>Projects</span>
            </NavLink>

            <NavLink to="/experiments/new" className={navLinkClass}>
              <PlusCircle className="h-5 w-5" />
              <span>New Experiment</span>
            </NavLink>
          </nav>
        </div>

        <div className="flex items-center gap-3 p-2 border-t border-zinc-800 pt-4">
          <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-xs text-white">
            ML
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium truncate text-zinc-200">Engineer Workspace</span>
            <span className="text-xs text-zinc-500 truncate">env: local-dev</span>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md flex items-center justify-end px-8 shrink-0">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-zinc-400 font-mono">FastAPI Connected</span>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-8 bg-zinc-950">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </section>
      </main>

    </div>
  );
}