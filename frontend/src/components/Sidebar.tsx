import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  History,
  Database,
  LineChart,
  BrainCircuit,
  Info,
  Settings,
  Recycle,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import type { HealthResponse } from '../types';

interface SidebarProps {
  health: HealthResponse | null;
  isLoadingHealth: boolean;
}

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Image Prediction', path: '/predict', icon: ScanLine },
  { name: 'Prediction History', path: '/history', icon: History },
  { name: 'Dataset Info', path: '/dataset', icon: Database },
  { name: 'Model Performance', path: '/performance', icon: LineChart },
  { name: 'Training & Models', path: '/training', icon: BrainCircuit },
  { name: 'About System', path: '/about', icon: Info },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ health, isLoadingHealth }) => {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-900/30">
          <Recycle className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base leading-tight">EcoClassify DL</h1>
          <p className="text-xs text-slate-400 font-medium">Waste AI System</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Main Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Model & Backend Status Card */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-800 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-slate-400 uppercase tracking-wider">FastAPI Backend</span>
            {isLoadingHealth ? (
              <span className="inline-block w-2 h-2 rounded-full bg-amber-400 animate-ping" />
            ) : health?.status === 'ok' ? (
              <span className="flex items-center gap-1 text-emerald-400 text-[11px] font-medium">
                <CheckCircle2 className="w-3 h-3" /> Online
              </span>
            ) : (
              <span className="flex items-center gap-1 text-rose-400 text-[11px] font-medium">
                <AlertCircle className="w-3 h-3" /> Offline
              </span>
            )}
          </div>
          <div className="text-slate-300 font-mono text-[11px] truncate">
            {health?.model_name || 'Loading Model...'}
          </div>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
            <span>Ver: {health?.model_version || 'v1.0'}</span>
            <span>6 Classes</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
