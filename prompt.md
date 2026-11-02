# 🚀 AI-VPS: ধাপে ধাপে প্রজেক্ট বাস্তবায়নের টেকনিক্যাল প্রম্পট গাইডলাইন (Backend-First)
### প্রজেক্ট: AI Funny Dubbing & Video Production Studio (AI-VPS)
**আর্কিটেকচার রেফারেন্স:** `architecture.md` (v2.1)  
**রিকোয়ারমেন্টস রেফারেন্স:** `prd.md` (v2.1) ও `idea.md` (v2.0)  
**উদ্দেশ্য:** সম্পূর্ণ রিলিজ ফেজ P1 (Core: Modes 01, 02, 03) বাস্তবায়নের জন্য এবং ফেজ P2-এর প্রস্তুতিমূলক আর্কিটেকচার নিশ্চিত করার জন্য ব্যাকএন্ড-ফার্স্ট এক্সিকিউশন প্রম্পট।  
**কৌশল:** ব্যাকএন্ড-ফার্স্ট (Backend-First), লাইটওয়েট কোর ও অপশনাল এআই ইঞ্জিন পৃথকীকরণ, নির্ধারিত SQLite (`aiosqlite`), জিরো এক্সট্রা কস্ট পার্মানেন্ট হার্ড-লক, মেমরি রিকভারি মেকানিজম সহ Resource-Aware Non-blocking Async Queue (FIFO), ডায়নামিক জেমিনি ৩-স্ট্যাটাস ফেইল-সেফ (`VERIFIED_FREE`, `MANUAL_CONFIRMATION`, `UNAVAILABLE`), সাইডকার ম্যানিফেস্ট-ভিত্তিক ৫-ধাপের ডিউরেবল স্টেট মেশিন (`INTENT → RENDERING → VALIDATED → OUTPUT_COMMITTED → DB_COMMITTED`) এবং কঠোরভাবে একক পোর্ট `127.0.0.1:8000`।

---

## 📌 রিলিজ ফেজ বনাম প্রম্পট এক্সিকিউশন ফেজ স্পষ্টীকরণ

১. **প্রোডাকশন রিলিজ ফেজ (Product Release Phases P1–P4):**
   - **P1 (Core Active):** Mode 01 (Funny Dubbing), Mode 02 (Cartoon Re-Creation), Mode 03 (Autonomous Content Creator) এবং Shared Training Center Core।
   - **P2 (Planned):** Mode 04 (Enhancement), Mode 05 (Voice Studio), Mode 06 (Subtitles) এবং Tauri Desktop Packaging Prototype।
   - **P3 (Planned):** Mode 07 (Shorts), Mode 08 (Editor), Mode 09 (Thumbnails)।
   - **P4 (Future):** Mode 10 (Background/Object), Mode 11 (Music/Sound)।

২. **প্রম্পট এক্সিকিউশন ফেজ (Implementation Execution Phases 1–13):**
   - এই ডকুমেন্টের Phase 1 থেকে 12 পর্যন্ত প্রম্পটগুলো P1 Core ব্যাকএন্ড, ইঞ্জিন, মোড ০১-০৩, ফ্রন্টএন্ড ও টেস্ট বাস্তবায়নের জন্য নির্দেশিত।
   - Phase 13 হলো Phase 2 (P2)-এর জন্য Tauri প্যাকেজিংয়ের প্রস্তুতিমূলক প্রোটোটাইপিং গাইডলাইন; এটি P1 সম্পন্ন করার বাধ্যতামূলক পূর্বশর্ত নয়।

৩. **গিট ও কস্ট পলিসি:**
   - কোনো ধাপ সম্পন্ন হওয়ার পর স্বয়ংক্রিয়ভাবে গিট কমিট বা পুশ করা সম্পূর্ণ নিষিদ্ধ; ব্যবহারকারীর স্পষ্ট অনুমতি নিয়ে কমিট করতে হবে।
   - কোনো পেইড ক্লাউড এপিআই, ক্লাউড GPU বা অটো-বিলিং যুক্ত করা সম্পূর্ণ নিষিদ্ধ।

---

# 🧱 ফেজ ১: পরিবেশ ও ব্যাকএন্ড ডিরেক্টরি সেটআপ

### 🎯 PROMPT 1.1: প্রজেক্ট ডিরেক্টরি স্ট্রাকচার ও ডিপেন্ডেন্সি আইসোলেশন
```text
১. Agent Role: সিনিয়র পাইথন ব্যাকএন্ড আর্কিটেক্ট ও সিস্টেমস ইঞ্জিনিয়ার।
২. Objective: architecture.md v2.1 এবং prd.md v2.1-এর ওপর ভিত্তি করে AI-VPS প্রজেক্টের প্রাথমিক ওয়ার্কস্পেস, মডুলার ডিরেক্টরি লেআউট এবং ডিপেন্ডেন্সি আইসোলেশন ফ্রেমওয়ার্ক তৈরি করা।
৩. Scope: প্রজেক্ট স্কেলিটন, কোর requirements.txt, অপশনাল ইঞ্জিন কনফিগ ও pydantic-settings কনফিগারেশন।
৪. Required Files:
   - app/__init__.py, app/main.py, app/config.py
   - app/api/ (routes_projects, routes_modes, routes_approval, routes_settings, routes_training, websocket)
   - app/core/ (config, queue, checkpointer, reconciliation, memory_manager, security, manifest)
   - app/db/ (database, models, crud)
   - app/engines/ (audio_separator, transcriber, inpainter, lipsync, timing_sync, compositor)
   - app/providers/ (base, gemini_provider, tts_provider, model_registry)
   - app/modes/ (mode01_dubbing, mode02_cartoon, mode03_autonomous)
   - storage/ (models, projects, training_profiles)
   - tests/
৫. Technical Requirements:
   - Core Lightweight Dependencies (`requirements.txt`):
     - fastapi>=0.110.0, uvicorn[standard]>=0.28.0
     - pydantic>=2.6.0, pydantic-settings>=2.2.0
     - aiosqlite>=0.20.0 (একমাত্র ডাটাবেজ সংযোগকারী)
     - python-multipart>=0.0.9, websockets>=12.0
     - psutil>=5.9.8, keyring>=24.3.0, requests>=2.31.0
     - opencv-python-headless>=4.9.0
   - Optional Engine Dependencies (ভারী ইঞ্জিন কোর থেকে আলাদা):
     - Edge-TTS: `edge-tts>=6.1.10` (Online Optional Engine; Core নয়)
     - Demucs: `demucs>=4.0.1` (Optional Audio Stem Splitter)
     - Whisper: `openai-whisper>=20231117` (Optional STT Engine)
     - PyTorch Core: `torch`, `torchaudio` (Tested pinned version: CUDA 12.1 এর জন্য `torch==2.2.2+cu121`, CPU-র জন্য `torch==2.2.2+cpu`)
     - Advanced Engines: `bark`, `meta-mms`, `wav2lip`, `lama`, `real-esrgan`
   - Engine Status Management:
     - ইঞ্জিনের ৪টি স্ট্যাটাস ট্র্যাক করো: `AVAILABLE`, `UNAVAILABLE`, `INSTALL_REQUIRED`, `VERIFICATION_REQUIRED`।
     - কোনো অপশনাল ইঞ্জিন অনুপস্থিত থাকলে অ্যাপ্লিকেশন ক্র্যাশ করবে না; সংশ্লিষ্ট ফিচার নিরাপদভাবে `UNAVAILABLE` থাকবে।
   - Settings Configuration (`app/config.py`):
     - সার্ভার হোস্ট কঠোরভাবে `127.0.0.1`-এ সীমাবদ্ধ থাকবে।
     - একক স্থায়ী পোর্ট: `8000` (URL: `http://127.0.0.1:8000`)। পোর্ট ব্যস্ত থাকলে কোনো ফলব্যাক পোর্ট খুঁজবে না, পরিষ্কার এরর দিয়ে টার্মিনেট করবে।
     - কোনো মেশিন-নির্দিষ্ট অ্যাবসোলিউট পাথ ব্যবহার না করে প্রজেক্ট রুট সাপেক্ষে রিলেটিভ পাথ কনফিগার করো।
৬. Constraints:
   - ব্যাকএন্ড টপ-লেভেলে ভারী `torch` বা অপশনাল ইঞ্জিন ইমপোর্ট করা যাবে না।
   - কোনো পেইড প্যাকেজ যুক্ত করা যাবে না।
৭. Error Handling:
   - ডিরেক্টরি পারমিশন বা মিসিং পাথ থাকলে পরিষ্কার `DirectoryInitError` রেইজ করো।
৮. Security Requirements:
   - রিলেটিভ পাথে পাথম্যাপিং সীমাবদ্ধ রাখা (Path Traversal গার্ড)।
৯. Acceptance Criteria:
   - সম্পূর্ণ ডিরেক্টরি ট্রি তৈরি হবে।
   - Core `requirements.txt` আলাদা থাকবে।
   - অপশনাল ইঞ্জিন না থাকলেও ব্যাকএন্ড সচল থাকবে।
১০. Test Requirements:
    - ফোল্ডার তৈরি ও কোর ডিপেন্ডেন্সি ইমপোর্ট ভেরিফাই করার জন্য টেস্ট স্ক্রিপ্ট তৈরি করো (`tests/test_init.py`)।
১১. Expected Deliverables:
    - ডিরেক্টরি কাঠামো, `requirements.txt`, `app/config.py`, এবং `tests/test_init.py`।
```

---

# 💾 ফেজ ২: ডাটাবেজ আর্কিটেকচার (মেটাডাটা ও ডুয়াল ডিউরেবিলিটি পলিসি)

### 🎯 PROMPT 2.1: SQLite ইঞ্জিন, ডুয়াল ডিউরেবিলিটি ও স্কিমা ম্যাপিং (aiosqlite)
```text
১. Agent Role: সিনিয়র ডাটাবেজ ইঞ্জিনিয়ার ও পারসিস্টেন্স আর্কিটেক্ট।
২. Objective: architecture.md v2.1 অনুযায়ী AI-VPS-এর জন্য aiosqlite ভিত্তিক ডুয়াল ডিউরেবিলিটি পারসিস্টেন্স লেয়ার ও স্কিমা তৈরি করা।
৩. Scope: `app/db/database.py`, `app/db/models.py`, `app/db/crud.py`, এবং `tests/test_db.py`।
৪. Required Files: `app/db/database.py`, `app/db/models.py`, `app/db/crud.py`, `tests/test_db.py`।
৫. Technical Requirements:
   - কোনো মিডিয়া ফাইল (ভিডিও, অডিও, মডেল) ডাটাবেজে সংরক্ষণ করা যাবে না; SQLite-এ কেবল মেটাডাটা ও পাথ থাকবে।
   - ডাটাবেজ সংযোগের জন্য সুনির্দিষ্টভাবে `aiosqlite` ব্যবহার করো (WAL Mode ও JSON1 সক্রিয় সহ)।
   - ডুয়াল ডিউরেবিলিটি পলিসি (Dual Durability Policy):
     ১. Critical Checkpoint Transactions: কঠোরভাবে `PRAGMA synchronous=FULL;` ব্যবহার করবে।
     ২. Non-critical Transactions: পারফরম্যান্সের স্বার্থে `PRAGMA synchronous=NORMAL;` ব্যবহার করবে।
   - স্কিমা ও ফিল্ড ম্যাপিং কনভেনশন (TypeScript camelCase <-> Backend <-> SQLite snake_case):
     - TypeScript Layer: `camelCase` (যেমন: `masterLevelDb`, `masterVolume`, `peakClippingDetected`)
     - SQLite Layer: `snake_case` (যেমন: `master_level_dbfs`, `master_volume`, `peak_clipping_detected`)
     - Backend Pydantic: `model_config = ConfigDict(populate_by_name=True)` দিয়ে স্বয়ংক্রিয় ম্যাপিং।
     - বিশেষ ম্যাপিং: TypeScript `masterLevelDb` <-> Pydantic `master_level_dbfs` (alias: `masterLevelDb`) <-> SQLite `master_level_dbfs`।
   - স্কিমা সংজ্ঞায়ন (`app/db/models.py`):
     - `Project`: id (UUID), title, mode (01 থেকে 11), input_video_path, target_languages (JSON), status, created_at, updated_at.
     - `TaskManifest`: task_id (UUID), project_id, step_name, status (INTENT, RENDERING, VALIDATED, OUTPUT_COMMITTED, DB_COMMITTED, PAUSED, FAILED, ABORTED), sidecar_path, staging_path, final_output_path, expected_format, file_size_bytes, sha256_checksum, recovery_metadata_json, updated_at.
     - `Script`: id, project_id, script_title, scenes_json, selected_flag, approval_status (PENDING, APPROVED, REJECTED).
     - `AudioMixerState`: id, project_id, original_backup_volume (0.0 to 1.5, default 1.0), original_backup_muted (default True), original_backup_solo (False), original_backup_pan (-1.0 to 1.0, default 0.0), vocal_volume (1.0), vocal_muted (False), vocal_solo (False), vocal_pan (0.0), accompaniment_volume (1.0), accompaniment_muted (False), accompaniment_solo (False), accompaniment_pan (0.0), ai_voice_volume (1.0), ai_voice_muted (False), ai_voice_solo (False), ai_voice_pan (0.0), master_volume (1.0), master_level_dbfs (-60.0 to +6.0, default -60.0), peak_clipping_detected (False), hard_limiter_enabled (True, -0.5 dBFS), normalizer_enabled (True), normalizer_target_lufs (-16.0 LUFS).
     - `SystemSettings`: id, verified_free_models (JSON), active_gemini_model, offline_mode_enabled (Boolean), commercial_mode_strict (Boolean).
     - `ModelRegistry` (২৭টি ফিল্ড সম্পূর্ণ সংজ্ঞায়িত): model_id, name, task_type, engine_type, version, weights_source, code_license, weights_license, dataset_license, voice_asset_license, exact_license_version, official_license_url, official_download_url, commercial_use_status (ALLOWED, FORBIDDEN, UNCERTAIN), attribution_required, attribution_text, verification_evidence, checksum_sha256, local_path, min_ram_gb, min_vram_gb, recommended_device, cpu_support, offline_capable, internet_requirement, verification_status, last_verified_date.
৬. Constraints:
   - ডাটাবেজে ফাইল BLOB নিষিদ্ধ।
৭. Error Handling:
   - ডাটাবেজ লক বা কনকারেন্সি এরর হ্যান্ডলিং ও স্বয়ংক্রিয় কানেকশন রিকভারি।
৮. Security Requirements:
   - প্যারামিটারাইজড কুয়েরি (SQL Injection প্রতিরোধ)।
৯. Acceptance Criteria:
   - WAL ও JSON1 ভেরিফাইড। ক্রিটিক্যাল ট্রানজ্যাকশনে `synchronous=FULL` প্রযোজ্য।
১০. Test Requirements:
    - `tests/test_db.py`: WAL মোড, JSON1 সমর্থন, ডুয়াল সিনক্রোনাস ট্রানজ্যাকশন এবং ডাটাবেজ ক্র্যাশ রিকভারির টেস্ট।
১১. Expected Deliverables:
    - `app/db/database.py`, `app/db/models.py`, `app/db/crud.py`, এবং `tests/test_db.py`।
```

---

# 🛡️ ফেজ ৩: সিকিউরিটি, জিরো-কস্ট কুয়াড-চেক ও প্রোভাইডার ম্যানেজার

### 🎯 PROMPT 3.1: লোকাল সিকিউরিটি, উইন্ডোজ ক্রেডেনশিয়াল স্টোরেজ ও ট্রাস্টেড অরিজিন
```text
১. Agent Role: সাইবার সিকিউরিটি ও ব্যাকএন্ড ইঞ্জিনিয়ার।
২. Objective: AI-VPS-এর জন্য সিঙ্গেল-পোর্ট লোকালহোস্ট সিকিউরিটি, হোস্ট হেডার গার্ড এবং ক্রেডেনশিয়াল স্টোরেজ তৈরি করা।
৩. Scope: `app/core/security.py`, `tests/test_security.py`।
৪. Required Files: `app/core/security.py`, `tests/test_security.py`।
৫. Technical Requirements:
   - FastAPI সার্ভার কঠোরভাবে শুধুমাত্র `127.0.0.1:8000`-এ বাইন্ড হবে।
   - Host Header Validation: `127.0.0.1:8000` বা `localhost:8000` ছাড়া অন্য কোনো হোস্ট হেডার সরাসরি রিজেক্ট করবে (DNS Rebinding প্রতিরোধ)।
   - Strict Origin ও CSRF প্রটেকশন মিডলওয়্যার: অননুমোদিত ব্রাউজার অরিজিন ব্লক করো। কোনো Wildcard CORS (`*`) সম্পূর্ণ নিষিদ্ধ।
   - ট্রাস্টেড অরিজিন তালিকা (কোনো 5173 বা 7860 থাকবে না):
     - `http://127.0.0.1:8000`, `http://localhost:8000`, `tauri://localhost`, `http://tauri.localhost`
   - WebSocket হ্যান্ডশেক অরিজিন ভ্যালিডেশন এই একই তালিকার সাথে সম্পূর্ণ সামঞ্জস্যপূর্ণ থাকবে।
   - ক্রেডেনশিয়াল স্টোরেজ: Windows Credential Manager হলো ওএস-লেভেল সিকিউর স্টোরেজ (`keyring` পাইথন লাইব্রেরির মাধ্যমে ইন্টারফেসড)। এপিআই কী কখনোই SQLite ডাটাবেজ বা লগে প্লেইন টেক্সট থাকবে না; ট্র্যাকিংয়ে `api_key_fingerprint` (SHA-256 ফিঙ্গারপ্রিন্ট) ব্যবহৃত হবে।
   - Permanent Zero Extra Cost Hard-Lock: কোনো অবস্থাতেই পেইড এপিআই বা বিলিং কল যেন না হয় সেজন্য মিডলওয়্যার লেভেলে স্থায়ী হার্ড-লক।
৬. Constraints:
   - কোনো ফলব্যাক পোর্ট খোঁজা নিষিদ্ধ।
৭. Error Handling:
   - অবৈধ হোস্ট বা অরিজিন এলে HTTP 403 Forbidden প্রদান।
৮. Security Requirements:
   - DNS Rebinding, CSRF, এবং Credential Leakage প্রতিরোধ।
৯. Acceptance Criteria:
   - পোর্টের বাইরে রিকোয়েস্ট ব্লক হবে। এপিআই কী সুরক্ষিতভাবে রিড/রাইট হবে।
১০. Test Requirements:
    - `tests/test_security.py`: হোস্ট হেডার, অরিজিন ব্লকিং এবং ক্রেডেনশিয়াল স্টোরেজ টেস্ট।
১১. Expected Deliverables:
    - `app/core/security.py` এবং `tests/test_security.py`।
```

### 🎯 PROMPT 3.2: ডায়নামিক জেমিনি ফ্রি টিয়ার প্রোভাইডার ও ৩-স্ট্যাটাস ফেইল-সেফ
```text
১. Agent Role: এআই ইন্টিগ্রেশন স্পেশালিস্ট ও এপিআই আর্কিটেক্ট।
২. Objective: জেমিনি এপিআই-এর বাস্তব সীমাবদ্ধতা অনুযায়ী ৩-স্ট্যাটাস ফেইল-সেফ প্রোভাইডার ও ফলব্যাক মেকানিজম তৈরি করা।
৩. Scope: `app/providers/base.py`, `app/providers/gemini_provider.py`, `tests/test_gemini_provider.py`।
৪. Required Files: `app/providers/base.py`, `app/providers/gemini_provider.py`, `tests/test_gemini_provider.py`।
৫. Technical Requirements:
   - কোনো মডেল আইডি হার্ডকোড করবে না (`list_models` দিয়ে সক্রিয় ফ্রি মডেল ডায়নামিকভাবে ফেচ হবে)।
   - ৩টি স্বতন্ত্র স্ট্যাটাস বজায় রাখো:
     1. `VERIFIED_FREE`: শুধুমাত্র এপিআই ও অফিসিয়াল ম্যাপিং দ্বারা নিশ্চিত হলে ক্লাউড কল অনুমোদিত হবে।
     2. `MANUAL_CONFIRMATION`: ব্যবহারকারীর সম্মতি ডাটাবেজে রেকর্ড থাকবে (`api_key_fingerprint`, ISO টাইমস্ট্যাম্প সহ); এটি কখনোই এপিআই ভ্যালিডেশন নয় এবং কোনো ক্লাউড রিকোয়েস্ট অনুমোদন করতে পারবে না।
     3. `UNAVAILABLE`: যেকোনো তথ্য UNKNOWN বা UNVERIFIED থাকলে ক্লাউড কল ব্লক (Fail-Closed) থাকবে।
   - কুয়াড-চেক বিশ্লেষণ:
     - Model Availability: এপিআই দিয়ে যাচাইযোগ্য।
     - Free Tier Eligibility: এপিআই সরাসরি বুলিয়ান ফ্রি ফ্ল্যাগ দেয় না; অফিশিয়াল ম্যাপিং ছাড়া UNKNOWN থাকবে।
     - Billing Configuration: গুগল এআই স্টুডিও প্রজেক্টে কার্ড বা পে-অ্যাজ-ইউ-গো আছে কিনা তা এপিআই দেয় না; এটি UNKNOWN থাকবে।
     - Remaining Quota: এপিআই ব্যালেন্স দেয় না; HTTP 429 ও Retry-After হলো রিঅ্যাক্টিভ টেলিমেট্রি, কোটা প্রিফ্লাইট ভ্যালিডেশনের বিকল্প নয়। ব্যালেন্স UNKNOWN থাকবে।
   - ফলব্যাক নীতি: জেমিনি অনুপলব্ধ হলে স্বয়ংক্রিয়ভাবে Local LLM অথবা Local Script Engine (রুল-বেসড হিউমারাস ডায়ালগ টেমপ্লেট)-এ ফলব্যাক করবে। লোকাল ইঞ্জিনও না থাকলে `UNAVAILABLE` দেখাবে (সিস্টেম ক্র্যাশ করবে না)। Mode 01, 02, 03-এর কোনোটিতেই জেমিনি নিশ্চিত বা বাধ্যতামূলক নয়।
   - Online Data Privacy Gate: ক্লাউড রিকোয়েস্ট পাঠানোর আগে ব্যবহারকারীকে স্পষ্টভাবে জানাতে হবে কোন ডাটা পাঠানো হচ্ছে (Text, Frames, Audio, Transcription, Metadata)।
   - অফলাইন মোড অন থাকলে ক্লাউড কল সরাসরি ব্লক থাকবে।
৬. Constraints:
   - কনজিউমার জেমিনি প্রো সাবস্ক্রিপশন হ্যাক সম্পূর্ণ নিষিদ্ধ।
৭. Error Handling:
   - HTTP 429 এলে টাস্ক স্টেট `PAUSED` হবে এবং চেকপয়েন্ট সেভ থাকবে।
৮. Security Requirements:
   - এপিআই কী মাস্কিং ও প্রাইভেসি কনসেন্ট গেট।
৯. Acceptance Criteria:
   - শুধুমাত্র `VERIFIED_FREE` অবস্থায় ক্লাউড কল হবে। `MANUAL_CONFIRMATION` বা `UNAVAILABLE`-এ ক্লাউড কল ব্লক থাকবে এবং লোকাল ফলব্যাক কার্যকর হবে।
১০. Test Requirements:
    - `tests/test_gemini_provider.py`: ৩-স্ট্যাটাস ভ্যালিডেশন, ৪২৯ টেলিমেট্রি হ্যান্ডলিং ও লোকাল ফলব্যাকের টেস্ট।
১১. Expected Deliverables:
    - `app/providers/base.py`, `app/providers/gemini_provider.py`, এবং `tests/test_gemini_provider.py`।
```

### 🎯 PROMPT 3.3: অনলাইন বনাম অফলাইন টিটিএস ইঞ্জিন ও কমার্শিয়াল লাইসেন্স রেজিস্ট্রি
```text
১. Agent Role: অডিও এআই ইঞ্জিনিয়ার ও লাইসেন্স কমপ্লায়েন্স অডিটর।
২. Objective: TTS ইঞ্জিন ক্লাসিফিকেশন এবং ২৭টি ফিল্ড বিশিষ্ট Model Commercial License Registry তৈরি করা।
৩. Scope: `app/providers/tts_provider.py`, `app/providers/model_registry.py`, `tests/test_tts_provider.py`।
৪. Required Files: `app/providers/tts_provider.py`, `app/providers/model_registry.py`, `tests/test_tts_provider.py`।
৫. Technical Requirements:
   - TTS Engine Classification:
     - `Online Optional Engine`: Edge-TTS (ইন্টারনেট আবশ্যক; ফ্রি প্রাপ্যতা নিশ্চিত নয়)। অফলাইন মোডে সরাসরি ব্লক থাকবে।
     - `Local Offline Optional Engines`: Bark / Meta MMS (অন-ডিমান্ড লোড; RAM/VRAM প্রিফ্লাইট ও CPU ফলব্যাক সতর্কবার্তা সহ)।
     - `Paid Engines`: ব্যাকএন্ডে স্থায়ীভাবে নিষিদ্ধ।
   - Model Commercial Registry (`app/providers/model_registry.py`):
     - ২৭টি মেটাডাটা ফিল্ড সংরক্ষণ করো (Model Weights, Source Code, Dataset, Voice Asset License, Exact Version, Official URLs, Attribution, Checksum ইত্যাদি)।
     - ৩টি বাণিজ্যিক স্ট্যাটাস: `ALLOWED`, `FORBIDDEN`, `UNCERTAIN`।
     - বাণিজ্যিক ভিডিও তৈরিতে `FORBIDDEN` বা `UNCERTAIN` মডেল কঠোরভাবে ব্লক থাকবে।
     - বাধ্যতামূলক Hardware ও License Preflight Gate তৈরি করো।
৬. Constraints:
   - ওপেন সোর্স নাম দেখেই বাণিজ্যিক অনুমোদন ধরে নেওয়া নিষিদ্ধ।
৭. Error Handling:
   - লাইসেন্স আনভেরিফাইড হলে `CommercialLicenseViolationError` রেইজ করো।
৮. Security Requirements:
   - ডাউনলোডেড মডেল ফাইলের SHA-256 চেকসাম ভ্যালিডেশন।
৯. Acceptance Criteria:
   - Edge-TTS অফলাইন মোডে ব্লক হবে। কমার্শিয়াল মোডে আনভেরিফাইড মডেল ব্লক থাকবে।
১০. Test Requirements:
    - `tests/test_tts_provider.py`: অফলাইন মোড ব্লকিং, লাইসেন্স গেট এবং চেকসাম ভ্যালিডেশনের টেস্ট।
১১. Expected Deliverables:
    - `app/providers/tts_provider.py`, `app/providers/model_registry.py`, এবং `tests/test_tts_provider.py`।
```

---

# ⚙️ ফেজ ৪: প্রোডাকশন-রেডি নন-ব্লকিং কিউ ও প্রসেস রিসাইক্লার

### 🎯 PROMPT 4.1: Async Event Loop সেফ Worker Lifecycle ও কিউ রিলায়াবিলিটি
```text
১. Agent Role: সিস্টেম রিলায়াবিলিটি ও কনকারেন্সি ইঞ্জিনিয়ার।
২. Objective: FastAPI Async Event Loop ব্লক না করে মেমরি ক্র্যাশ রোধে Resource-Aware Non-blocking Sequential Queue তৈরি করা।
৩. Scope: `app/core/queue.py`, `app/core/memory_manager.py`, `tests/test_queue.py`।
৪. Required Files: `app/core/queue.py`, `app/core/memory_manager.py`, `tests/test_queue.py`।
৫. Technical Requirements:
   - নন-ব্লকিং প্রসেস এক্সিকিউশন: FastAPI-এর async event loop-এর মধ্যে ব্লকিং `subprocess.Popen.communicate()` চালানো নিষিদ্ধ; বাধ্যতামূলকভাবে `asyncio.create_subprocess_exec()` ব্যবহার করো।
   - ডিপেন্ডেন্সি আইসোলেশন ও মেমরি বাস্তবতা:
     - ব্যাকএন্ডের টপ-লেভেলে কখনোই ভারী `torch` ইমপোর্ট করবে না (এটি ওয়ার্কার সাবপ্রসেসে অলসভাবে অন-ডিমান্ড ইমপোর্ট হবে)।
     - `torch.cuda.empty_cache()` অপারেটিং সিস্টেম ও ড্রাইভার মেমরি শতভাগ ফাঁকা করার নিশ্চয়তা দেয় না।
   - ১০-ধাপের প্রোডাকশন ওয়ার্কার লাইফসাইকেল:
     1. Resource Readiness Check (রিসোর্স প্রিফ্লাইট)
     2. Worker Process Start (`asyncio.create_subprocess_exec`)
     3. Async Process Monitoring (বাউন্ডেড স্ট্রিমিং লগিং — মেমরিতে আনবাউন্ডেড বাফার জমা নিষিদ্ধ)
     4. Timeout Monitoring (ডিফল্ট ৬০০ সেকেন্ড)
     5. Cancellation Handling (টাস্ক বাতিল সিগন্যাল)
     6. Windows Child Process Tree Cleanup (`psutil.Process(pid).children(recursive=True)` নিরাপদ এক্সেপশন হ্যান্ডলিং সহ)
     7. Process Exit Verification (প্রসেস সম্পূর্ণ বন্ধ হওয়া নিশ্চিতকরণ)
     8. RAM/VRAM Re-measurement (মেমরি পুনর্পরিমাপ)
     9. Resource Readiness Gate (পর্যাপ্ত মেমরি নিশ্চিতকরণ)
     10. পরবর্তী Heavy Task অনুমোদন
   - এক্সেপশন ও ক্লিনআপ রুল:
     - টাইমআউট বা ক্র্যাশের পর প্রসেস ক্লিনআপ ব্যর্থ হলেও মূল এক্সেপশন যেন আড়াল না হয় (Exception Chaining ব্যবহার করো)।
     - `finally` ব্লকে মেমরি চেকের ব্যর্থতা মূল টাস্ক এররকে চাপবে না।
   - Queue Reliability Features:
     - Duplicate Task Prevention: Task Parameters ও Project ID হ্যাশ করে আইডেমপোটেন্সি কি নিশ্চিত করা।
     - Task Cancellation: `/api/v1/queue/cancel/{task_id}` এন্ডপয়েন্ট দিয়ে রানিং ওয়ার্কার সাবপ্রসেস ও চাইল্ড প্রসেসে গ্রেসফুল টার্মিনেশন পাঠানো।
     - Retry Limit: রিকভারেবল এররে সর্বোচ্চ ২ বার রিট্রাই; Out-Of-Memory (OOM) এররে ০ রিট্রাই (সরাসরি টার্মিনেশন)।
     - Stale Task Recovery: স্টার্টআপে রানিং থাকা কিন্তু বাস্তবে কোনো জীবন্ত প্রসেস না থাকা ডেড টাস্ক শনাক্তকরণ।
৬. Constraints:
   - মেমরি ক্লিনআপ ১০০% র‍্যাম ফাঁকা করে—এমন অবাস্তব দাবি নিষিদ্ধ।
৭. Error Handling:
   - টাইমআউটে `TimeoutError` এবং OOM-এ `ResourceExhaustionError` রেইজ করো।
৮. Security Requirements:
   - সাবপ্রসেস আর্গুমেন্ট স্যানিটাইজেশন (Command Injection প্রতিরোধ)।
৯. Acceptance Criteria:
   - ইভেন্ট লুপ ফ্রিজ হবে না। উইন্ডোজ চাইল্ড প্রসেস নিশ্চিতভাবে টার্মিনেট হবে।
১০. Test Requirements:
    - `tests/test_queue.py`: ডুপ্লিকেট টাস্ক প্রিভেনশন, ক্যান্সেলেশন, টাইমআউট, OOM জিরো রিট্রাই এবং প্রসেস টার্মিনেশনের স্বয়ংক্রিয় টেস্ট।
১১. Expected Deliverables:
    - `app/core/queue.py`, `app/core/memory_manager.py`, এবং `tests/test_queue.py`।
```

---

# 🔄 ফেজ ৫: ৫-ধাপের চেকপয়েন্ট স্টেট মেশিন ও আইডেমপোটেন্ট রিকনসিলিয়েশন

### 🎯 PROMPT 5.1: স্টেট মেশিন, উইন্ডোজ ফাইল লকিং ও কেস A–K রিকনসিলিয়েশন
```text
১. Agent Role: রিলায়াবিলিটি ও ডেটা ইন্টিগ্রিটি ইঞ্জিনিয়ার।
২. Objective: ৫-ধাপের ডিউরেবল চেকপয়েন্ট স্টেট মেশিন ও আইডেমপোটেন্ট স্টার্টআপ রিকনসিলিয়েশন ইঞ্জিন তৈরি করা।
৩. Scope: `app/core/checkpointer.py`, `app/core/manifest.py`, `app/core/reconciliation.py`, `tests/test_checkpointer.py`।
৪. Required Files: `app/core/checkpointer.py`, `app/core/manifest.py`, `app/core/reconciliation.py`, `tests/test_checkpointer.py`।
৫. Technical Requirements:
   - চেকপয়েন্ট স্টেট মেশিন বনাম টাস্ক লাইফসাইকেল পৃথকীকরণ:
     - Durable Commit State: `INTENT → RENDERING → VALIDATED → OUTPUT_COMMITTED → DB_COMMITTED`
     - Task Lifecycle State: `QUEUED → RUNNING → PAUSED → WAITING_FOR_APPROVAL → COMPLETED / FAILED / CANCELLED / RECOVERY_REQUIRED`
   - কঠোর এক্সিকিউশন অর্ডার (`app/core/checkpointer.py`):
     ১. রেন্ডার শুরুর আগে ইউনিক Task ID তৈরি করে `.manifests/[task_id].json` ফাইলে `INTENT` স্টেট সেভ করো।
        (সাইডকার অ্যাটমিক রাইট: `.tmp → flush() → fsync() → close() → os.replace()`)
     ২. ফাইনাল আউটপুটের একই ডিস্ক ভলিউমে `.staging/[task_id].tmp` অস্থায়ী ফাইল তৈরি করো এবং স্টেট `RENDERING` করো।
     ৩. জেনারেটেড কন্টেন্ট রাইট করো $\rightarrow$ `flush()` $\rightarrow$ `os.fsync()`।
     ৪. ফাইল হ্যান্ডেল সঠিকভাবে `close()` করো (উইন্ডোজ ফাইল লকিং প্রিভেনশন)।
     ৫. Output Validation: ফাইলের সাইজ, রানটাইমে ক্যালকুলেটেড প্রকৃত SHA-256 চেকসাম এবং FFprobe দিয়ে কন্টেইনার, কোডেক, ডিউরেশন ও স্ট্রিম ভ্যালিডেশন করো (স্টেট `VALIDATED`)।
     ৬. অ্যাটমিক রিপ্লেস: গন্তব্যে আনভেরিফায়েড ফাইল থাকলে ওভাররাইট প্রতিরোধ করো; এরপর `os.replace(staging_path, final_output_path)` কার্যকর করো (স্টেট `OUTPUT_COMMITTED`)।
     ৭. SQLite ট্রানজ্যাকশন কমিট: সাইডকার ডিস্কে ডিউরেবল হওয়ার পরেই `aiosqlite`-এ টাস্ক স্টেট `COMPLETED` বা `DB_COMMITTED` মার্ক করো (`synchronous=FULL` সহ)।
     ৮. সাইডকার স্টেট সিঙ্ক: DB সফল হওয়ার পর সাইডকার ফাইলে স্টেট `DB_COMMITTED` করো।
   - অথরিটেটিভ কনফ্লিক্ট রুল: ক্র্যাশ রিকভারিতে ভেরিফাইড ডিস্ক মিডিয়া ফাইল ও সাইডকার ম্যানিফেস্ট হলো মিডিয়া ফাইলের চূড়ান্ত সত্য (Physical Ground Truth); SQLite হলো রিলেশনাল ইনডেক্স।
   - স্টার্টআপ রিকনসিলিয়েশন ম্যাট্রিক্স (Case A থেকে K, সম্পূর্ণ আইডেমপোটেন্ট):
     - Case A (DB_COMMITTED, DB COMPLETED, Final File Valid): সম্পূর্ণ ভেরিফাইড; কোনো অ্যাকশন নেই।
     - Case B (OUTPUT_COMMITTED, DB IN_PROGRESS, Final File Valid): ফাস্ট-ফরোয়ার্ড — DB-তে `COMPLETED` কমিট করো এবং সাইডকারে `DB_COMMITTED` আপডেট করো।
     - Case C (VALIDATED / RENDERING, Staging File Valid): ফাইনাল আউটপুটে `os.replace()` করো, সাইডকারে `OUTPUT_COMMITTED` লিখে DB কমিট করো।
     - Case D (RENDERING / INTENT, Staging Corrupted/Incomplete): করাপ্ট ফাইল সরাসরি ডিলিট করা নিষিদ্ধ; এটিকে প্রজেক্টের কোয়ারেন্টিন ফোল্ডারে সরাও: `.staging/quarantine/[task_id]_[timestamp].corrupt`। ম্যানিফেস্ট ও DB-তে `FAILED` মার্ক করো।
     - Case E (Final File Valid, Staging Missing, DB IN_PROGRESS): ফাইনাল ফাইলের SHA-256 চেকসাম সাইডকার মিলিয়ে ভ্যালিড হলে DB-তে `COMPLETED` কমিট করো।
     - Case F (SQLite Commit Failed after Output Replacement): সাইডকার ম্যানিফেস্টের মেটাডাটা ব্যবহার করে DB রেকর্ড রিকনস্ট্রাক্ট করো।
     - Case G (Sidecar Corrupted / Unreadable): শুধু FFprobe পাস করলেই সাইডকার রিবিল্ড করা যাবে না; Task ID, Project ID, Output Path, Size, SHA-256, Output Identity, Format ডাটাবেজের সাথে মিলিয়ে তবেই রিবিল্ড করতে হবে। ডাটাবেজেও রেকর্ড না থাকলে ফাইল কোয়ারেন্টিনে নিয়ে ইউজারকে সতর্ক করো।
     - Case H (DB Record Missing, Sidecar & Final File Valid): সাইডকার ম্যানিফেস্ট থেকে SQLite-এ হারানো ডাটাবেজ রেকর্ড রিকনস্ট্রাক্ট করো।
     - Case I (Destination File Conflict): গন্তব্যে পূর্ববর্তী অপ্রত্যাশিত ফাইল থাকলে ওভাররাইট না করে টাইমস্ট্যাম্প যুক্ত ইউনিক সাফিক্স দাও বা ইউজার কনফার্মেশন চাও।
     - Case J (Path Traversal Attempt): পাথে `..` বা প্রজেক্ট রুটের বাইরের পাথ থাকলে সাথে সাথে সিকিউরিটি এক্সেপশন রেইজ করো।
     - Case K (DB COMPLETED, Sidecar OUTPUT_COMMITTED): SQLite ট্রানজ্যাকশন সফল হওয়ার পর সাইডকার আপডেট ক্র্যাশ করেছিল। রিকনসিলিয়েশন ফাইনাল ফাইল, চেকসাম, Task ID ও Project ID মিলিয়ে সাইডকারে স্টেট `DB_COMMITTED` আপডেট করে রিকনসিলিয়েশন সম্পন্ন করবে।
৬. Constraints:
   - প্রজেক্ট ডিরেক্টরির বাইরে কোনো ফাইল মুভ বা ডিলিট করা সম্পূর্ণ নিষিদ্ধ। সমস্ত রিকনসিলিয়েশন অপারেশন সম্পূর্ণ আইডেমপোটেন্ট (Idempotent) হতে হবে।
৭. Error Handling:
   - ফাইল লক থাকলে উইন্ডোজে নির্দিষ্ট ব্যাকঅফ রিট্রাই।
৮. Security Requirements:
   - প্রজেক্ট রুট কন্টেইনমেন্ট ভ্যালিডেশন (Path Traversal গার্ড)।
৯. Acceptance Criteria:
   - ক্র্যাশের পর ডাটাবেজ ও ফাইলসিস্টেম সম্পূর্ণ সামঞ্জস্যপূর্ণভাবে রিকনসিল হবে।
১০. Test Requirements:
    - `tests/test_checkpointer.py`: করাপ্ট সাইডকার, মিসিং আউটপুট, ডুপ্লিকেট ডেস্টিনেশন, পাথ ট্রাভার্সাল, কোয়ারেন্টিন এবং Case K-এর আইডেমপোটেন্ট টেস্ট।
১১. Expected Deliverables:
    - `app/core/checkpointer.py`, `app/core/manifest.py`, `app/core/reconciliation.py`, এবং `tests/test_checkpointer.py`।
```

---

# 🎛️ ফেজ ৬: অডিও পাইপলাইন ও ৪-ট্র্যাক মিক্সার

### 🎯 PROMPT 6.1: Demucs স্টেম স্প্লিটার ও মাস্টার অডিও ব্যাকআপ
```text
১. Agent Role: অডিও এআই ইঞ্জিনিয়ার ও ডিএসপি প্রোগ্রামার।
২. Objective: Demucs v4 স্টেম স্প্লিটার ইন্টিগ্রেশন এবং মাস্টার অডিও ব্যাকআপ সংরক্ষণ ব্যবস্থা তৈরি করা।
৩. Scope: `app/engines/audio_separator.py`, `tests/test_audio_separator.py`।
৪. Required Files: `app/engines/audio_separator.py`, `tests/test_audio_separator.py`।
৫. Technical Requirements:
   - মূল অরিজিনাল অডিওকে মাস্টার ব্যাকআপ হিসেবে অপরিবর্তিত সংরক্ষণ করতে হবে।
   - Demucs Vocal Stem নিখুঁত স্পিচ আইসোলেটর নয়; এতে গান, হাসি, চিৎকার বা অন্যান্য ভোকাল সাউন্ড এফেক্ট থেকে যেতে পারে (ডকুমেন্টেশনে উল্লেখ করো)।
   - FFmpeg দিয়ে মূল অডিও এক্সট্রাক্ট করে `master_audio.wav` হিসেবে সেভ করো।
   - Demucs রান করে `vocals.wav` এবং `accompaniment.wav` তৈরি করো।
   - মডেল আনলোড এবং মেমরি রিসাইক্লিং করো।
৬. Constraints:
   - অরিজিনাল অডিও ট্র্যাক কোনোভাবেই ডিলিট বা ওভাররাইট করা যাবে না।
৭. Error Handling:
   - Demucs রানটাইম ফেইল করলে মাস্টার অডিও অপরিবর্তিত রেখে এরর হ্যান্ডল করো।
৮. Security Requirements:
   - অডিও এক্সট্রাকশন পাথের কন্টেইনমেন্ট চেক।
৯. Acceptance Criteria:
   - পৃথক ভোকাল ও ব্যাকগ্রাউন্ড ফাইল তৈরি হবে এবং মাস্টার অডিও সংরক্ষিত থাকবে।
১০. Test Requirements:
    - `tests/test_audio_separator.py`: স্টেম সেপারেশন ও মাস্টার অডিও অক্ষুণ্ণ থাকার টেস্ট।
১১. Expected Deliverables:
    - `app/engines/audio_separator.py` এবং `tests/test_audio_separator.py`।
```

### 🎯 PROMPT 6.2: অডিও স্পিড-স্ট্রেচ পেসিং ইঞ্জিন ও ডায়ালগ সেফটি
```text
১. Agent Role: অডিও ডিএসপি ইঞ্জিনিয়ার।
২. Objective: ভিডিওর মোট ফ্রেম সংখ্যা বজায় রেখে সংলাপের গতি স্বাভাবিক করার অডিও স্পিড-স্ট্রেচ পেসিং ইঞ্জিন তৈরি করা।
৩. Scope: `app/engines/timing_sync.py`, `tests/test_timing_sync.py`।
৪. Required Files: `app/engines/timing_sync.py`, `tests/test_timing_sync.py`।
৫. Technical Requirements:
   - মূল ভিডিওর ফ্রেম সংখ্যা এবং মোট ভিডিওর দৈর্ঘ্য কোনোভাবেই পরিবর্তন করা যাবে না।
   - Playback Speed Multiplier: 0.85x (ধীর), 1.00x (স্বাভাবিক), 1.25x (দ্রুত)।
   - এই সীমার মধ্যে অডিও স্ট্রেচ এবং স্বাভাবিক Silence Padding ব্যবহার করো।
   - কোনো অর্থপূর্ণ ডায়ালগ স্বয়ংক্রিয়ভাবে মুছে ফেলা বা ট্রিম করা সম্পূর্ণ নিষিদ্ধ।
   - ডায়ালগ রেঞ্জে না ধরলে `AudioTimingOverflowWarning` দেবে এবং ডায়ালগ ছোট করতে ইউজারের স্পষ্ট অনুমোদন চাইবে।
৬. Constraints:
   - অডিও পিচ বিকৃত না করে WSOLA বা FFmpeg `atempo` ফিল্টার ব্যবহার করো।
৭. Error Handling:
   - টাইমিং ওভারফ্লো হলে পাইপলাইন পজ করে ইউজার রিভিউয়ের জন্য পাঠানো।
৮. Security Requirements:
   - বাফার ওভারফ্লো প্রিভেনশন।
৯. Acceptance Criteria:
   - ভিডিও দৈর্ঘ্য অপরিবর্তিত থাকবে এবং অনুমোদিত রেঞ্জে স্পিড অ্যাডজাস্ট হবে।
১০. Test Requirements:
    - `tests/test_timing_sync.py`: 0.85x - 1.25x স্পিড স্ট্রেচ ও ওভারফ্লো ওয়ার্নিং টেস্ট।
১১. Expected Deliverables:
    - `app/engines/timing_sync.py` এবং `tests/test_timing_sync.py`।
```

### 🎯 PROMPT 6.3: ৪-ট্র্যাক মিক্সার, লিমিটার ও ক্লিপিং গার্ড
```text
১. Agent Role: অডিও সিস্টেম ইঞ্জিনিয়ার ও মিক্সিং স্পেশালিস্ট।
২. Objective: ৪টি ট্র্যাকসহ ইন্টারঅ্যাক্টিভ অডিও মিক্সার, মাস্টার লিমিটার ও ক্লিপিং ডিটেক্টর তৈরি করা।
৩. Scope: `app/engines/compositor.py`, `tests/test_compositor.py`।
৪. Required Files: `app/engines/compositor.py`, `tests/test_compositor.py`।
৫. Technical Requirements:
   - ৪টি অডিও ট্র্যাক:
     - Track 1: Original Audio Backup (ডুপ্লিকেট সাউন্ড এড়াতে ডিফল্টভাবে MUTED থাকবে, ভলিউম 1.0, প্যান 0.0)।
     - Track 2: Demucs Vocal Stem (আলাদা করা ভোকাল, ভলিউম 1.0, প্যান 0.0)।
     - Track 3: Demucs Accompaniment Stem (পরিবেশ ও ব্যাকগ্রাউন্ড শব্দ, ভলিউম 1.0, প্যান 0.0)।
     - Track 4: New AI Voice (নতুন জেনারেটেড ভয়েস, ভলিউম 1.0, প্যান 0.0)।
   - প্রতি ট্র্যাকে Volume Slider (0-150%), Mute, Solo ও Pan (-1.0 to +1.0) কন্ট্রোল।
   - মাস্টার আউটপুট সেফটি:
     - Master Volume (0-150%, default 1.0)।
     - Master Level Telemetry: -60.0 to +6.0 dBFS (TypeScript: masterLevelDb <-> Backend/SQLite: master_level_dbfs)।
     - Peak Clipping Detection: 0 dBFS ক্লিপিং শনাক্তকরণ এবং ফ্রন্টএন্ডে ভিজ্যুয়াল ওয়ার্নিং প্রেরণ।
     - Hard Limiter: -0.5 dBFS সিলিং সহ ডিফল্টভাবে সক্রিয় থাকবে।
     - Loudness Normalizer: EBU R128 স্ট্যান্ডার্ড অনুযায়ী -16.0 LUFS টার্গেটে নরমালাইজেশন।
   - বাস্তব সীমাবদ্ধতা: লিমিটার ও নরমালাইজার ক্লিপিং ঝুঁকি কমায়, কিন্তু এটি অডিও ডিসটর্শন সম্পূর্ণ দূর করার অলীক গ্যারান্টি দেয় না।
৬. Constraints:
   - মিক্সড অডিওর স্যাম্পল রেট ৪৪.১ বা ৪৮ kHz-এ লকড রাখা।
৭. Error Handling:
   - ক্লিপিং হলে লগ ও মেটাডাটাতে `PeakClippingWarning` ফ্ল্যাগ যুক্ত করা।
৮. Security Requirements:
   - অডিও টেম্পোরারি ফাইল স্যানিটাইজেশন।
৯. Acceptance Criteria:
   - ৪টি ট্র্যাক সফলভাবে মিক্স হবে এবং লেভেল টেলিমেট্রি জেনারেট হবে।
১০. Test Requirements:
    - `tests/test_compositor.py`: ৪-ট্র্যাক ব্যালেন্সিং, ক্লিপিং ডিটেকশন ও লিমিটারের টেস্ট।
১১. Expected Deliverables:
    - `app/engines/compositor.py` এবং `tests/test_compositor.py`।
```

---

# 🎭 ফেজ ৭: MODE 01 — ফানি ভিডিও ডাবিং পাইপলাইন

### 🎯 PROMPT 7.1: প্রি-প্রসেসিং ইনপেইন্টিং (OpenCV vs LaMa) ও ভিডিও কনটেক্সট অ্যানালাইসিস
```text
১. Agent Role: কম্পিউটার ভিশন ইঞ্জিনিয়ার।
২. Objective: Mode 01-এর জন্য অনুমতিপ্রাপ্ত কন্টেন্টের ওয়াটারমার্ক রিমুভাল ও স্ক্রিপ্ট তৈরির কনটেক্সট বিশ্লেষণ তৈরি করা।
৩. Scope: `app/engines/inpainter.py`, `app/modes/mode01_dubbing.py` (পার্ট ১), `tests/test_mode01_pipeline.py`।
৪. Required Files: `app/engines/inpainter.py`, `app/modes/mode01_dubbing.py`, `tests/test_mode01_pipeline.py`।
৫. Technical Requirements:
   - OpenCV Inpainting (Navier-Stokes / Telea) হলো বেসিক সিপিইউ ফলব্যাক ইঞ্জিন। প্রসেসিং সময় হার্ডওয়্যার ও মাস্ক রেজোলিউশন অনুযায়ী পরিবর্তিত হবে। মুভিং অবজেক্ট, বড় টেক্সট বা জটিল ব্যাকগ্রাউন্ড মোছার কোনো নিশ্চয়তা নেই।
   - LaMa হলো অপশনাল অ্যাডভান্সড লোকাল ইঞ্জিন; চালুর আগে ন্যূনতম ৪ জিবি জিপিইউ মেমরি ও কমার্শিয়াল লাইসেন্স প্রিফ্লাইট গেটে যাচাই করো। ইঞ্জিন অনুপলব্ধ থাকলে UI-তে 'UNAVAILABLE' দেখাও।
   - আসল ভিডিও কখনোই ওভাররাইট করা যাবে না।
   - ইনপেইন্টিং কোয়ালিটি কম হলে `LowConfidenceInpaintingWarning` জারি করো।
   - কী-ফ্রেম এক্সট্রাক্ট করে স্ক্রিপ্ট তৈরি: জেমিনি সম্পূর্ণ `VERIFIED_FREE` থাকলে তা দিয়ে স্ক্রিপ্ট তৈরি করো। অন্যথায় Local LLM বা রুল-বেসড Local Script Engine-এ ফলব্যাক করো। জেমিনি কখনোই নিশ্চিত বা বাধ্যতামূলক নয়।
৬. Constraints:
   - অনুমতিহীন কন্টেন্টের কপিরাইট ফাঁকি দেওয়ার উদ্দেশ্যে ব্যবহার নিষিদ্ধ।
৭. Error Handling:
   - ইনপেইন্টিং ব্যর্থ হলে আসল ভিডিও ফ্রেম ব্যবহার করে প্রসেসিং বজায় রাখা।
৮. Security Requirements:
   - ফ্রেম ডিরেক্টরি পাথ কন্টেইনমেন্ট।
৯. Acceptance Criteria:
   - ইনপেইন্টেড ভিডিও তৈরি হবে এবং স্ক্রিপ্ট জেনারেট হবে।
১০. Test Requirements:
    - `tests/test_mode01_pipeline.py`: OpenCV ফলব্যাক ও স্ক্রিপ্ট অটো-সিলেকশন টেস্ট।
১১. Expected Deliverables:
    - `app/engines/inpainter.py`, `app/modes/mode01_dubbing.py`, এবং `tests/test_mode01_pipeline.py`।
```

### 🎯 PROMPT 7.2: সার্বজনীন ভয়েস অ্যাপ্রুভাল গেটওয়ে ও ৫টি স্ট্যান্ডার্ড আউটপুট ভাষা
```text
১. Agent Role: ফুল পাইপলাইন ও ইন্টিগ্রেশন ইঞ্জিনিয়ার।
২. Objective: Mode 01-এর ভয়েস গেটওয়ে, লিপ-সিঙ্ক ও ৫-ভাষার রেন্ডারিং পাইপলাইন সম্পন্ন করা।
৩. Scope: `app/modes/mode01_dubbing.py` (পার্ট ২), `app/api/routes_approval.py`, `tests/test_mode01_pipeline.py`।
৪. Required Files: `app/modes/mode01_dubbing.py`, `app/api/routes_approval.py`, `tests/test_mode01_pipeline.py`।
৫. Technical Requirements:
   - সার্বজনীন ভয়েস অ্যাপ্রুভাল পলিসি (Unified Voice Approval Policy) ও ডুয়াল-স্ক্রিপ্ট নীতি:
     - আপলোড করা ভিডিওতে কথা/সংলাপ থাকলে তা বিশ্লেষণ করে হাসির বাংলা ভাবানুবাদ (`translation_script_text`) তৈরি করা হবে যা চরিত্রের কথা বলার টাইমিংয়ের সাথে মিলে যাবে।
     - ভিডিওতে কথা না থাকলে (সাইলেন্ট/এনিম্যাল/মিউজিক) পুরো ব্যাপ্তির ওপর ভিত্তি করে মৌলিক কমেডি ধারাভাষ্য (`commentary_script_text`) তৈরি করা হবে।
     - উভয় স্ক্রিপ্টই প্রস্তুত থাকবে এবং গেটওয়েতে ১-ক্লিক সোয়াপ বাটনের মাধ্যমে অদলবদল করা যাবে।
     - AI Voice অথবা Real Voice — উভয় ক্ষেত্রেই ফাইনাল ভিডিও এক্সপোর্টের পূর্বে বাস্তব অডিও প্লেব্যাক প্রিভিউ ও ব্যবহারকারীর সুস্পষ্ট অনুমোদন (Approval / Permission) বাধ্যতামূলক।
     - অনুমোদন ছাড়া ফাইনাল রেন্ডার কোনো অবস্থাতেই শুরু হবে না (`WAITING_FOR_VOICE_APPROVAL` স্ট্যাটাস)।
     - ব্যবহারকারী চাইলে Regenerate, ডায়ালগ Edit, অথবা Re-Preview করতে পারবেন।
     - Approval Status ডাটাবেজ ও টাস্ক স্টেটে সংরক্ষিত থাকবে।
   - একীভূত আউটপুট ভাষা ম্যাট্রিক্স (ঠিক ৫টি নির্দিষ্ট অপশন; কোনো "ইত্যাদি" নেই):
     ১. `Bangla` -> ১টি বাংলা ভিডিও
     ২. `Hindi` -> ১টি হিন্দি ভিডিও
     ৩. `English` -> ১টি ইংরেজি ভিডিও
     ৪. `Bangla + Hindi` -> ২টি আলাদা ভিডিও
     ৫. `Bangla + Hindi + English` -> ৩টি আলাদা ভিডিও
     *শুধু নির্বাচিত ভাষার আউটপুটই এক্সপোর্ট হবে।*
   - ভিডিও রেজোলিউশন ও রেন্ডার:
     - সোর্স রেজোলিউশন ও সোর্স অ্যাসপেক্ট রেশিও হুবহু অক্ষুণ্ণ রাখবে; জোরপূর্বক 1080p তে রূপান্তর করবে না।
     - Wav2Lip বা লোকাল লিপ-সিঙ্ক ইঞ্জিন উপলব্ধ থাকলে লিপ-সিঙ্ক করো; অনুপলব্ধ থাকলে লিপ-সিঙ্ক `UNAVAILABLE` রেখে ভয়েস ওভারলে সহ FFmpeg H.264 MP4 এক্সপোর্ট করো।
৬. Constraints:
   - অনুমোদন ছাড়া রেন্ডারিং শুরু করা কঠোরভাবে নিষিদ্ধ।
৭. Error Handling:
   - রেন্ডারিং ক্র্যাশ হলে চেকপয়েন্ট স্টেটে সেভ রেখে রিকনসিলিয়েশন অনুমোদন করা।
৮. Security Requirements:
   - আউটপুট ফাইল পাথ কন্টেইনমেন্ট।
৯. Acceptance Criteria:
   - অ্যাপ্রুভাল গেট কার্যকর হবে এবং নির্বাচিত ভাষার MP4 ফাইল রেন্ডার হবে।
১০. Test Requirements:
    - `tests/test_mode01_pipeline.py`: ভয়েস অ্যাপ্রুভাল গেটওয়ে ও ভাষা ম্যাট্রিক্স টেস্ট।
১১. Expected Deliverables:
    - `app/modes/mode01_dubbing.py`, `app/api/routes_approval.py`, এবং `tests/test_mode01_pipeline.py`।
```

---

# 🎨 ফেজ ৮: MODE 02 — কার্টুন ভিডিও রিক্রিয়েশন স্টুডিও

### 🎯 PROMPT 8.1: কার্টুন রিক্রিয়েশন, ভয়েস অপশন ও ডেল্টা রি-রেন্ডার
```text
১. Agent Role: ভিডিও এআই ইঞ্জিনিয়ার ও অ্যানিমেশন পাইপলাইন স্পেশালিস্ট।
২. Objective: Mode 02 (Cartoon Video Re-Creation Studio)-এর মিনিং-প্রিজার্ভিং রূপান্তর, ভয়েস অপশন ও ১-ক্লিক ডেল্টা অডিও সোয়াপ তৈরি করা।
৩. Scope: `app/engines/transcriber.py`, `app/modes/mode02_cartoon.py`, `tests/test_mode02_cartoon.py`।
৪. Required Files: `app/engines/transcriber.py`, `app/modes/mode02_cartoon.py`, `tests/test_mode02_cartoon.py`।
৫. Technical Requirements:
   - মূল ভিডিওর দৃশ্য, সিকোয়েন্স ও অ্যাকশন বজায় রেখে সংলাপের মূল ভাবার্থ রূপান্তর (Meaning-preserving adaptation)।
   - ক্যারেক্টার ফেস এমবেডিং রেফারেন্স শিট তৈরি করে সিন কাটেও মুখের সামঞ্জস্য বজায় রাখো। ইঞ্জিন উপলব্ধ না থাকলে UNAVAILABLE দেখাও।
   - ভয়েস অপশন নীতি:
     - Option A: Real Voice (আসল অডিও সিঙ্ক হবে; ইউজারের বৈধ অধিকার থাকতে হবে)।
     - Option B: AI Voice (বিকল্প নতুন সিন্থেটিক ভয়েস; এটি কপিরাইট-মুক্তির অলীক গ্যারান্টি নয়)।
   - সার্বজনীন ভয়েস অ্যাপ্রুভাল পলিসি: Real Voice বা AI Voice যেটাই নির্বাচিত হোক না কেন, ফাইনাল রেন্ডারের আগে প্লেব্যাক প্রিভিউ ও ইউজার অ্যাপ্রুভাল বাধ্যতামূলক।
   - ১-ক্লিক ডেল্টা অডিও রি-রেন্ডার: কার্টুন ফ্রেম ও অডিও আলাদা ক্যাশে থাকবে। Real Voice থেকে AI Voice-এ মুহূর্তের মধ্যে অডিও সোয়াপ করা যাবে।
   - একীভূত আউটপুট ভাষা ম্যাট্রিক্স (ঠিক ৫টি অপশন):
     ১. `Bangla`, ২. `Hindi`, ৩. `English`, ৪. `Bangla + Hindi`, ৫. `Bangla + Hindi + English`।
৬. Constraints:
   - নতুন কাল্পনিক গল্প বা অপ্রাসঙ্গিক দৃশ্য তৈরি করা নিষিদ্ধ।
৭. Error Handling:
   - ট্রান্সক্রিপশন ব্যর্থ হলে ইউজারকে ম্যানুয়াল টেক্সট ইনপুটের সুযোগ দেওয়া।
৮. Security Requirements:
   - রাইটস ওয়ার্নিং ও ক্যাশ আইসোলেশন।
৯. Acceptance Criteria:
   - কার্টুন ফ্রেম ও অডিও ক্যাশ আলাদা থাকবে এবং ১-ক্লিকে অডিও সোয়াপ কাজ করবে।
১০. Test Requirements:
    - `tests/test_mode02_cartoon.py`: ট্রান্সক্রিপশন, ডেল্টা সোয়াপ ও অ্যাপ্রুভাল গেটের টেস্ট।
১১. Expected Deliverables:
    - `app/engines/transcriber.py`, `app/modes/mode02_cartoon.py`, এবং `tests/test_mode02_cartoon.py`।
```

---

# 🤖 ফেজ ৯: MODE 03 — অটোনোমাস কন্টেন্ট ক্রিয়েটর স্টুডিও

### 🎯 PROMPT 9.1: Mode 03 ইঞ্জিন রেজিস্ট্রি ও অটোনোমাস পাইপলাইন
```text
১. Agent Role: জেনারেটিভ পাইপলাইন ইঞ্জিনিয়ার।
২. Objective: Mode 03 (AI Autonomous Content Creator)-এর রিয়েল ইঞ্জিন অ্যাভেইলেবিলিটি গেট ও অটোনোমাস পাইপলাইন তৈরি করা।
৩. Scope: `app/modes/mode03_autonomous.py`, `tests/test_mode03_autonomous.py`।
৪. Required Files: `app/modes/mode03_autonomous.py`, `tests/test_mode03_autonomous.py`।
৫. Technical Requirements:
   - Engine Availability Gate:
     - যদি লোকাল স্টেবল ডিফিউশন বা ফ্রি মডেল পিসিতে কনফিগার না থাকে, তবে ভিজ্যুয়াল জেনারেশনকে 'UNAVAILABLE' হিসেবে মার্ক করো।
     - স্লাইডশো বা Ken Burns ইফেক্টকে কখনোই "Full AI 3D Animation" হিসেবে উপস্থাপন করবে না; ভিজ্যুয়াল ইঞ্জিন না থাকলে তা স্পষ্টভাবে জানাও।
   - পাইপলাইন ফ্লো:
     ১. টপিক/আইডিয়া ইনপুট নেওয়া।
     ২. স্ক্রিপ্ট তৈরি: জেমিনি VERIFIED_FREE হলে ক্লাউড, অন্যথায় Local LLM বা Local Script Engine (জেমিনি আবশ্যক নয়)।
     ৩. টিটিএস দিয়ে ভয়েস জেনারেশন।
     ৪. সার্বজনীন ভয়েস অ্যাপ্রুভাল পলিসি: ফাইনাল ভিডিও রেন্ডারের আগে প্লেব্যাক প্রিভিউ শুনে ব্যবহারকারীর অনুমোদন বাধ্যতামূলক।
     ৫. ভিজ্যুয়াল অ্যাসেম্বলি (উপলব্ধ ওপেন-সোর্স ইঞ্জিন থাকলে)।
     ৬. একীভূত আউটপুট ভাষা ম্যাট্রিক্স অনুযায়ী এক্সপোর্ট (Bangla, Hindi, English, Bangla+Hindi, Bangla+Hindi+English)।
৬. Constraints:
   - অসমর্থিত ফিচার বানিয়ে নেওয়ার ভান করা বা স্বয়ংক্রিয়ভাবে পেইড ক্লাউড জেনারেটর কল করা নিষিদ্ধ।
7. Error Handling:
   - ভিজ্যুয়াল ইঞ্জিন অনুপস্থিতিতে অডিও-অনলি বা স্ট্যাটিক মন্টাজ মোডে গ্রেসফুল ফলব্যাক।
৮. Security Requirements:
   - স্ক্রিপ্ট ইনপুট স্যানিটাইজেশন।
৯. Acceptance Criteria:
   - ইঞ্জিন অনুপস্থিত থাকলে UNAVAILABLE দেখাবে এবং ভয়েস অ্যাপ্রুভাল ছাড়া রেন্ডার হবে না।
১০. Test Requirements:
    - `tests/test_mode03_autonomous.py`: ইঞ্জিন অ্যাভেইলেবিলিটি গেট ও স্ক্রিপ্ট ফলব্যাক টেস্ট।
১১. Expected Deliverables:
    - `app/modes/mode03_autonomous.py` এবং `tests/test_mode03_autonomous.py`।
```

---

# 🏛️ ফেজ ১০: ট্রেনিং সেন্টার কোর ও শেয়ার্ড রিপোজিটরি

### 🎯 PROMPT 10.1: শেয়ার্ড ট্রেনিং সেন্টার কোর ও রি-ইউজেবল প্রোফাইল হাব
```text
১. Agent Role: সিস্টেম আর্কিটেক্ট ও প্রোফাইল ডাটাবেজ ইঞ্জিনিয়ার।
২. Objective: Layer 4: Shared Training Center Core এবং রি-ইউজেবল এসেট হাব তৈরি করা।
৩. Scope: `app/core/training_center.py`, `app/api/routes_training.py`, `tests/test_training_center.py`।
৪. Required Files: `app/core/training_center.py`, `app/api/routes_training.py`, `tests/test_training_center.py`।
৫. Technical Requirements:
   - ট্রেনিং সেন্টার কোনো মডেল ফাইন-টিউনিং বা রি-ট্রেনিং সিস্টেম নয়। এটি কোনো আলাদা প্রোডাকশন মোড ১২ নয়।
   - সঠিক শব্দ ও মেকানিজম ব্যবহার করো:
     - AI-assisted reference analysis
     - Reusable comedy style profiles
     - Dialogue pattern profiles
     - Punchline timing preferences
     - Voice profiles
     - Character consistency sheets
     - Reference video library
     - Custom SFX/BGM presets
   - `app/core/training_center.py` তৈরি করো যা রেফারেন্স ভিডিও বিশ্লেষণ করে রি-ইউজেবল প্রোফাইল সংরক্ষণ করবে।
   - `app/api/routes_training.py`-তে এন্ডপয়েন্ট তৈরি করো যাতে মোড ০১, ০২, ০৩ প্রজেক্ট তৈরির সময় এই প্রোফাইলগুলো ব্যবহার করতে পারে।
৬. Constraints:
   - কোনো ভারী ব্যাকপ্রোপাগেশন বা GPU ফাইন-টিউনিং কোড লেখা নিষিদ্ধ।
৭. Error Handling:
   - করাপ্ট রেফারেন্স ভিডিও আপলোড হলে ভ্যালিডেশন এরর দেওয়া।
৮. Security Requirements:
   - প্রোফাইল ফাইল কন্টেইনমেন্ট।
৯. Acceptance Criteria:
   - প্রোফাইল সেভ ও লোড হবে এবং মোড ০১-০৩ থেকে এক্সেস করা যাবে।
১০. Test Requirements:
    - `tests/test_training_center.py`: প্রোফাইল ক্রিয়েশন ও রি-ইউজ টেস্ট।
১১. Expected Deliverables:
    - `app/core/training_center.py`, `app/api/routes_training.py`, এবং `tests/test_training_center.py`।
```

---

# 🌐 ফেজ ১১: REST এপিআই, ওয়েবসকেট ও FASTAPI সার্ভার

### 🎯 PROMPT 11.1: সম্পূর্ণ FastAPI এন্ডপয়েন্ট ও লাইভ ওয়েবসকেট
```text
১. Agent Role: সিনিয়র এপিআই ও রিয়েলটাইম আর্কিটেক্ট।
২. Objective: সমস্ত ব্যাকএন্ড মডিউলকে একক পোর্ট 8000-এ এপিআই ও লাইভ ওয়েবসকেটে যুক্ত করা।
৩. Scope: `app/main.py`, `app/api/routes_projects.py`, `app/api/routes_settings.py`, `app/api/websocket.py`, `tests/test_api_endpoints.py`।
৪. Required Files: `app/main.py`, `app/api/routes_projects.py`, `app/api/routes_settings.py`, `app/api/websocket.py`, `tests/test_api_endpoints.py`।
৫. Technical Requirements:
   - `app/api/routes_projects.py`: প্রজেক্ট তৈরি, স্ট্যাটাস, বিস্তারিত ও চেকপয়েন্ট রিজিউম এন্ডপয়েন্ট।
   - `app/api/routes_settings.py`: ভেরিফায়েড ফ্রি মডেলের তালিকা, কী ম্যানেজমেন্ট (api_key_fingerprint সহ) ও লাইভ রিসোর্স স্ট্যাটাস।
   - `app/api/websocket.py`: কিউ পজিশন, কারেন্ট স্টেপ, অডিও লেভেল মিটার ডাটা, টাইমিং ওভারফ্লো ওয়ার্নিং ও কোটা পজ অ্যালার্ট স্ট্রিমিং।
   - `app/main.py`:
     - কঠোরভাবে শুধুমাত্র `127.0.0.1:8000`-এ বাইন্ড। পোর্ট ব্যস্ত থাকলে কোনো ফলব্যাক পোর্ট নয়, নিরাপদ এরর দিয়ে টার্মিনেট করবে।
     - স্টার্টআপ রিকনসিলিয়েশন লুপ কল (Case A থেকে K)।
     - হোস্ট হেডার (`127.0.0.1:8000`, `localhost:8000`) ও অরিজিন সিকিউরিটি মিডলওয়্যার।
     - বিল্ট ফ্রন্টএন্ড (`frontend/dist`) স্ট্যাটিক ফাইল হিসেবে রুট পাথে (`/`) সার্ভ করো।
৬. Constraints:
   - কোনো ফলব্যাক পোর্টে রান করা নিষিদ্ধ।
৭. Error Handling:
   - গ্লোবাল এক্সেপশন হ্যান্ডলার দিয়ে ইউনিফাইড JSON এরর রেসপন্স।
৮. Security Requirements:
   - CSRF ও Origin চেক সমস্ত এন্ডপয়েন্টে কার্যকর।
৯. Acceptance Criteria:
   - সার্ভার 8000 পোর্টে রান হবে এবং ওয়েবসকেট স্ট্রিমিং কাজ করবে।
১০. Test Requirements:
    - `tests/test_api_endpoints.py`: REST রুটস ও ওয়েবসকেট কানেকশন টেস্ট।
১১. Expected Deliverables:
    - `app/main.py`, সম্পূর্ণ `app/api/` মডিউল এবং `tests/test_api_endpoints.py`।
```

---

# 💻 ফেজ ১২: প্রেজেন্টেশন লেয়ার (VITE + REACT + TAILWIND)

### 🎯 PROMPT 12.1: সিঙ্গেল-পোর্ট রেসপনসিভ ড্যাশবোর্ড
```text
১. Agent Role: সিনিয়র ফ্রন্টএন্ড ইঞ্জিনিয়ার ও UI/UX স্পেশালিস্ট।
২. Objective: Vite + React + TypeScript + Tailwind CSS দিয়ে সিঙ্গেল-পোর্ট রেসপনসিভ ড্যাশবোর্ড তৈরি করা।
৩. Scope: `frontend/` ডিরেক্টরি, SPA কম্পোনেন্টস, TypeScript স্কিমা ও বিল্ড কনফিগ।
৪. Required Files: `frontend/package.json`, `frontend/src/App.tsx`, `frontend/src/types/`, `frontend/src/components/`।
৫. Technical Requirements:
   - সমস্ত API এবং WebSocket রিকোয়েস্ট সরাসরি `http://127.0.0.1:8000`-এ পাঠাতে হবে। কোনো পৃথক রানটাইম পোর্ট (যেমন 5173 বা 7860) থাকবে না।
   - ফ্রন্টএন্ড বিল্ড হয়ে `frontend/dist` ডিরেক্টরিতে জমা হবে যা FastAPI ব্যাকএন্ড সরাসরি সার্ভ করবে।
   - TypeScript camelCase স্কিমা definitions (`AudioMixerState`, `Project`, `ModelRegistry` ব্যাকএন্ডের সাথে ফিল্ড-বাই-ফিল্ড সিঙ্কড)।
   - ড্যাশবোর্ড UI:
     - ১১টি মোড কার্ড (P1 Active, P2 Planned, P3 Planned, P4 Future ব্যাজ সহ)।
     - P2-P4 মোডগুলো আনভেরিফায়েড অবস্থায় ডিজেবল থাকবে।
     - লাইভ প্রসেসিং বার ও কিউ মনিটর।
   - Voice Approval Studio:
     - সমস্ত P1 মোডের জন্য প্লেব্যাক প্রিভিউ প্লেয়ার, ডায়ালগ এডিটর ও 'Approve Voice' বাটন।
   - ৪-ট্র্যাক অডিও মিক্সার:
     - Track 1 (Original Backup - Muted toggle), Track 2 (Vocal), Track 3 (Accompaniment), Track 4 (AI Voice)।
     - ভলিউম (0-150%), Mute, Solo ও Pan স্লাইডার।
     - Master Output Level Meter (`masterLevelDb`: -60 to +6 dBFS) ও ভিজ্যুয়াল Peak Clipping Warning।
     - Hard Limiter ও Normalizer টগল।
   - সেটিংস মোডাল: জেমিনি কী ইনপুট (`api_key_fingerprint` প্রদর্শন), ফ্রি মডেল ড্রপডাউন, অফলাইন মোড টগল এবং ডেটা প্রাইভেসি ডিসক্লোজার।
৬. Constraints:
   - কোনো এক্সটার্নাল সিডিএন বা আনট্রাস্টেড থার্ড-পার্টি স্ক্রিপ্ট লোড নিষিদ্ধ।
৭. Error Handling:
   - ওয়েবসকেট ডিসকানেক্ট হলে অটোমেটিক রিকানেক্ট ও UI ব্যানার।
৮. Security Requirements:
   - এক্সএসএস (XSS) স্যানিটাইজেশন।
৯. Acceptance Criteria:
   - বিল্ড ফাইল FastAPI থেকে সার্ভ হবে এবং সমস্ত কন্ট্রোল কাজ করবে।
১০. Test Requirements:
    - কম্পোনেন্ট রেন্ডারিং ও অডিও মিক্সার স্টেট টেস্ট।
১১. Expected Deliverables:
    - সম্পূর্ণ `frontend/` সোর্স কোড ও প্রোডাকশন বিল্ড কনফিগ।
```

---

# 📦 ফেজ ১৩: উইন্ডোজ লঞ্চার ও তৌরি প্যাকেজিং (Phase 2 Readiness)

> [!NOTE]
> **তৌরি প্যাকেজিং সিদ্ধান্ত (Tauri Decision Gate):**  
> তৌরি বিল্ড P1 রিলিজের জন্য বাধ্যতামূলক নয়। Release Phase P2 শুরু হওয়ার পূর্বে একটি সুনির্দিষ্ট স্ট্র্যাটেজি নির্বাচন করতে হবে (Standalone Embedded Python বনাম PyInstaller; দুটি একসাথে নয়)। এই ফেজটি P2-এর জন্য প্রস্তুতিমূলক আর্কিটেকচার ও প্রোটোটাইপ হিসেবে অন্তর্ভুক্ত।

### 🎯 PROMPT 13.1: এক ক্লিকে উইন্ডোজ লঞ্চার ও তৌরি আর্কিটেকচারাল প্রোটোটাইপ
```text
১. Agent Role: ডেস্কটপ অ্যাপ্লিকেশন ও প্যাকেজিং স্পেশালিস্ট।
২. Objective: প্রজেক্টের জন্য Windows ব্যাচ লঞ্চার এবং Tauri v2 ডেস্কটপ প্রোটোটাইপ কনফিগারেশন তৈরি করা।
৩. Scope: `run_studio.bat`, `src-tauri/` কনফিগারেশন।
৪. Required Files: `run_studio.bat`, `src-tauri/tauri.conf.json`, `src-tauri/src/main.rs`।
৫. Technical Requirements:
   - প্রজেক্টের রুটে `run_studio.bat` তৈরি করো যা পাইথন, এনভায়রনমেন্ট ও FFmpeg বাইনারি চেক করে একক পোর্ট `http://127.0.0.1:8000` চালু করবে এবং ব্রাউজার ওপেন করবে।
   - Tauri v2 উইন্ডোজ র্যাপার প্রোটোটাইপ কনফিগার করো (`src-tauri/`):
     - প্যাকেজিং স্ট্র্যাটেজি ডিসিশন গেট: Standalone Embedded Python runtime এবং PyInstaller-এর মধ্যে পারফরম্যান্স ও লাইফসাইকেল তুলনা করে একটি নির্দিষ্ট স্ট্র্যাটেজি নির্ধারণ করো।
     - বান্ডেল্ড FFmpeg ও FFprobe স্ট্যাটিক বাইনারি Tauri রিসোর্স ডিরেক্টরিতে অন্তর্ভুক্ত করো।
     - ব্যাকএন্ড হেলথ চেক: অ্যাপ চালুর পর `http://127.0.0.1:8000/api/v1/health` এন্ডপয়েন্টে পোলিং করে ব্যাকএন্ড সক্রিয় হওয়া নিশ্চিত করো।
     - পোর্ট দখল হ্যান্ডলিং: পোর্ট `8000` অধিকৃত থাকলে নেটিভ ওএস ডায়ালগ দেখিয়ে অ্যাপ টার্মিনেট করো (কোনো ফলব্যাক পোর্টে যাবে না)।
     - প্রসেস-ট্রি ক্লিনআপ ও লাইফসাইকেল: Tauri উইন্ডো বন্ধ হলে ব্যাকএন্ড প্রসেস এবং সমস্ত চাইল্ড প্রসেসে গ্রেসফুল শাটডাউন সিগন্যাল পাঠিয়ে পরিচ্ছন্ন এক্সিট নিশ্চিত করো।
৬. Constraints:
   - P1 বাস্তবায়নের জন্য তৌরি বিল্ডকে ব্লকার হিসেবে বিবেচনা করা নিষিদ্ধ।
৭. Error Handling:
   - ব্যাকএন্ড ক্র্যাশ করলে নেটিভ ডায়ালগ দিয়ে ইউজারকে লগ ফাইল লোকেশন দেখানো।
৮. Security Requirements:
   - Tauri স্কোপ ও লোকালহোস্ট রেস্ট্রিকশন।
৯. Acceptance Criteria:
   - `run_studio.bat` এক ক্লিকে ব্যাকএন্ড ও ব্রাউজার চালু করবে; Tauri কনফিগ প্রোটোটাইপ প্রস্তুত থাকবে।
১০. Test Requirements:
    - পোর্ট দখল টেস্ট এবং উইন্ডো ক্লোজ ক্লিনআপ টেস্ট।
১১. Expected Deliverables:
    - `run_studio.bat` এবং `src-tauri/` ডিরেক্টরির কনফিগারেশন ফাইলসমূহ।
```
