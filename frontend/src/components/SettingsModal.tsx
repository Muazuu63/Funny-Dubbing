import React, { useState } from 'react';
import { X, Key, Shield, Cpu, HardDrive, Check, AlertCircle } from 'lucide-react';
import { SystemSettings } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: SystemSettings;
  onSaveKey: (key: string) => Promise<boolean>;
  onClearKey: () => Promise<boolean>;
  onToggleOffline: (enabled: boolean) => Promise<boolean>;
  onSelectModel: (model: string) => Promise<boolean>;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSaveKey,
  onClearKey,
  onToggleOffline,
  onSelectModel
}) => {
  const [apiKeyInput, setApiKeyInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  if (!isOpen) return null;

  const handleSaveKey = async () => {
    if (!apiKeyInput.trim()) return;
    setLoading(true);
    setMessage(null);
    try {
      const ok = await onSaveKey(apiKeyInput.trim());
      if (ok) {
        setApiKeyInput('');
        setMessage({ text: 'API Key securely stored in Windows Credential Locker', type: 'success' });
      } else {
        setMessage({ text: 'Failed to securely store API key', type: 'error' });
      }
    } catch {
      setMessage({ text: 'Error saving key', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleClearKey = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const ok = await onClearKey();
      if (ok) {
        setMessage({ text: 'API Key removed from Windows Credential Locker', type: 'success' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center space-x-2.5">
            <Shield className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-slate-100">System & Security Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto max-h-[75vh]">
          {/* Zero Cost Policy Banner */}
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3.5 flex items-start space-x-3 text-xs text-emerald-300">
            <Check className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
            <div>
              <span className="font-bold">Permanent Zero Extra Cost Guarantee:</span> This engine exclusively uses Google AI Studio Free Tier models and local CPU/GPU engines. No auto-billing or paid API endpoints are invoked.
            </div>
          </div>

          {/* Gemini API Key Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                <Key className="w-4 h-4 text-amber-400" />
                <span>Google Gemini API Key</span>
              </label>
              {settings.api_key_configured && (
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Fingerprint: {settings.api_key_fingerprint}
                </span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="password"
                placeholder={settings.api_key_configured ? settings.api_key_masked : 'Enter AI Studio API Key (AIzaSy...)'}
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
              />
              <button
                onClick={handleSaveKey}
                disabled={loading || !apiKeyInput.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition disabled:opacity-50"
              >
                Save Key
              </button>
              {settings.api_key_configured && (
                <button
                  onClick={handleClearKey}
                  disabled={loading}
                  className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium rounded-lg border border-red-500/30 transition disabled:opacity-50"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Active Model Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Active Free Tier Model</span>
            </label>
            <select
              value={settings.active_gemini_model}
              onChange={(e) => onSelectModel(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 font-mono cursor-pointer"
            >
              {settings.verified_free_models.map((model) => (
                <option key={model} value={model}>
                  {model} (Verified Zero-Cost Free Tier)
                </option>
              ))}
            </select>
          </div>

          {/* Offline Mode Switch */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-slate-200">Strict Offline Mode</div>
              <p className="text-xs text-slate-500 mt-0.5">
                Block all external cloud AI requests and run using CPU local fallback heuristics only.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.offline_mode_enabled}
                onChange={(e) => onToggleOffline(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          {/* System RAM Telemetry */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
                <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
                <span>Local System RAM Allocation Gate</span>
              </span>
              <span className="font-mono text-slate-400">
                {settings.system_memory.available_gb.toFixed(1)} GB Available / {settings.system_memory.total_gb.toFixed(1)} GB Total
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  settings.system_memory.percent_used > 85 ? 'bg-red-500' : 'bg-indigo-500'
                }`}
                style={{ width: `${Math.min(100, settings.system_memory.percent_used)}%` }}
              />
            </div>
            <div className="text-[11px] text-slate-500 flex justify-between">
              <span>Single Port Lock: {settings.single_port_binding}</span>
              <span>Memory Pressure: {settings.system_memory.percent_used}%</span>
            </div>
          </div>

          {/* Feedback status message */}
          {message && (
            <div
              className={`p-3 rounded-lg text-xs flex items-center space-x-2 ${
                message.type === 'success'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}
            >
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{message.text}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-950/50 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
