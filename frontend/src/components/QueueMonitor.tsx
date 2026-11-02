import React from 'react';
import { Activity, Wifi, WifiOff, StopCircle, CheckCircle2 } from 'lucide-react';

interface QueueMonitorProps {
  wsConnected: boolean;
  activeTaskId?: string | null;
  activeProjectTitle?: string | null;
  currentStep?: string;
  progressPercent: number;
  queueDepth: number;
  onCancelTask?: (taskId: string) => void;
}

export const QueueMonitor: React.FC<QueueMonitorProps> = ({
  wsConnected,
  activeTaskId,
  activeProjectTitle,
  currentStep = 'Idle',
  progressPercent = 0,
  queueDepth = 0,
  onCancelTask
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200">Execution Engine & Pipeline Queue</h3>
        </div>

        {/* WebSocket Live Indicator */}
        <div className="flex items-center space-x-2">
          {wsConnected ? (
            <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
              <Wifi className="w-3.5 h-3.5" />
              <span>Telemetry WS: Live</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs animate-pulse">
              <WifiOff className="w-3.5 h-3.5" />
              <span>WS Reconnecting...</span>
            </div>
          )}
        </div>
      </div>

      {activeTaskId ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400">Rendering Project:</div>
              <div className="text-sm font-semibold text-slate-100">{activeProjectTitle || activeTaskId}</div>
            </div>
            {onCancelTask && (
              <button
                onClick={() => onCancelTask(activeTaskId)}
                className="px-3 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold rounded-lg border border-red-500/30 transition flex items-center space-x-1"
              >
                <StopCircle className="w-3.5 h-3.5" />
                <span>Cancel Render</span>
              </button>
            )}
          </div>

          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-cyan-400 font-mono">{currentStep}</span>
              <span className="text-slate-300 font-bold font-mono">{progressPercent}%</span>
            </div>
            <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-300 rounded-full"
                style={{ width: `${Math.min(100, Math.max(0, progressPercent))}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-5 gap-1.5 text-center text-[10px] text-slate-500 font-mono">
            <span className={`p-1 rounded ${progressPercent >= 10 ? 'bg-slate-800 text-cyan-300' : 'bg-slate-950'}`}>1. INTENT</span>
            <span className={`p-1 rounded ${progressPercent >= 35 ? 'bg-slate-800 text-cyan-300' : 'bg-slate-950'}`}>2. RENDERING</span>
            <span className={`p-1 rounded ${progressPercent >= 70 ? 'bg-slate-800 text-cyan-300' : 'bg-slate-950'}`}>3. VALIDATED</span>
            <span className={`p-1 rounded ${progressPercent >= 90 ? 'bg-slate-800 text-cyan-300' : 'bg-slate-950'}`}>4. OUTPUT_COMMITTED</span>
            <span className={`p-1 rounded ${progressPercent >= 100 ? 'bg-slate-800 text-cyan-300' : 'bg-slate-950'}`}>5. DB_COMMITTED</span>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between py-2 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Worker Queue Idle — Standing by for video generation request</span>
          </div>
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded border border-slate-800 text-slate-400">
            Pending Tasks: {queueDepth}
          </span>
        </div>
      )}
    </div>
  );
};
