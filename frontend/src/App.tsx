import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { ModeCards } from './components/ModeCards';
import { VoiceApprovalStudio } from './components/VoiceApprovalStudio';
import { AudioMixer } from './components/AudioMixer';
import { QueueMonitor } from './components/QueueMonitor';
import { SettingsModal } from './components/SettingsModal';
import { TrainingCenterView } from './components/TrainingCenterView';
import {
  AudioMixerState,
  ApprovalState,
  SystemSettings,
  OutputLanguageOption
} from './types';
import { Play, Sparkles, FolderOpen, Film, Video, CheckCircle2, Brain, UploadCloud, Check, X } from 'lucide-react';

export const App: React.FC = () => {
  // Top Navigation Tabs
  const [activeTab, setActiveTab] = useState<'production' | 'training'>('production');

  // Mode Selection (default to Mode 01)
  const [selectedMode, setSelectedMode] = useState<string>('mode01_dubbing');
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  // Mode Specific States
  // Mode 02 states
  const [cartoonAudioMode, setCartoonAudioMode] = useState<'real' | 'ai'>('ai');
  const [deltaAudioSwap, setDeltaAudioSwap] = useState<boolean>(true);

  // Mode 03 states
  const [autonomousPrompt, setAutonomousPrompt] = useState<string>('একটি চালাক বিড়াল ও রোবট শেফের মধ্যে বিরিয়ানি রান্না নিয়ে কমেডি ঝগড়া');
  const [autonomousStyle, setAutonomousStyle] = useState<string>('SLAPSTICK_CHAOS');

  // Video generation input state
  const [videoTitle, setVideoTitle] = useState<string>('Bengali Dubbing Comedy Test');
  const [videoPath, setVideoPath] = useState<string>('');
  const [videoUploading, setVideoUploading] = useState<boolean>(false);
  const [uploadedVideoInfo, setUploadedVideoInfo] = useState<{
    filename: string;
    sizeMb: number;
    durationSec?: number;
    formattedDuration?: string;
  } | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<OutputLanguageOption>('Bangla');
  const [selectedProfileName, setSelectedProfileName] = useState<string>('Dhallywood Classic Satire');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [trainingVideos, setTrainingVideos] = useState<any[]>([]);
  const [showTrainingVideoPicker, setShowTrainingVideoPicker] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Active rendering queue state
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeProjectTitle, setActiveProjectTitle] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('Idle');
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [queueDepth, setQueueDepth] = useState<number>(0);

  // Voice Approval Gateway state
  const [approvalState, setApprovalState] = useState<ApprovalState | null>(null);

  // 4-Track Mixer state
  const [mixerState, setMixerState] = useState<AudioMixerState>({
    originalAudioVolume: 0.0,
    originalAudioMuted: true,
    demucsVocalVolume: 0.2,
    demucsAccompanimentVolume: 0.8,
    aiVoiceVolume: 1.0,
    masterVolume: 1.0,
    masterLevelDb: -3.2,
    peakClippingDetected: false,
    hardLimiterEnabled: true,
    normalizerEnabled: true,
    normalizerTargetLufs: -16.0
  });

  // Settings State
  const [settings, setSettings] = useState<SystemSettings>({
    active_gemini_model: 'gemini-2.5-flash',
    verified_free_models: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash'],
    offline_mode_enabled: false,
    single_port_binding: '127.0.0.1:8000',
    api_key_configured: false,
    api_key_fingerprint: '',
    api_key_masked: '',
    system_memory: {
      total_gb: 16.0,
      available_gb: 8.5,
      used_gb: 7.5,
      percent_used: 46.8
    }
  });

  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial settings & status
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch('/api/v1/settings');
        if (res.ok) {
          const data = await res.json();
          setSettings(data);
        }
      } catch (err) {
        console.warn('Could not fetch settings from backend:', err);
      }
    };
    fetchSettings();
  }, []);

  // WebSocket live telemetry setup
  useEffect(() => {
    let reconnectTimer: any = null;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
      
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'QUEUE_PROGRESS') {
              setProgressPercent(data.progressPercent ?? 0);
              setCurrentStep(data.step ?? 'Processing');
            } else if (data.type === 'VOICE_APPROVAL_TRIGGER') {
              setApprovalState({
                project_id: data.project_id,
                status: 'WAITING_FOR_VOICE_APPROVAL',
                audio_preview_url: data.preview_url,
                notes: data.notes
              });
            } else if (data.type === 'MIXER_LEVEL') {
              setMixerState(prev => ({
                ...prev,
                masterLevelDb: data.levelDb ?? prev.masterLevelDb,
                peakClippingDetected: (data.levelDb ?? prev.masterLevelDb) > -0.1
              }));
            }
          } catch (e) {
            console.error('WebSocket parse error:', e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          reconnectTimer = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch {
        setWsConnected(false);
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, []);

  // Load training videos ledger so user can use ANY training video directly for dubbing
  const fetchTrainingVideos = async () => {
    try {
      const res = await fetch('/api/v1/training/ledger');
      if (res.ok) {
        const data = await res.json();
        if (data && data.records) {
          setTrainingVideos(data.records);
        }
      }
    } catch (e) {
      console.error('Failed to fetch training videos:', e);
    }
  };

  useEffect(() => {
    fetchTrainingVideos();
  }, [activeTab]);

  // Select any Training Video directly for dubbing
  const handleSelectTrainingVideoForDubbing = (
    chosenVideoPath: string,
    filename: string,
    sizeMb?: number,
    durationSec?: number
  ) => {
    setVideoPath(chosenVideoPath);
    const dur = durationSec || 58.8;
    const mins = Math.floor(dur / 60);
    const secs = Math.floor(dur % 60);
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    setUploadedVideoInfo({
      filename: filename,
      sizeMb: sizeMb || 0,
      durationSec: dur,
      formattedDuration: formatted,
    });
    setVideoTitle(filename.replace(/\.[^/.]+$/, ''));
    setActiveTab('production');
    setShowTrainingVideoPicker(false);
  };

  // Handle Video File Upload from File Picker
  const handleVideoFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setVideoUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/projects/upload', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setVideoPath(data.saved_path);
        setUploadedVideoInfo({
          filename: data.filename,
          sizeMb: data.size_mb,
          durationSec: data.duration_sec,
          formattedDuration: data.formatted_duration,
        });
        if (!videoTitle || videoTitle === 'Bengali Dubbing Comedy Test') {
          setVideoTitle(data.filename.replace(/\.[^/.]+$/, ''));
        }
      } else {
        alert('Video upload failed. Check the file format.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      alert('Error uploading video.');
    } finally {
      setVideoUploading(false);
    }
  };

  // Clear / Cancel Selected Video
  const handleCancelVideo = () => {
    setVideoPath('');
    setUploadedVideoInfo(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handlers for Voice Approval
  const handleApproveVoice = async (projectId: string, finalScript?: string) => {
    try {
      await fetch(`/api/v1/approval/${projectId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ final_script: finalScript })
      });
      setApprovalState(null);
      setCurrentStep('Audio Stem Multiplexing & Inpainting');
    } catch (e) {
      console.error('Approve failed:', e);
    }
  };

  const handleRegenerateVoice = async (projectId: string, editedScript: string, notes: string) => {
    try {
      await fetch(`/api/v1/approval/${projectId}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes, edited_script: editedScript })
      });
      setCurrentStep(`Re-synthesizing voice with edited script...`);
      alert('সফল হয়েছে! আপনার এডিট করা স্ক্রিপ্ট দিয়ে নতুন ভয়েস তৈরি হচ্ছে...');
    } catch (e) {
      console.error('Regenerate failed:', e);
    }
  };

  const handleRejectVoice = async (projectId: string, reason: string) => {
    try {
      await fetch(`/api/v1/approval/${projectId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      setApprovalState(null);
      setActiveTaskId(null);
      setActiveProjectTitle(null);
      setCurrentStep('Idle');
      setProgressPercent(0);
    } catch (e) {
      console.error('Reject failed:', e);
    }
  };

  // Start Generation Action
  const handleStartProduction = async () => {
    if (!videoPath) {
      alert('Please upload or select a video file first!');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: videoTitle || 'Dubbing Project',
          mode: selectedMode,
          input_video_path: videoPath,
          target_languages: [selectedLanguage]
        })
      });

      if (res.ok) {
        const project = await res.json();
        setActiveTaskId(project.id);
        setActiveProjectTitle(project.title);
        setCurrentStep('Separating Stems with Demucs (Preserving Master Audio)...');
        setProgressPercent(20);

        // Step 2: Request Full-Length Timeline Script & Voice Preview
        try {
          const previewRes = await fetch('/api/v1/projects/generate-preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              project_id: project.id,
              input_video_path: videoPath,
              target_language: selectedLanguage,
              comedy_profile: selectedProfileName
            })
          });

          if (previewRes.ok) {
            const previewData = await previewRes.json();
            setCurrentStep(`Synthesizing Comedic Pacing Voice (Full Timeline 00:00 - ${previewData.formatted_duration})...`);
            setProgressPercent(80);

            setApprovalState({
              project_id: project.id,
              status: 'WAITING_FOR_VOICE_APPROVAL',
              script_text: previewData.script_text,
              translation_script_text: previewData.translation_script_text,
              commentary_script_text: previewData.commentary_script_text,
              has_original_voice: previewData.has_original_voice,
              duration_sec: previewData.duration_sec,
              formatted_duration: previewData.formatted_duration,
              audio_preview_url: previewData.audio_preview_url,
              notes: `Mode: ${previewData.has_original_voice ? '🎙️ মূল কণ্ঠের কমেডি অনুবাদ' : '🎭 দৃশ্যভিত্তিক কমেডি কমেন্ট্রি'} (${previewData.formatted_duration}, ${previewData.total_words} শব্দ)`
            });
          } else {
            // Fallback preview
            setApprovalState({
              project_id: project.id,
              status: 'WAITING_FOR_VOICE_APPROVAL',
              duration_sec: uploadedVideoInfo?.durationSec || 58.8,
              formatted_duration: uploadedVideoInfo?.formattedDuration || '00:58',
              notes: `Comedy profile: ${selectedProfileName} (${selectedLanguage})`
            });
          }
        } catch {
          setApprovalState({
            project_id: project.id,
            status: 'WAITING_FOR_VOICE_APPROVAL',
            duration_sec: uploadedVideoInfo?.durationSec || 58.8,
            formatted_duration: uploadedVideoInfo?.formattedDuration || '00:58',
            notes: `Comedy profile: ${selectedProfileName} (${selectedLanguage})`
          });
        }
      }
    } catch (err) {
      console.error('Failed to start project:', err);
      alert('Error starting project pipeline');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Settings Handlers
  const handleSaveKey = async (key: string): Promise<boolean> => {
    try {
      const res = await fetch('/api/v1/settings/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(prev => ({
          ...prev,
          api_key_configured: true,
          api_key_fingerprint: data.fingerprint,
          api_key_masked: data.masked
        }));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const handleClearKey = async (): Promise<boolean> => {
    try {
      const res = await fetch('/api/v1/settings/key', { method: 'DELETE' });
      if (res.ok) {
        setSettings(prev => ({
          ...prev,
          api_key_configured: false,
          api_key_fingerprint: '',
          api_key_masked: ''
        }));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const handleToggleOffline = async (enabled: boolean): Promise<boolean> => {
    try {
      const res = await fetch('/api/v1/settings/offline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offline: enabled })
      });
      if (res.ok) {
        setSettings(prev => ({ ...prev, offline_mode_enabled: enabled }));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const handleSelectModel = async (model: string): Promise<boolean> => {
    try {
      const res = await fetch('/api/v1/settings/model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model })
      });
      if (res.ok) {
        setSettings(prev => ({ ...prev, active_gemini_model: model }));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* Top Navbar */}
      <Navbar
        onOpenSettings={() => setIsSettingsOpen(true)}
        offlineMode={settings.offline_mode_enabled}
        freeTierModel={settings.active_gemini_model}
      />

      {/* Main Tab Navigation */}
      <div className="bg-slate-900/80 border-b border-slate-800 px-6 py-2">
        <div className="max-w-7xl mx-auto flex items-center space-x-4">
          <button
            onClick={() => setActiveTab('production')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
              activeTab === 'production'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Film className="w-4 h-4" />
            <span>🎬 Studio Video Production</span>
          </button>

          <button
            onClick={() => setActiveTab('training')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
              activeTab === 'training'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Brain className="w-4 h-4" />
            <span>🧠 Training Center Hub (Reference Video & Comedy Style)</span>
          </button>
        </div>
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {activeTab === 'training' ? (
          /* TRAINING CENTER TAB VIEW */
          <TrainingCenterView
            onSelectProfileForDubbing={(profile) => {
              setSelectedProfileName(profile.name);
              setActiveTab('production');
              alert(`Selected comedy profile: "${profile.name}". Ready for dubbing!`);
            }}
            onSelectVideoForDubbing={handleSelectTrainingVideoForDubbing}
          />
        ) : (
          /* STUDIO PRODUCTION TAB VIEW */
          <>
            {/* Mode Selector */}
            <section>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                  Studio Production Modes
                </h2>
                <span className="text-xs text-indigo-400 font-medium">Click a card to select active pipeline</span>
              </div>
              <ModeCards selectedMode={selectedMode} onSelectMode={setSelectedMode} />
            </section>

            {/* Dynamic Studio Workspace Based on Selected Mode */}
            {selectedMode === 'mode01_dubbing' && (
              <section className="bg-slate-900 border border-indigo-500/40 rounded-xl p-6 shadow-xl space-y-5 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      <Film className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-100">01. Funny Video Dubbing Studio Workspace</h3>
                      <p className="text-xs text-slate-400">Demucs stem isolation, watermark removal, comedic pacing & multi-language dubbing</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400">Dubbing Language:</span>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value as OutputLanguageOption)}
                      className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-indigo-300 font-semibold focus:outline-none focus:border-indigo-500 cursor-pointer"
                    >
                      <option value="Bangla">Bangla (বাঙালি)</option>
                      <option value="Hindi">Hindi (हिन्दी)</option>
                      <option value="English">English</option>
                      <option value="Bangla + Hindi">Bilingual: Bangla + Hindi</option>
                      <option value="Bangla + Hindi + English">Trilingual: Bangla + Hindi + English</option>
                    </select>
                  </div>
                </div>

                {/* Video Upload Drop Area */}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
                    Upload Source Video to Dub
                  </label>
                  
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="video/*"
                    onChange={handleVideoFileChange}
                    className="hidden"
                  />

                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/60 group"
                  >
                    <UploadCloud className="w-10 h-10 text-slate-500 group-hover:text-indigo-400 mb-2 transition" />
                    <p className="text-sm font-semibold text-slate-300">
                      {videoUploading ? 'Uploading Video to Local Storage...' : 'Click to Browse Video File or Drag and Drop Here'}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">MP4, MKV, WebM, AVI (Local-First Privacy — No Cloud Upload)</p>
                  </div>

                  {/* Select from Training Library Option */}
                  {trainingVideos.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                      <span className="text-slate-400 text-[11px] flex items-center gap-1.5">
                        <Brain className="w-3.5 h-3.5 text-purple-400" />
                        <span>পূর্বে আপলোড করা ট্রেনিং ভিডিও দিয়ে সরাসরি ডাবিং করতে চান?</span>
                      </span>

                      <button
                        type="button"
                        onClick={() => setShowTrainingVideoPicker(!showTrainingVideoPicker)}
                        className="px-2.5 py-1 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/30 text-[11px] font-semibold transition flex items-center space-x-1 cursor-pointer"
                      >
                        <Film className="w-3 h-3 text-purple-400" />
                        <span>📂 ট্রেনিং লাইব্রেরি থেকে ভিডিও নিন ({trainingVideos.length})</span>
                      </button>
                    </div>
                  )}

                  {/* Training Videos Quick Selector Dropdown / Cards */}
                  {showTrainingVideoPicker && trainingVideos.length > 0 && (
                    <div className="mt-3 bg-slate-950 border border-purple-500/30 rounded-xl p-3 space-y-2 animate-in fade-in">
                      <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 text-[11px] font-bold text-purple-300">
                        <span>ট্রেনিং ভিডিও তালিকা থেকে যেকোনো একটি সিলেক্ট করুন:</span>
                        <button
                          type="button"
                          onClick={() => setShowTrainingVideoPicker(false)}
                          className="text-slate-500 hover:text-slate-300"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-[180px] overflow-y-auto pr-1">
                        {trainingVideos.map((tv, idx) => (
                          <div
                            key={idx}
                            onClick={() => handleSelectTrainingVideoForDubbing(
                              tv.video_path,
                              tv.video_name,
                              tv.video_size_mb,
                              tv.video_specs?.duration_sec
                            )}
                            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-purple-500 cursor-pointer transition flex items-center justify-between text-xs group"
                          >
                            <div className="min-w-0 flex-1">
                              <p className="font-semibold text-slate-200 group-hover:text-purple-300 truncate" title={tv.video_name}>
                                {tv.video_name}
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                                {tv.video_size_mb} MB • {tv.video_specs?.duration_sec ? `${tv.video_specs.duration_sec}s` : '58.8s'}
                              </p>
                            </div>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 shrink-0 font-medium ml-2">
                              সিলেক্ট করুন
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {uploadedVideoInfo && (
                    <div className="mt-3 bg-slate-950 border border-emerald-500/30 rounded-xl p-3 flex items-center justify-between text-xs gap-3">
                      <div className="flex items-center space-x-2 min-w-0 flex-1">
                        <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span className="font-semibold text-slate-200 truncate" title={uploadedVideoInfo.filename}>
                          {uploadedVideoInfo.filename}
                        </span>
                        <span className="text-slate-500 font-mono shrink-0">
                          ({uploadedVideoInfo.sizeMb} MB{uploadedVideoInfo.formattedDuration ? ` • ${uploadedVideoInfo.formattedDuration} মিনিট` : ''})
                        </span>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0">
                        <span className="text-emerald-400 font-mono text-[11px] bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/20 whitespace-nowrap">
                          ✓ Ready to Dub
                        </span>

                        <button
                          type="button"
                          onClick={handleCancelVideo}
                          className="px-2 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-[11px] font-medium transition flex items-center space-x-1"
                          title="ভিডিও বাতিল বা রিমুভ করুন"
                        >
                          <X className="w-3.5 h-3.5" />
                          <span>Cancel / Remove</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Project Title and Profile Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                      Project Title
                    </label>
                    <input
                      type="text"
                      value={videoTitle}
                      onChange={(e) => setVideoTitle(e.target.value)}
                      placeholder="e.g. Hilarious Cat Dubbing Episode 1"
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                      Learned Comedy Style Profile
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        readOnly
                        value={selectedProfileName}
                        className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm font-semibold text-purple-300 focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => setActiveTab('training')}
                        className="px-3 py-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/30 text-xs font-semibold whitespace-nowrap"
                      >
                        Change in Training Hub
                      </button>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                  <div className="flex items-center space-x-2 text-xs text-slate-400">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>Voice Approval Gateway will pause render for your audio preview.</span>
                  </div>

                  <button
                    onClick={handleStartProduction}
                    disabled={isSubmitting || !videoPath || videoUploading}
                    className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-indigo-500/20 transition flex items-center space-x-2 disabled:opacity-40"
                  >
                    <Play className="w-4 h-4 fill-current" />
                    <span>{isSubmitting ? 'Starting Dubbing Pipeline...' : 'Start Dubbing Generation'}</span>
                  </button>
                </div>
              </section>
            )}

            {/* Mode 02: Cartoon Re-Creation Studio Workspace */}
            {selectedMode === 'mode02_cartoon' && (
              <section className="bg-slate-900 border border-sky-500/40 rounded-xl p-6 shadow-xl space-y-5 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-100">02. Cartoon Re-Creation Studio Workspace</h3>
                      <p className="text-xs text-slate-400">2D comic adaptation, Real Voice preservation or AI Puppet Dubbing</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400">Target Language:</span>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value as OutputLanguageOption)}
                      className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-sky-300 font-semibold focus:outline-none focus:border-sky-500 cursor-pointer"
                    >
                      <option value="Bangla">Bangla (বাঙালি)</option>
                      <option value="Hindi">Hindi (हिन्दी)</option>
                      <option value="English">English</option>
                      <option value="Bangla + Hindi">Bilingual: Bangla + Hindi</option>
                    </select>
                  </div>
                </div>

                {/* Video Upload Area for Mode 02 */}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
                    Upload Original Real-Life Video to Convert to Cartoon
                  </label>
                  
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="video/*"
                    onChange={handleVideoFileChange}
                    className="hidden"
                  />

                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/60 group"
                  >
                    <UploadCloud className="w-10 h-10 text-slate-500 group-hover:text-sky-400 mb-2 transition" />
                    <p className="text-sm font-semibold text-slate-300">
                      {videoUploading ? 'Uploading Video...' : 'Click to Browse Video to Convert to Cartoon Animation'}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">Accepts live action clips, funny pet clips, reaction videos</p>
                  </div>

                  {uploadedVideoInfo && (
                    <div className="mt-3 bg-slate-950 border border-emerald-500/30 rounded-xl p-3 flex items-center justify-between text-xs gap-3">
                      <div className="flex items-center space-x-2 min-w-0 flex-1">
                        <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span className="font-semibold text-slate-200 truncate" title={uploadedVideoInfo.filename}>
                          {uploadedVideoInfo.filename}
                        </span>
                        <span className="text-slate-500 font-mono shrink-0">
                          ({uploadedVideoInfo.sizeMb} MB{uploadedVideoInfo.formattedDuration ? ` • ${uploadedVideoInfo.formattedDuration} মিনিট` : ''})
                        </span>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0">
                        <span className="text-emerald-400 font-mono text-[11px] bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/20 whitespace-nowrap">
                          ✓ Ready
                        </span>

                        <button
                          type="button"
                          onClick={handleCancelVideo}
                          className="px-2 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-[11px] font-medium transition flex items-center space-x-1"
                          title="ভিডিও বাতিল বা রিমুভ করুন"
                        >
                          <X className="w-3.5 h-3.5" />
                          <span>Cancel / Remove</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Mode 02 Audio Mode & 1-Click Delta Audio Swap Controls */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-2">
                      Voice Delivery Strategy
                    </label>
                    <div className="flex items-center space-x-3">
                      <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                        <input
                          type="radio"
                          name="cartoonAudio"
                          checked={cartoonAudioMode === 'real'}
                          onChange={() => setCartoonAudioMode('real')}
                          className="accent-sky-500"
                        />
                        <span>Keep Real Voice (আসল কণ্ঠ বজায় রাখুন)</span>
                      </label>
                      <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                        <input
                          type="radio"
                          name="cartoonAudio"
                          checked={cartoonAudioMode === 'ai'}
                          onChange={() => setCartoonAudioMode('ai')}
                          className="accent-sky-500"
                        />
                        <span>AI Cartoon Voice (কার্টুন এআই ভয়েস)</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-2">
                      Fast Muxing Option
                    </label>
                    <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={deltaAudioSwap}
                        onChange={(e) => setDeltaAudioSwap(e.target.checked)}
                        className="accent-sky-500 rounded"
                      />
                      <span>1-Click Delta Audio Swap (Zero video re-encoding with -c:v copy)</span>
                    </label>
                  </div>
                </div>

                {/* Action Button */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                  <span className="text-xs text-slate-400">
                    Creates 2D animated comic representation preserving dialogue timing.
                  </span>

                  <button
                    onClick={handleStartProduction}
                    disabled={isSubmitting || !videoPath || videoUploading}
                    className="px-6 py-2.5 bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-sky-500/20 transition flex items-center space-x-2 disabled:opacity-40"
                  >
                    <Play className="w-4 h-4 fill-current" />
                    <span>{isSubmitting ? 'Processing Cartoon...' : 'Start Cartoon Re-Creation'}</span>
                  </button>
                </div>
              </section>
            )}

            {/* Mode 03: AI Autonomous Content Creator Workspace */}
            {selectedMode === 'mode03_autonomous' && (
              <section className="bg-slate-900 border border-emerald-500/40 rounded-xl p-6 shadow-xl space-y-5 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-100">03. AI Autonomous Content Creator Workspace</h3>
                      <p className="text-xs text-slate-400">Prompt-to-Video Engine: Audio-First Narrative Montage (No source video needed!)</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400">Story Language:</span>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value as OutputLanguageOption)}
                      className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-emerald-300 font-semibold focus:outline-none focus:border-emerald-500 cursor-pointer"
                    >
                      <option value="Bangla">Bangla (বাঙালি)</option>
                      <option value="Hindi">Hindi (हिन्दी)</option>
                      <option value="English">English</option>
                    </select>
                  </div>
                </div>

                {/* Prompt / Idea Input Textarea */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                    Enter Comedy Story Idea or Script Prompt
                  </label>
                  <textarea
                    rows={3}
                    value={autonomousPrompt}
                    onChange={(e) => setAutonomousPrompt(e.target.value)}
                    placeholder="e.g. একটি দুষ্টু বিড়াল এবং রোবট শেফের মধ্যে বিরিয়ানি রান্না নিয়ে মজার কমেডি ঝগড়া..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 leading-relaxed"
                  />
                </div>

                {/* Autonomous Generation Style Controls */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                      Narrative Comedy Pace
                    </label>
                    <select
                      value={autonomousStyle}
                      onChange={(e) => setAutonomousStyle(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 cursor-pointer"
                    >
                      <option value="SLAPSTICK_CHAOS">Slapstick Chaos (দ্রুত হাসির ঘটনা ও সাউন্ড)</option>
                      <option value="SATIRICAL_MOCKUMENTARY">Satirical Mockumentary (ব্যঙ্গাত্মক ডকুমেন্টারি টোন)</option>
                      <option value="FAST_STANDUP">Bengali Standup Punchlines (মিরাক্কেল স্টাইল)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                      Applied Voice Style
                    </label>
                    <input
                      type="text"
                      readOnly
                      value={selectedProfileName}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-semibold text-purple-300 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Action Button for Mode 03 */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                  <div className="text-xs text-slate-400">
                    Automatically writes humorous script, synthesizes voice, and mounts narrative montage.
                  </div>

                  <button
                    onClick={async () => {
                      setIsSubmitting(true);
                      try {
                        const res = await fetch('/api/v1/projects', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({
                            title: `Autonomous: ${autonomousPrompt.slice(0, 25)}...`,
                            mode: 'mode03_autonomous',
                            input_video_path: 'autonomous_narrative_montage',
                            target_languages: [selectedLanguage]
                          })
                        });
                        if (res.ok) {
                          const project = await res.json();
                          setActiveTaskId(project.id);
                          setActiveProjectTitle(project.title);
                          setCurrentStep('Writing Autonomous Comedy Script (Gemini Free Tier)...');
                          setProgressPercent(20);
                        }
                      } finally {
                        setIsSubmitting(false);
                      }
                    }}
                    disabled={isSubmitting || !autonomousPrompt.trim()}
                    className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-emerald-500/20 transition flex items-center space-x-2 disabled:opacity-40"
                  >
                    <Sparkles className="w-4 h-4 fill-current" />
                    <span>{isSubmitting ? 'Generating Storyboard...' : 'Generate Autonomous Video'}</span>
                  </button>
                </div>
              </section>
            )}

            {/* Other Planned Modes (P2-P4) */}
            {!['mode01_dubbing', 'mode02_cartoon', 'mode03_autonomous'].includes(selectedMode) && (
              <section className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 space-y-2">
                <Sparkles className="w-10 h-10 mx-auto text-sky-400 mb-2" />
                <h3 className="text-base font-bold text-slate-200">This Mode is Planned for Release Phase P2/P3/P4</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Currently, Phase 1 (P1 Core) features Mode 01 (Dubbing), Mode 02 (Cartoon Re-Creation), and Mode 03 (Autonomous Creator). Please select one of the top 3 active modes above.
                </p>
              </section>
            )}

            {/* Voice Approval Gateway Component */}
            <section>
              <VoiceApprovalStudio
                approvalState={approvalState}
                onApprove={handleApproveVoice}
                onRegenerate={handleRegenerateVoice}
                onReject={handleRejectVoice}
                currentLanguage={selectedLanguage}
              />
            </section>

            {/* 4-Track Audio Mixer */}
            <section>
              <AudioMixer
                mixerState={mixerState}
                onChange={setMixerState}
                onSaveDefaults={() => {
                  setMixerState({
                    originalAudioVolume: 0.0,
                    originalAudioMuted: true,
                    demucsVocalVolume: 0.2,
                    demucsAccompanimentVolume: 0.8,
                    aiVoiceVolume: 1.0,
                    masterVolume: 1.0,
                    masterLevelDb: -3.2,
                    peakClippingDetected: false,
                    hardLimiterEnabled: true,
                    normalizerEnabled: true,
                    normalizerTargetLufs: -16.0
                  });
                }}
              />
            </section>

            {/* Real-Time Queue Monitor */}
            <section>
              <QueueMonitor
                wsConnected={wsConnected}
                activeTaskId={activeTaskId}
                activeProjectTitle={activeProjectTitle}
                currentStep={currentStep}
                progressPercent={progressPercent}
                queueDepth={queueDepth}
                onCancelTask={(id) => {
                  setActiveTaskId(null);
                  setCurrentStep('Cancelled');
                  setProgressPercent(0);
                }}
              />
            </section>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/70 py-4 px-6 text-center text-xs text-slate-500">
        Muazu Studio • Single Port Architecture (127.0.0.1:8000) • Zero Extra Cost Hard-Lock • Checkpoint Durability Full
      </footer>

      {/* System Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveKey={handleSaveKey}
        onClearKey={handleClearKey}
        onToggleOffline={handleToggleOffline}
        onSelectModel={handleSelectModel}
      />
    </div>
  );
};

export default App;
