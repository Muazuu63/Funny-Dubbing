export type OutputLanguageOption =
  | 'Bangla'
  | 'Hindi'
  | 'English'
  | 'Bangla + Hindi'
  | 'Bangla + Hindi + English';

export interface AudioMixerState {
  originalAudioVolume: number;
  originalAudioMuted: boolean;
  demucsVocalVolume: number;
  demucsAccompanimentVolume: number;
  aiVoiceVolume: number;
  masterVolume: number;
  masterLevelDb: number;
  peakClippingDetected: boolean;
  hardLimiterEnabled: boolean;
  normalizerEnabled: boolean;
  normalizerTargetLufs: number;
}

export interface Project {
  id: string;
  title: string;
  mode: string;
  inputVideoPath?: string;
  targetLanguages: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProductionMode {
  id: string;
  name: string;
  phase: 'P1' | 'P2' | 'P3' | 'P4';
  status: 'ACTIVE' | 'PLANNED' | 'FUTURE';
  description: string;
}

export interface ApprovalState {
  project_id: string;
  status: 'WAITING_FOR_VOICE_APPROVAL' | 'APPROVED' | 'REJECTED' | 'REGENERATION_REQUESTED';
  audio_preview_url?: string;
  notes?: string;
  script_text?: string;
  translation_script_text?: string;
  commentary_script_text?: string;
  has_original_voice?: boolean;
  duration_sec?: number;
  formatted_duration?: string;
}

export interface SystemSettings {
  active_gemini_model: string;
  verified_free_models: string[];
  offline_mode_enabled: boolean;
  single_port_binding: string;
  api_key_configured: boolean;
  api_key_fingerprint: string;
  api_key_masked: string;
  system_memory: {
    total_gb: number;
    available_gb: number;
    used_gb: number;
    percent_used: number;
  };
}
