import React, { useState, useEffect, useRef } from 'react';
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
  Mic,
  MessageSquare,
  VolumeX
} from 'lucide-react';
import { ApprovalState } from '../types';

interface VoiceApprovalStudioProps {
  approvalState: ApprovalState | null;
  onApprove: (projectId: string, finalScript?: string, outputLanguage?: string) => Promise<void>;
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
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string>(approvalState?.audio_preview_url || '');

  const [showLanguageModal, setShowLanguageModal] = useState<boolean>(false);
  const [finalOutputLanguage, setFinalOutputLanguage] = useState<string>('Bangla');

  const [activeTab, setActiveTab] = useState<'translation' | 'commentary'>(
    approvalState?.has_original_voice ? 'translation' : 'commentary'
  );

  // Script text in editable form
  const [scriptText, setScriptText] = useState<string>(
    approvalState?.script_text ||
    'আরে ভাই দেখো কারবার! এই বিড়ালটা নাকি এখন স্পেশাল বিরিয়ানি রান্না করবে! ধুর মিয়া ফাইজলামি নাকি?'
  );

  // Comedic Delivery Notes
  const [deliveryNotes, setDeliveryNotes] = useState<string>('পাঞ্চলাইনে একটু নাটকীয় বিরতি দিন');

  // Stale script auto-replacement
  useEffect(() => {
    if (scriptText.trim() === 'আরে ভাই, এই কার্টুন সিনটা দেখছ?' || scriptText.trim() === 'আরে ভাই এই কার্টুন সিনটা দেখছ?') {
      if (approvalState?.translation_script_text) {
        setScriptText(approvalState.translation_script_text);
      } else if (approvalState?.commentary_script_text) {
        setScriptText(approvalState.commentary_script_text);
      } else {
        setScriptText(
          "[00:00 - 00:02] হাঁস ১ [COMIC_WHISPER]: আরে আস্তে কথা বল! এই বিছানাটা কিন্তু অভিশপ্ত!\n\n" +
          "[00:02 - 00:03] হাঁস ২ [SURPRISED_SHOCK]: সত্যি নাকি?\n\n" +
          "[00:03 - 00:06] হাঁস ১ [SUSPENSE_MYSTERY]: হ্যাঁ দোস্ত! সত্যি সত্যিই মারাত্মক অভিশপ্ত।\n\n" +
          "[00:06 - 00:07] হাঁস ২ [SURPRISED_SHOCK]: কীভাবে সম্ভব?\n\n" +
          "[00:07 - 00:11] হাঁস ১ [SUSPENSE_MYSTERY]: দেখতে পাচ্ছিস না? বিড়ালটা আস্তে আস্তে কেমন কালো হয়ে যাচ্ছে!\n\n" +
          "[00:11 - 00:12] হাঁস ২ [SURPRISED_SHOCK]: ওরে হ্যাঁ তাই তো!\n\n" +
          "[00:12 - 00:15] হাঁস ১ [SUSPENSE_MYSTERY]: এবার ওর চোখ দুটোও আস্তে আস্তে পুরো ঘোর অন্ধকার হয়ে যাবে।\n\n" +
          "[00:15 - 00:16] হাঁস ২ [SURPRISED_SHOCK]: তারপর কী হবে?\n\n" +
          "[00:16 - 00:18] হাঁস ১ [SUSPENSE_MYSTERY]: তারপর ও অন্ধকারের মধ্যে চিরতরে হারিয়ে যাবে!\n\n" +
          "[00:18 - 00:19] হাঁস ২ [SURPRISED_SHOCK]: তারপর?\n\n" +
          "[00:19 - 00:21] হাঁস ১ [COMIC_PUNCHLINE]: তারপর ব্যাটা একেবারে খেল খতম! [SFX_COMIC_CHUCKLE]\n\n" +
          "[00:21 - 00:23] বিড়াল (ভয়ার্ত চিৎকার) [SURPRISED_SHOCK]: ওরে মাগো! আমাকে বাঁচাও রে!\n\n" +
          "[00:23 - 00:25] হাঁস ১ [COMIC_WHISPER]: চল দোস্ত, এবার আয়েশ করে বিছানায় বসা যাক।\n\n" +
          "[00:25 - 00:27] হাঁস ২ [SURPRISED_SHOCK]: আরে কিন্তু বিছানাটা তো অভিশপ্ত ছিল, তাই না?\n\n" +
          "[00:27 - 00:29] হাঁস ১ [COMIC_PUNCHLINE]: আরে বোকা, ও তো বিড়ালটাকে তাড়ানোর জন্য বানিয়ে বলেছিলাম! [SFX_COMIC_CHUCKLE]\n\n" +
          "[00:29 - 00:30] হাঁস ২ [COMIC_PUNCHLINE]: দারুণ বুদ্ধি তো চাচা! এভাবে তো আমরা ওকে বাড়ি থেকেও তাড়িয়ে দিতে পারি!"
        );
      }
    }
  }, [scriptText, approvalState]);

  // Sync when approvalState changes
  useEffect(() => {
    if (approvalState) {
      if (approvalState.script_text) {
        setScriptText(approvalState.script_text);
      }
      if (approvalState.audio_preview_url) {
        setCurrentAudioUrl(approvalState.audio_preview_url);
      }
      if (approvalState.has_original_voice !== undefined) {
        setActiveTab(approvalState.has_original_voice ? 'translation' : 'commentary');
      }
    }
  }, [approvalState]);

  // Auto-synthesize preview voice if currentAudioUrl is missing
  useEffect(() => {
    if (!currentAudioUrl && scriptText && approvalState?.project_id) {
      let isMounted = true;
      fetch('/api/v1/projects/synthesize-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: approvalState.project_id,
          script_text: scriptText,
          language: currentLanguage
        })
      })
      .then(res => res.json())
      .then(data => {
        if (isMounted && data.audio_url) {
          setCurrentAudioUrl(data.audio_url);
        }
      })
      .catch(() => {});
      return () => { isMounted = false; };
    }
  }, [currentAudioUrl, scriptText, approvalState?.project_id, currentLanguage]);

  // Explicitly reload audio tag when currentAudioUrl changes
  useEffect(() => {
    if (audioRef.current && currentAudioUrl) {
      audioRef.current.src = currentAudioUrl;
      audioRef.current.load();
    }
  }, [currentAudioUrl]);

  // Cleanup browser speech on unmount
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!approvalState) {
    return null;
  }

  // Copy Script to Clipboard
  const handleCopyScript = () => {
    navigator.clipboard.writeText(scriptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Browser Speech Synthesis fallback (Guaranteed sound in any browser)
  const playBrowserSpeech = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanSpeech = scriptText.replace(/\[\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(cleanSpeech || scriptText);
    utterance.lang = currentLanguage === 'Hindi' ? 'hi-IN' : currentLanguage === 'English' ? 'en-US' : 'bn-BD';
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);
    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
  };

  // Toggle Audio Playback (Edge-TTS Audio tag first, then on-demand synthesize, then browser speech fallback)
  const togglePlayAudio = async () => {
    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setIsPlaying(false);
    } else {
      if (currentAudioUrl) {
        if (audioRef.current) {
          audioRef.current.currentTime = 0;
          audioRef.current
            .play()
            .then(() => {
              setIsPlaying(true);
            })
            .catch((err) => {
              console.warn('Primary audio tag play failed, trying new Audio instance:', err);
              try {
                const directAudio = new Audio(currentAudioUrl);
                directAudio.onended = () => setIsPlaying(false);
                directAudio.onerror = () => setIsPlaying(false);
                directAudio.play()
                  .then(() => setIsPlaying(true))
                  .catch(() => playBrowserSpeech());
              } catch {
                playBrowserSpeech();
              }
            });
        } else {
          try {
            const directAudio = new Audio(currentAudioUrl);
            directAudio.onended = () => setIsPlaying(false);
            directAudio.onerror = () => setIsPlaying(false);
            directAudio.play()
              .then(() => setIsPlaying(true))
              .catch(() => playBrowserSpeech());
          } catch {
            playBrowserSpeech();
          }
        }
      } else {
        // Synthesize on the fly
        setLoading(true);
        try {
          const res = await fetch('/api/v1/projects/synthesize-script', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              project_id: approvalState.project_id || 'preview_adhoc',
              script_text: scriptText,
              language: currentLanguage
            })
          });
          if (res.ok) {
            const data = await res.json();
            if (data.audio_url) {
              setCurrentAudioUrl(data.audio_url);
              if (audioRef.current) {
                audioRef.current.src = data.audio_url;
                audioRef.current.load();
                audioRef.current.play().then(() => setIsPlaying(true)).catch(() => playBrowserSpeech());
              } else {
                const directAudio = new Audio(data.audio_url);
                directAudio.onended = () => setIsPlaying(false);
                directAudio.onerror = () => setIsPlaying(false);
                directAudio.play().then(() => setIsPlaying(true)).catch(() => playBrowserSpeech());
              }
              return;
            }
          }
          playBrowserSpeech();
        } catch {
          playBrowserSpeech();
        } finally {
          setLoading(false);
        }
      }
    }
  };

  const handleSelectTab = (tab: 'translation' | 'commentary') => {
    setActiveTab(tab);
    if (tab === 'translation') {
      if (approvalState.translation_script_text) {
        setScriptText(approvalState.translation_script_text);
      }
    } else {
      if (approvalState.commentary_script_text) {
        setScriptText(approvalState.commentary_script_text);
      }
    }
  };

  const handleApprove = () => {
    // Open language selection dialog before final render
    setShowLanguageModal(true);
  };

  const handleConfirmApproval = async () => {
    setShowLanguageModal(false);
    setLoading(true);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    try {
      await onApprove(approvalState.project_id, scriptText, finalOutputLanguage);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setLoading(true);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    try {
      const res = await fetch('/api/v1/projects/synthesize-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: approvalState.project_id,
          script_text: scriptText,
          language: currentLanguage
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.audio_url) {
          setCurrentAudioUrl(data.audio_url);
          if (audioRef.current) {
            audioRef.current.src = data.audio_url;
            audioRef.current.load();
            audioRef.current.play().then(() => setIsPlaying(true)).catch(() => playBrowserSpeech());
          }
        }
      }

      await onRegenerate(approvalState.project_id, scriptText, deliveryNotes);
    } catch {
      playBrowserSpeech();
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
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

      {/* 1. Audio Preview Player (Real Edge-TTS Audio + Fallback) */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <button
            type="button"
            onClick={togglePlayAudio}
            className="w-12 h-12 rounded-full bg-amber-500 hover:bg-amber-400 text-slate-950 flex items-center justify-center transition-transform active:scale-95 shadow-lg shadow-amber-500/20 shrink-0 cursor-pointer"
            title={isPlaying ? 'ভয়েস থামান' : 'ভয়েস শুনুন'}
          >
            {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
          </button>
          <div>
            <div className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-amber-400" />
              <span>বর্তমান ভয়েস প্রিভিউ (00:00 - {approvalState?.formatted_duration || '00:58'})</span>
              {isPlaying && (
                <span className="text-xs text-amber-400 font-normal animate-pulse flex items-center gap-1 ml-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
                  শব্দ প্লে হচ্ছে...
                </span>
              )}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              কমেডি অ্যাকসেন্টুয়েশন | Microsoft Neural Voice | পূর্ণাঙ্গ ভিডিও ব্যাপ্তি: {approvalState?.formatted_duration || '00:58'} মিনিট
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
            Timing Sync: 1.05x Safe (Full Timeline)
          </span>
        </div>
      </div>

      {/* Universal HTML5 Native Audio Control Bar */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 flex items-center justify-between gap-3 shadow-inner">
        <audio
          ref={audioRef}
          controls
          src={currentAudioUrl || undefined}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onEnded={() => setIsPlaying(false)}
          className="w-full h-8 accent-amber-500"
        />
      </div>

      {/* 2. Intelligent Dual Script Mode Selector */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5 text-xs">
          {approvalState.has_original_voice ? (
            <div className="flex items-center space-x-2 text-emerald-400">
              <Mic className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="font-semibold">
                মূল ভিডিওতে আসল সংলাপ/কণ্ঠস্বর পাওয়া গেছে — ডায়ালগ ভাবানুবাদ মোড
              </span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-blue-400">
              <VolumeX className="w-4 h-4 text-blue-400 shrink-0" />
              <span className="font-semibold">
                ভিডিওতে কোনো কথা নেই (Silent/BGM) — দৃশ্যভিত্তিক কমেডি কমেন্ট্রি মোড
              </span>
            </div>
          )}
        </div>

        {/* 1-Click Tab Switcher Buttons */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            type="button"
            onClick={() => handleSelectTab('translation')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'translation'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20 border border-amber-400'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>🎙️ মূল সংলাপের ভাবানুবাদ (Translation)</span>
          </button>

          <button
            type="button"
            onClick={() => handleSelectTab('commentary')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'commentary'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20 border border-amber-400'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>🎭 মৌলিক কমেডি ধারাভাষ্য (Commentary)</span>
          </button>
        </div>
      </div>

      {/* 3. Text Script Editor Box */}
      <div className="bg-slate-950 border border-amber-500/30 rounded-xl p-4 space-y-2.5">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <div className="flex items-center space-x-2 text-xs font-bold text-amber-300">
            <Edit3 className="w-4 h-4 text-amber-400" />
            <span>
              পূর্ণাঙ্গ সংলাপ / স্ক্রিপ্ট এডিটর (00:00 - {approvalState?.formatted_duration || '00:58'})
              {activeTab === 'translation' ? ' — [মূল সংলাপের ভাবানুবাদ]' : ' — [মৌলিক কমেডি ধারাভাষ্য]'}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyScript}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium border border-slate-700 transition flex items-center space-x-1 cursor-pointer"
              title="Copy text to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'কপি হয়েছে!' : 'সম্পূর্ণ স্ক্রিপ্ট কপি করুন'}</span>
            </button>
          </div>
        </div>

        {/* Textarea for Full Length Script */}
        <textarea
          rows={6}
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          placeholder="এখানে সম্পূর্ণ ভিডিওর সংলাপ দৃশ্য অনুযায়ী লিখুন বা পেস্ট করুন..."
          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 leading-relaxed font-sans font-mono"
        />

        <div className="flex items-center justify-between text-[11px] text-slate-500">
          <span>মোট বর্ণ: {scriptText.length} | শব্দ: {scriptText.trim().split(/\s+/).filter(Boolean).length}</span>
          <span className="text-amber-400/80">আপনি সংলাপ পরিবর্তন করলে নতুন ভয়েস এই ডায়ালগ অনুযায়ী তৈরি হবে</span>
        </div>
      </div>

      {/* 4. Delivery Adjustment / Comedic Note Input */}
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

      {/* 5. Action Buttons */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
        <button
          onClick={handleReject}
          disabled={loading}
          className="px-4 py-2 rounded-xl border border-red-500/30 hover:bg-red-500/10 text-red-400 text-xs font-semibold transition flex items-center space-x-1.5 disabled:opacity-50 cursor-pointer"
        >
          <XCircle className="w-4 h-4" />
          <span>বাতিল করুন (Reject)</span>
        </button>

        <button
          onClick={handleRegenerate}
          disabled={loading || !scriptText.trim()}
          className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition flex items-center space-x-1.5 shadow-lg shadow-amber-500/20 disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>নতুন স্ক্রিপ্ট অ্যাপ্রুভ করে ভয়েস জেনারেট করে দাও</span>
        </button>

        <button
          onClick={handleApprove}
          disabled={loading || !scriptText.trim()}
          className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center space-x-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50 cursor-pointer"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>ভয়েস অ্যাপ্রুভ করে ফাইনাল ভিডিও জেনারেট করুন</span>
        </button>
      </div>

      {/* Language Selection Modal (Triggered when user clicks Approve) */}
      {showLanguageModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-150">
          <div className="bg-slate-900 border-2 border-emerald-500/50 rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-5 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2.5">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">ফাইনাল ভিডিও আউটপুট ভাষা নির্বাচন করুন</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowLanguageModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm p-1 rounded-lg hover:bg-slate-800 transition"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              ডিফল্ট বাংলায় প্রিভিউ ভয়েস ও স্ক্রিপ্ট অনুমোদন সম্পন্ন হয়েছে। এখন আপনার এই অনুমোদিত স্ক্রিপ্ট দিয়ে কোন কোন ভাষায় ফাইনাল ডাবিং ভিডিও আউটপুট পেতে চান?
            </p>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                ডাবিং আউটপুট ভাষা (Dubbing Output Language):
              </label>
              <select
                value={finalOutputLanguage}
                onChange={(e) => setFinalOutputLanguage(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-sky-300 font-semibold focus:outline-none focus:border-emerald-500 cursor-pointer shadow-inner"
              >
                <option value="Bangla">Bangla (বাঙালি) — ১টি বাংলা ভিডিও</option>
                <option value="Hindi">Hindi (हिन्दी) — ১টি হিন্দি ভিডিও</option>
                <option value="English">English — ১টি ইংরেজি ভিডিও</option>
                <option value="Bangla + Hindi">Bilingual: Bangla + Hindi — ২টি আলাদা ভিডিও</option>
                <option value="Bangla + Hindi + English">Trilingual: Bangla + Hindi + English — ৩টি আলাদা ভিডিও</option>
              </select>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center space-x-2.5">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>
                {finalOutputLanguage === 'Bangla'
                  ? 'শুধু ১টি ফুল বাংলা ডাবিং ভিডিও তৈরি হবে।'
                  : finalOutputLanguage === 'Hindi'
                  ? 'শুধু ১টি হিন্দি ডাবিং ভিডিও তৈরি হবে।'
                  : finalOutputLanguage === 'English'
                  ? 'শুধু ১টি ইংরেজি ডাবিং ভিডিও তৈরি হবে।'
                  : finalOutputLanguage === 'Bangla + Hindi'
                  ? 'বাংলা ও হিন্দি মিলিয়ে ২টি আলাদা ফুল ভিডিও তৈরি হবে।'
                  : 'বাংলা, হিন্দি ও ইংরেজি মিলিয়ে ৩টি আলাদা ফুল ভিডিও তৈরি হবে।'}
              </span>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setShowLanguageModal(false)}
                className="px-4 py-2 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs font-semibold transition cursor-pointer"
              >
                বাতিল করুন
              </button>
              <button
                type="button"
                onClick={handleConfirmApproval}
                disabled={loading}
                className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center space-x-2 shadow-lg shadow-emerald-500/20 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>🚀 ভয়েস অ্যাপ্রুভড — ফাইনাল ভিডিও জেনারেট করুন ({finalOutputLanguage})</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
