# 🏛️ Master System Architecture Specification
### Project: AI Funny Dubbing & Video Production Studio (AI-VPS)
**Document Version:** 2.2  
**Date:** 2026-11-01  
**Scope:** Single-User Personal Local Studio (No Public SaaS)  
**Cost Model:** ZERO EXTRA COST Permanent Hard-Lock Architecture  
**Target Environment:** Local Windows PC (`http://127.0.0.1:8000`) $\rightarrow$ Tauri Desktop Packaging (Phase 2 Target)  

---

## 📚 Supporting Technical Documents & Hierarchy

```
+-----------------------------------------------------------------------------------------+
|                               DOCUMENT HIERARCHY & PRIORITY                             |
|   1. idea.md (v2.0)               — Product Vision, Core Concept & User Requirements    |
|   2. prd.md (v2.2)                — Functional Requirements, Scope & Acceptance Criteria|
|   3. architecture.md (v2.2)       — Technical Architecture, Security & Cost Policy (This)|
|   4. agent.md (v2.4)              — Agent Operational Rules & Engineering Directives    |
|   5. prompt.md (Backend-First)    — Step-by-Step Implementation Execution Prompts       |
+-----------------------------------------------------------------------------------------+
```

> [!IMPORTANT]
> **আর্কিটেকচারাল অথরিটি রুল:** এই স্পেসিফিকেশনের Zero Extra Cost Hard-Lock, সিকিউরিটি বাউন্ডারি, ডাবল ডিউরেবিলিটি পলিসি এবং সিঙ্গেল পোর্ট নীতি কোনো ফাংশনাল রিকোয়ারমেন্ট দ্বারা শিথিল বা ওভাররাইড করা যাবে না।

---

## ১. ওভারভিউ ও মূলনীতি (Core Architectural Principles)

1. **Zero Extra Cost Protection (Permanent Hard-Lock):**
   - সমস্ত Paid API endpoints, Paid AI Providers, Paid Fallback Models, Paid Cloud GPU Services এবং Automatic Billing ব্যাকএন্ড মিডলওয়্যার ও কোড লেভেলে স্থায়ীভাবে হার্ড-লক ও ব্লক থাকবে।
   - কনজিউমার জেমিনি প্রো বা ক্লড প্রো সাবস্ক্রিপশন কোনো ডেভেলপার এপিআই কোটা দেয় না—এমন ভুল ধারণা বা ব্রাউজার সেশন, কুকি বা টোকেন স্ক্র্যাপ করা নিষিদ্ধ।
2. **Local-First Architecture & Storage:**
   - মূল মেটাডাটা ডাটাবেজ হিসেবে SQLite (WAL Mode ও JSON1 সক্রিয় সহ) ব্যবহৃত হবে।
   - সমস্ত ভিডিও, অডিও, ক্যাশ ও মডেল ওয়েটস সরাসরি লোকাল ফাইল সিস্টেমে রিলেটিভ পাথে সংরক্ষিত থাকবে।
   - অনলাইন ডাটা প্রাইভেসি গেটওয়ে: ক্লাউড এপিআই বা অনলাইন টিটিএস ব্যবহারের সময় প্রয়োজনীয় ডাটা ইন্টারনেটে যাওয়ার পূর্বে ব্যবহারকারীর সম্মতি বাধ্যতামূলক।
3. **Resource-Aware Sequential Processing:**
   - সাধারণ পার্সোনাল পিসির মেমরি ক্র্যাশ রোধে ভারী এআই মডেলগুলো কঠোরভাবে Sequential FIFO Queue-তে চলবে।
   - একবারে একটি ভারী মডেল চলবে; টাস্ক শেষে Worker Process Recycling কার্যকর করা হবে।
4. **Dynamic AI Configuration & Fail-Closed Quad-Check:**
   - কোনো নির্দিষ্ট মডেল আইডি বা কোটা হার্ডকোড থাকবে না।
   - মডেল প্রাপ্যতা, ফ্রি টিয়ার অন্তর্ভুক্তি, বিলিং কনফিগারেশন এবং অবশিষ্ট কোটা—এই চারটি বিষয়কে আলাদা স্বাধীন ভ্যালিডেশন হিসেবে দেখা হবে। কোনো তথ্য অস্পষ্ট হলে রিকোয়েস্ট ব্লক থাকবে।
5. **Durable Checkpoint State Machine & Crash Recovery:**
   - ৫-ধাপের স্টেট মেশিন (`INTENT → RENDERING → VALIDATED → OUTPUT_COMMITTED → DB_COMMITTED`) এবং সাইডকার ম্যানিফেস্টের মাধ্যমে ক্র্যাশ-প্রুফ রিকভারি নিশ্চিত করা হবে।

---

## ২. অনুমোদিত ৭টি লেয়ার আর্কিটেকচার (Approved 7-Layer Architecture)

```
+-----------------------------------------------------------------------------------------+
|                               LAYER 1: PRESENTATION LAYER                               |
|   • Frontend: Vite + React + TypeScript + Tailwind CSS                                  |
|   • Localhost Dashboard: http://127.0.0.1:8000 (একক স্থায়ী পোর্ট)                     |
|   • UI Features: ১১টি প্রোডাকশন মোড কার্ড, অডিও প্রিভিউ/মিক্সার, লাইভ কিউ প্রগ্রেস       |
+-----------------------------------------------------------------------------------------+
                                             ↕ (REST API ও WebSockets)
+-----------------------------------------------------------------------------------------+
|                        LAYER 2: APPLICATION & ORCHESTRATION LAYER                       |
|   • Backend Framework: Python 3.10+ & FastAPI (127.0.0.1:8000-এ সীমাবদ্ধ)               |
|   • Security: Host Header, Strict Origin, CSRF, DNS Rebinding, Windows Credential Store |
|   • Non-blocking Worker Supervisor: asyncio.create_subprocess_exec + Process Recycling  |
|   • State Checkpointer: ৫-ধাপের চেকপয়েন্ট স্টেট মেশিন ও আইডেমপোটেন্ট রিকনসিলিয়েশন   |
|   • Parallel Lightweight Tasks: UI, SQLite DB ও ফাইল অপারেশনস সমান্তরালভাবে সচল       |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                        LAYER 3: LOCAL STORAGE & DATABASE LAYER                          |
|   • Database (Metadata Only): SQLite (aiosqlite, WAL Mode, JSON1)                       |
|   • Dual Durability Policy: Critical Checkpoints=FULL, Telemetry/Logs=NORMAL            |
|   • Local Filesystem: ভিডিও, অডিও, .staging, .manifests, quarantine ও মডেল ওয়েটস        |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 4: SHARED TRAINING CENTER CORE                           |
|   (Shared Infrastructure — ১১টি মোডের জন্য সার্বজনীন প্রোফাইল ও এসেট হাব, কোনো মোড ১২ নয়)|
|   • Voice Profiles, Character Reference Sheets, Comedy Style Profiles, SFX/BGM Presets  |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                         LAYER 5: SMART HYBRID AI PROVIDER LAYER                         |
|   [Zero-Cost Hard-Lock: কোনো পেইড এপিআই বা অটো-বিলিং কল হবে না]                          |
|   • Optional Google AI Studio Free Tier — available only after successful eligibility    |
|   • Online Optional Engine: Edge-TTS (Internet Required; Free Availability Not Guarant.)|
|   • Local Offline Optional Engines: Demucs v4, Whisper, Bark, Wav2Lip, OpenCV / LaMa   |
|   • Model Commercial License Registry: ২৭টি মেটাডাটা ফিল্ড (ALLOWED/FORBIDDEN/UNCERTAIN)|
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 6: MEDIA COMPOSITOR & AUDIO PIPELINE                     |
|   • Master Audio Track Preservation: আসল অডিও ব্যাকআপ সংরক্ষণ (ডিফল্ট: Muted)           |
|   • Interactive 4-Track Audio Mixer: Backup, Vocal, Accompaniment, AI Voice             |
|   • Master Audio Safety: Master Level Telemetry (-60 to +6 dBFS), Peak Clipping Detector|
|   • Hard Limiter (-0.5 dBFS) ও EBU R128 Loudness Normalizer (-16.0 LUFS)                |
|   • Audio Speed-Stretch Pacing: ফ্রেম নষ্ট না করে 0.85x-1.25x নিরাপদ সিঙ্ক               |
|   • Source Resolution Preservation: সোর্স রেজোলিউশন ও অ্যাসপেক্ট রেশিও অক্ষুণ্ণ রাখা   |
|   • FFmpeg Engine: মাল্টি-অডিও ট্র্যাকসহ নেটিভ H.264 MP4 রেন্ডারিং                      |
+-----------------------------------------------------------------------------------------+
                                             ↕ (Phase 2 Target)
+-----------------------------------------------------------------------------------------+
|                           LAYER 7: LIGHTWEIGHT DESKTOP PACKAGING                        |
|   • Tauri (Rust Core + System WebView2): নেটিভ সিস্টেমে লাইটওয়েট .exe ইনস্টলার         |
|   • প্যাকেজিং স্ট্র্যাটেজি ডিসিশন গেট: Standalone Embedded Python বনাম PyInstaller      |
+-----------------------------------------------------------------------------------------+
```

---

## ৩. গুরুত্বপূর্ণ কোর সাবসিস্টেম ও টেকনিক্যাল স্পেসিফিকেশন

### ৩.১ একক স্থায়ী পোর্ট ও সিকিউরিটি আর্কিটেকচার (`127.0.0.1:8000`)
- **Fixed Binding:** ব্যাকএন্ড কঠোরভাবে শুধুমাত্র `127.0.0.1:8000`-এ বাইন্ড হবে। অন্য কোনো নেটওয়ার্ক ইন্টারফেসে বাইন্ড করা যাবে না।
- **বিল্ট ফ্রন্টএন্ড পরিবেশন:** Vite শুধুমাত্র ডেভেলপমেন্ট ও বিল্ড টুল হিসেবে ব্যবহৃত হবে। রানটাইমে কোনো পৃথক Vite সার্ভার (যেমন `5173`) চলবে না; FastAPI সরাসরি বিল্ট ফ্রন্টএন্ড স্ট্যাটিক ফাইল (`frontend/dist`) রুট পাথে (`/`) সার্ভ করবে।
- **কোনো ফলব্যাক পোর্ট নেই:** পোর্ট ৮০০০ ব্যস্ত থাকলে কোনো বিকল্প পোর্ট (যেমন ৭৮৬০) খোঁজা যাবে না; ব্যবহারকারীকে স্পষ্ট ত্রুটি ডায়ালগ দেখিয়ে অ্যাপ টার্মিনেট করবে।
- **সিকিউরিটি মিডলওয়্যার:**
  - Host Header Allowlist: `127.0.0.1:8000`, `localhost:8000` (DNS Rebinding প্রতিরোধ)।
  - Trusted Origin Allowlist: `http://127.0.0.1:8000`, `http://localhost:8000`, `tauri://localhost`, `http://tauri.localhost`।
  - CSRF প্রটেকশন ও WebSocket Origin হ্যান্ডশেক ভ্যালিডেশন।
  - Wildcard CORS (`*`) সম্পূর্ণ নিষিদ্ধ।
  - Windows Credential Manager হলো ওএস-লেভেল সিকিউর স্টোরেজ (`keyring` পাইথন লাইব্রেরির মাধ্যমে ইন্টারফেসড)। এপিআই কী কখনোই ডাটাবেজ বা লগে প্লেইন টেক্সট থাকবে না; ট্র্যাকিংয়ে `api_key_fingerprint` (SHA-256 ফিঙ্গারপ্রিন্ট) ব্যবহৃত হবে।

### ৩.২ জেমিনি প্রোভাইডার আর্কিটেকচার ও ৩-স্ট্যাটাস ফেইল-সেফ
- **স্পেসিফিকেশন রিভিশন:** Layer 5-এর সংজ্ঞা হবে:
  > **Optional Google AI Studio Free Tier — available only after successful eligibility verification.**
- **চারটি স্বাধীন ভ্যালিডেশন চেক (Quad-Check):**
  1. `Model Availability`: অফিশিয়াল এপিআই (`list_models`) দিয়ে সচল মডেল শনাক্তকরণ।
  2. `Free-tier Eligibility`: অফিশিয়াল ফ্রি মডেল ম্যাপিং ছাড়া এটি `UNKNOWN` থাকবে।
  3. `Billing Configuration`: গুগল এআই স্টুডিও প্রজেক্টে কার্ড যুক্ত আছে কিনা তা এপিআই দেয় না বিধায় এটি `UNKNOWN` থাকবে।
  4. `Remaining Quota`: ব্যালেন্সের কোনো এপিআই নেই; HTTP 429 ও Retry-After হলো রিঅ্যাক্টিভ টেলিমেট্রি। ব্যালেন্স `UNKNOWN` থাকবে।
- **সিস্টেম স্ট্যাটাস ট্রায়াঙ্গেল:**
  - `VERIFIED_FREE`: শতভাগ নিশ্চিত হলে ক্লাউড কল হবে।
  - `MANUAL_CONFIRMATION`: ব্যবহারকারীর সম্মতি ডাটাবেজে রেকর্ড থাকবে; এটি কখনোই এপিআই ভ্যালিডেশন নয় এবং কোনো ক্লাউড কল অনুমোদন করতে পারবে না।
  - `UNAVAILABLE`: যেকোনো তথ্য UNKNOWN বা UNVERIFIED হলে ক্লাউড কল সরাসরি ব্লক (Fail-Closed) থাকবে।
- **ফলব্যাক নীতি:** জেমিনি ডাউন বা আনভেরিফাইড হলে লোকাল এলএলএম বা রুল-বেসড লোকাল স্ক্রিপ্ট ইঞ্জিনে গ্রেসফুল ফলব্যাক করবে। কোনো অবস্থাতেই পেইড এন্ডপয়েন্ট বা অটো-বিলিং সক্রিয় হবে না।

### ৩.৩ অনলাইন বনাম অফলাইন টিটিএস ইঞ্জিন
- **Edge-TTS (Online Optional Engine):** ইন্টারনেট সংযোগ আবশ্যক এবং ফ্রি প্রাপ্যতা নিশ্চিত নয়। অফলাইন মোড চালু থাকলে এটি সম্পূর্ণ ব্লক থাকবে।
- **Bark / Meta MMS (Local Offline Engines):** সম্পূর্ণ অফলাইনে লোকাল সিপিইউ/জিপিইউতে চলবে (হার্ডওয়্যার প্রিফ্লাইট ও লাইসেন্স গেট সাপেক্ষে)।
- **Paid Engines:** ব্যাকএন্ড ও ফ্রন্টএন্ডে স্থায়ীভাবে হার্ড-লকড।

### ৩.৪ প্রোডাকশন-রেডি নন-ব্লকিং ওয়ার্কার লাইফসাইকেল
- FastAPI-এর async event loop-এর মধ্যে ব্লকিং `subprocess.Popen.communicate()` চালানো সম্পূর্ণ নিষিদ্ধ; বাধ্যতামূলকভাবে `asyncio.create_subprocess_exec()` ব্যবহার করতে হবে।
- ব্যাকএন্ডের টপ-লেভেলে কখনোই ভারী `torch` ইমপোর্ট করা যাবে না (ওয়ার্কার সাবপ্রসেসে অন-ডিমান্ড ইমপোর্ট হবে)।
- `torch.cuda.empty_cache()` শতভাগ মেমরি ফাঁকা করার গ্যারান্টি দেয় না।
- **১০-ধাপের প্রসেস লাইফসাইকেল:**
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
- ক্লিনআপ ব্যর্থ হলেও মূল এক্সেপশন যেন আড়াল না হয় (Exception Chaining ব্যবহার বাধ্যতামূলক)।

### ৩.৫ চেকপয়েন্ট স্টেট মেশিন বনাম টাস্ক লাইফসাইকেল
- **Durable Commit State (ফাইল ও চেকপয়েন্ট ট্রানজিশন):**
  `INTENT → RENDERING → VALIDATED → OUTPUT_COMMITTED → DB_COMMITTED`
- **Task Lifecycle State (কিউ ও ওয়ার্কার এক্সিকিউশন):**
  `QUEUED → RUNNING → PAUSED → WAITING_FOR_APPROVAL → COMPLETED / FAILED / CANCELLED / RECOVERY_REQUIRED`
- সাইডকার ম্যানিফেস্ট অ্যাটমিক রাইট প্রটোকল: `.tmp → flush() → fsync() → close() → os.replace()`।
- উইন্ডোজ ফাইল লকিং রুল: ফাইলের সমস্ত হ্যান্ডেল `close()` নিশ্চিত করার পরই কেবল `os.replace()` কার্যকর হবে।

---

## ৪. স্টার্টআপ রিকনসিলিয়েশন ম্যাট্রিক্স (Case A–K, সম্পূর্ণ আইডেমপোটেন্ট)

ক্র্যাশ বা পাওয়ার লসের পর সিস্টেম রিস্টার্টের সময় ডাটাবেজ ও ডিস্কের মধ্যে মেলবন্ধন নিশ্চিত করার সুনির্দিষ্ট প্রটোকল:

| Case | Initial DB State | Initial Sidecar State | Physical File State | Verification Requirements | Recovery Action | Final State |
|---|---|---|---|---|---|---|
| **Case A** | `COMPLETED` | `DB_COMMITTED` | ফাইনাল ফাইল উপস্থিত | সাইজ, SHA-256 ও FFprobe ভ্যালিড | কোনো অ্যাকশন নেই; সম্পূর্ণ ভেরিফাইড | `COMPLETED` / `DB_COMMITTED` |
| **Case B** | `IN_PROGRESS` | `OUTPUT_COMMITTED` | ফাইনাল ফাইল উপস্থিত | সাইজ ও SHA-256 সাইডকার অনুযায়ী ভ্যালিড | ফাস্ট-ফরোয়ার্ড: SQLite-এ `COMPLETED` কমিট করো, সাইডকার `DB_COMMITTED` করো | `COMPLETED` / `DB_COMMITTED` |
| **Case C** | `IN_PROGRESS` | `VALIDATED` বা `RENDERING` | Staging `.tmp` ফাইল উপস্থিত | স্ট্যাজিং ফাইলের SHA-256 ও FFprobe ভ্যালিড | `os.replace()` কার্যকর করো, সাইডকার `OUTPUT_COMMITTED` করো, DB কমিট করো | `COMPLETED` / `DB_COMMITTED` |
| **Case D** | `IN_PROGRESS` | `RENDERING` বা `INTENT` | Staging অসম্পূর্ণ বা করাপ্ট | ফাইল অসম্পূর্ণ বা করাপ্ট | ফাইল কোয়ারেন্টিনে সরাও: `.staging/quarantine/`, DB ও সাইডকারে `FAILED` মার্ক করো | `FAILED` / `FAILED` |
| **Case E** | `IN_PROGRESS` | `OUTPUT_COMMITTED` | ফাইনাল ফাইল উপস্থিত, staging অনুপস্থিত | ফাইনাল ফাইলের SHA-256 সাইডকার অনুযায়ী ভ্যালিড | ডাটাবেজে টাস্ক `COMPLETED` কমিট করো এবং সাইডকার `DB_COMMITTED` করো | `COMPLETED` / `DB_COMMITTED` |
| **Case F** | `IN_PROGRESS` | `OUTPUT_COMMITTED` | ফাইনাল ফাইল উপস্থিত | SQLite কমিট ফেইল করেছিল কিন্তু ফাইল ভ্যালিড | সাইডকার ম্যানিফেস্টের মেটাডাটা ব্যবহার করে SQLite রেকর্ড রিকনস্ট্রাক্ট/কমিট করো | `COMPLETED` / `DB_COMMITTED` |
| **Case G** | `IN_PROGRESS` বা `COMPLETED` | সাইডকার ফাইল করাপ্ট বা অপাঠ্য | ফাইনাল ফাইল উপস্থিত | শুধু FFprobe যথেষ্ট নয়; DB রেকর্ডের Task ID, Project ID, Path, Size, SHA-256 ভ্যালিড হতে হবে | DB মেটাডাটা থেকে সাইডকার রিবিল্ড করো; DB রেকর্ডও না থাকলে ফাইল কোয়ারেন্টিনে নিয়ে অ্যালার্ট দাও | `RECOVERED` বা `QUARANTINED` |
| **Case H** | DB রেকর্ড অনুপস্থিত | সাইডকার ফাইল ভ্যালিড | ফাইনাল ফাইল উপস্থিত | সাইডকারের SHA-256 ও FFprobe ফাইল অনুযায়ী ভ্যালিড | সাইডকার ম্যানিফেস্ট থেকে SQLite-এ হারানো ডাটাবেজ রেকর্ড রিকনস্ট্রাক্ট করো | `COMPLETED` / `DB_COMMITTED` |
| **Case I** | `IN_PROGRESS` | `VALIDATED` | গন্তব্য ফাইলে অপ্রত্যাশিত কনফ্লিক্ট বিদ্যমান | পূর্ববর্তী অপ্রত্যাশিত ফাইল বিদ্যমান | ডিটারমিনিস্টিক আইডেমপোটেন্ট পলিসি: কনফ্লিক্টিং ফাইল কোয়ারেন্টিনে সরাও এবং বর্তমান ভ্যালিডেটেড ফাইল প্রতিস্থাপন করো | `OUTPUT_COMMITTED` |
| **Case J** | যেকোনো | পাথে `..` বা প্রজেক্ট রুটের বাইরে | যেকোনো | পাথ ট্রাভার্সাল প্রতিরোধ ভ্যালিডেশন | অবিলম্বে সিকিউরিটি এক্সেপশন রেইজ করো এবং অপারেশন বাতিল করো | `ABORTED_SECURITY_VIOLATION` |
| **Case K** | `COMPLETED` | `OUTPUT_COMMITTED` | ফাইনাল ফাইল উপস্থিত | DB রেকর্ড, ফাইনাল ফাইল ও চেকসাম ভ্যালিড | সাইডকার ফাইলে স্টেট `DB_COMMITTED` আপডেট করে রিকনসিলিয়েশন সম্পন্ন করো | `COMPLETED` / `DB_COMMITTED` |

*আইডেমপোটেন্সি ও সেফটি রুল:* প্রতিটি রিকনসিলিয়েশন অপারেশন সম্পূর্ণ Idempotent হবে; একাধিকবার রান করলেও ডেটা ক্ষতিগ্রস্ত হবে না। প্রজেক্ট রুটের বাইরের কোনো ফাইল কখনোই ডিলিট বা সরানো যাবে না।

---

## ৫. অডিও পাইপলাইন, মিক্সার স্কিমা ও সোর্স রেজোলিউশন পলিসি

### ৫.১ AudioMixerState ফিল্ড ম্যাপিং (TypeScript <-> SQLite)
| TypeScript (`camelCase`) | SQLite Table (`snake_case`) | Data Type | Default Value | Valid Range / Unit | Validation Rule |
|---|---|---|---|---|---|
| `masterVolume` | `master_volume` | Float | `1.0` (100%) | `0.0 to 1.5` (Ratio) | ভলিউম ০ থেকে ১৫০% এর মধ্যে সীমাবদ্ধ |
| `masterLevelDbfs` | `master_level_dbfs` | Float | `-60.0` | `-60.0 to +6.0` (dBFS) | রিয়েল-টাইম টেলিমেট্রি মিটার ডাটা |
| `peakClippingDetected` | `peak_clipping_detected` | Boolean | `false` | `true / false` | `masterLevelDbfs >= 0.0` হলে সত্য |
| `hardLimiterEnabled` | `hard_limiter_enabled` | Boolean | `true` | `true / false` | সিলিং: `-0.5 dBFS` |
| `normalizerEnabled` | `normalizer_enabled` | Boolean | `true` | `true / false` | লাউডনেস টার্গেট সক্রিয়করণ |
| `normalizerTargetLufs` | `normalizer_target_lufs` | Float | `-16.0` | `-24.0 to -12.0` (LUFS) | EBU R128 স্ট্যান্ডার্ড টার্গেট |
| `originalAudioVolume` | `original_audio_volume` | Float | `1.0` (100%) | `0.0 to 1.5` (Ratio) | ট্র্যাক ১ (Original Backup) |
| `originalAudioMuted` | `original_audio_muted` | Boolean | `true` | `true / false` | ডুপ্লিকেট শব্দ এড়াতে ডিফল্ট Muted |
| `demucsVocalVolume` | `demucs_vocal_volume` | Float | `1.0` (100%) | `0.0 to 1.5` (Ratio) | ট্র্যাক ২ (Demucs Vocal Stem) |
| `demucsAccompanimentVolume`| `demucs_accompaniment_volume`| Float | `1.0` (100%) | `0.0 to 1.5` (Ratio) | ট্র্যাক ৩ (Demucs Accompaniment) |
| `aiVoiceVolume` | `ai_voice_volume` | Float | `1.0` (100%) | `0.0 to 1.5` (Ratio) | ট্র্যাক ৪ (New AI Voice Track) |

*বাস্তব সীমাবদ্ধতা:* লিমিটার ও নরমালাইজার ক্লিপিং ঝুঁকি উল্লেখযোগ্যভাবে কমায়, তবে এটি অডিও ডিসটর্শন সম্পূর্ণ দূর করার অলীক গ্যারান্টি দেয় না। Demucs ভোকাল স্টেম নিখুঁত ডায়ালগ আইসোলেটর নয়; এতে হাসি, কান্না বা ব্যাকগ্রাউন্ড গানের শব্দ থেকে যেতে পারে।

### ৫.২ অডিও স্পিড পেসিং ও ডায়ালগ প্রিজার্ভেশন
- অডিও পেসিং মাল্টিপ্লায়ার: `0.85x` (ধীর), `1.00x` (স্বাভাবিক), `1.25x` (দ্রুত) এবং সাইলেন্স প্যাডিং।
- মূল ভিডিওর ফ্রেম সংখ্যা এবং মোট দৈর্ঘ্য কোনোভাবেই পরিবর্তন করা যাবে না।
- কোনো অর্থপূর্ণ ডায়ালগ স্বয়ংক্রিয়ভাবে মুছে ফেলা বা ট্রিম করা সম্পূর্ণ নিষিদ্ধ। ডায়ালগ রেঞ্জে না ধরলে `AudioTimingOverflowWarning` দেবে এবং ট্রিম করতে ব্যবহারকারীর স্পষ্ট সম্মতি লাগবে।

### ৫.৩ সোর্স রেজোলিউশন ও এক্সপোর্ট পলিসি
- **Universal 1080p গ্যারান্টি পরিহার:**
  - সোর্স ভিডিওর মূল অ্যাসপেক্ট রেশিও হুবহু সংরক্ষিত থাকবে।
  - সোর্স ভিডিওর মূল রেজোলিউশন হুবহু সংরক্ষিত থাকবে, যদি না ব্যবহারকারী আলাদা রেজোলিউশন নির্বাচন করেন।
  - লো-রেজোলিউশন সোর্সকে নিজে থেকে 1080p কোয়ালিটি দাবি করা যাবে না।
  - আপস্কেলিং ইঞ্জিন অনুপলব্ধ থাকলে নেটিভ রেজোলিউশনেই এক্সপোর্ট হবে।
  - আউটপুট ফরম্যাট: H.264 কোডেক সহ MP4 কন্টেইনার। ফাইনাল এক্সপোর্টের আগে FFprobe ভ্যালিডেশন বাধ্যতামূলক।

---

## ৬. হার্ডওয়্যার, ডিপেন্ডেন্সি ও তৌরি ফেজ ২ ডিসিশন গেট

### ৬.১ হার্ডওয়্যার প্রোফাইল ও ডিপেন্ডেন্সি আইসোলেশন
- **Core Dependencies:** FastAPI, Uvicorn, Pydantic, aiosqlite, psutil, keyring, requests, python-multipart, websockets, opencv-python-headless। (OpenCV বেসিক ফ্রেম এক্সট্রাকশন ও ইনপেইন্টিং ফলব্যাকের জন্য কোর ডিপেন্ডেন্সিতে অন্তর্ভুক্ত)।
- **Optional Heavy Dependencies:** PyTorch, Demucs, Whisper, Wav2Lip, Bark, Meta MMS, LaMa, Real-ESRGAN। কোনো অপশনাল ইঞ্জিন অনুপস্থিত থাকলে অ্যাপ্লিকেশন ক্র্যাশ করবে না; সংশ্লিষ্ট ফিচার নিরাপদভাবে `UNAVAILABLE` থাকবে।

### ৬.২ Tauri Packaging Decision Gate (Phase 2 Target)
- তৌরি প্যাকেজিং Phase 1 (P1 Core)-এর জন্য বাধ্যতামূলক নয়।
- Release Phase P2 শুরু হওয়ার পূর্বে একটি সুনির্দিষ্ট স্ট্র্যাটেজি নির্বাচন করার জন্য প্রোটোটাইপ ডিসিশন গেট থাকবে:
  - **Option A:** Standalone Embedded Python runtime
  - **Option B:** PyInstaller-based backend packaging
- **মূল্যায়ন মানদণ্ড:** প্রসেস লাইফসাইকেল ম্যানেজমেন্ট, ফিক্সড পোর্ট ৮০০০ বাইন্ডিং, হেলথ চেক নির্ভরযোগ্যতা, FFmpeg বাইনারি পাথ হ্যান্ডলিং, উইন্ডোজ চাইল্ড প্রসেস টার্মিনেশন এবং অ্যান্টিভাইরাস কম্প্যাটিবিলিটি।

---

## ৭. টেকনিক্যাল স্ট্যাক সামারি

| কম্পোনেন্ট | প্রযুক্তি ও স্পেসিফিকেশন |
|---|---|
| **Frontend UI** | Vite + React + TypeScript + Tailwind CSS (FastAPI রুট থেকে সার্ভ হবে) |
| **Backend API** | Python 3.10+ & FastAPI (কঠোরভাবে `127.0.0.1:8000`-এ বাইন্ড) |
| **Database** | SQLite via `aiosqlite` (WAL Mode, JSON1; Checkpoints=`FULL`, Telemetry=`NORMAL`) |
| **Task Queue** | Resource-Aware Sequential Queue (FIFO) with Non-blocking Worker Subprocess |
| **State Machine** | ৫-ধাপের সাইডকার ম্যানিফেস্ট ও স্টার্টআপ রিকনসিলিয়েশন (Case A–K) |
| **Media Compositor**| FFmpeg Static Binaries, FFprobe Validator, ৪-ট্র্যাক অডিও মিক্সার ও Limiter |
| **Desktop Wrapper** | Tauri v2 (Phase 2 Target — Decision Gate: Embedded Python বনাম PyInstaller) |
| **Zero-Cost Lock** | Permanent Hard-Lock against Paid Endpoints, Paid GPU & Auto-Billing |

---

*Master System Architecture Version: 2.2 | Approved & Aligned with prd.md v2.2, agent.md v2.4 & prompt.md*
