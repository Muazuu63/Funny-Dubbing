import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  Sparkles,
  Brain,
  Check,
  Film,
  Sliders,
  RefreshCw,
  Trash2,
  ArrowRight,
  FileText,
  TrendingUp,
  Download,
  Eye,
  Smile,
  Mic,
  Clock,
  Volume2,
  X,
  PlusCircle,
  CheckCircle2,
  Video,
  Camera,
  MessageSquare
} from 'lucide-react';

interface VideoLearningRecord {
  record_id: string;
  video_name: string;
  video_path: string;
  video_size_mb: number;
  timestamp: string;
  sequence_index: number;
  video_specs?: {
    resolution?: string;
    aspect_ratio?: string;
    fps?: number;
    duration_sec?: number;
    total_frames?: number;
    bitrate_mbps?: number;
    orientation?: string;
    codec_container?: string;
  };
  learned_voice: {
    speech_cadence_multiplier: number;
    dramatic_pause_sec: number;
    pitch_accentuation_semitones: number;
    f0_pitch_range_hz?: string;
    energy_contour: string;
    voice_modulation: string;
    laughter_burst_type?: string;
  };
  learned_lip_sync: {
    viseme_closure_duration_ms: number;
    plosive_synchrony_bengali: string;
    smile_spread_ratio: number;
    jaw_drop_openness: string;
    fricative_closure_timing?: string;
    lip_cadence_smoothing: string;
  };
  learned_comedy_timing: {
    punchline_delay_after_setup_sec: number;
    laughter_track_ducking_db: number;
    background_music_duck_delay_ms: number;
    music_duck_recovery_time_ms?: number;
    sfx_climax_drop: string;
    pacing_genre?: string;
  };
  learned_visual_gestures?: {
    eyebrow_raise_timing?: string;
    eye_wideness_ratio?: number;
    double_take_timing_ms?: number;
    reaction_freeze_sec?: number;
    reaction_camera_zoom?: string;
  };
  learned_audio_design?: {
    laugh_track_envelope?: string;
    comedy_sfx_cues?: string[];
    vocal_eq_clarity?: string;
  };
  learned_linguistic_humor?: {
    detected_dialect?: string;
    comedy_genre?: string;
    punchline_formula?: string;
    sarcasm_quotient?: string;
    dubbing_tone_guideline?: string;
  };
  learned_slang_and_style: string[];
  improvements_delta: string[];
  learning_document_md: string;
}

interface TrainingProfile {
  id: string;
  name: string;
  category: string;
  description?: string;
  parameters: Record<string, any>;
  reference_media_path?: string;
}

interface TrainingCenterViewProps {
  onSelectProfileForDubbing?: (profile: TrainingProfile) => void;
}

export const TrainingCenterView: React.FC<TrainingCenterViewProps> = ({
  onSelectProfileForDubbing
}) => {
  const [profiles, setProfiles] = useState<TrainingProfile[]>([]);
  const [ledger, setLedger] = useState<VideoLearningRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);

  // Uploaded file info
  const [uploadedPath, setUploadedPath] = useState<string>('');
  const [uploadedFilename, setUploadedFilename] = useState<string>('');
  const [uploadedSizeMb, setUploadedSizeMb] = useState<number>(0);
  const [analyzedVideoPath, setAnalyzedVideoPath] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Active / Selected Learning Record for detailed view
  const [activeRecord, setActiveRecord] = useState<VideoLearningRecord | null>(null);
  const [showFullMarkdown, setShowFullMarkdown] = useState<boolean>(false);

  // New profile form
  const [profileName, setProfileName] = useState<string>('Dhallywood Comedy Master');
  const [profileCategory, setProfileCategory] = useState<string>('COMEDIC_SATIRE');
  const [statusMessage, setStatusMessage] = useState<string>('');

  // Fetch initial profiles & learning ledger
  const fetchData = async () => {
    setLoading(true);
    try {
      const [resProfiles, resLedger] = await Promise.all([
        fetch('/api/v1/training/profiles'),
        fetch('/api/v1/training/ledger')
      ]);

      if (resProfiles.ok) {
        const profData = await resProfiles.json();
        setProfiles(profData);
      }

      if (resLedger.ok) {
        const ledgerData = await resLedger.json();
        const records = ledgerData.records || [];
        setLedger(records);
        if (records.length > 0 && !activeRecord) {
          setActiveRecord(records[records.length - 1]);
        }
      }
    } catch (err) {
      console.error('Failed to load training data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle Reference Video Upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setAnalyzedVideoPath(null);
    setStatusMessage('Uploading reference comedy video...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/training/upload-reference', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setUploadedPath(data.saved_path);
        setUploadedFilename(data.filename);
        setUploadedSizeMb(data.size_mb);
        setStatusMessage(`Reference video uploaded (${data.size_mb} MB). Click Analyze below!`);
      } else {
        setStatusMessage('Upload failed. Please check file format.');
      }
    } catch {
      setStatusMessage('Upload connection error');
    } finally {
      setUploading(false);
    }
  };

  // Clear / Cancel Uploaded Video
  const handleCancelUpload = () => {
    setUploadedPath('');
    setUploadedFilename('');
    setUploadedSizeMb(0);
    setAnalyzedVideoPath(null);
    setStatusMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Upload Next Video (Resets slot and triggers file dialog)
  const handleUploadNextVideo = () => {
    setUploadedPath('');
    setUploadedFilename('');
    setUploadedSizeMb(0);
    setAnalyzedVideoPath(null);
    setStatusMessage('নতুন রেফারেন্স ভিডিও সিলেক্ট করুন...');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  // Analyze reference and learn
  const handleAnalyzeReference = async () => {
    if (!uploadedPath) return;
    setAnalyzing(true);
    setStatusMessage('AI analyzing comedic timing, speech cadence, and lip visemes...');

    try {
      const res = await fetch('/api/v1/training/analyze-reference', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_path: uploadedPath }),
      });

      if (res.ok) {
        const data = await res.json();
        const record: VideoLearningRecord = data.analysis || data;
        setActiveRecord(record);
        setAnalyzedVideoPath(uploadedPath);
        setStatusMessage(`✓ "${uploadedFilename}" এর বিশ্লেষণ ও শিখন সম্পন্ন! নিচে বিস্তারিত খতিয়ান তৈরি হয়েছে।`);
        fetchData();
      } else {
        setStatusMessage('Analysis failed.');
      }
    } catch {
      setStatusMessage('Error during reference analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Download Markdown Report to local computer
  const handleDownloadReport = (record: VideoLearningRecord) => {
    const element = document.createElement('a');
    const file = new Blob([record.learning_document_md], { type: 'text/markdown;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = `AI_Learning_Report_${record.sequence_index}_${record.video_name}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Save as reusable profile
  const handleSaveProfile = async () => {
    if (!profileName.trim()) return;

    try {
      const res = await fetch('/api/v1/training/profiles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: profileName,
          category: profileCategory,
          description: `Extracted from video: ${activeRecord?.video_name || uploadedFilename}`,
          parameters: activeRecord ? {
            speech_cadence: activeRecord.learned_voice.speech_cadence_multiplier,
            punchline_pause_sec: activeRecord.learned_voice.dramatic_pause_sec,
            pitch_shift_semitones: activeRecord.learned_voice.pitch_accentuation_semitones,
            laughter_ducking_db: activeRecord.learned_comedy_timing.laughter_track_ducking_db
          } : {},
          reference_media_path: uploadedPath || null,
        }),
      });

      if (res.ok) {
        setStatusMessage('Saved to Studio Comedy Presets!');
        fetchData();
      }
    } catch (e) {
      console.error('Error saving profile:', e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-950 via-slate-900 to-indigo-950 border border-purple-500/30 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Brain className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                Training Center & AI Learning Knowledge Ledger
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-normal">
                  Explainable AI (XAI)
                </span>
              </h2>
              <p className="text-xs text-purple-300 mt-0.5">
                প্রতিটি রেফারেন্স ভিডিও থেকে এআই কী কী শিখল এবং আগের ভিডিওগুলোর চেয়ে কণ্ঠ, লিপ-সিঙ্ক ও কমেডি টাইমিংয়ে কী কী উন্নতি হলো তার লিখিত অডিট খতিয়ান।
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href="/api/v1/training/export-ledger"
              download="muazu_learning_ledger_backup.json"
              className="px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/30 text-xs font-semibold transition flex items-center space-x-1.5"
              title="সম্পূর্ণ এআই শিখন খতিয়ান ডাউনলোড করে ব্যাকআপ রাখুন"
            >
              <Download className="w-3.5 h-3.5" />
              <span>ব্যাকআপ ডাউনলোড</span>
            </a>

            <button
              onClick={fetchData}
              className="p-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-700 transition"
              title="Refresh Ledger"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 Cols): Upload & Video Selector */}
        <div className="lg:col-span-5 space-y-6">
          {/* Upload Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center space-x-2 pb-2.5 border-b border-slate-800">
              <UploadCloud className="w-5 h-5 text-purple-400" />
              <h3 className="text-sm font-bold text-slate-100">১. রেফারেন্স কমেডি ভিডিও আপলোড</h3>
            </div>

            <label className="border-2 border-dashed border-slate-700 hover:border-purple-500 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/60 group">
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <UploadCloud className="w-10 h-10 text-slate-500 group-hover:text-purple-400 mb-2 transition" />
              <p className="text-xs font-semibold text-slate-300 text-center">
                {uploading
                  ? 'ভিডিও আপলোড হচ্ছে...'
                  : analyzedVideoPath === uploadedPath && uploadedPath
                  ? '🔄 অন্য নতুন ভিডিও আপলোড করতে এখানে ক্লিক করুন'
                  : uploadedFilename
                  ? 'ভিডিও পরিবর্তন করতে ক্লিক করুন'
                  : 'ক্লিক করে রেফারেন্স কমেডি ভিডিও সিলেক্ট করুন'}
              </p>
              <p className="text-[11px] text-slate-500 mt-1">MP4, MKV, WebM (বাংলা ও হিন্দি কমেডি দৃশ্য)</p>
            </label>

            {uploadedFilename && (
              <div className={`rounded-xl p-3 flex items-center justify-between text-xs gap-3 border ${
                analyzedVideoPath === uploadedPath
                  ? 'bg-emerald-950/30 border-emerald-500/30'
                  : 'bg-slate-950 border-purple-500/30'
              }`}>
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <Film className={`w-4 h-4 shrink-0 ${
                    analyzedVideoPath === uploadedPath ? 'text-emerald-400' : 'text-purple-400'
                  }`} />
                  <span className="font-semibold text-slate-200 truncate" title={uploadedFilename}>
                    {uploadedFilename}
                  </span>
                  <span className="text-slate-500 font-mono shrink-0">({uploadedSizeMb} MB)</span>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  {analyzedVideoPath === uploadedPath ? (
                    <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/30 flex items-center gap-1 font-semibold whitespace-nowrap">
                      <Check className="w-3 h-3" /> Learned
                    </span>
                  ) : (
                    <span className="text-[11px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20 whitespace-nowrap">
                      Ready to Analyze
                    </span>
                  )}

                  <button
                    onClick={handleCancelUpload}
                    className="px-2 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-[11px] font-medium transition flex items-center space-x-1"
                    title="ভিডিওটি বাদ দিন বা সরান"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Clear</span>
                  </button>
                </div>
              </div>
            )}

            {analyzedVideoPath === uploadedPath && uploadedPath ? (
              <button
                onClick={handleUploadNextVideo}
                className="w-full py-2.5 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-emerald-600/20 transition flex items-center justify-center space-x-2 cursor-pointer"
              >
                <PlusCircle className="w-4 h-4" />
                <span>➕ পরবর্তী রেফারেন্স ভিডিও আপলোড করুন (Upload Next Video)</span>
              </button>
            ) : (
              <button
                onClick={handleAnalyzeReference}
                disabled={!uploadedPath || analyzing}
                className="w-full py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-purple-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-40"
              >
                <Sparkles className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
                <span>{analyzing ? 'AI বিশ্লেষণ ও জ্ঞান আহরণ করছে...' : 'বিশ্লেষণ করুন ও শিখন ডকুমেন্ট তৈরি করুন'}</span>
              </button>
            )}

            {statusMessage && (
              <div className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px] text-purple-300 text-center font-mono">
                {statusMessage}
              </div>
            )}
          </div>

          {/* Analyzed Videos History Ledger */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-100">ভিডিওভিত্তিক শিখনের ধারাবাহিক খতিয়ান ({ledger.length})</h3>
              </div>
            </div>

            {ledger.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-4">এখনও কোনো রেফারেন্স ভিডিও বিশ্লেষণ করা হয়নি। উপরে একটি ভিডিও আপলোড করুন।</p>
            ) : (
              <div className="space-y-2.5 max-h-[350px] overflow-y-auto pr-1">
                {ledger.map((rec) => (
                  <div
                    key={rec.record_id}
                    onClick={() => setActiveRecord(rec)}
                    className={`p-3 rounded-lg border cursor-pointer transition flex items-center justify-between ${
                      activeRecord?.record_id === rec.record_id
                        ? 'bg-purple-950/40 border-purple-500 text-white shadow-md shadow-purple-950/50'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-purple-300">#{String(rec.sequence_index).padStart(2, '0')}</span>
                        <span className="text-xs font-medium truncate max-w-[180px]">{rec.video_name}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        ক্যাডেন্স: {rec.learned_voice.speech_cadence_multiplier}x | বিরতি: {rec.learned_voice.dramatic_pause_sec}s
                      </div>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-mono">
                        +{rec.improvements_delta.length} উন্নতি
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column (7 Cols): Comprehensive Learning Knowledge Card */}
        <div className="lg:col-span-7 space-y-6">
          {activeRecord ? (
            <div className="bg-slate-900 border border-purple-500/30 rounded-xl p-6 shadow-2xl space-y-6">
              {/* Card Header */}
              <div className="flex items-start justify-between pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2.5 mb-1">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      ভিডিও #{activeRecord.sequence_index} শিখন কার্ড
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {new Date(activeRecord.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    {activeRecord.video_name}
                  </h3>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowFullMarkdown(!showFullMarkdown)}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-700 transition flex items-center space-x-1"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>{showFullMarkdown ? 'কার্ড ভিউ' : 'লিখিত রিপোর্ট'}</span>
                  </button>

                  <button
                    onClick={() => handleDownloadReport(activeRecord)}
                    className="px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-lg text-xs font-semibold border border-purple-500/30 transition flex items-center space-x-1"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>ডাউনলোড (.md)</span>
                  </button>
                </div>
              </div>

              {showFullMarkdown ? (
                /* FULL MARKDOWN DOCUMENT VIEW */
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-5 max-h-[500px] overflow-y-auto">
                  <pre className="text-xs font-mono text-purple-200 whitespace-pre-wrap leading-relaxed">
                    {activeRecord.learning_document_md}
                  </pre>
                </div>
              ) : (
                /* STRUCTURED VISUAL KNOWLEDGE CARD */
                <>
                  {/* Section 1: What was learned from this video */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center space-x-2">
                      <FileText className="w-4 h-4" />
                      <span>১. এই ভিডিও থেকে এআই কী কী শিখেছে (Concrete Multi-Dimensional Learnings)</span>
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      {/* Video Media Specs Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-cyan-400 font-bold">
                          <Video className="w-4 h-4" />
                          <span>ভিডিও ও টেকনিক্যাল স্পেক্স (Media Specs)</span>
                        </div>
                        <ul className="space-y-1 text-slate-300 text-[11px]">
                          <li>• রেজোলিউশন: <strong className="text-white">{activeRecord.video_specs?.resolution || '1920x1080 (Full HD)'}</strong></li>
                          <li>• ফ্রেম রেট ও মোট ফ্রেম: <strong className="text-white">{activeRecord.video_specs?.fps || 30.0} FPS</strong> ({activeRecord.video_specs?.total_frames || 450} frames)</li>
                          <li>• অনুপাত ও সময়: <strong className="text-white">{activeRecord.video_specs?.aspect_ratio || '16:9 Landscape'}</strong> ({activeRecord.video_specs?.duration_sec || 15}s)</li>
                        </ul>
                      </div>

                      {/* Voice & Cadence Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-indigo-400 font-bold">
                          <Mic className="w-4 h-4" />
                          <span>কণ্ঠ ও সংলাপের গতি (Voice Delivery)</span>
                        </div>
                        <ul className="space-y-1 text-slate-300 text-[11px]">
                          <li>• পাঞ্চলাইনের গতি: <strong className="text-white">{activeRecord.learned_voice.speech_cadence_multiplier}x</strong> দ্রুত</li>
                          <li>• নাটকীয় বিরতি (Pause): <strong className="text-white">{activeRecord.learned_voice.dramatic_pause_sec} সেকেন্ড</strong></li>
                          <li>• পিচ অ্যাকসেন্ট: <strong className="text-white">+{activeRecord.learned_voice.pitch_accentuation_semitones} st</strong> (ব্যঙ্গাত্মক টান)</li>
                          {activeRecord.learned_voice.f0_pitch_range_hz && (
                            <li>• ফ্রিকোয়েন্সি: <span className="text-slate-400 font-mono">{activeRecord.learned_voice.f0_pitch_range_hz}</span></li>
                          )}
                        </ul>
                      </div>

                      {/* Lip-Sync Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-pink-400 font-bold">
                          <Smile className="w-4 h-4" />
                          <span>ঠোঁটের নড়াচড়া ও লিপ-সিঙ্ক (Lip-Sync)</span>
                        </div>
                        <ul className="space-y-1 text-slate-300 text-[11px]">
                          <li>• মুখ বন্ধের সময়: <strong className="text-white">{activeRecord.learned_lip_sync.viseme_closure_duration_ms} ms</strong></li>
                          <li>• বাংলা বর্ণমালা সিঙ্ক: <strong className="text-white">প, ব, ম, ফ ওষ্ঠ্য বর্ণের নিখুঁত ট্রানজিশন</strong></li>
                          <li>• হাসিমুখের অনুপাত: <strong className="text-white">{activeRecord.learned_lip_sync.smile_spread_ratio}x</strong> বিস্তার</li>
                          <li>• স্বরবর্ণ হাঁ: <span className="text-slate-400">{activeRecord.learned_lip_sync.jaw_drop_openness}</span></li>
                        </ul>
                      </div>

                      {/* Comedy Timing & Audio Ducking Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-amber-400 font-bold">
                          <Clock className="w-4 h-4" />
                          <span>হাসি ও পাঞ্চলাইন টাইমিং (Punchline)</span>
                        </div>
                        <ul className="space-y-1 text-slate-300 text-[11px]">
                          <li>• হাসির সাউন্ড ড্রপ: ডায়ালগের <strong className="text-white">{activeRecord.learned_comedy_timing.punchline_delay_after_setup_sec}s</strong> পর</li>
                          <li>• মিউজিক অডিও ডাকিং: <strong className="text-white">{activeRecord.learned_comedy_timing.laughter_track_ducking_db} dB</strong></li>
                          <li>• ডাকিং রিকভারি: <strong className="text-white">{activeRecord.learned_comedy_timing.music_duck_recovery_time_ms || 360} ms</strong></li>
                          <li>• এসএফএক্স ড্রপ: <span className="text-slate-400">{activeRecord.learned_comedy_timing.sfx_climax_drop}</span></li>
                        </ul>
                      </div>

                      {/* Visual Acting & Facial Gestures Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-purple-400 font-bold">
                          <Camera className="w-4 h-4" />
                          <span>মুখভঙ্গি ও অভিনয় (Facial Acting)</span>
                        </div>
                        <ul className="space-y-1 text-slate-300 text-[11px]">
                          <li>• ভ্রুর চমক: <span className="text-slate-300">{activeRecord.learned_visual_gestures?.eyebrow_raise_timing || 'পাঞ্চলাইনের ০.১২s পূর্বে ভ্রু উঁচু করা'}</span></li>
                          <li>• চোখের পুতুলের বিস্তার: <strong className="text-white">{activeRecord.learned_visual_gestures?.eye_wideness_ratio || 1.35}x</strong> বড় হওয়া</li>
                          <li>• ডাবল-টেক টাইমিং: <strong className="text-white">{activeRecord.learned_visual_gestures?.double_take_timing_ms || 340} ms</strong></li>
                          <li>• কমেডি রিয়্যাকশন জুম: <span className="text-slate-300">{activeRecord.learned_visual_gestures?.reaction_camera_zoom || '1.15x ডিজিটাল পুশ-ইন'}</span></li>
                        </ul>
                      </div>

                      {/* Linguistic Humor & Slang Box */}
                      <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                          <MessageSquare className="w-4 h-4" />
                          <span>আঞ্চলিক কমেডি রস ও স্ল্যাং (Slang)</span>
                        </div>
                        <div className="text-[11px] text-slate-400">
                          ধরণ: <strong className="text-emerald-300">{activeRecord.learned_linguistic_humor?.comedy_genre || 'ব্যঙ্গাত্মক সামাজিক কমেডি'}</strong>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {activeRecord.learned_slang_and_style.map((s, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] border border-emerald-500/20 font-medium">
                              "{s}"
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Section 2: Incremental Improvements Over Previous Videos */}
                  <div className="space-y-3 pt-2 border-t border-slate-800">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-2">
                      <TrendingUp className="w-4 h-4" />
                      <span>২. পূর্বের ভিডিওগুলোর তুলনায় কী কী উন্নত হলো? (Improvements Delta)</span>
                    </h4>

                    <div className="bg-slate-950 border border-emerald-500/20 rounded-lg p-4 space-y-2">
                      {activeRecord.improvements_delta.map((imp, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-xs text-slate-200">
                          <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{imp}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {/* Save As Profile Form */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
                <div className="flex-1 flex items-center space-x-2">
                  <input
                    type="text"
                    value={profileName}
                    onChange={(e) => setProfileName(e.target.value)}
                    placeholder="প্রিসেটের নাম দিন..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                  />
                  <select
                    value={profileCategory}
                    onChange={(e) => setProfileCategory(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
                  >
                    <option value="COMEDIC_SATIRE">Satire</option>
                    <option value="SLAPSTICK_PHYSICAL">Slapstick</option>
                    <option value="STANDUP_PUNCHLINE">Standup</option>
                  </select>
                </div>

                <button
                  onClick={handleSaveProfile}
                  className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-lg transition whitespace-nowrap"
                >
                  প্রিসেট হিসেবে সেভ করুন
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 flex flex-col items-center justify-center min-h-[400px]">
              <Brain className="w-12 h-12 text-slate-600 mb-3" />
              <h3 className="text-base font-bold text-slate-300">কোনো শিখন রেকর্ড সক্রিয় নেই</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                বামে একটি রেফারেন্স কমেডি ভিডিও আপলোড করে "বিশ্লেষণ করুন" বাটনে চাপুন। এআই তার থেকে কী কী শিখল এবং আগের ভিডিওর চেয়ে কী উন্নত হলো তার লিখিত রূপ দেখতে পাবেন।
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
