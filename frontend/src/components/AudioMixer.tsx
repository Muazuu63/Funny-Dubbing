import React from 'react';
import { Sliders, VolumeX, AlertTriangle, ShieldCheck, Zap } from 'lucide-react';
import { AudioMixerState } from '../types';

interface AudioMixerProps {
  mixerState: AudioMixerState;
  onChange: (newState: AudioMixerState) => void;
  onSaveDefaults?: () => void;
}

export const AudioMixer: React.FC<AudioMixerProps> = ({
  mixerState,
  onChange,
  onSaveDefaults
}) => {
  const updateTrack = (key: keyof AudioMixerState, value: any) => {
    onChange({
      ...mixerState,
      [key]: value
    });
  };

  const isClipping = mixerState.peakClippingDetected || mixerState.masterLevelDb > -0.1;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">4-Track Studio Audio Mixer</h3>
            <p className="text-xs text-slate-400">Fine-tune stem balances, comedic voice headroom, and broadcast loudness</p>
          </div>
        </div>

        {/* Peak Clipping Alert Pill */}
        {isClipping ? (
          <div className="flex items-center space-x-1.5 px-3 py-1 bg-red-500/20 border border-red-500/50 rounded-full text-red-400 text-xs font-semibold animate-pulse">
            <AlertTriangle className="w-4 h-4" />
            <span>Peak Clipping Detected! Hard Limiter Engaged</span>
          </div>
        ) : (
          <div className="flex items-center space-x-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>Safe Headroom ({mixerState.masterLevelDb.toFixed(1)} dBFS)</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* Track 1: Original Audio (Permanent Backup) */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">1. Original Master</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">Backup</span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">Unaltered preserved reference audio</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Volume</span>
              <span className="font-mono">{mixerState.originalAudioMuted ? 'Muted' : `${Math.round(mixerState.originalAudioVolume * 100)}%`}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1.5"
              step="0.05"
              disabled={mixerState.originalAudioMuted}
              value={mixerState.originalAudioVolume}
              onChange={(e) => updateTrack('originalAudioVolume', parseFloat(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer disabled:opacity-40"
            />
            <button
              onClick={() => updateTrack('originalAudioMuted', !mixerState.originalAudioMuted)}
              className={`w-full py-1 text-xs font-medium rounded flex items-center justify-center space-x-1 border transition ${
                mixerState.originalAudioMuted
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <VolumeX className="w-3.5 h-3.5" />
              <span>{mixerState.originalAudioMuted ? 'Muted (Recommended)' : 'Mute Track'}</span>
            </button>
          </div>
        </div>

        {/* Track 2: Demucs Vocal */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">2. Demucs Vocal</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">Isolated</span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">Original extracted dialogue stem</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Volume</span>
              <span className="font-mono">{Math.round(mixerState.demucsVocalVolume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1.5"
              step="0.05"
              value={mixerState.demucsVocalVolume}
              onChange={(e) => updateTrack('demucsVocalVolume', parseFloat(e.target.value))}
              className="w-full accent-blue-500 cursor-pointer"
            />
            <div className="text-[11px] text-center text-slate-500 font-mono">
              Level: {(mixerState.demucsVocalVolume * 100 - 100).toFixed(0)} dB
            </div>
          </div>
        </div>

        {/* Track 3: Demucs Accompaniment */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">3. Background SFX / Music</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30">BGM</span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">Retained ambient sound effects & score</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Volume</span>
              <span className="font-mono">{Math.round(mixerState.demucsAccompanimentVolume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1.5"
              step="0.05"
              value={mixerState.demucsAccompanimentVolume}
              onChange={(e) => updateTrack('demucsAccompanimentVolume', parseFloat(e.target.value))}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="text-[11px] text-center text-slate-500 font-mono">
              Level: {(mixerState.demucsAccompanimentVolume * 100 - 100).toFixed(0)} dB
            </div>
          </div>
        </div>

        {/* Track 4: AI Voice */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">4. AI Comedy Voice</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Dubbed</span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">Synthesized Bengali / Hindi dialogue</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Volume</span>
              <span className="font-mono">{Math.round(mixerState.aiVoiceVolume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1.5"
              step="0.05"
              value={mixerState.aiVoiceVolume}
              onChange={(e) => updateTrack('aiVoiceVolume', parseFloat(e.target.value))}
              className="w-full accent-emerald-500 cursor-pointer"
            />
            <div className="text-[11px] text-center text-slate-500 font-mono">
              Level: {(mixerState.aiVoiceVolume * 100 - 100).toFixed(0)} dB
            </div>
          </div>
        </div>
      </div>

      {/* Master Section */}
      <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Master Fader */}
        <div className="w-full md:w-1/3 flex items-center space-x-3">
          <span className="text-xs font-bold text-slate-300 whitespace-nowrap">Master Output:</span>
          <input
            type="range"
            min="0"
            max="1.5"
            step="0.05"
            value={mixerState.masterVolume}
            onChange={(e) => updateTrack('masterVolume', parseFloat(e.target.value))}
            className="w-full accent-cyan-500 cursor-pointer"
          />
          <span className="text-xs font-mono text-cyan-400 w-12 text-right">
            {Math.round(mixerState.masterVolume * 100)}%
          </span>
        </div>

        {/* Master dB Meter */}
        <div className="w-full md:w-1/3 flex items-center space-x-2">
          <span className="text-xs font-medium text-slate-400">VU Meter:</span>
          <div className="flex-1 h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800 flex">
            <div
              className={`h-full rounded-full transition-all duration-150 ${
                isClipping ? 'bg-red-500' : 'bg-gradient-to-r from-emerald-500 via-yellow-400 to-amber-500'
              }`}
              style={{
                width: `${Math.min(100, Math.max(5, ((mixerState.masterLevelDb + 30) / 30) * 100))}%`
              }}
            />
          </div>
          <span className="text-xs font-mono text-slate-300">
            {mixerState.masterLevelDb.toFixed(1)} dB
          </span>
        </div>

        {/* DSP Controls */}
        <div className="w-full md:w-1/3 flex items-center justify-end space-x-4">
          <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={mixerState.hardLimiterEnabled}
              onChange={(e) => updateTrack('hardLimiterEnabled', e.target.checked)}
              className="accent-indigo-500 rounded"
            />
            <span>Limiter (-0.5 dBFS)</span>
          </label>

          <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={mixerState.normalizerEnabled}
              onChange={(e) => updateTrack('normalizerEnabled', e.target.checked)}
              className="accent-indigo-500 rounded"
            />
            <span>EBU R128 (-16 LUFS)</span>
          </label>

          {onSaveDefaults && (
            <button
              onClick={onSaveDefaults}
              className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded border border-slate-700 transition"
            >
              Reset
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
