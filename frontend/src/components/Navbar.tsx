import React from 'react';
import { Settings, ShieldCheck, Wifi, WifiOff } from 'lucide-react';

interface NavbarProps {
  singlePort?: string;
  offlineMode: boolean;
  freeTierModel?: string;
  onOpenSettings: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  singlePort = '127.0.0.1:8000',
  offlineMode,
  freeTierModel = 'gemini-2.5-flash',
  onOpenSettings
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <div className="bg-sky-500/20 text-sky-400 p-2 rounded-lg border border-sky-500/30">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Muazu Studio
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
              v2.2 Local-First
            </span>
          </h1>
          <p className="text-xs text-slate-400">Muazu • Local AI Funny Dubbing & Video Production Suite</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Model Tag */}
        <div className="hidden sm:flex items-center space-x-1.5 bg-slate-800/60 px-2.5 py-1 rounded border border-slate-700/60 text-[11px] font-mono text-cyan-300">
          <span>Model: {freeTierModel}</span>
        </div>

        {/* Single Port Indicator */}
        <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-mono text-slate-300">{singlePort}</span>
        </div>

        {/* Offline Mode Indicator */}
        <div className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${
          offlineMode 
            ? 'bg-amber-500/10 text-amber-300 border-amber-500/30' 
            : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
        }`}>
          {offlineMode ? <WifiOff className="w-3.5 h-3.5" /> : <Wifi className="w-3.5 h-3.5" />}
          <span>{offlineMode ? 'Offline Mode' : 'Online Free Tier'}</span>
        </div>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          title="Open Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
