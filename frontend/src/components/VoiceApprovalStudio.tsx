import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  RefreshCw,
  XCircle,
  Volume2,
  Play,
  Pause,
  Sparkles,
  Copy,
  Check,
  Edit3,
  FileText
} from 'lucide-react';
import { ApprovalState } from '../types';

interface VoiceApprovalStudioProps {
  approvalState: ApprovalState | null;
  onApprove: (projectId: string, finalScript?: string) => Promise<void>;
  onRegenerate: (projectId: string, editedScript: string, notes: string) => Promise<void>;
  onReject: (projectId: string, reason: string) => Promise<void>;
  currentLanguage?: string;
}

export const VoiceApprovalStudio: React.FC<VoiceApprovalStudioProps> = ({
  approvalState,
  onApprove,
  onRegenerate,
  onReject,
  currentLanguage = 'Bangla'
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  // Script text in editable form
  const [scriptText, setScriptText] = useState<string>(
    approvalState?.script_text ||
    'আরে ভাই দেখো কারবার! এই বিড়ালটা নাকি এখন স্পেশাল বিরিয়ানি রান্না করবে! ধুর মিয়া ফাইজলামি নাকি?'
  );

  // Comedic Delivery Notes
  const [deliveryNotes, setDeliveryNotes] = useState<string>('পাঞ্চলাইনে একটু নাটকীয় বিরতি দিন');

  // Sync when approvalState changes
  useEffect(() => {
    if (approvalState?.script_text) {
      setScriptText(approvalState.script_text);
    }
  }, [approvalState?.script_text]);

  if (!approvalState) {
    return null;
  }

  // Copy Script to Clipboard
  const handleCopyScript = () => {
    navigator.clipboard.writeText(scriptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      await onApprove(approvalState.project_id, scriptText);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setLoading(true);
    try {
      await onRegenerate(approvalState.project_id, scriptText, deliveryNotes);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await onReject(approvalState.project_id, deliveryNotes || 'Rejected by user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border-2 border-amber-500/40 rounded-2xl p-6 shadow-2xl relative overflow-hidden space-y-5 animate-in fade-in duration-200">
      {/* Top Banner Tag */}
      <div className="absolute top-0 right-0 bg-amber-500/20 text-amber-300 text-xs px-4 py-1 font-bold rounded-bl-xl border-b border-l border-amber-500/30 flex items-center space-x-1.5">
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        <span>Universal Voice Approval & Script Editor Gateway</span>
      </div>

      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="w-3.5 h-3.5 rounded-full bg-amber-400 animate-ping" />
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            AI Voice Preview & Script Editor
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-amber-300 font-mono border border-amber-500/30">
              {currentLanguage}
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            নিচে এআই-এর তৈরি করা স্ক্রিপ্টটি টেক্সট আকারে দেওয়া আছে। আপনি চাইলে সরাসরি এডিট বা নিজের সংলাপ পেস্ট করে নতুন করে ভয়েস তৈরি করতে পারেন।
          </p>
        </div>
      </div>

      {/* 1. Audio Preview Player */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-12 h-12 rounded-full bg-amber-500 hover:bg-amber-400 text-slate-950 flex items-center justify-center transition-transform active:scale-95 shadow-lg shadow-amber-500/20"
          >
            {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
          </button>
          <div>
            <div className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-amber-400" />
              <span>বর্তমান ভয়েস প্রিভিউ (00:00 - 00:08)</span>
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              কমেডি অ্যাকসেন্টুয়েশন | Limiter: -0.5 dBFS Engaged
            </div>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
            Timing Sync: 1.05x Safe
          </span>
        </div>
      </div>

      {/* 2. Text Script Editor Box (যা ইউজার চেয়েছেন) */}
      <div className="bg-slate-950 border border-amber-500/30 rounded-xl p-4 space-y-2.5">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <div className="flex items-center space-x-2 text-xs font-bold text-amber-300">
            <Edit3 className="w-4 h-4 text-amber-400" />
            <span>সংলাপ / স্ক্রিপ্ট এডিটর (Edit or Paste Your Script Here)</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyScript}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium border border-slate-700 transition flex items-center space-x-1"
              title="Copy text to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'কপি হয়েছে!' : 'স্ক্রিপ্ট কপি করুন'}</span>
            </button>
          </div>
        </div>

        {/* Textarea for Script */}
        <textarea
          rows={3}
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          placeholder="এখানে আপনার পরিবর্তিত সংলাপ লিখুন বা পেস্ট করুন..."
          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 leading-relaxed font-sans"
        />

        <div className="flex items-center justify-between text-[11px] text-slate-500">
          <span>মোট বর্ণ: {scriptText.length} | শব্দ: {scriptText.trim().split(/\s+/).filter(Boolean).length}</span>
          <span className="text-amber-400/80">আপনি সংলাপ পরিবর্তন করলে নতুন ভয়েস এই ডায়ালগ অনুযায়ী তৈরি হবে</span>
        </div>
      </div>

      {/* 3. Delivery Adjustment / Comedic Note Input */}
      <div>
        <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
          কণ্ঠের ভাবভঙ্গি / এক্সপ্রেশন নোট (Delivery Tone Note)
        </label>
        <input
          type="text"
          value={deliveryNotes}
          onChange={(e) => setDeliveryNotes(e.target.value)}
          placeholder="যেমন: শেষ লাইনে একটু বেশি হাসির টান দিন, অথবা পিচ একটু বাড়িয়ে দিন..."
          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-500"
        />
      </div>

      {/* 4. Action Buttons */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
        <button
          onClick={handleReject}
          disabled={loading}
          className="px-4 py-2 rounded-xl border border-red-500/30 hover:bg-red-500/10 text-red-400 text-xs font-semibold transition flex items-center space-x-1.5 disabled:opacity-50"
        >
          <XCircle className="w-4 h-4" />
          <span>বাতিল করুন (Reject)</span>
        </button>

        <button
          onClick={handleRegenerate}
          disabled={loading || !scriptText.trim()}
          className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition flex items-center space-x-1.5 shadow-lg shadow-amber-500/20 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>এডিট করা স্ক্রিপ্ট দিয়ে নতুন ভয়েস বানান (Regenerate Voice)</span>
        </button>

        <button
          onClick={handleApprove}
          disabled={loading}
          className="px-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center space-x-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>এই ভয়েস অ্যাপ্রুভ করুন ও ফাইনাল ভিডিও তৈরি করুন</span>
        </button>
      </div>
    </div>
  );
};
