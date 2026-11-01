# 🏛️ Master System Architecture Specification
### Project: AI Funny Dubbing & Video Production Studio (AI-VPS)
**Document Version:** 2.0  
**Scope:** Single-User Personal Local Studio  
**Cost Model:** ZERO EXTRA COST Hard-Lock Architecture  
**Target Environment:** Local Windows PC (`http://localhost:7860` / `8000`) $\rightarrow$ Tauri Desktop Installer

---

## ১. ওভারভিউ ও মূলনীতি (Core Architectural Principles)

1. **Zero Extra Cost Protection:** কোনো পেইড এপিআই, ক্লাউড জিপিইউ বা স্বয়ংক্রিয় বিলিং চালু হবে না। ফ্রি টিয়ারের নিশ্চয়তা না থাকলে কোনো ক্লাউড মডেল কল করা যাবে না।
2. **Local-First & Zero-Dependency:** মূল ডাটাবেজ হিসেবে SQLite (WAL Mode) ব্যবহৃত হবে। সমস্ত ভিডিও, অডিও ও ক্যাশ লোকাল ফাইল সিস্টেমে থাকবে।
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
|   • Backend Framework: Python 3.10+ & FastAPI                                           |
|   • Resource-Aware Sequential Worker (FIFO): একবারে ১টি ভারী মডেল + Worker Restart      |
|   • State Checkpointer: কোটা বা নেটওয়ার্কে Pause এবং রিস্টার্টে Instant Resume          |
|   • Parallel Lightweight Tasks: UI, SQLite DB ও ফাইল অপারেশনস সমান্তরালভাবে সচল       |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                     LAYER 3: PERSISTENCE & ZERO-DEPENDENCY STORAGE                      |
|   • Database: SQLite (with WAL Mode & Native JSON1) — studio.db                         |
|   • Media Store: Structured Local Disk Storage (/storage/projects/[id]/...)             |
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
|   4. Paid Engines: HARD-DISABLED (ব্যবহারকারীর স্পষ্ট অনুমোদন ছাড়া অক্ষম)               |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 6: MEDIA COMPOSITOR & AUDIO PIPELINE                     |
|   • Master Audio Track Preservation: আসল অডিওর স্থায়ী ব্যাকআপ সংরক্ষণ                   |
|   • Interactive Audio Mixer: Demucs স্প্লিট + আসল ট্র্যাকের ম্যানুয়াল লেভেল অ্যাডজাস্ট  |
|   • Audio Speed-Stretch Pacing Engine: ভিডিওর ফ্রেম নষ্ট না করে ভয়েসের গতি সিঙ্ক        |
|   • Mode 02 Delta Re-renderer: কার্টুন মোডে 1-ক্লিকে Real Voice <-> AI Voice সোয়াপ      |
|   • FFmpeg Engine: মাল্টি-অডিও ট্র্যাকসহ ফাইনাল MP4 (1080p, H.264) রেন্ডারিং             |
+-----------------------------------------------------------------------------------------+
                                             ↕ (Phase 2 Target)
+-----------------------------------------------------------------------------------------+
|                           LAYER 7: LIGHTWEIGHT DESKTOP PACKAGING                        |
|   • Tauri (Rust Core + System Webview): মাত্র ৩০-৪০ MB র‍্যাম ব্যবহার করে উইন্ডোজ .exe  |
+-----------------------------------------------------------------------------------------+
```

---

## ৩. গুরুত্বপূর্ণ ৪টি সংশোধনের কারিগরি বাস্তবায়ন

### ১. Dynamic Gemini Model Configuration
* **ডাইনামিক সিলেকশন:** কোডে কোনো নির্দিষ্ট মডেল আইডি স্থায়ী থাকবে না। ব্যবহারকারী Settings থেকে Google AI Studio-র সক্রিয় ফ্রি মডেল নির্বাচন করতে পারবেন।
* **ফ্রি টিয়ার ভ্যালিডেশন:** মডেল কল করার পূর্বে তার Active স্ট্যাটাস এবং Free Tier Eligibility নিশ্চিত করা হবে। ফ্রি টিয়ার নিশ্চিত না হলে কোনো রিকোয়েস্ট যাবে না।
* **সতর্কবার্তা ও ফেইল-সেফ:** কোনো মডেল বন্ধ হয়ে গেলে বা ফ্রি কোটা তুলে নিলে সিস্টেম ব্যবহারকারীকে সতর্ক করবে। কোনো পেইড মডেলে স্বয়ংক্রিয় Fallback নিষিদ্ধ।

### ২. TTS Engine Classification (Online vs Offline)
ইঞ্জিনগুলোকে তিনটি সুস্পষ্ট বিভাগে ভাগ করা হয়েছে:
1. **Local Offline Engines:** Bark / Meta MMS — ইন্টারনেট ছাড়া লোকাল কম্পিউটারে সম্পূর্ণ অফলাইনে চলে।
2. **Free Online Engines:** Edge-TTS — উচ্চমানের নিউরাল ভয়েস তৈরি করে, তবে **সক্রিয় ইন্টারনেট কানেকশন আবশ্যক**। এটি অফলাইন ইঞ্জিন নয় এবং একে স্থায়ী ফ্রি হিসেবে দাবি করা যাবে না। অফলাইন মোড চালু থাকলে এটিতে কোনো রিকোয়েস্ট যাবে না।
3. **Paid Engines:** সম্পূর্ণ Disabled।

### ৩. Resource-Aware Sequential Processing & Memory Recycling
* **Worker Process Recycling:** পাইথনের `gc.collect()` এবং `torch.cuda.empty_cache()` সবসময় VRAM সম্পূর্ণ মুক্ত করতে পারে না। তাই প্রতিটি ভারী মডেল আনলোডের পর মেমরি পর্যবেক্ষণ করা হবে; মেমরি লিক বা ব্লকেজ থাকলে ব্যাকএন্ড **Worker Process রিস্টার্ট** করে মেমরি ১০০% পরিষ্কার করা হবে।
* **Resource Readiness Gate:** পরবর্তী ভারী মডেল চালানোর পূর্বে পর্যাপ্ত RAM/VRAM নিশ্চিত না হওয়া পর্যন্ত টাস্ক কিউতে অপেক্ষা করবে।
* **সমান্তরাল হালকা টাস্ক:** ভারী মডেল যখন লাইনে থাকবে, তখন হালকা UI রেসপন্স, ডাটাবেজ রিড-রাইট ও ফাইল প্রসেসিং প্যারালালে সচল থাকবে।

### ৪. Copyright, Voice Rights & Checkpoint Resume Policy
* **Mode 02 Voice Rights:** Real Voice ব্যবহারের জন্য ব্যবহারকারীর বৈধ অধিকার থাকতে হবে। AI Voice ব্যবহার করলেই পুরো ভিডিও কপিরাইট-মুক্ত হয়ে যায়—এমন দাবি নিষিদ্ধ; এটি শুধুই একটি বিকল্প ভয়েস অপশন।
* **Checkpoint State Engine:** 
  * প্রতিটি সফল স্টেপ SQLite-এ সংরক্ষিত হবে।
  * কোটা বা নেটওয়ার্ক ফেইলিওরে টাস্ক `PAUSED` স্টেটে যাবে। `retry-after` হেডার পাওয়া গেলে সেই সময় পর্যন্ত অপেক্ষা করবে।
  * রিজিউম করার সময় পূর্বের সম্পন্ন হওয়া স্টেপ পুনরায় রেন্ডার হবে না; শুধুমাত্র অসম্পূর্ণ স্টেপ নতুন কনফিগারেশন পাওয়ার পর চলবে।

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
