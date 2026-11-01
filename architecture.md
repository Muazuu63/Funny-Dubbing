# 🏛️ Master System Architecture Specification
### Project: AI Funny Dubbing & Video Production Studio (AI-VPS)
**Document Version:** 2.1  
**Scope:** Single-User Personal Local Studio  
**Cost Model:** ZERO EXTRA COST Hard-Lock Architecture  
**Target Environment:** Local Windows PC (`http://localhost:7860` / `8000`) $\rightarrow$ Tauri Desktop Installer

---

## ১. ওভারভিউ ও মূলনীতি (Core Architectural Principles)

1. **Zero Extra Cost Protection (Permanent Hard-Lock):** বর্তমান v2.1 আর্কিটেকচারে সমস্ত Paid API endpoints, Paid AI Providers, Paid Fallback Models, Paid Cloud GPU Services এবং Automatic Billing ব্যাকএন্ড কোড লেভেলে স্থায়ীভাবে হার্ড-লক ও ব্লক থাকবে। কোনো পেইড সার্ভিস চালু করার সুযোগ নেই; ভবিষ্যতে কোনো পেইড পরিবর্তন আনতে হলে আলাদা অনুমোদিত আর্কিটেকচার রিভিশন প্রয়োজন হবে।
2. **Local-First Architecture & Storage:** মূল ডাটাবেজ হিসেবে SQLite (WAL Mode) ব্যবহৃত হবে। সমস্ত ভিডিও, অডিও ও ক্যাশ লোকাল ফাইল সিস্টেমে থাকবে। তবে Cloud API ও Online TTS ব্যবহারের সময় প্রয়োজনীয় ডাটা ইন্টারনেটে আদান-প্রদান হতে পারে, যা ব্যবহারকারীকে পরিষ্কারভাবে জানানো হবে।
3. **Resource-Aware Sequential Processing:** সাধারণ পিসির মেমরি ক্র্যাশ রোধে একবারে একটি ভারী AI মডেল চলবে। প্রয়োজনে Worker Process Recycle/Restart করা হবে।
4. **Dynamic AI Configuration:** কোনো নির্দিষ্ট মডেল আইডি বা ফিক্সড কোটা হার্ডকোড থাকবে না।
5. **Checkpoint-Based Recovery:** ব্যর্থ বা স্থগিত টাস্ক পূর্বের সফল কাজ নষ্ট না করে ঠিক পেন্ডিং পয়েন্ট থেকে কাজ শুরু করবে।

---

## ২. অনুমোদিত ৭টি লেয়ার আর্কিটেকচার (Approved 7-Layer Architecture)

```
+-----------------------------------------------------------------------------------------+
|                               LAYER 1: PRESENTATION LAYER                               |
|   • Frontend: Vite + React + TypeScript + Tailwind CSS                                  |
|   • Localhost Dashboard: http://localhost:7860 (অটো-ফলব্যাক to 8000)                  |
|   • UI Features: ১১টি প্রোডাকশন মোড কার্ড, অডিও প্রিভিউ/ম্যানুয়াল মিক্সার, লাইভ প্রগ্রেস |
+-----------------------------------------------------------------------------------------+
                                             ↕ (REST API / WebSockets)
+-----------------------------------------------------------------------------------------+
|                        LAYER 2: APPLICATION & ORCHESTRATION LAYER                       |
|   • Backend Framework: Python 3.10+ & FastAPI (Bound strictly to 127.0.0.1)             |
|   • Security: Local Origin/CSRF Protection + Windows Credential Manager for API Keys   |
|   • Resource-Aware Sequential Worker (FIFO): একবারে ১টি ভারী মডেল + Worker Restart      |
|   • State Checkpointer: কোটা বা নেটওয়ার্কে Pause এবং রিস্টার্টে Checkpoint-Based Resume |
|   • Parallel Lightweight Tasks: UI, SQLite DB ও ফাইল অপারেশনস সমান্তরালভাবে সচল       |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                        LAYER 3: LOCAL STORAGE & DATABASE LAYER                          |
|   • Database (Metadata Only): SQLite (WAL Mode, JSON1) — প্রজেক্ট মেটাডাটা, চেকপয়েন্ট ও পাথ|
|   • Local Filesystem (Media & Weights): ভিডিও, অডিও, ক্যাশ ও AI মডেল ফাইলস সরাসরি ডিস্কে|
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 4: SHARED TRAINING CENTER CORE                           |
|   (Shared Infrastructure — ১১টি মোডের জন্য সার্বজনীন প্রোফাইল ও এসেট হাব)              |
|   • Voice Profiles (ক্যারেক্টার ভিত্তিক পিচ/টোন)     • Character Reference Sheets       |
|   • Comedy Style Profiles (হিউমার প্যাটার্ন)       • Language & Pacing Preferences    |
|   • Reusable Reference Video Library                • Custom SFX / BGM Presets         |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                         LAYER 5: SMART HYBRID AI PROVIDER LAYER                         |
|   [Zero-Cost Hard-Lock: কোনো পেইড এপিআই বা অটো-বিলিং কল হবে না]                          |
|                                                                                         |
|   1. Local Offline Engines: Demucs v4 (Stems), Whisper (STT), Wav2Lip, OpenCV/LaMa    |
|   2. Free Online Engines: Edge-TTS (ইন্টারনেট আবশ্যক, ফ্রি নিউরাল ভয়েস)                  |
|   3. Free Cloud API: Google AI Studio Active Free Tier (Dynamic Model ID & Observer)   |
|   4. Paid Engines: PERMANENTLY BLOCKED (v2.0-এ কোনো পেইড ইঞ্জিন/বিলিং সম্পূর্ণ নিষিদ্ধ)  |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 6: MEDIA COMPOSITOR & AUDIO PIPELINE                     |
|   • Master Audio Track Preservation: আসল অডিও ব্যাকআপ সংরক্ষণ (ডিফল্ট: Muted)           |
|   • Interactive 4-Track Audio Mixer: ৪টি ট্র্যাক + ভলিউম (0-150%), Mute ও Solo কন্ট্রোল  |
|   • Master Audio Safety: Output Level Meter, Peak Clipping Detector ও Master Limiter     |
|   • Audio Speed-Stretch Pacing Engine: ফ্রেম নষ্ট না করে 0.85x-1.25x নিরাপদ সিঙ্ক       |
|   • Dialogue Preservation: স্বয়ংক্রিয় ডায়ালগ ডিলিট সম্পূর্ণ নিষিদ্ধ; ট্রিম করতে সম্মতি লাগবে|
|   • Mode 02 Delta Re-renderer: কার্টুন মোডে 1-ক্লিকে Real Voice <-> AI Voice সোয়াপ      |
|   • FFmpeg Engine: মাল্টি-অডিও ট্র্যাকসহ ফাইনাল MP4 (1080p, H.264) রেন্ডারিং             |
+-----------------------------------------------------------------------------------------+
                                             ↕ (Phase 2 Target)
+-----------------------------------------------------------------------------------------+
|                           LAYER 7: LIGHTWEIGHT DESKTOP PACKAGING                        |
|   • Tauri (Rust Core + System Webview): নেটিভ সিস্টেম ওয়েবভিউ ব্যবহার করে লাইটওয়েট .exe |
+-----------------------------------------------------------------------------------------+
```

---

## ৩. গুরুত্বপূর্ণ ৪টি সংশোধনের কারিগরি বাস্তবায়ন

### ১. Dynamic Gemini Model Configuration & Eligibility Fail-Safe
* **ডাইনামিক সিলেকশন ও ভেরিফায়েড লিস্ট:** কোডে কোনো নির্দিষ্ট মডেল আইডি স্থায়ী থাকবে না। User Settings-এ একটি "Verified Free Models" তালিকা থাকবে এবং ব্যবহারকারী সেখান থেকে মডেল নির্বাচন বা কাস্টমাইজ করতে পারবেন।
* **চারটি পৃথক বিষয় হিসেবে ভ্যালিডেশন (Quad-Check Fail-Safe):** Model Availability, Free Tier Eligibility, Billing Configuration এবং Remaining Quota—এই চারটি বিষয়কে আলাদা স্বাধীন বিষয় হিসেবে বিবেচনা করা হবে। তবে গুগল এপিআই থেকে বিলিং বা অ্যাকাউন্টের অভ্যন্তরীণ সব তথ্য স্বয়ংক্রিয়ভাবে যাচাই করা সম্ভব নাও হতে পারে। তাই ব্যবহারকারীর ডিক্লেয়ারেশন এবং অফিসিয়াল মডেল ভ্যালিডেশন উভয়ই বিবেচনায় থাকবে। যদি কোনো একটি তথ্য অজানা (Unknown), অপ্রমাণিত বা অনিরাপদ হয়, তবে ক্লাউড API রিকোয়েস্ট সরাসরি **ব্লক (Fail-Safe Block)** থাকবে।
* **সতর্কবার্তা ও ব্যাকএন্ড পার্মানেন্ট হার্ড-লক:** মডেল বন্ধ হলে বা ফ্রি টিয়ার থেকে বাদ পড়লে সফটওয়্যার ব্যবহারকারীকে সতর্ক করবে। Paid Provider শুধু UI-তে নয়, Backend Level-এও স্থায়ীভাবে Block থাকবে। কোনো অবস্থাতেই Paid API, Paid Endpoint, Auto-billing বা Paid Fallback চলবে না।

### ২. TTS Engine Classification, Offline Compatibility & Model Download Safety
ইঞ্জিনগুলোকে তিনটি সুস্পষ্ট বিভাগে ভাগ করা হয়েছে:
1. **Online Engines (Edge-TTS — Internet Required; Free Availability Not Guaranteed):** উচ্চমানের নিউরাল ভয়েস তৈরি করে, তবে **সক্রিয় ইন্টারনেট কানেকশন আবশ্যক**। এটি অফলাইন ইঞ্জিন নয় এবং ভবিষ্যতে এর ফ্রি প্রাপ্যতা নিশ্চিত নয়। অফলাইন মোড চালু থাকলে এতে কোনো রিকোয়েস্ট যাবে না।
2. **Local Offline Engines (Bark / Meta MMS):** সম্পূর্ণ অফলাইনে লোকাল পিসিতে চলে।
   * *মডেল ডাউনলোড ও প্রি-চেক গার্ডরেইল:* Bark, Meta MMS, Whisper বা অন্য যেকোনো লোকাল মডেল প্রথমবার ডাউনলোডের আগে: (১) ১০০% ওপেন-সোর্স লাইসেন্স যাচাই, (২) প্রয়োজনীয় ডিস্ক স্পেস যাচাই, (৩) ডাউনলোডের সাইজ ও প্রয়োজনীয়তা প্রদর্শন, এবং (৪) অফিসিয়াল/বিশ্বস্ত সোর্স নিশ্চিত করা হবে। এতে কোনো পেইড মডেল যুক্ত হওয়ার সুযোগ থাকবে না।
   * *রিসোর্স ও CPU Fallback:* কোনো নির্দিষ্ট VRAM স্থায়ী হার্ডকোড থাকবে না; CPU Fallback will be available only when supported by the selected model, runtime and dependencies; performance may be significantly slower.
   * *কোয়ালিটি ও লাইসেন্সিং সতর্কতা:* লাইসেন্স ও ডিপেন্ডেন্সি যাচাই করতে হবে। নির্বাচিত মডেলটি স্থানীয়ভাবে টেস্ট করার পূর্বে বাংলা, হিন্দি বা ইংরেজিতে নিখুঁত প্রাকৃতিক ভয়েস দেওয়ার কোনো অলীক নিশ্চয়তা দেওয়া যাবে না।
3. **Paid Engines:** Backend ও Frontend উভয় লেভেলে স্থায়ীভাবে Blocked।

### ৩. Resource-Aware Sequential Processing & Memory Recovery Mechanism
* **Worker Process Recycling:** পাইথনের `gc.collect()` এবং `torch.cuda.empty_cache()` VRAM সম্পূর্ণ ফাঁকা করার শতভাগ নিশ্চয়তা দেয় না। তাই Worker Shutdown ও Process Exit নিশ্চিত করার পর মেমরি রিকভারি মেকানিজম হিসেবে ব্যাকএন্ড **Worker Process Restart** কার্যকর করা হবে এবং RAM/VRAM পুনরায় মেপে নিশ্চিত করা হবে। পর্যাপ্ত রিসোর্স না পাওয়া পর্যন্ত পরবর্তী ভারী মডেল চালু হবে না।
* **Resource Readiness Gate:** পরবর্তী ভারী মডেল চালানোর পূর্বে পর্যাপ্ত RAM/VRAM নিশ্চিত না হওয়া পর্যন্ত টাস্ক কিউতে অপেক্ষা করবে।
* **সমান্তরাল হালকা টাস্ক:** ভারী মডেল যখন লাইনে থাকবে, তখন হালকা UI রেসপন্স, ডাটাবেজ রিড-রাইট ও ফাইল প্রসেসিং প্যারালালে সচল থাকবে।

### ৪. Checkpoint Atomicity, 4-Track Mixer & Audio Pacing Safety
* **Checkpoint Atomicity & Output Verification:**
  - প্রতিটি সফল প্রসেসিং স্টেপের আউটপুট প্রথমে একটি Temporary File (`.tmp`)-এ তৈরি হবে।
  - আউটপুট ফাইল সাইজ ও ফরম্যাট ভেরিফিকেশন সফল হলে Final Path-এ **Atomic Replace** করা হবে।
  - ফাইল সম্পূর্ণ সংরক্ষিত হওয়ার পর SQLite-এ Checkpoint commit হবে।
  - সিস্টেম রিস্টার্টের সময় পূর্বে থেকে থাকা কোনো অসম্পূর্ণ বা Orphaned Temporary File স্ক্যান করে স্বয়ংক্রিয়ভাবে পরিষ্কার করা হবে।
  - রিস্টার্ট বা কোটা রিকভারির পর পূর্বের সফল কাজ পুনরায় না চালিয়ে সরাসরি অসমাপ্ত ধাপ থেকে Checkpoint-Based Resume হবে।
* **Demucs 4 Audio Tracks & Limiter Protection:**
  1. `Original Audio Backup` (মূল ভিডিওর আসল মাস্টার অডিও — **ডুপ্লিকেট সাউন্ড এড়াতে ডিফল্টভাবে MUTED থাকবে**, তবে রিস্টোরেশনের জন্য সংরক্ষিত)।
  2. `Demucs Vocal Stem` (আলাদা করা ভোকাল — গান বা অন্যান্য আওয়াজও থাকতে পারে)।
  3. `Demucs Accompaniment Stem` (আলাদা করা ব্যাকগ্রাউন্ড মিউজিক/পরিবেশের শব্দ)।
  4. `New AI Voice` (নতুন জেনারেটেড সিন্থেটিক ভয়েস)।
  * *সুরক্ষা ও ক্লিপিং হ্রাস:* প্রতি ট্র্যাকে Volume Slider (0-150%), Mute ও Solo কন্ট্রোল থাকবে। মিক্সারে **Master Output Level Meter, Peak Clipping Detector ও Master Audio Limiter / Loudness Normalizer** থাকবে। এটি অতিরিক্ত গেইনে অডিও বিকৃতি বা ফেটে যাওয়ার ঝুঁকি উল্লেখযোগ্যভাবে কমাবে; তবে ফাইনাল রেন্ডারের পূর্বে ব্যবহারকারীকে প্রিভিউ শুনে নিশ্চিত হতে হবে।
* **Audio Speed-Stretch (Playback Speed Multiplier) & Dialogue Safety:**
  - অডিও স্পিড-স্ট্রেচিংয়ের কারণে **মূল ভিডিওর Frame Count বা মোট Duration কোনোভাবেই পরিবর্তন হবে না**।
  - টাইমিং সিঙ্কে **Playback Speed Multiplier (0.85x ধীর – 1.00x স্বাভাবিক – 1.25x দ্রুত)** রেঞ্জে ভয়েসের গতি সামঞ্জস্য করা হবে; কথা শেষ হয়ে গেলে দৃশ্যের বাকি অংশে স্বাভাবিক **Silence Padding** ব্যবহার করা হবে।
  - **কোনো অর্থপূর্ণ ডায়ালগ স্বয়ংক্রিয়ভাবে মুছে ফেলা বা ট্রিম করা সম্পূর্ণ নিষিদ্ধ।**
  - ডায়ালগ অনুমোদিত স্পিড রেঞ্জে ফিট না হলে সিস্টেম UI-তে **Audio Timing Overflow Warning** দেবে এবং ডায়ালগ কাটছাঁট করতে **ব্যবহারকারীর স্পষ্ট অনুমোদন (User Approval)** লাগবে।
* **Mode 02 Dialogue & Copyright Policy:**
  * অরিজিনাল স্টোরি, কনসেপ্ট, সিন সিকোয়েন্স, ক্যারেক্টার রোল ও অ্যাকশন বজায় থাকবে; প্রয়োজন অনুযায়ী Meaning-Preserving Contextual Dialogue Adaptation করা যাবে।
  * Real Voice ব্যবহারের ক্ষেত্রে বৈধ অধিকার থাকতে হবে। AI Voice কোনো Copyright-Free Guarantee নয়; এটি কেবল একটি বিকল্প সিন্থেটিক ভয়েস।

### ৫. Voice Approval Gate, Security & Standardized Output Language Matrix
* **Primary Language Voice Approval Timing:** Default Primary Language হবে **Bangla**। ভয়েস প্রিভিউ, স্ক্রিপ্ট তৈরি ও প্রস্তুতিমূলক কাজ প্যারালালে চললেও **Final Video Rendering-এর ঠিক আগে বাংলায় Voice Approval নেওয়া বাধ্যতামূলক**। Approval না পাওয়া পর্যন্ত ফাইনাল রেন্ডারিং শুরু হবে না।
* **Local Security & Origin Protection:**
  - FastAPI লোকালহোস্ট সার্ভার কঠোরভাবে শুধুমাত্র **`127.0.0.1`**-এ বাইন্ড হবে।
  - লোকাল এপিআই-তে Origin ও CSRF Protection থাকবে।
  - API Key লোকাল ডিস্কে সাধারণ ফাইলে না রেখে উইন্ডোজের নিজস্ব **Windows Credential Manager**-এ নিরাপদে এনক্রিপ্টেড অবস্থায় সংরক্ষিত থাকবে।
* **Output Language Matrix (Strict User-Selection & Capitalization):**
  - `"Bangla"` = ১টি বাংলা ভিডিও
  - `"Hindi"` = ১টি হিন্দি ভিডিও
  - `"English"` = ১টি ইংরেজি ভিডিও
  - `"Bangla + Hindi"` = ২টি আলাদা ভিডিও
  - `"Bangla + Hindi + English"` = ৩টি আলাদা ভিডিও
  - শুধুমাত্র ব্যবহারকারীর নির্বাচিত ভাষার আউটপুটই তৈরি হবে।

---

## ৪. ১১টি প্রোডাকশন মোড ও শেয়ার্ড সিস্টেমস (Production Modes)

* **Shared Foundation:** **Training Center Core** (Voice, Character, Comedy & Style Profiles Repository — No Heavy Fine-tuning)।
* **P1 (Core Active):** Mode 01 (Funny Video Dubbing), Mode 02 (Cartoon Re-Creation), Mode 03 (Autonomous Content Creator)।
* **P2 (Planned):** Mode 04 (Video Enhancement), Mode 05 (Voice Studio), Mode 06 (Subtitle & Translation)।
* **P3 (Planned):** Mode 07 (Shorts & Reels Creator), Mode 08 (Video Editor), Mode 09 (Thumbnail Creator)।
* **P4 (Future):** Mode 10 (Background & Object Studio), Mode 11 (Music & Sound Studio)।

---

## ৫. টেকনিক্যাল স্ট্যাক সামারি

| কম্পোনেন্ট | প্রযুক্তি |
|---|---|
| **Frontend UI** | Vite + React + TypeScript + Tailwind CSS |
| **Backend API** | Python 3.10+ & FastAPI |
| **Database** | SQLite (WAL Mode, JSON1 Extension) |
| **Task Queue** | Resource-Aware Sequential Queue (FIFO) with Process Recycling |
| **Video Engine** | FFmpeg Static Binary + FFprobe |
| **Desktop Wrapper** | Tauri (Phase 2) |
| **Zero-Cost Lock** | Hardcoded restriction against paid endpoints & auto-billing |
