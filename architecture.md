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

### ১. Dynamic Gemini Model Configuration & Eligibility Validation
* **ডাইনামিক সিলেকশন ও ভেরিফায়েড লিস্ট:** কোডে কোনো নির্দিষ্ট মডেল আইডি স্থায়ী থাকবে না। User Settings-এ একটি "Verified Free Models" তালিকা থাকবে এবং ব্যবহারকারী সেখান থেকে মডেল নির্বাচন বা কাস্টমাইজ করতে পারবেন।
* **ডুয়েল ভ্যালিডেশন (Availability vs Free Tier):** শুধু মডেলটি সক্রিয় (Available) থাকলেই সেটি কল করা যাবে না; তার Free Tier Eligibility আলাদাভাবে সক্রিয় কি না তা নিশ্চিত হতে হবে।
* **সতর্কবার্তা ও হার্ড-লক:** মডেল বন্ধ হলে বা ফ্রি টিয়ার থেকে বাদ পড়লে সফটওয়্যার ব্যবহারকারীকে সতর্ক করবে। কোনো পেইড মডেল বা পেইড বিলিং-এ কোনো অবস্থাতেই Fallback করা যাবে না।

### ২. TTS Engine Classification & Quality Realities (Online vs Offline)
ইঞ্জিনগুলোকে তিনটি সুস্পষ্ট বিভাগে ভাগ করা হয়েছে:
1. **Free Online Engines:** Edge-TTS — উচ্চমানের নিউরাল ভয়েস তৈরি করে, তবে **সক্রিয় ইন্টারনেট কানেকশন আবশ্যক**। এটি অফলাইন ইঞ্জিন নয় এবং স্থায়ী ফ্রি হিসেবে গ্যারান্টি দেওয়া যায় না। অফলাইন মোড চালু থাকলে এতে কোনো রিকোয়েস্ট যাবে না।
2. **Local Offline Engines:** Bark / Meta MMS — সম্পূর্ণ অফলাইনে লোকাল পিসিতে চলে। 
   * *বাস্তবতা ও সীমাবদ্ধতা:* বাংলা, হিন্দি ও ইংরেজির ভয়েস কোয়ালিটি Edge-TTS-এর সমকক্ষ নয়। Bark-এর জন্য উল্লেখযোগ্য VRAM/RAM (৪GB+) এবং মডেল ডাউনলোড স্পেস আবশ্যক। কোনো লোকাল ইঞ্জিন সব ভাষায় নিখুঁত প্রাকৃতিক ভয়েস দেবে—এমন অলীক নিশ্চয়তা দেওয়া যাবে না।
3. **Paid Engines:** সম্পূর্ণ Disabled।

### ৩. Resource-Aware Sequential Processing & Memory Recovery Mechanism
* **Worker Process Recycling:** পাইথনের `gc.collect()` এবং `torch.cuda.empty_cache()` VRAM সম্পূর্ণ ফাঁকা করার শতভাগ নিশ্চয়তা দেয় না। তাই Worker Shutdown ও Process Exit নিশ্চিত করার পর মেমরি রিকভারি মেকানিজম হিসেবে ব্যাকএন্ড **Worker Process Restart** কার্যকর করা হবে এবং RAM/VRAM পুনরায় মেপে নিশ্চিত করা হবে। পর্যাপ্ত রিসোর্স না পাওয়া পর্যন্ত পরবর্তী ভারী মডেল চালু হবে না।
* **Resource Readiness Gate:** পরবর্তী ভারী মডেল চালানোর পূর্বে পর্যাপ্ত RAM/VRAM নিশ্চিত না হওয়া পর্যন্ত টাস্ক কিউতে অপেক্ষা করবে।
* **সমান্তরাল হালকা টাস্ক:** ভারী মডেল যখন লাইনে থাকবে, তখন হালকা UI রেসপন্স, ডাটাবেজ রিড-রাইট ও ফাইল প্রসেসিং প্যারালালে সচল থাকবে।

### ৪. Checkpoint-Based Resume & Audio Mixing Architecture
* **Checkpoint-Based Resume:** `Instant Resume` নয়; প্রতিটি সফল প্রসেসিং স্টেপের পর ক্যাশ ও স্টেট SQLite-এ সেভ থাকবে। রিস্টার্ট বা কোটা রিকভারির পর পূর্বের সফল কাজ পুনরায় না চালিয়ে সরাসরি অসমাপ্ত ধাপ থেকে Checkpoint-Based Resume হবে।
* **Demucs 5-Track Interactive Mixer:** Demucs কোনো পারফেক্ট অ্যাম্বিয়েন্ট আইসোলেটর নয়। তাই অডিও মিক্সারে স্পষ্টভাবে ৫টি ট্র্যাক থাকবে:
  1. Original Audio Backup (মাস্টার ব্যাকআপ)
  2. Demucs Vocal Stem (আলাদা করা ভোকাল)
  3. Demucs Accompaniment Stem (আলাদা করা ব্যাকগ্রাউন্ড)
  4. New AI Voice (নতুন জেনারেটেড ভয়েস)
  5. Manual Volume Adjustment (প্রতিটি ট্র্যাকের ভলিউম ব্যালেন্সিং কন্ট্রোল)
* **Mode 02 Dialogue & Copyright Policy:**
  * অরিজিনাল স্টোরি, কনসেপ্ট, সিন সিকোয়েন্স, ক্যারেক্টার রোল ও অ্যাকশন বজায় থাকবে।
  * প্রয়োজন অনুযায়ী Meaning-Preserving Contextual Dialogue Adaptation করা যাবে।
  * Real Voice ব্যবহারের ক্ষেত্রে বৈধ অধিকার থাকতে হবে। AI Voice কোনো Copyright-Free Guarantee নয়; এটি কেবল একটি বিকল্প সিন্থেটিক ভয়েস।

### ৫. Voice Approval Gate & Output Language Matrix (Enforced)
* **Primary Language Voice Approval:** Default Primary Language হবে **Bangla**। ব্যবহারকারী প্রথমে বাংলায় ভয়েস প্রিভিউ শুনে Approve করবেন। Approval না পাওয়া পর্যন্ত Final Video Processing শুরু হবে না।
* **Output Language Matrix (Strict User-Selection):**
  - `"Bangla"` = ১টি বাংলা ভিডিও
  - `"hindi"` = ১টি হিন্দি ভিডিও
  - `"english"` = ১টি ইংরেজি ভিডিও
  - `"Bangla + Hindi"` = ২টি আলাদা ভিডিও
  - `"Bangla + Hindi + english"` = ৩টি আলাদা ভিডিও
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
