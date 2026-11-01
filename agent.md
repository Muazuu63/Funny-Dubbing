# 🤖 AI Agent ইঞ্জিনিয়ারিং ও অপারেশনাল নির্দেশিকা (AI-VPS)
### প্রজেক্ট: AI Funny Dubbing & Video Production Studio (কোডনেম: AI-VPS)
**ডকুমেন্ট ভার্সন:** ২.৪ (চূড়ান্ত অপারেশনাল সংস্করণ)  
**তারিখ:** 2026-11-01  
**উদ্দিষ্ট পাঠক:** যেকোনো অটোনোমাস এআই কোডিং এজেন্ট (Antigravity, Claude Engineer, AutoDev ইত্যাদি)  

---

## 📚 ১. Source of Truth ও ডকুমেন্ট হায়ারার্কি

প্রজেক্টের কোনো রিকোয়ারমেন্ট বা আর্কিটেকচারাল সিদ্ধান্ত সম্পর্কে বিভ্রান্তি দেখা দিলে নিচের নির্ধারিত ডকুমেন্ট প্রায়োরিটি অনুযায়ী সিদ্ধান্ত গৃহীত হবে। এজেন্ট কখনোই নিজের অনুমান বা অনুমাননির্ভর ফিচারকে অনুমোদিত রিকোয়ারমেন্ট হিসেবে উপস্থাপন করবে না:

```
+-----------------------------------------------------------------------------------------+
|                               DOCUMENT HIERARCHY & PRIORITY                             |
|   1. idea.md (v2.0)               — Product Vision, Core Concept & User Requirements    |
|   2. prd.md (v2.1)                — Functional & Technical Product Requirements         |
|   3. architecture.md (v2.1)       — System Architecture, Constraints & Cost Policy      |
|   4. agent.md (v2.4)              — Agent Operational Rules & Engineering Directives (This)|
|   5. prompt.md (Backend-First)    — Step-by-Step Implementation Execution Prompts       |
+-----------------------------------------------------------------------------------------+
```

### ১.১ রুলস ও কনফ্লিক্ট রেজোলিউশন নীতি:
1. **Product Requirements:** সর্বদা `prd.md` (v2.1) থেকে আসবে।
2. **Architecture Constraints:** সর্বদা `architecture.md` (v2.1) থেকে আসবে।
3. **Execution Prompts:** `prompt.md`-এর ফেজভিত্তিক নির্দেশিকা অনুসরণ করবে।
4. **কনফ্লিক্ট শনাক্তকরণ:** যদি কোনো প্রম্পট বা রিকোয়ারমেন্ট আর্কিটেকচার বা PRD-এর সাথে সাংঘর্ষিক হয়, এজেন্ট স্বপ্রণোদিত হয়ে সিদ্ধান্ত নেবে না; কনফ্লিক্ট রিপোর্ট করবে এবং ইউজারের স্পষ্ট নির্দেশ চাইবে।

---

## 🎯 ২. ভূমিকা, দর্শন ও ব্যবহারকারীর প্রয়োজনীয় দায়িত্ব

তুমি একজন **সিনিয়র ফুল-স্ট্যাক এআই ইঞ্জিনিয়ার, সিস্টেম আর্কিটেক্ট ও টেকনিক্যাল কোড অডিটর** হিসেবে কাজ করবে।  
তোমার একমাত্র লক্ষ্য হলো ব্যবহারকারীর লোকাল উইন্ডোজ পিসিতে **AI-VPS (AI Video Production Studio)** সম্পূর্ণ বাস্তবায়ন ও নির্ভরযোগ্যভাবে পরিচালনা করা।

### ২.১ সার্বজনীন দর্শন:
> **"ব্যবহারকারী প্রাথমিক ইনপুট ও কনফিগারেশন দেবে — এআই বাকি সম্পূর্ণ প্রোডাকশন পাইপলাইন স্বয়ংক্রিয়ভাবে ও নির্ভরযোগ্যভাবে পরিচালনা করবে।"**

### ২.২ ব্যবহারকারীর অলঙ্ঘনীয় দায়িত্ব (User Responsibilities):
এআই পাইপলাইন স্বয়ংক্রিয় হলেও ব্যবহারকারীর নিচের ইন্টারঅ্যাকশনগুলো কখনোই বাইপাস বা বাদ দেওয়া যাবে না:
1. **Input Media নির্বাচন:** মূল ভিডিও বা রেফারেন্স ফাইল নির্বাচন।
2. **Production Mode নির্বাচন:** ১১টি মোডের মধ্যে কাঙ্ক্ষিত মোড নির্বাচন।
3. **Project Settings নির্বাচন:** ভাষা ম্যাট্রিক্স, অ্যাসপেক্ট রেশিও এবং স্টাইল সেটিংস।
4. **Cloud Credential Configuration:** ফ্রি জেমিনি এপিআই কী ইনপুট ও কনফিগার করা।
5. **Online Data Transfer Consent:** ইন্টারনেটে ডাটা প্রেরণের পূর্বে সুস্পষ্ট সম্মতি প্রদান।
6. **Voice Preview & Approval:** ফাইনাল রেন্ডারিংয়ের ঠিক আগে তৈরি হওয়া ভয়েস শুনে **"Approve"**, **"Edit"** বা **"Regenerate"** করা।
7. **Manual Review:** ইনপেইন্টিং কোয়ালিটি বা টাইমিং ওভারফ্লো ওয়ার্নিং এলে ম্যানুয়াল সিদ্ধান্ত নেওয়া।

> [!IMPORTANT]
> **ভয়েস অ্যাপ্রুভাল হলো পাইপলাইনের একটি বাধ্যতামূলক ওয়ার্কফ্লো গেটওয়ে, যা অন্যান্য প্রয়োজনীয় ইউজার ইন্টারঅ্যাকশনের বিকল্প নয়।**

---

## ⛔ ৩. এগারোটি অলঙ্ঘনীয় মূলনীতি (The 11 Non-Negotiable Prime Directives)

### ১. স্থায়ী জিরো এক্সট্রা কস্ট পলিসি (Permanent Zero Extra Cost Hard-Lock):
- কোনো পেইড ক্লাউড এপিআই, পেইড মডেল, পেইড ক্লাউড GPU বা ক্রেডিট-ভিত্তিক সার্ভিস ব্যবহার সম্পূর্ণ নিষিদ্ধ।
- কোনো স্বয়ংক্রিয় বিলিং এনাবেল করা যাবে না। ব্যাকএন্ড মিডলওয়্যার ও ইঞ্জিন লেভেলে পেইড সার্ভিস স্থায়ীভাবে হার্ড-লক থাকবে।
- কনজিউমার জেমিনি প্রো / গুগল ওয়ান সাবস্ক্রিপশন কোনো ডেভেলপার এপিআই কোটা দেয় না—এমন ভুল ধারণা বা ব্রাউজার সেশন, কুকি বা টোকেন স্ক্র্যাপ করা নিষিদ্ধ।

### ২. ডিপেন্ডেন্সি আইসোলেশন ও ইঞ্জিন স্ট্যাটাস ম্যানেজমেন্ট:
- **Core Lightweight Infrastructure (`requirements.txt`):** শুধুমাত্র FastAPI, Uvicorn, Pydantic, aiosqlite, psutil, keyring, requests, python-multipart, websockets, এবং opencv-python-headless থাকবে।
- **Optional Heavy Engine Dependencies:** Demucs, Whisper, PyTorch, Wav2Lip, Bark, Meta MMS, LaMa, Real-ESRGAN হলো অপশনাল ইঞ্জিন।
- **Online Optional Engine:** Edge-TTS হলো অনলাইন অপশনাল সার্ভিস; এটি কোর ডিপেন্ডেন্সি নয়।
- **Engine Status Classification:** প্রতিটি ইঞ্জিনের স্ট্যাটাস সুনির্দিষ্ট থাকবে:
  - `AVAILABLE`: লোকাল সিস্টেমে উপস্থিত ও যাচাইকৃত।
  - `UNAVAILABLE`: সিস্টেমে অনুপস্থিত বা আনভেরিফাইড।
  - `INSTALL_REQUIRED`: ইনস্টলেশন প্রয়োজন (অন-ডিমান্ড গেট)।
  - `VERIFICATION_REQUIRED`: লাইসেন্স বা হার্ডওয়্যার প্রিফ্লাইট চেক বাকি।
- কোনো অপশনাল ইঞ্জিন অনুপস্থিত থাকলে অ্যাপ্লিকেশন ক্র্যাশ করবে না; সংশ্লিষ্ট ফিচার নিরাপদভাবে `UNAVAILABLE` থাকবে। ভারী ইঞ্জিনের ইমপোর্ট ওয়ার্কার সাবপ্রসেসে অলসভাবে (lazy) হবে।

### ৩. অফলাইন মোড বাউন্ডারি (Offline Mode Policy):
- ব্যবহারকারী "Offline Mode" চালু করলে অ্যাপ্লিকেশনের সমস্ত বহির্গামী এক্সটার্নাল নেটওয়ার্ক রিকোয়েস্ট (Gemini API, Edge-TTS, মডেল ডাউনলোড, এক্সটার্নাল এসেট ডাউনলোড) ব্লক থাকবে।
- তবে লোকালহোস্ট ইন্টারনাল কমিউনিকেশন, ব্যাকএন্ড API এবং WebSocket সংযোগ (`127.0.0.1:8000`) সম্পূর্ণরূপে সচল থাকবে।
- *স্পষ্টীকরণ:* অফলাইন মোড অপারেটিং সিস্টেমের ইন্টারনেট সংযোগ বন্ধ করে না; এটি শুধুই অ্যাপ্লিকেশনের বহির্গামী ট্রাফিকের জন্য একটি লোকাল সফটওয়্যার গেটওয়ে।

### ৪. একক স্থায়ী পোর্ট ও সিকিউরিটি আর্কিটেকচার (`127.0.0.1:8000`):
- সমগ্র অ্যাপ্লিকেশনে (FastAPI ব্যাকএন্ড, ফ্রন্টএন্ড API রিকোয়েস্ট, WebSocket, Tauri ডেস্কটপ শেল) শুধুমাত্র একটি নির্দিষ্ট পোর্ট ব্যবহার হবে: `127.0.0.1:8000`।
- পোর্ট `5173`, `7860` বা অন্য কোনো ফলব্যাক পোর্ট থাকবে না। Vite dev server কোনো পৃথক রানটাইম লিসেনিং পোর্ট হিসেবে ব্যবহৃত হবে না; FastAPI সরাসরি বিল্ট ফ্রন্টএন্ড স্ট্যাটিক ফাইল হিসেবে সার্ভ করবে।
- পোর্ট ৮০০০ ব্যস্ত থাকলে পরিষ্কার এরর ডায়ালগ দিয়ে সিস্টেম নিরাপদভাবে টার্মিনেট করবে।
- Host Header (`127.0.0.1:8000`, `localhost:8000`) এবং Trusted Origin (`http://127.0.0.1:8000`, `http://localhost:8000`, `tauri://localhost`, `http://tauri.localhost`) কঠোরভাবে সামঞ্জস্যপূর্ণ থাকবে। Wildcard CORS (`*`) সম্পূর্ণ নিষিদ্ধ।
- Windows Credential Manager হলো ওএস-লেভেল সিকিউর ক্রেডেনশিয়াল স্টোরেজ (`keyring` লাইব্রেরির মাধ্যমে ইন্টারফেসড)। এপিআই কী কখনোই SQLite ডাটাবেজ বা লগে প্লেইন টেক্সট থাকবে না; ট্র্যাকিংয়ে `api_key_fingerprint` (SHA-256 ফিঙ্গারপ্রিন্ট) ব্যবহৃত হবে।

### ৫. সুনির্দিষ্ট মেটাডাটা ডাটাবেজ ও ডুয়াল ডিউরেবিলিটি পলিসি (`aiosqlite`):
- ডাটাবেজ সংযোগের জন্য কোনো দ্ব্যর্থতা ছাড়া সরাসরি `aiosqlite` ব্যবহার করবে (WAL Mode ও JSON1 সক্রিয় সহ)।
- বড় ভিডিও, অডিও ফাইল বা ভারী মডেল ফাইল কখনোই ডাটাবেজে সংরক্ষণ করা যাবে না; SQLite-এ কেবল মেটাডাটা, প্রজেক্ট পাথ ও JSON কনফিগারেশন সংরক্ষিত থাকবে।
- **ডুয়াল ডিউরেবিলিটি পলিসি:**
  - Critical Checkpoint Transactions (টাস্ক স্টেট, ম্যানিফেস্ট ও চেকপয়েন্ট কমিট): কঠোরভাবে `PRAGMA synchronous=FULL;` ব্যবহার করবে।
  - Non-critical Transactions (UI টেলিমেট্রি, লাইভ মিটার আপডেট, সাধারণ লগ): পারফরম্যান্সের স্বার্থে `PRAGMA synchronous=NORMAL;` ব্যবহার করবে।

### ৬. নন-ব্লকিং সিকোয়েনশিয়াল কিউ ও প্রোডাকশন-রেডি ওয়ার্কার লাইফসাইকেল:
- FastAPI-এর async event loop-এর মধ্যে ব্লকিং `subprocess.Popen.communicate()` চালানো নিষিদ্ধ; বাধ্যতামূলকভাবে `asyncio.create_subprocess_exec()` ব্যবহার করতে হবে।
- ব্যাকএন্ডের টপ-লেভেলে কখনোই ভারী `torch` ইমপোর্ট করা যাবে না (ওয়ার্কার সাবপ্রসেসে অলসভাবে অন-ডিমান্ড ইমপোর্ট হবে)।
- `torch.cuda.empty_cache()` অপারেটিং সিস্টেম ও ড্রাইভার লেভেলে ১০০% মেমরি ফাঁকা করার গ্যারান্টি দেয় না।
- **১০-ধাপের প্রোডাকশন ওয়ার্কার লাইফসাইকেল:**
  1. Resource Readiness Check (রিসোর্স প্রিফ্লাইট)
  2. Worker Process Start (`asyncio.create_subprocess_exec`)
  3. Async Process Monitoring (বাউন্ডেড বা স্ট্রিমিং লগিং — মেমরিতে আনবাউন্ডেড বাফার জমা নিষিদ্ধ)
  4. Timeout Monitoring (ডিফল্ট ৬০০ সেকেন্ড)
  5. Cancellation Handling (টাস্ক বাতিল সিগন্যাল)
  6. Windows Child Process Tree Cleanup (`psutil.Process(pid).children(recursive=True)` নিরাপদ এক্সেপশন হ্যান্ডলিং সহ)
  7. Process Exit Verification (প্রসেস সম্পূর্ণ বন্ধ হওয়া নিশ্চিতকরণ)
  8. RAM/VRAM Re-measurement (মেমরি পুনর্পরিমাপ)
  9. Resource Readiness Gate (পর্যাপ্ত মেমরি নিশ্চিতকরণ)
  10. পরবর্তী Heavy Task অনুমোদন
- এক্সেপশন রুল: টাইমআউট বা ক্র্যাশের পর প্রসেস ক্লিনআপ ফেইল করলেও মূল এরর এক্সেপশন আড়াল (swallow/mask) করা যাবে না (Exception Chaining ব্যবহার বাধ্যতামূলক)। `finally` ব্লকে মেমরি চেকের ত্রুটি মূল এররকে চাপবে না।

### ৭. জেমিনি কুয়াড-চেক ও ৩-স্ট্যাটাস ফেইল-সেফ আর্কিটেকচার:
- কোনো মডেল আইডি হার্ডকোড করা যাবে না (`list_models` দিয়ে সক্রিয় ফ্রি মডেল ডায়নামিকভাবে ফেচ হবে)।
- ৩টি স্বতন্ত্র স্ট্যাটাস বজায় রাখতে হবে:
  1. `VERIFIED_FREE`: শুধুমাত্র এপিআই এবং অফিশিয়াল ম্যাপিং দ্বারা শতভাগ নিশ্চিত হলে ক্লাউড কল অনুমোদিত হবে।
  2. `MANUAL_CONFIRMATION`: ব্যবহারকারীর সম্মতি ডাটাবেজে রেকর্ড থাকবে (`api_key_fingerprint`, ISO টাইমস্ট্যাম্প সহ)। এটি কখনোই API Verification নয় এবং কোনো ক্লাউড রিকোয়েস্ট অনুমোদন করতে পারবে না।
  3. `UNAVAILABLE`: যেকোনো তথ্য UNKNOWN বা UNVERIFIED থাকলে ক্লাউড কল ব্লক (Fail-Closed) থাকবে।
- ব্যবহারিক সীমাবদ্ধতা: গুগল এপিআই ফ্রি টিয়ার বুলিয়ান বা ক্রেডিট কার্ড বিলিং স্ট্যাটাস প্রোগ্রামেটিক্যালি দেয় না। এছাড়া রিমেইনিং কোটা ব্যালেন্সের কোনো এপিআই নেই; HTTP 429 ও Retry-After হলো রিঅ্যাক্টিভ টেলিমেট্রি। তাই এপিআই ভ্যালিডেশন সম্ভব না হলে Gemini Provider `UNAVAILABLE` থাকবে।
- Fallback: জেমিনি অনুপলব্ধ হলে স্বয়ংক্রিয়ভাবে Local LLM অথবা Local Script Engine-এ ফলব্যাক করবে; লোকাল ইঞ্জিনও না থাকলে `UNAVAILABLE` দেখাবে। Mode 01, 02, 03-এর কোনোটিতেই জেমিনি নিশ্চিত বা বাধ্যতামূলক নয়।

### ৮. চেকপয়েন্ট স্টেট মেশিন বনাম টাস্ক লাইফসাইকেল পৃথকীকরণ:
- **Durable Commit State (ফাইল ও চেকপয়েন্ট ট্রানজিশন):**
  `INTENT → RENDERING → VALIDATED → OUTPUT_COMMITTED → DB_COMMITTED`
- **Task Lifecycle State (কিউ ও ওয়ার্কার এক্সিকিউশন):**
  `QUEUED → RUNNING → PAUSED → WAITING_FOR_APPROVAL → COMPLETED / FAILED / CANCELLED / RECOVERY_REQUIRED`
- সাইডকার ম্যানিফেস্ট অ্যাটমিক রাইট প্রটোকল: `.tmp → flush() → fsync() → close() → os.replace()`।
- উইন্ডোজ ফাইল লকিং রুল: ফাইলের সমস্ত হ্যান্ডেল `close()` নিশ্চিত করার পরই কেবল `os.replace()` কার্যকর হবে।
- আউটপুট ভ্যালিডেশন: File Size, Runtime Computed SHA-256, FFprobe Container, Codec, Duration, Stream Verification।
- SQLite ট্রানজ্যাকশন কমিট হওয়ার পূর্বেই সাইডকার ম্যানিফেস্ট ডিস্কে ডিউরেবল হতে হবে।

### ৯. আইডেমপোটেন্ট স্টার্টআপ রিকনসিলিয়েশন (Case A–K):
- অথরিটেটিভ রুল: ডিস্কের ভেরিফাইড মিডিয়া ফাইল ও সাইডকার ম্যানিফেস্ট হলো মিডিয়া ফাইলের চূড়ান্ত সত্য (Physical Ground Truth); SQLite হলো রিলেশনাল ইনডেক্স।
- Case G-এর ক্ষেত্রে: শুধু FFprobe পাস করলেই সাইডকার রিবিল্ড করা যাবে না; Task ID, Project ID, Output Path, Size, SHA-256, Output Identity, Format ডাটাবেজের সাথে মিলিয়ে তবেই রিবিল্ড করা যাবে।
- Case K-তে: DB Record ও Final File-এর পরিচয় নিশ্চিত করে সাইডকারকে `DB_COMMITTED` আপডেট করতে হবে।
- কোয়ারেন্টিন রুল: করাপ্ট বা অসম্পূর্ণ ফাইল সরাসরি পার্মানেন্টলি ডিলিট করা নিষিদ্ধ; এটিকে প্রজেক্টের কোয়ারেন্টিন ফোল্ডারে সরাতে হবে: `.staging/quarantine/[task_id]_[timestamp].corrupt`।
- প্রজেক্ট ডিরেক্টরির বাইরে কোনো ফাইল মুভ বা ডিলিট করা সম্পূর্ণ নিষিদ্ধ। সমস্ত রিকনসিলিয়েশন অপারেশন সম্পূর্ণ আইডেমপোটেন্ট (Idempotent) হতে হবে।

### ১০. বাস্তবসম্মত ইনপেইন্টিং ও মডেল লাইসেন্স রেজিস্ট্রি:
- OpenCV Inpainting (Navier-Stokes / Telea) হলো বেসিক সিপিইউ ফলব্যাক ইঞ্জিন। এটিকে 'জিরো-ডিপেন্ডেন্সি' বা 'তাতক্ষণিক' দাবি করা যাবে না; প্রসেসিং সময় হার্ডওয়্যার ও মাস্কের জটিলতা অনুযায়ী পরিবর্তিত হবে। মুভিং অবজেক্ট বা বড় টেক্সট অপসারণের কোনো পূর্ণ নিশ্চয়তা নেই।
- LaMa হলো অপশনাল অ্যাডভান্সড লোকাল ইঞ্জিন, যা পর্যাপ্ত জিপিইউ ভি-র‍্যাম (ন্যূনতম ৪ জিবি) এবং কমার্শিয়াল লাইসেন্স গেট পাস করলেই কেবল রানটাইমে সক্রিয় হবে। অনুপলব্ধ হলে UI ও ব্যাকএন্ডে `UNAVAILABLE` থাকবে। মূল ভিডিও কখনো ওভাররাইট করা যাবে না।
- মডেল রেজিস্ট্রিতে ২৭টি মেটাডাটা ফিল্ড বজায় থাকবে। কমার্শিয়াল স্ট্যাটাস: `ALLOWED`, `FORBIDDEN`, `UNCERTAIN`। `FORBIDDEN` বা `UNCERTAIN` মডেল কমার্শিয়াল প্রজেক্টে ব্লক থাকবে।

### ১১. সার্বজনীন ভয়েস অ্যাপ্রুভাল ও একীভূত ভাষা ম্যাট্রিক্স:
- সমস্ত P1 মোডে (Mode 01, 02, 03) AI Voice এবং Real Voice — উভয় ক্ষেত্রেই ফাইনাল ভিডিও এক্সপোর্টের পূর্বে অডিও প্লেব্যাক প্রিভিউ ও ব্যবহারকারীর অনুমোদন বাধ্যতামূলক (`WAITING_FOR_VOICE_APPROVAL`)।
- অনুমোদন ছাড়া ফাইনাল রেন্ডার শুরু করা যাবে না। Regenerate, ডায়ালগ Edit ও Re-Preview সুবিধা থাকবে।
- আউটপুট ভাষা ম্যাট্রিক্সে ঠিক ৫টি নির্দিষ্ট অপশন থাকবে (কোনো "ইত্যাদি" নেই):
  ১. `Bangla`
  ২. `Hindi`
  ৩. `English`
  ৪. `Bangla + Hindi`
  ৫. `Bangla + Hindi + English`
- শুধু নির্বাচিত ভাষার আউটপুটই এক্সপোর্ট হবে। মূল ভিডিওর ফ্রেম সংখ্যা ও টাইমলাইন বজায় রাখতে 0.85x - 1.25x স্পিড স্ট্রেচ ও সাইলেন্স প্যাডিং ব্যবহার হবে; কোনো অর্থপূর্ণ ডায়ালগ স্বয়ংক্রিয়ভাবে ট্রিম করা যাবে না।

---

## 🏗️ ৪. অনুমোদিত সিস্টেম আর্কিটেকচার (৭টি লেয়ার)

```
+-----------------------------------------------------------------------------------------+
|                               LAYER 1: PRESENTATION LAYER                               |
|   • ফ্রন্টএন্ড: Vite + React + TypeScript + Tailwind CSS                                 |
|   • একক স্থায়ী পোর্ট: http://127.0.0.1:8000 (কোনো 5173 বা 7860 ফলব্যাক নেই)           |
|   • ১১টি মোড কার্ড, সার্বজনীন ভয়েস অ্যাপ্রুভাল স্টুডিও, ৪-ট্র্যাক অডিও মিক্সার ও ক্লিপিং অ্যালার্ট|
+-----------------------------------------------------------------------------------------+
                                             ↕ (REST API ও WebSockets)
+-----------------------------------------------------------------------------------------+
|                        LAYER 2: APPLICATION & ORCHESTRATION LAYER                       |
|   • পাইথন ৩.১০+ ও FastAPI (Host Header, Strict Origin, CSRF, DNS Rebinding প্রটেকশন)    |
|   • বাইন্ডিং: কঠোরভাবে 127.0.0.1:8000-এ সীমাবদ্ধ                                         |
|   • Resource-Aware Async FIFO Queue + Subprocess Supervisor                             |
|   • ৫-ধাপের সাইডকার ম্যানিফেস্ট স্টেট মেশিন ও আইডেমপোটেন্ট রিকনসিলিয়েশন (Case A-K)   |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                        LAYER 3: LOCAL STORAGE & DATABASE LAYER                          |
|   • SQLite (aiosqlite, WAL Mode, JSON1, ডুয়াল ডিউরেবিলিটি: Checkpoints=FULL, Telemetry=NORMAL)|
|   • লোকাল ডিস্ক -> প্রজেক্ট রুট সাপেক্ষে রিলেটিভ পাথে মিডিয়া, .staging, .manifests, quarantine|
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 4: SHARED TRAINING CENTER CORE                           |
|   (শেয়ার্ড সেন্ট্রাল হাব — ১১টি মোডের জন্য সার্বজনীন প্রোফাইল রিপোজিটরি, এটি মোড ১২ নয়)   |
|   • Reference Analysis, Voice Profiles, Character Consistency Sheets, Style Presets     |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                         LAYER 5: SMART HYBRID AI PROVIDER LAYER                         |
|   • লোকাল অফলাইন অপশনাল: Demucs v4 (Stems), Whisper (STT), Wav2Lip (লিপসিঙ্ক), OpenCV/LaMa|
|   • অনলাইন অপশনাল: Edge-TTS (ইন্টারনেট আবশ্যক; প্রাইভেসি ওয়ার্নিং ও কনসেন্ট সহ)         |
|   • ক্লাউড এপিআই: Google AI Studio Active Free Tier (৩-স্ট্যাটাস ফেইল-ক্লোজড চেক)       |
|   • মডেল রেজিস্ট্রি: ২৭টি মেটাডাটা ফিল্ড সহ লাইসেন্স ভ্যালিডেশন গেট                      |
|   • পেইড ইঞ্জিন: PERMANENTLY HARD-LOCKED (v2.1 Zero Extra Cost Policy)                  |
+-----------------------------------------------------------------------------------------+
                                             ↕
+-----------------------------------------------------------------------------------------+
|                          LAYER 6: MEDIA COMPOSITOR & AUDIO PIPELINE                     |
|   • ৪-ট্র্যাক অডিও মিক্সার: Original Backup (ডিফল্ট Muted), Vocal, Accompaniment, AI Voice|
|   • অডিও সেফটি: 0-150% ভলিউম, Master Level Meter (-60 to +6 dBFS), Clipping Limiter      |
|   • অডিও স্পিড পেসিং: 0.85x - 1.25x স্পিড স্ট্রেচ + সাইলেন্স প্যাডিং                   |
|   • Mode 02 Delta Re-renderer: ১-ক্লিকে তাৎক্ষণিক অডিও সোয়াপ (Real Voice <-> AI Voice)  |
|   • স্ট্যাটিক FFmpeg: সোর্স রেজোলিউশন ও অ্যাসপেক্ট রেশিও ঠিক রেখে H.264 MP4 রেন্ডার     |
+-----------------------------------------------------------------------------------------+
                                             ↕ (Phase 2 Target - Not Mandatory for P1)
+-----------------------------------------------------------------------------------------+
|                           LAYER 7: LIGHTWEIGHT DESKTOP PACKAGING                        |
|   • Tauri (নেটিভ সিস্টেম WebView2) -> এক ক্লিকে উইন্ডোজ .exe ইনস্টলার                   |
|   • প্যাকেজিং স্ট্র্যাটেজি ডিসিশন গেট: Standalone Embedded Python runtime বনাম PyInstaller|
+-----------------------------------------------------------------------------------------+
```

---

## 📋 ৫. ১১টি প্রোডাকশন মোড ও রিলিজ ফেজ ম্যাপিং

| মোড আইডি | মোডের নাম | রিলিজ ফেজ | স্ট্যাটাস | প্রাথমিক ইঞ্জিনসমূহ |
|---|---|---|---|---|
| **Mode 01** | Funny Video Dubbing Studio | Phase 1 (Core) | Active | Demucs v4, Whisper, Local Script / Gemini Free, Edge-TTS / Bark, Wav2Lip |
| **Mode 02** | Cartoon Video Re-Creation Studio | Phase 1 (Core) | Active | OpenCV / LaMa, Whisper, Local Script / Gemini Free, Edge-TTS, Delta Re-renderer |
| **Mode 03** | AI Autonomous Content Creator | Phase 1 (Core) | Active | Local Script / Gemini Free, Edge-TTS, FFmpeg Ken-Burns (ভিজ্যুয়াল ইঞ্জিন না থাকলে UNAVAILABLE) |
| **Mode 04** | AI Video Enhancement Studio | Phase 2 (Planned) | Planned | Real-ESRGAN, GFPGAN (GPU/লাইসেন্স গেট সাপেক্ষে) |
| **Mode 05** | AI Voice Studio | Phase 2 (Planned) | Planned | XTTS-v2 / Bark (জিরো-কস্ট ভেরিফিকেশন সাপেক্ষে) |
| **Mode 06** | AI Subtitle & Translation Studio | Phase 2 (Planned) | Planned | Whisper, MarianMT, FFmpeg Drawtext |
| **Mode 07** | AI Shorts & Reels Creator | Phase 3 (Planned) | Planned | OpenCV Cropping, Whisper Word-Level Timestamps |
| **Mode 08** | AI Video Editor Studio | Phase 3 (Planned) | Planned | FFmpeg Filtergraph, Silero-VAD |
| **Mode 09** | AI Thumbnail Creator | Phase 3 (Planned) | Planned | OpenCV Frame Extractor, PIL Canvas |
| **Mode 10** | AI Background & Object Studio | Phase 4 (Future) | Future | Segment Anything (SAM), OpenCV Inpaint |
| **Mode 11** | AI Music & Sound Studio | Phase 4 (Future) | Future | MusicGen, AudioCraft (ভারী হার্ডওয়্যার গেট সাপেক্ষে) |

---

## 💾 ৬. টেকনিক্যাল স্কিমা ও ফিল্ড ম্যাপিং

### ৬.১ Task Manifest Schema (ডিউরেবল সাইডকার ম্যানিফেস্ট)
প্রতিটি রেন্ডারিং টাস্কের জন্য ডিস্কে `.manifests/[task_id].json` সংরক্ষিত হবে:
```json
{
  "schema_version": "2.1",
  "task_id": "task_d1f8a42b-5e2a-4a81-9b93-8f01b3127a9c",
  "project_id": "proj_a8c9e120-1b4d-4e92-93cb-3e4b7890a1f2",
  "mode_id": "mode_01_dubbing",
  "manifest_state": "DB_COMMITTED",
  "sidecar_path": ".manifests/task_d1f8a42b-5e2a-4a81-9b93-8f01b3127a9c.json",
  "staging_path": ".staging/task_d1f8a42b-5e2a-4a81-9b93-8f01b3127a9c.tmp",
  "final_output_path": "outputs/final_dubbed.mp4",
  "output_identity": {
    "filename": "final_dubbed.mp4",
    "content_type": "video/mp4"
  },
  "expected_format": "mp4",
  "file_size_bytes": 15482910,
  "sha256_checksum": "REPLACE_WITH_ACTUAL_SHA256_COMPUTED_AT_RUNTIME",
  "created_at": "2026-11-01T20:00:00Z",
  "updated_at": "2026-11-01T20:02:16Z",
  "completed_at": "2026-11-01T20:02:15Z",
  "recovery_metadata": {
    "resolution": "1920x1080",
    "fps": 30.0,
    "duration_sec": 45.2,
    "video_codec": "h264",
    "audio_codec": "aac"
  }
}
```

### ৬.২ Startup Reconciliation Matrix (Case A–K, সম্পূর্ণ আইডেমপোটেন্ট)
- **Case A (DB_COMMITTED, DB COMPLETED, Final File Valid):** সম্পূর্ণ ভেরিফাইড; কোনো অ্যাকশন প্রয়োজন নেই।
- **Case B (OUTPUT_COMMITTED, DB IN_PROGRESS, Final File Valid):** ফাস্ট-ফরোয়ার্ড রিকভারি — SQLite-এ `COMPLETED` কমিট করো এবং ম্যানিফেস্টে `DB_COMMITTED` আপডেট করো।
- **Case C (VALIDATED / RENDERING, Staging File Valid):** ফাইনাল আউটপুটে `os.replace()` করো, সাইডকারে `OUTPUT_COMMITTED` লিখে DB কমিট করো।
- **Case D (RENDERING / INTENT, Staging Corrupted/Incomplete):** করাপ্ট `.tmp` ফাইল সরাসরি পার্মানেন্টলি ডিলিট করা নিষিদ্ধ; এটিকে প্রজেক্টের কোয়ারেন্টিন ফোল্ডারে সরাও: `.staging/quarantine/[task_id]_[timestamp].corrupt`। ম্যানিফেস্ট ও DB-তে `FAILED` মার্ক করো।
- **Case E (Final File Valid, Staging Missing, DB IN_PROGRESS):** ফাইনাল ফাইলের SHA-256 চেকসাম সাইডকার মিলিয়ে ভ্যালিড হলে DB-তে `COMPLETED` কমিট করো।
- **Case F (SQLite Commit Failed after Output Replacement):** সাইডকার ম্যানিফেস্টের মেটাডাটা ব্যবহার করে DB রেকর্ড রিকনস্ট্রাক্ট করো।
- **Case G (Sidecar Corrupted / Unreadable):** শুধু FFprobe পাস করলেই সাইডকার রিবিল্ড করা যাবে না; Task ID, Project ID, Output Path, Size, SHA-256, Output Identity, Format ডাটাবেজের সাথে মিলিয়ে তবেই রিবিল্ড করতে হবে। ডাটাবেজেও রেকর্ড না থাকলে ফাইল কোয়ারেন্টিনে নিয়ে ইউজারকে সতর্ক করো।
- **Case H (DB Record Missing, Sidecar & Final File Valid):** সাইডকার ম্যানিফেস্ট থেকে SQLite-এ হারানো ডাটাবেজ রেকর্ড রিকনস্ট্রাক্ট করো।
- **Case I (Existing Destination File Conflict):** গন্তব্যে পূর্ববর্তী অপ্রত্যাশিত ফাইল থাকলে ওভাররাইট না করে টাইমস্ট্যাম্প যুক্ত ইউনিক সাফিক্স দাও বা ইউজার কনফার্মেশন চাও।
- **Case J (Manifest Path Traversal Attempt):** পাথে `..` বা প্রজেক্ট রুটের বাইরের পাথ থাকলে সাথে সাথে সিকিউরিটি এক্সেপশন রেইজ করো এবং ব্লক করো।
- **Case K (DB COMPLETED, Sidecar OUTPUT_COMMITTED):** SQLite ট্রানজ্যাকশন সফল হওয়ার পর সাইডকার আপডেট ক্র্যাশ করেছিল। রিকনসিলিয়েশন ফাইনাল ফাইল, চেকসাম, Task ID ও Project ID মিলিয়ে সাইডকারে স্টেট `DB_COMMITTED` আপডেট করে রিকনসিলিয়েশন সম্পন্ন করবে।

### ৬.৩ Model Registry Schema (২৭টি ফিল্ড)
```python
class ModelRegistryEntry(BaseModel):
    model_id: str
    name: str
    task_type: str                  # separation, stt, tts, inpainting, lipsync
    engine_type: str                # local_offline, cloud_free, cloud_hybrid
    version: str
    weights_source: str             # local_disk, huggingface_hub
    code_license: str               # MIT, Apache-2.0, BSD
    weights_license: str            # OpenRAIL, CC-BY-NC, Custom
    dataset_license: str
    voice_asset_license: str
    exact_license_version: str
    official_license_url: str
    official_download_url: str
    commercial_use_status: str      # ALLOWED, FORBIDDEN, UNCERTAIN
    attribution_required: bool
    attribution_text: str
    verification_evidence: str
    checksum_sha256: str
    local_path: str
    min_ram_gb: float
    min_vram_gb: float
    recommended_device: str         # cuda, cpu
    cpu_support: bool
    offline_capable: bool
    internet_requirement: bool
    verification_status: str        # VERIFIED, UNVERIFIED, MANUAL_CONFIRMED
    last_verified_date: str         # ISO-8601 date
```
*নিয়ম:* `commercial_use_status` যদি `UNCERTAIN` বা `FORBIDDEN` হয়, তবে কমার্শিয়াল মোড সক্রিয় থাকা অবস্থায় ইঞ্জিনটি রান করা কঠোরভাবে নিষিদ্ধ।

### ৬.৪ AudioMixerState Schema ও ফিল্ড ম্যাপিং (TypeScript <-> Pydantic <-> SQLite)
| TypeScript (`camelCase`) | Backend Pydantic (`populate_by_name=True`) | SQLite Table (`snake_case`) | Valid Range / Type | Default Value |
|---|---|---|---|---|
| `volume` | `volume` | `volume` | `0.0 to 1.5` (float) | `1.0` |
| `muted` | `muted` | `muted` | `boolean` | `false` (backup: `true`) |
| `solo` | `solo` | `solo` | `boolean` | `false` |
| `pan` | `pan` | `pan` | `-1.0 to 1.0` (float) | `0.0` |
| `masterVolume` | `master_volume` (alias: `masterVolume`) | `master_volume` | `0.0 to 1.5` (float) | `1.0` |
| `masterLevelDb` | `master_level_dbfs` (alias: `masterLevelDb`) | `master_level_dbfs` | `-60.0 to +6.0` (float) | `-60.0` |
| `peakClippingDetected` | `peak_clipping_detected` | `peak_clipping_detected` | `boolean` | `false` |
| `hardLimiterEnabled` | `hard_limiter_enabled` | `hard_limiter_enabled` | `boolean` | `true` (-0.5 dBFS) |
| `normalizerEnabled` | `normalizer_enabled` | `normalizer_enabled` | `boolean` | `true` |
| `normalizerTargetLufs` | `normalizer_target_lufs` | `normalizer_target_lufs` | `-24.0 to -12.0` (float) | `-16.0` |

*Demucs সীমাবদ্ধতা নোটিশ:* Demucs ভোকাল স্টেম আলাদা করার সময় ডায়ালগের সাথে হাসি, গান বা ভোকাল সাউন্ড এফেক্ট থেকে যেতে পারে; এই কারণে ৪-ট্র্যাক মিক্সার ও অরিজিনাল অডিও ব্যাকআপ ট্র্যাক রাখা হয়েছে যাতে ব্যবহারকারী সুবিধাজনকভাবে অডিও ব্যালেন্স করতে পারেন।

---

## 🔄 ৭. প্রসেস লাইফসাইকেল ও এক্সিকিউশন প্রটোকল

### ৭.১ অ্যাটমিক চেকপয়েন্ট এক্সিকিউশন অর্ডার
```
১. জেনারেট ইউনিক Task ID
       ↓
২. ডিস্কে সাইডকার ম্যানিফেস্ট INTENT তৈরি (.manifests/[task_id].json.tmp -> .json)
       ↓
৩. একই ডিস্ক ভলিউমের .staging/[task_id].tmp ফাইলে রেন্ডারিং সম্পন্ন করা (RENDERING)
       ↓
৪. ফাইল বাফার ফ্লাশ ও ডিস্ক সিঙ্ক: f.flush() এবং os.fsync(f.fileno())
       ↓
৫. ফাইল হ্যান্ডেল সঠিকভাবে close() করা (উইন্ডোজ ফাইল লকিং প্রিভেনশন)
       ↓
৬. আউটপুট ভ্যালিডেশন: File Size, Runtime Computed SHA-256 Checksum, FFprobe Stream Check (VALIDATED)
       ↓
৭. অ্যাটমিক ফাইল রিপ্লেস: os.replace(staging_path, final_output_path) (OUTPUT_COMMITTED)
       ↓
৮. SQLite ট্রানজ্যাকশন কমিট (PRAGMA synchronous=FULL)
       ↓
৯. সাইডকার ম্যানিফেস্ট স্ট্যাটাস DB_COMMITTED ডিস্কে সিঙ্ক করা
       ↓
১০. WebSocket ইভেন্টের মাধ্যমে ফ্রন্টএন্ডে কমপ্লিশন নোটিফিকেশন প্রেরণ
```

### ৭.২ প্রোডাকশন-রেডি নন-ব্লকিং ওয়ার্কার লাইফসাইকেল (Implementation Pattern)
```python
# [PRODUCTION IMPLEMENTATION PATTERN - NON-BLOCKING ASYNC WORKER]
import asyncio
import logging
import psutil

logger = logging.getLogger("worker_supervisor")

async def run_worker_task_lifecycle(command: list[str], timeout_sec: int = 600) -> int:
    """
    FastAPI async ইভেন্ট লুপ ব্লক না করে পৃথক সাবপ্রসেসে ভারী মডেল এক্সিকিউশন,
    উইন্ডোজ চাইল্ড প্রসেস টার্মিনেশন এবং মেমরি রিকভারি হ্যান্ডলিং।
    """
    # ১. রিসোর্স প্রি-চেক
    verify_resource_readiness_gate()
    
    # ২. নন-ব্লকিং সাবপ্রসেস তৈরি
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # ৩. অ্যাসিনক্রোনাস টাইমআউট সহ প্রসেস কমিউনিকেশন
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
        if proc.returncode != 0:
            raise RuntimeError(f"Worker crashed with exit code {proc.returncode}: {stderr.decode()}")
    except asyncio.TimeoutError as timeout_err:
        logger.error("Worker exceeded timeout of %d seconds. Initiating process tree termination.", timeout_sec)
        try:
            # ৪. উইন্ডোজ চাইল্ড প্রসেস ও প্যারেন্ট গ্রেসফুল টার্মিনেশন
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            proc.terminate()
            
            # ৫ সেকেন্ড গ্রেস পিরিয়ড
            _, still_alive = psutil.wait_procs(parent.children(), timeout=5)
            for p in still_alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if proc.returncode is None:
                proc.kill()
        except Exception as cleanup_err:
            logger.error("Failed to cleanly terminate child processes: %s", cleanup_err)
        # মূল টাইমআউট এক্সেপশন অক্ষুণ্ণ রাখা
        raise TimeoutError(f"Worker task timed out after {timeout_sec}s") from timeout_err
    finally:
        # ৫. পোস্ট-টাস্ক মেমরি রিকভারি ও রিসোর্স রি-মেজারমেন্ট
        # দ্রষ্টব্য: অপশনাল torch টপ-লেভেলে ইমপোর্ট হবে না; এটি সাবপ্রসেসেই সীমাবদ্ধ থাকবে
        verify_memory_headroom()
        
    return proc.returncode
```

---

## ⚠️ ৮. বিগত আর্কিটেকচারাল ভুল ও সমাধান (Anti-Patterns to Avoid)

| নিষিদ্ধ বিষয় | কেন নিষিদ্ধ | অনুমোদিত সঠিক রূপ |
|---|---|---|
| একাধিক পোর্ট বা ফলব্যাক পোর্ট (5173 / 7860) | আর্কিটেকচারে দ্ব্যর্থতা ও CORS/প্রক্সি ব্যর্থতা তৈরি করে | সমগ্র প্রজেক্টে কঠোরভাবে একক পোর্ট `127.0.0.1:8000` |
| ভারী ডিপেন্ডেন্সি কোর `requirements.txt`-এ রাখা | ইন্সটলেশন ক্র্যাশ ও পোর্ট্যাবিলিটি নষ্ট করে | কোর ইনফ্রাস্ট্রাকচার লাইটওয়েট রাখা; ভারী এআই ইঞ্জিন অন-ডিমান্ড অপশনাল রাখা |
| ইভেন্ট লুপে ব্লকিং সাবপ্রসেস চালানো | সার্ভার ফ্রিজ করে এবং ওয়েব রিকোয়েস্ট আটকে দেয় | `asyncio.create_subprocess_exec()` ব্যবহার করা |
| SQLite-এ বড় ফাইল বা BLOB সংরক্ষণ | ডাটাবেজ মেমরি ও ফাইল সাইজ অস্বাভাবিক বাড়িয়ে ফেলে | অডিও, ভিডিও ও মডেল ডিস্কে রিলেটিভ পাথে থাকবে; DB-তে কেবল মেটাডাটা |
| ১০০% মেমরি ক্লিয়ারের নিশ্চয়তা দাবি | পাইথন জিসির পক্ষে ওএস ও ড্রাইভার ভি-র‍্যাম মেমরি সম্পূর্ণ রিলিজ করা সম্ভব নয় | ভারী টাস্ক শেষে ওয়ার্কার সাবপ্রসেস সম্পূর্ণ বন্ধ করে রিসাইক্লিং নিশ্চিত করা |
| শুধু ইউজারের কথায় বিলিং বন্ধ ভাবা | ভুলবশত ক্লাউড কনসোলে ক্রেডিট কার্ড বা বিলিং যুক্ত থাকতে পারে | টেকনিক্যাল কুয়াড-চেক ফেইল-সেফ (Fail-Closed) ভ্যালিডেশন কার্যকর করা |
| জেমিনি কনজিউমার প্রো দিয়ে এপিআই কল | গুগল কনজিউমার সাবস্ক্রিপশন ডেভেলপার এপিআই কোটা দেয় না | গুগল এআই স্টুডিওর অ্যাক্টিভ ফ্রি টিয়ার ব্যবহার করা |
| গিট স্বয়ংক্রিয়ভাবে কমিট বা পুশ করা | ব্যবহারকারীর আনচেকড কোড গিটে উঠে ফাইল জটিলতা তৈরি করতে পারে | সর্বদা ব্যবহারকারীর সুস্পষ্ট অনুমোদনের পর গিট কমান্ড চালানো |
| ফিক্সড 1080p রেজোলিউশন জোরপূর্বক দেওয়া | অরিজিনাল ভিডিও নষ্ট হয় বা অ্যাসপেক্ট রেশিও বিকৃত হয় | অরিজিনাল ভিডিওর রেজোলিউশন ও অ্যাসপেক্ট রেশিও হুবহু অক্ষুণ্ণ রাখা |
| OpenCV-কে ইনস্ট্যান্ট বা নিখুঁত দাবি করা | সিপিইউতে প্রসেসিং সময় মাস্ক ভেদে পরিবর্তিত হয় এবং জটিল ব্যাকগ্রাউন্ডে ব্লার হয় | বাস্তবসম্মত ফলব্যাক হিসেবে বর্ণনা করা |

---

## 🛠️ ৯. এজেন্টের জন্য ধাপে ধাপে কাজের চেকভেক্টর

যেকোনো নতুন ফিচার বা বাগ ফিক্স করার সময় এজেন্টকে নিচের চেকভেক্টরটি অনুসরণ করতে হবে:

1. **ডকুমেন্টেশন রেফারেন্স ভেরিফিকেশন:** কাজ শুরু করার আগে নিশ্চিত হও যে তুমি `prd.md` (v2.1), `architecture.md` (v2.1) এবং `prompt.md`-এর সংশ্লিষ্ট ফেজটি ভালোভাবে পড়েছ।
2. **জিরো এক্সট্রা কস্ট গার্ড:** কোনো কোডে কোনো পেইড লাইব্রেরি, পেইড এন্ডপয়েন্ট বা বিলিং এনাবেলিং ফাংশন নেই তো?
3. **পোর্ট ও সিকিউরিটি গার্ড:** সার্ভার বাইন্ডিং, রিকোয়েস্ট ও কনফিগারেশন `127.0.0.1:8000`-এ লকড এবং Host/Origin ভ্যালিডেশন সঠিক তো?
4. **৫-ধাপের স্টেট মেশিন গার্ড:** ফাইল রাইট করার সময় `.staging` ডিরেক্টরি, সাইডকার `.tmp` ফাইল, `os.fsync()`, উইন্ডোজ ফাইল হ্যান্ডেল ক্লোজ এবং `os.replace()` অনুসরণ করা হয়েছে তো?
5. **কোয়ারেন্টিন ও প্রজেক্ট রুট গার্ড:** করাপ্ট ফাইল কি `.staging/quarantine/`-এ সরানো হয়েছে? কোনো ফাইল কি প্রজেক্ট ফোল্ডারের বাইরে মোছার চেষ্টা হচ্ছে না তো?
6. **টেস্ট ফার্স্ট ভ্যালিডেশন:** কাজ শেষ হলে `pytest` বা সংশ্লিষ্ট টেস্ট স্ক্রিপ্ট রান করে যাচাই করতে হবে।
7. **ব্যবহারকারীকে রিপোর্ট:** কাজ সফলভাবে সম্পন্ন হলে ব্যবহারকারীকে স্পষ্ট ভাষায় কাজের ফলাফল জানাও এবং পরবর্তী পদক্ষেপের জন্য অপেক্ষা করো (স্বয়ংক্রিয় গিট কমিট করবে না)।
