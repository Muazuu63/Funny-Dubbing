import React, { useState } from 'react';
import { Film, Sparkles, Bot, Wand2, Mic, Subtitles, Video, Scissors, Image as ImageIcon, Layers, Music } from 'lucide-react';
import { ProductionMode } from '../types';

interface ModeCardsProps {
  selectedMode: string;
  onSelectMode: (modeId: string) => void;
}

const MODES: (ProductionMode & { icon: React.FC<{ className?: string }> })[] = [
  {
    id: 'mode01_dubbing',
    name: '01. Funny Video Dubbing Studio',
    phase: 'P1',
    status: 'ACTIVE',
    description: 'Automatic watermark removal, comedic scene analysis, Demucs stem isolation, and multi-language dubbing.',
    icon: Film,
  },
  {
    id: 'mode02_cartoon',
    name: '02. Cartoon Re-Creation Studio',
    phase: 'P1',
    status: 'ACTIVE',
    description: 'Meaning-preserving 2D adaptation with Real Voice preservation or AI Cartoon Voice options.',
    icon: Sparkles,
  },
  {
    id: 'mode03_autonomous',
    name: '03. AI Autonomous Content Creator',
    phase: 'P1',
    status: 'ACTIVE',
    description: 'Prompt-to-video studio with automatic script, audio-first narrative, and comedic voice approval.',
    icon: Bot,
  },
  {
    id: 'mode04_enhancement',
    name: '04. Video Enhancement Studio',
    phase: 'P2',
    status: 'PLANNED',
    description: 'Face restoration, upscaling and frame interpolation.',
    icon: Wand2,
  },
  {
    id: 'mode05_voice',
    name: '05. AI Voice Studio',
    phase: 'P2',
    status: 'PLANNED',
    description: 'Advanced voice synthesis, cloning profiles and pitch editing.',
    icon: Mic,
  },
  {
    id: 'mode06_subtitle',
    name: '06. Subtitle & Translation Studio',
    phase: 'P2',
    status: 'PLANNED',
    description: 'Auto-sync subtitle translation for Bangla, Hindi, and English.',
    icon: Subtitles,
  },
  {
    id: 'mode07_shorts',
    name: '07. Shorts & Reels Repurposer',
    phase: 'P2',
    status: 'PLANNED',
    description: 'Smart vertical cropping with punchline auto-highlighting.',
    icon: Video,
  },
  {
    id: 'mode08_clip',
    name: '08. Smart Clip Extraction Studio',
    phase: 'P3',
    status: 'FUTURE',
    description: 'Detects peak comedy moments and laughter spikes across long videos.',
    icon: Scissors,
  },
  {
    id: 'mode09_thumbnail',
    name: '09. AI Thumbnail & Meme Generator',
    phase: 'P3',
    status: 'FUTURE',
    description: 'High-CTR comedy thumbnails with localized text overlays.',
    icon: ImageIcon,
  },
  {
    id: 'mode10_effects',
    name: '10. VFX & Green Screen Studio',
    phase: 'P4',
    status: 'FUTURE',
    description: 'Comedic meme visual overlays and motion tracking.',
    icon: Layers,
  },
  {
    id: 'mode11_music',
    name: '11. Music & Sound Studio',
    phase: 'P4',
    status: 'FUTURE',
    description: 'Zero-copyright comedy sound effects and background scoring.',
    icon: Music,
  },
];

export const ModeCards: React.FC<ModeCardsProps> = ({ selectedMode, onSelectMode }) => {
  const [filter, setFilter] = useState<'active' | 'roadmap'>('active');

  const visibleModes = filter === 'active' 
    ? MODES.filter(m => m.status === 'ACTIVE')
    : MODES.filter(m => m.status !== 'ACTIVE');

  return (
    <div className="space-y-4">
      {/* Header with Clean Filter Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            Production Studios
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              {filter === 'active' ? '3 Ready to Use' : '8 Planned in Roadmap'}
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {filter === 'active' ? 'Click any active studio to configure its workspace below.' : 'Future capabilities scheduled for upcoming releases.'}
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs self-start sm:self-auto">
          <button
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1.5 ${
              filter === 'active'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Active Studios (3)</span>
          </button>

          <button
            onClick={() => setFilter('roadmap')}
            className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1.5 ${
              filter === 'roadmap'
                ? 'bg-slate-800 text-sky-300 border border-slate-700 shadow'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <span>🚀 Future Roadmap (8)</span>
          </button>
        </div>
      </div>

      {/* Grid: 3 Columns for Active Modes */}
      <div className={`grid gap-4 ${
        filter === 'active' 
          ? 'grid-cols-1 md:grid-cols-3' 
          : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
      }`}>
        {visibleModes.map((mode) => {
          const Icon = mode.icon;
          const isActive = mode.status === 'ACTIVE';
          const isSelected = selectedMode === mode.id;

          return (
            <div
              key={mode.id}
              onClick={() => isActive && onSelectMode(mode.id)}
              className={`p-4 rounded-xl border transition-all relative ${
                isActive
                  ? isSelected
                    ? 'bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500/50 cursor-pointer shadow-xl shadow-indigo-950/50 scale-[1.01]'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80 cursor-pointer'
                  : 'bg-slate-950/40 border-slate-800/40 opacity-60 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2.5 rounded-xl ${
                  isActive 
                    ? isSelected 
                      ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' 
                      : 'bg-slate-800 text-slate-300' 
                    : 'bg-slate-900 text-slate-600'
                }`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                    mode.phase === 'P1'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : mode.phase === 'P2'
                      ? 'bg-sky-500/10 text-sky-400 border-sky-500/20'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {mode.phase} {mode.status}
                  </span>
                </div>
              </div>

              <h3 className="font-bold text-sm text-slate-100 mb-1.5">{mode.name}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{mode.description}</p>

              {isActive && isSelected && (
                <div className="mt-3 pt-2.5 border-t border-indigo-500/30 flex items-center justify-between text-[11px] font-bold text-indigo-400 font-mono">
                  <span>● Active Workspace Open Below</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
