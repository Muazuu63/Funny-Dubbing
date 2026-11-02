# 📋 Product Requirements Document (PRD)
## AI Funny Dubbing & Video Production Studio
### Unified AI-Powered Video Production Platform
**Document Version:** 2.2  
**Date:** 2026-11-01  
**Status:** Approved & Architecture-Aligned  
**Project Codename:** AI-VPS (AI Video Production Studio)  

---

## 📚 Supporting Technical Documents & Hierarchy

এই PRD-টি সিস্টেমের মূল টেকনিক্যাল আর্কিটেকচার স্পেসিফিকেশনের সাথে সম্পূর্ণ সামঞ্জস্যপূর্ণ। কোনো কনফ্লিক্ট দেখা দিলে নিচের নির্ধারিত ডকুমেন্ট হায়ারার্কি ও প্রায়োরিটি অনুযায়ী সিদ্ধান্ত গৃহীত হবে:

```
+-----------------------------------------------------------------------------------------+
|                               DOCUMENT HIERARCHY & PRIORITY                             |
|   1. idea.md (v2.0)               — Product Vision, Core Concept & User Requirements    |
|   2. prd.md (v2.2)                — Functional Requirements, Scope & Acceptance Criteria|
|   3. architecture.md (v2.2)       — Technical Architecture, Security & Cost Policy      |
|   4. agent.md (v2.4)              — Agent Operational Rules & Engineering Directives    |
|   5. prompt.md (Backend-First)    — Step-by-Step Implementation Execution Prompts       |
+-----------------------------------------------------------------------------------------+
```

> [!IMPORTANT]
> **অথরিটি বাউন্ডারি রুল:** PRD-এর কোনো ফাংশনাল রিকোয়ারমেন্ট `architecture.md`-এর Permanent Zero Extra Cost Hard-Lock, সিকিউরিটি পলিসি বা অনুমোদিত টেকনিক্যাল বাউন্ডারি ওভাররাইড করতে পারবে না।

---

## 1. PRODUCT OVERVIEW & AUTOMATION BOUNDARY

### 1.1 Product Name & Codename
- **Product Name:** AI Funny Dubbing & Video Production Studio
- **Project Codename:** AI-VPS

### 1.2 Product Summary
একটি ইউনিফাইড পার্সোনাল ডেস্কটপ/ওয়েব এআই ভিডিও প্রোডাকশন স্টুডিও যেখানে ১১টি আলাদা প্রোডাকশন মোড থাকবে। ব্যবহারকারী প্রাথমিক ইনপুট ও কনফিগারেশন দেবে এবং সিস্টেমের রিসোর্স-অ্যাওয়ার এআই পাইপলাইন স্বয়ংক্রিয়ভাবে ভিডিও প্রসেসিং, স্ক্রিপ্ট, ভয়েস, টাইমিং সিঙ্ক ও কম্পোজিটিং সম্পন্ন করবে।

### 1.3 Personal Local Studio Scope (No SaaS / Single User)
- **Primary User:** Software Owner (একক ব্যক্তিগত ব্যবহারকারী — কোনো পাবলিক মাল্টি-ইউজার বা টিম নয়)।
- **Architecture Model:** সম্পূর্ণ লোকাল পার্সোনাল প্রোডাকশন স্টুডিও (No Public SaaS)।
- **Out of Scope (অননুমোদিত বিষয়সমূহ):**
  - কোনো পাবলিক ইউজার রেজিস্ট্রেশন, লগইন বা মাল্টি-টেন্যান্ট অথেনটিকেশন থাকবে না।
  - কোনো পেমেন্ট গেটওয়ে, সাবস্ক্রিপশন প্ল্যান বা অটো-বিলিং সিস্টেম থাকবে না।
  - ক্লাউড স্টোরেজ বাধ্যতামূলক নয়; সমস্ত অরিজিনাল মিডিয়া, ক্যাশ ও আউটপুট ডিস্কে লোকাল ডিরেক্টরিতে সংরক্ষিত থাকবে।
  - কোনো পেইড ক্লাউড এপিআই বা পেইড ক্লাউড GPU থাকবে না।

### 1.4 Automation Philosophy & User Interaction Boundary
> **"ব্যবহারকারী প্রাথমিক ইনপুট ও কনফিগারেশন দেবে — এআই বাকি সম্পূর্ণ প্রোডাকশন পাইপলাইন স্বয়ংক্রিয়ভাবে পরিচালনা করবে।"**

স্বয়ংক্রিয়তার অর্থ ব্যবহারকারীর প্রয়োজনীয় সিদ্ধান্ত বাদ দেওয়া নয়। সিস্টেমে নিচের ইউজার ইন্টারঅ্যাকশনগুলো সংরক্ষিত থাকবে:
1. **Source Media Selection:** মূল ভিডিও ও রেফারেন্স ফাইল নির্বাচন।
2. **Production Mode Selection:** ১১টি মোডের মধ্যে সুনির্দিষ্ট মোড নির্বাচন।
3. **Project Configuration:** অ্যাসপেক্ট রেশিও, কোয়ালিটি ও সেটিংস নির্ধারণ।
4. **Language Selection:** ৫টি অনুমোদিত অপশনের মধ্যে ভাষা নির্বাচন।
5. **Online Data Transfer Consent:** ইন্টারনেটে টেক্সট বা ফ্রেম প্রেরণের পূর্বে সুস্পষ্ট সম্মতি প্রদান।
6. **Voice Preview & Approval:** প্রতিটি নির্বাচিত ভাষার জন্য ফাইনাল রেন্ডারের পূর্বে ভয়েস প্রিভিউ শোনা ও অ্যাপ্রুভ করা।
7. **Dialogue Editing & Regeneration:** সংলাপ সম্পাদন বা ভয়েস পুনরায় তৈরি করা।
8. **Final Output Review:** রেন্ডার হওয়া আউটপুট ফাইল যাচাই।
9. **Manual Confirmation:** ইনপেইন্টিং কোয়ালিটি বা টাইমিং ওভারফ্লো সতর্কবার্তায় ম্যানুয়াল অনুমোদন।

*রুল:* ভয়েস অ্যাপ্রুভাল হলো পাইপলাইনের একটি বাধ্যতামূলক ওয়ার্কফ্লো গেটওয়ে, যা অন্যান্য প্রয়োজনীয় ইউজার ইন্টারঅ্যাকশনের বিকল্প নয়।

---

## 2. ZERO EXTRA COST PERMANENT HARD-LOCK POLICY

### 2.1 নিষিদ্ধ পেইড সার্ভিসসমূহ
- ❌ পেইড ক্লাউড এপিআই কল সম্পূর্ণ নিষিদ্ধ।
- ❌ পেইড ক্লাউড GPU বা ক্লাউড প্রসেসিং নিষিদ্ধ।
- ❌ পেইড মডেল ইনফারেন্স বা ক্রেডিট-ভিত্তিক সার্ভিস নিষিদ্ধ।
- ❌ কোনো প্রকার অটো-বিলিং সক্রিয় করা সম্পূর্ণ নিষিদ্ধ।
- ❌ পেইড ফলব্যাক প্রোভাইডারে স্বয়ংক্রিয় সুইচ করা নিষিদ্ধ।
- ❌ কনজিউমার জেমিনি প্রো বা ক্লড প্রো সাবস্ক্রিপশনকে ডেভেলপার এপিআই এনটাইটেলমেন্ট হিসেবে গণ্য করা নিষিদ্ধ।
- ❌ ব্রাউজার কুকি, সেশন স্ক্র্যাপিং বা টোকেন হাইজ্যাকিং সম্পূর্ণ নিষিদ্ধ।

### 2.2 ক্লাউড এপিআই ভ্যালিডেশন ও ৩-স্ট্যাটাস ফেইল-সেফ
গুগল এআই স্টুডিও ফ্রি টিয়ার ব্যবহারের পূর্বে ৪টি স্বাধীন বিষয় যাচাই করতে হবে:
1. **Model Availability:** এপিআই দিয়ে মডেলের প্রাপ্যতা।
2. **Free-tier Eligibility:** অফিশিয়াল ম্যাপিং অনুযায়ী ফ্রি টিয়ার অন্তর্ভুক্ত কি না।
3. **Billing Configuration:** কোনো ক্রেডিট কার্ড বা পেইড বিলিং যুক্ত আছে কি না।
4. **Remaining Quota:** বর্তমান আরপিএম/আরপিডি কোটা অবশিষ্ট আছে কি না।

**সিস্টেম স্ট্যাটাস ট্রায়াঙ্গেল:**
- `VERIFIED_FREE`: সব ভ্যালিডেশন সফল হলে কেবল ক্লাউড রিকোয়েস্ট অনুমোদিত হবে।
- `MANUAL_CONFIRMATION`: ব্যবহারকারীর সম্মতি ডাটাবেজে `api_key_fingerprint` সহ সংরক্ষিত থাকবে; এটি কখনোই এপিআই ভ্যালিডেশন নয় এবং কোনো ক্লাউড কল অনুমোদন করতে পারবে না।
- `UNAVAILABLE`: যেকোনো তথ্য UNKNOWN বা UNVERIFIED হলে ক্লাউড কল সরাসরি ব্লক (Fail-Closed) থাকবে।

*রুল:* গুগল এপিআই ফ্রি টিয়ার সবসময় সচল বা গ্যারান্টিড—এমন কোনো দাবি PRD-তে থাকবে না। ক্লাউড এপিআই ব্লক থাকলে লোকাল এলএলএম বা রুল-বেসড লোকাল স্ক্রিপ্ট ইঞ্জিনে গ্রেসফুল ফলব্যাক করবে।

---

## 3. PRODUCTION MODES & RELEASE GATING

প্রজেক্টের ১১টি প্রোডাকশন মোড এবং তাদের রিলিজ ফেজ অপরিবর্তিত থাকবে:

| Mode # | মোডের নাম | রিলিজ ফেজ | বর্তমান স্ট্যাটাস | প্রাথমিক টেকনিক্যাল ইঞ্জিন |
|---|---|---|---|---|
| **Mode 01** | 🎭 Funny Video Dubbing Studio | **P1 (Core)** | Active Development | OpenCV / LaMa, Whisper, Gemini Free / Local Script, Edge-TTS / Bark, Wav2Lip, Demucs v4 |
| **Mode 02** | 🎨 Cartoon Video Re-Creation Studio | **P1 (Core)** | Active Development | OpenCV / LaMa, Whisper, Delta Re-renderer, Gemini Free / Local Script, Edge-TTS |
| **Mode 03** | 🤖 AI Autonomous Content Creator | **P1 (Core)** | Active Development | Gemini Free / Local LLM, Edge-TTS, FFmpeg Ken-Burns (ভিজ্যুয়াল ইঞ্জিন না থাকলে UNAVAILABLE) |
| **Mode 04** | ✨ AI Video Enhancement Studio | **P2 (Planned)** | Planned | Real-ESRGAN, GFPGAN (GPU ও লাইসেন্স ভেরিফিকেশন সাপেক্ষে) |
| **Mode 05** | 🎙️ AI Voice Studio | **P2 (Planned)** | Planned | XTTS-v2, Bark (জিরো-কস্ট ও কমার্শিয়াল লাইসেন্স সাপেক্ষে) |
| **Mode 06** | 📄 AI Subtitle & Translation Studio | **P2 (Planned)** | Planned | Whisper, MarianMT, FFmpeg Drawtext |
| **Mode 07** | 📱 AI Shorts & Reels Creator | **P3 (Planned)** | Planned | OpenCV Dynamic Cropping, Whisper Timestamps |
| **Mode 08** | ✂️ AI Video Editor Studio | **P3 (Planned)** | Planned | FFmpeg Filtergraph, Silero-VAD |
| **Mode 09** | 🖼️ AI Thumbnail Creator | **P3 (Planned)** | Planned | OpenCV Best-Frame Extractor, PIL Compositor |
| **Mode 10** | 🎭 AI Background & Object Studio | **P4 (Future)** | Future | Segment Anything (SAM), OpenCV Inpaint |
| **Mode 11** | 🎵 AI Music & Sound Studio | **P4 (Future)** | Future | MusicGen, AudioCraft (ভারী হার্ডওয়্যার গেট সাপেক্ষে) |

### 3.1 Feature-Level Engine Availability Gate
- P1 অ্যাক্টিভ ডেভেলপমেন্টের প্রতিটি ফিচারের জন্য বাস্তব **Engine Availability Gate** থাকবে।
- প্রয়োজনীয় এআই ইঞ্জিন সিস্টেমে উপস্থিত না থাকলে UI-তে পরিষ্কারভাবে `UNAVAILABLE` প্রদর্শিত হবে।
- কোনো ভুয়া প্রসেসিং, ডামি প্রগ্রেস বার বা কৃত্রিম আউটপুট দেখানো সম্পূর্ণ নিষিদ্ধ।
- **Training Center Core:** এটি একটি শেয়ার্ড ইনফ্রাস্ট্রাকচার (Layer 4); কোনো ১২ নম্বর প্রোডাকশন মোড নয়।

---

## 4. STANDARDIZED FIVE-LANGUAGE OUTPUT MATRIX

সমগ্র অ্যাপ্লিকেশনে ভাষা নির্বাচন ও রেন্ডারিংয়ের নিয়ম কঠোরভাবে একীভূত:

| ব্যবহারকারীর ইনপুট নির্বাচন | সিস্টেম আউটপুট ফাইল |
|---|---|
| **"Bangla" (ডিফল্ট)** | শুধুমাত্র ১টি Bangla Video |
| **"Hindi"** | শুধুমাত্র ১টি Hindi Video |
| **"English"** | শুধুমাত্র ১টি English Video |
| **"Bangla + Hindi"** | ২টি আলাদা Video (১টি বাংলা এবং ১টি হিন্দি) |
| **"Bangla + Hindi + English"** | ৩টি আলাদা Video (বাংলা, হিন্দি এবং ইংরেজি) |

> [!WARNING]
> অনুমোদিত আর্কিটেকচার অনুযায়ী ঠিক এই **৫টি সুনির্দিষ্ট অপশন** থাকবে। কোনো অতিরিক্ত বা আরবি/স্প্যানিশ জাতীয় ভাষা সিস্টেমে থাকবে না। শুধুমাত্র ব্যবহারকারীর নির্বাচিত ভাষার ফাইলই রেন্ডার হবে।

---

## 5. UNIVERSAL VOICE APPROVAL POLICY

সমস্ত P1 মোডে (Mode 01, Mode 02, Mode 03) ফাইনাল রেন্ডারিংয়ের পূর্বে ভয়েস প্রিভিউ ও অনুমতি গ্রহণ (Approval) বাধ্যতামূলক:
1. **Mode 01 (Funny Dubbing):** 
   - **ভয়েস উপস্থিতি অনুযায়ী দ্বৈত স্ক্রিপ্ট শাখা (Dual Script Branching):** আপলোড করা ভিডিওতে যদি মূল কথা/সংলাপ থাকে তবে তা বিশ্লেষণ করে সংলাপে সংলাপে হাসির **বাংলা ভাবানুবাদ (Translated Bengali Dialogue)** তৈরি হবে; আর যদি ভিডিওতে কোনো কথা না থাকে (সাইলেন্ট, পেট/এনিম্যাল স্ল্যাপস্টিক, ব্যাকগ্রাউন্ড মিউজিক), তবে সম্পূর্ণ টাইমলাইনের জন্য দৃশ্যভিত্তিক আকর্ষণীয় **মৌলিক কমেডি ধারাভাষ্য (Creative Scene Commentary)** স্ক্রিপ্ট তৈরি হবে।
   - **বাধ্যতামূলক প্লেব্যাক প্রিভিউ ও অনুমোদন গেটওয়ে:** মাইক্রোসফট এজ-টিটিএস নিউরাল অডিও এবং ব্রাউজার স্পিচ এপিআই দিয়ে রিয়েল সাউন্ড প্লেব্যাক সহ স্ক্রিপ্ট এডিটরে ব্যবহারকারীর সামনে পেশ করতে হবে। ব্যবহারকারী সংলাপ দেখতে পারবেন, ১-ক্লিকে অনুবাদ বনাম কমেন্ট্রি সোয়াপ করতে পারবেন, এবং স্পষ্ট অনুমোদন (`APPROVE`) দেওয়ার পরই ফাইনাল ভিডিও রেন্ডারিং ও এক্সপোর্ট সম্পন্ন হবে।
2. **Mode 02 (Cartoon Re-Creation):** Real Voice অথবা AI Voice — উভয় অপশনের ক্ষেত্রেই ফাইনাল এক্সপোর্টের আগে প্রিভিউ ও ইউজার অ্যাপ্রুভাল বাধ্যতামূলক।
3. **Mode 03 (Autonomous Creator):** নির্বাচিত ভাষার এআই ভয়েস প্রিভিউ শুনে ব্যবহারকারী অনুমোদন দেওয়ার পরই ভিডিও অ্যাসেম্বলি ও রেন্ডারিং শুরু হবে।
4. **Approval Workflow:** ব্যবহারকারী চাইলে `Approve`, `Edit Dialogue`, বা `Regenerate Voice` করতে পারবেন। অনুমোদন স্ট্যাটাস টাস্ক স্টেটের সাথে ডাটাবেজে সংরক্ষিত থাকবে (`WAITING_FOR_VOICE_APPROVAL` $\rightarrow$ `APPROVED`)।

---

## 6. MODE 01 — RIGHTS-AWARE CLEANUP & DUBBING PIPELINE

### 6.1 Rights-Aware Cleanup (Watermark, Logo & Overlay Removal)
- ব্যবহারকারীর নিজস্ব বা ব্যবহারের অধিকারপ্রাপ্ত ফুটেজের ক্ষেত্রে অপ্রয়োজনীয় ওয়াটারমার্ক বা টেক্সট ওভারলে ক্লিন করার ব্যবস্থা থাকবে।
- **ইঞ্জিন স্পেসিফিকেশন:**
  - **OpenCV Basic Inpainting (Telea / Navier-Stokes):** ডিফল্ট সিপিইউ ফলব্যাক।
  - **Optional LaMa Engine:** জিপিইউতে ন্যূনতম ৪ জিবি VRAM ও লাইসেন্স গেট পাস করলেই কেবল রানটাইমে সক্রিয় হবে।
- **বাস্তব সীমাবদ্ধতা:**
  - মূল ভিডিও কখনোই ওভাররাইট করা যাবে না; ক্লিনড ফুটেজ আলাদা ইন্টারমিডিয়েট ফাইল হিসেবে তৈরি হবে।
  - দ্রুত চলমান বস্তু, বড় ব্যানার বা জটিল ব্যাকগ্রাউন্ডের ওয়াটারমার্ক নিখুঁতভাবে মোছার কোনো অলীক গ্যারান্টি নেই।
  - কোয়ালিটি সন্তোষজনক না হলে সিস্টেমে `LowConfidenceInpaintingWarning` প্রদর্শিত হবে এবং ম্যানুয়াল রিভিউয়ের সুযোগ থাকবে।

### 6.2 Script Generation & Dual-Mode Dubbing Engine
- **Voice Presence Detection:** ভিডিও ফাইল ও অডিও স্ট্রিম অ্যানালাইসিস করে ভয়েসের উপস্থিতি শনাক্ত করা হবে।
  - **Speech Present (মূল কণ্ঠস্বর উপস্থিত):** মূল ডায়ালগগুলোকে স্বাভাবিক, চটপটে ও হাসির বাংলা ভাবানুবাদে (Humorous Translation) রূপান্তরিত করা হবে, যা চরিত্রের মুখ ও টাইমিংয়ের সাথে মিলে যাবে।
  - **Speech Absent (কোনো কথা নেই / সাইলেন্ট / এনিম্যাল ক্লিপ):** ভিডিওর সম্পূর্ণ সময়কালের ওপর ভিত্তি করে দৃশ্যভিত্তিক মৌলিক কমেডি ধারাভাষ্য (Scene Commentary) রচিত হবে।
- **Dual Script Availability:** ব্যাকএন্ড একইসাথে `translation_script_text` এবং `commentary_script_text` জেনারেট করে রাখবে, যাতে ব্যবহারকারী ইচ্ছানুযায়ী যেকোনো মোড বেছে নিয়ে ভয়েস তৈরি করতে পারেন।
- **Zero Cost AI Execution:** জেমিনি সম্পূর্ণ `VERIFIED_FREE` থাকলে এআই স্ক্রিপ্ট তৈরি হবে; অন্যথায় লোকাল এলএলএম বা লোকাল স্ক্রিপ্ট ইঞ্জিনে গ্রেসফল ফলব্যাক করবে।
- লিপ-সিঙ্ক ইঞ্জিন (Wav2Lip) উপলব্ধ না থাকলে ফিচারটি `UNAVAILABLE` থাকবে এবং অডিও ডাবিং ওভারলে সহ এক্সপোর্ট হবে।

---

## 7. MODE 02 — CARTOON RE-CREATION & RIGHTS PRESERVATION

### 7.1 Story & Meaning Preservation
- মূল ভিডিওর দৃশ্য, সিকোয়েন্স, ক্যারেক্টার রোল, অ্যাকশন এবং **সংলাপের মূল ভাবার্থ (Meaning-preserving contextual adaptation)** হুবহু সংরক্ষিত থাকবে। কোনো নতুন কাল্পনিক গল্প বা অপ্রাসঙ্গিক দৃশ্য তৈরি হবে না।

### 7.2 Voice Options & Rights Policy
1. **Option A: Real Voice (অরিজিনাল অডিও):** মূল সংলাপ ও কণ্ঠ সরাসরি কার্টুন অ্যানিমেশনের সাথে সিঙ্ক হবে (ব্যবহারকারীর অবশ্যই বৈধ অধিকার থাকতে হবে)।
2. **Option B: AI Voice (সিন্থেটিক ভয়েস):** অরিজিনাল অডিও ট্রান্সক্রিপ্ট করে নতুন এআই ভয়েস দিয়ে রিক্রিয়েট হবে।
   - *অধিকার সতর্কতা:* AI Voice ব্যবহার করলেই পুরো ভিডিও স্বয়ংক্রিয়ভাবে কপিরাইট-মুক্ত হয়ে যায় না; এটি শুধু একটি বিকল্প সিন্থেটিক অডিও ট্র্যাক।

### 7.3 ১-ক্লিক ডেল্টা অডিও সোয়াপ (Delta Re-renderer)
- ভিডিও ফ্রেম ও অডিও ট্র্যাক আলাদা ক্যাশে সংরক্ষিত থাকবে। ব্যবহারকারী চাইলে সম্পূর্ণ ভিডিও পুনরায় রেন্ডার না করে ১-ক্লিকে Real Voice থেকে AI Voice-এ মুহূর্তের মধ্যে অডিও সোয়াপ করতে পারবেন।

---

## 8. MODE 03 — AI AUTONOMOUS CONTENT CREATOR

### 8.1 Engine Availability Gating
Mode 03-এর প্রতিটি প্রক্রিয়াকরণ ধাপ স্বাধীন ইঞ্জিন অ্যাভেইলেবিলিটি গেট দিয়ে পরিচালিত হবে:
- **Script Generation:** Gemini Free Tier / Local LLM / Local Script Engine।
- **Voice Generation:** Edge-TTS / Bark।
- **Visual Generation:** যদি লোকাল টেক্সট-টু-ভিডিও বা স্টেবল ডিফিউশন ইঞ্জিন অনুপলব্ধ থাকে, তবে ভিজ্যুয়াল জেনারেশন `UNAVAILABLE` প্রদর্শিত হবে।
- *সতর্কতা:* স্লাইডশো বা Ken Burns ইফেক্টকে কখনোই "Full AI 3D Animation" হিসেবে প্রচার করা যাবে না। ইঞ্জিন না থাকলে ব্যবহারকারীকে প্রসেসিং সীমাবদ্ধতা স্পষ্টভাবে জানাতে হবে।

---

## 9. MEDIA COMPOSITOR & 4-TRACK AUDIO MIXER SPECIFICATION

### 9.1 ৪টি স্বতন্ত্র অডিও ট্র্যাক
```
Track 1: [ Original Audio Backup ]  -> ডিফল্টভাবে MUTED (মাস্টার ব্যাকআপ হিসেবে অপরিবর্তিত)
Track 2: [ Demucs Vocal Stem     ]  -> আলাদা করা আসল ভোকাল (গান/হাসির শব্দ থাকতে পারে)
Track 3: [ Demucs Accompaniment  ]  -> আলাদা করা ব্যাকগ্রাউন্ড মিউজিক ও অ্যাম্বিয়েন্স
Track 4: [ New AI Voice Track    ]  -> নতুন জেনারেটেড সিন্থেটিক ভয়েস ট্র্যাক
```

### 9.2 ট্র্যাক ও মাস্টার কন্ট্রোল স্পেসিফিকেশন
- **প্রতি ট্র্যাকে:**
  - Volume Slider: `0% to 150%` (ডিফল্ট: `100%` বা `1.0`)
  - Mute: Boolean (Track 1 ডিফল্ট `true`, অন্যান্য `false`)
  - Solo: Boolean (ডিফল্ট `false`)
  - Pan Slider: `-1.0 to +1.0` (ডিফল্ট: `0.0`)
- **মাস্টার সেফটি কন্ট্রোল:**
  - Master Volume Slider: `0% to 150%` (ডিফল্ট: `100%` বা `1.0`)
  - Master Level Telemetry: `-60.0 to +6.0 dBFS` রিয়েল-টাইম মিটার ডাটা
  - Peak Clipping Detection: `0.0 dBFS` থ্রেশহোল্ডে ক্লিপিং শনাক্তকরণ এবং ফ্রন্টএন্ডে ভিজ্যুয়াল অ্যালার্ট
  - Hard Limiter: `-0.5 dBFS` সিলিং সহ ডিফল্টভাবে সক্রিয় থাকবে
  - Loudness Normalizer: EBU R128 স্ট্যান্ডার্ড অনুযায়ী `-16.0 LUFS` টার্গেটে নরমালাইজেশন
- *বাস্তব সীমাবদ্ধতা:* লিমিটার ও নরমালাইজার ক্লিপিং ঝুঁকি কমায়, তবে এটি অডিও ডিসটর্শন সম্পূর্ণ দূর করার অলীক গ্যারান্টি দেয় না। Demucs ভোকাল স্টেম নিখুঁত ডায়ালগ আইসোলেটর নয়; এতে হাসি বা গানের আওয়াজ থেকে যেতে পারে বিধায় এই ৪-ট্র্যাক মিক্সার প্রয়োজনীয় ম্যানুয়াল ব্যালেন্সিং নিশ্চিত করে।

### 9.3 অডিও টাইমিং ও স্পিড পেসিং
- অডিও পেসিং মাল্টিপ্লায়ার: `0.85x` (ধীর), `1.00x` (স্বাভাবিক), `1.25x` (দ্রুত) এবং সাইলেন্স প্যাডিং ব্যবহার হবে।
- মূল ভিডিওর ফ্রেম সংখ্যা এবং মোট দৈর্ঘ্য কোনোভাবেই পরিবর্তন করা যাবে না।
- কোনো অর্থপূর্ণ ডায়ালগ স্বয়ংক্রিয়ভাবে মুছে ফেলা বা ট্রিম করা সম্পূর্ণ নিষিদ্ধ। ডায়ালগ রেঞ্জে না ধরলে `AudioTimingOverflowWarning` দেবে এবং ট্রিম করতে ব্যবহারকারীর স্পষ্ট সম্মতি লাগবে।

---

## 10. SOURCE RESOLUTION & EXPORT POLICY

> [!IMPORTANT]
> **Universal 1080p গ্যারান্টি পরিহার:** আর্কিটেকচারে উল্লেখিত 1080p কোনো বাধ্যতামূলক ইউনিভার্সাল রেজোলিউশন নয়।

- **রেজোলিউশন ও অ্যাসপেক্ট রেশিও রুল:**
  - সোর্স ভিডিওর মূল অ্যাসপেক্ট রেশিও হুবহু বজায় থাকবে।
  - সোর্স ভিডিওর মূল রেজোলিউশন হুবহু বজায় থাকবে, যদি না ব্যবহারকারী আলাদা রেজোলিউশন বেছে নেন।
  - লো-রেজোলিউশন সোর্সকে নিজে থেকে 1080p কোয়ালিটি বলে দাবি করা যাবে না।
  - আপস্কেলিং ইঞ্জিন অনুপলব্ধ থাকলে নেটিভ রেজোলিউশনেই এক্সপোর্ট হবে।
- **এক্সপোর্ট ফরম্যাট:** H.264 কোডেক সহ MP4 কন্টেইনার। ফাইনাল এক্সপোর্টের আগে FFprobe ভ্যালিডেশন বাধ্যতামূলক।

---

## 11. RESOURCE-AWARE SEQUENTIAL QUEUE & RELIABILITY

### 11.1 Sequential FIFO Execution Policy
- মেমরি ক্র্যাশ রোধে ভারী এআই মডেলগুলো কঠোরভাবে **Sequential FIFO Queue** দিয়ে চলবে।
- হালকা কাজগুলো (UI নেভিগেশন, ডাটাবেজ কুয়েরি, লোকাল ফাইল রিড/রাইট) সমান্তরালভাবে (Parallel) সচল থাকবে।
- একাধিক ভারী এআই মডেল কখনোই মেমরিতে একসাথে লোড হবে না।

### 11.2 Queue Reliability Features
- **Duplicate Task Prevention:** Task Parameters ও Project ID হ্যাশ দিয়ে আইডেমপোটেন্সি কি নিশ্চিত করা।
- **Task Cancellation:** রানিং প্রসেসে গ্রেসফুল টার্মিনেশন পাঠিয়ে টাস্ক বাতিল করার সুবিধা।
- **Timeout Monitoring:** ডিফল্ট ৬০০ সেকেন্ড পার হলে গ্রেসফুল টার্মিনেশন ও চাইল্ড প্রসেস কিল।
- **Retry Limits:** রিকভারেবল এররে সর্বোচ্চ ২ বার রিট্রাই; OOM (Out-of-Memory) এররে ০ রিট্রাই (সরাসরি টার্মিনেশন)।
- **Stale Task Recovery:** অ্যাপ স্টার্টআপে রানিং থাকা কিন্তু বাস্তবে প্রসেস না থাকা ডেড টাস্ক শনাক্তকরণ।
- **Quota Pause & Local Fallback:** HTTP 429 রেসপন্স এলে টাস্ক স্টেট `PAUSED` হবে এবং নিরাপদ লোকাল ফলব্যাক প্রস্তাব করা হবে।

---

## 12. MODEL COMMERCIAL LICENSE REGISTRY (27-FIELD SCHEMA)

বাণিজ্যিক প্রজেক্টে মেধা স্বত্ব সুরক্ষার জন্য প্রতিটি এআই মডেল ও এসেটের জন্য নিচের ২৭টি মেটাডাটা ফিল্ড সংরক্ষিত থাকবে:

| ক্র. | Field Name | Data Type | Required | Description & Validation Rule |
|---|---|---|---|---|
| 1 | `model_id` | String | Yes | মডেলের ইউনিক আইডেন্টিফায়ার (UUID/স্লাগ) |
| 2 | `name` | String | Yes | মডেলের ডিসপ্লে নাম (যেমন: Whisper-Small) |
| 3 | `task_type` | String | Yes | কাজের ধরন (separation, stt, tts, inpaint, lipsync) |
| 4 | `engine_type` | String | Yes | `local_offline`, `cloud_free`, `cloud_hybrid` |
| 5 | `version` | String | Yes | মডেল রিলিজ ভার্সন |
| 6 | `weights_source` | String | Yes | ওয়েটস ডাউনলোডের উৎস (HuggingFace, Local) |
| 7 | `code_license` | String | Yes | সোর্স কোডের লাইসেন্স (MIT, Apache-2.0, BSD) |
| 8 | `weights_license` | String | Yes | মডেল ওয়েটসের লাইসেন্স (OpenRAIL, CC-BY-NC) |
| 9 | `dataset_license` | String | Yes | ট্রেনিং ডাটাবেজের লাইসেন্স |
| 10 | `voice_asset_license` | String | Yes | সংশ্লিষ্ট ভয়েস এসেটের লাইসেন্স |
| 11 | `exact_license_version` | String | Yes | লাইসেন্সের সুনির্দিষ্ট সংস্করণ (যেমন: 2.0, 3.0) |
| 12 | `official_license_url` | String | Yes | অফিসিয়াল লাইসেন্স টেক্সটের ইউআরএল |
| 13 | `official_download_url` | String | Yes | অফিসিয়াল ডাউনলোড সোর্স লিংক |
| 14 | `commercial_use_status` | Enum | Yes | `ALLOWED`, `FORBIDDEN`, `UNCERTAIN` |
| 15 | `attribution_required` | Boolean | Yes | ক্রেডিটস দেওয়া বাধ্যতামূলক কি না |
| 16 | `attribution_text` | String | Optional | প্রয়োজনীয় অফিসিয়াল অ্যাট্রিবিউশন টেক্সট |
| 17 | `verification_evidence` | String | Yes | অডিট ও ভ্যালিডেশন এভিডেন্স নোট |
| 18 | `checksum_sha256` | String | Yes | মডেল ওয়েটস ফাইলের SHA-256 চেকসাম |
| 19 | `local_path` | String | Yes | লোকাল ডিস্কে মডেলের রিলেটিভ ফাইল পাথ |
| 20 | `min_ram_gb` | Float | Yes | ন্যূনতম প্রয়োজনীয় র‍্যাম (জিবি) |
| 21 | `min_vram_gb` | Float | Yes | ন্যূনতম প্রয়োজনীয় জিপিইউ মেমরি (জিবি) |
| 22 | `recommended_device` | String | Yes | `cuda` অথবা `cpu` |
| 23 | `cpu_support` | Boolean | Yes | সিপিইউতে এক্সিকিউশন সমর্থিত কি না |
| 24 | `offline_capable` | Boolean | Yes | ইন্টারনেট ছাড়া অফলাইনে চলে কি না |
| 25 | `internet_requirement` | Boolean | Yes | সক্রিয় ইন্টারনেট আবশ্যক কি না |
| 26 | `verification_status` | Enum | Yes | `VERIFIED`, `UNVERIFIED`, `MANUAL_CONFIRMED` |
| 27 | `last_verified_date` | Date/ISO | Yes | সর্বশেষ লাইসেন্স অডিটের তারিখ |

*বাণিজ্যিক রুল:* `commercial_use_status` যদি `FORBIDDEN` বা `UNCERTAIN` হয়, তবে বাণিজ্যিক প্রজেক্টে মডেলটি কঠোরভাবে ব্লক থাকবে।

---

## 13. DEPENDENCY ISOLATION & TAURI PHASE 2

### 13.1 ডিপেন্ডেন্সি বিভাজন
- **Core Dependencies:** FastAPI, Uvicorn, Pydantic, aiosqlite, psutil, keyring, requests, python-multipart, websockets, opencv-python-headless। (OpenCV বেসিক ফ্রেম এক্সট্রাকশন ও ইনপেইন্টিং ফলব্যাকের জন্য কোর ডিপেন্ডেন্সিতে অন্তর্ভুক্ত)।
- **Optional Heavy Dependencies:** PyTorch, Demucs, Whisper, Wav2Lip, Bark, Meta MMS, LaMa, Real-ESRGAN। কোনো অপশনাল ইঞ্জিন অনুপস্থিত থাকলে অ্যাপ্লিকেশন ক্র্যাশ করবে না; সংশ্লিষ্ট ফিচার নিরাপদভাবে `UNAVAILABLE` থাকবে।

### 13.2 Tauri Packaging Decision Gate (Phase 2)
- তৌরি প্যাকেজিং Phase 1-এর জন্য বাধ্যতামূলক নয়।
- Release Phase P2 শুরু হওয়ার পূর্বে একটি সুনির্দিষ্ট স্ট্র্যাটেজি নির্বাচন করার জন্য প্রোটোটাইপ ডিসিশন গেট থাকবে:
  - **Option A:** Standalone Embedded Python runtime
  - **Option B:** PyInstaller-based backend packaging
- ডিসিশন ক্রাইটেরিয়া: প্রসেস-ট্রি ক্লিনআপ, ফিক্সড পোর্ট ৮০০০ ম্যানেজমেন্ট, হেলথ চেক এবং উইন্ডোজ অ্যান্টিভাইরাস কম্প্যাটিবিলিটি।

---

## 14. REALISTIC ACCEPTANCE CRITERIA

PRD-তে অবাস্তব নিশ্চয়তার পরিবর্তে পরীক্ষণযোগ্য শর্তাবলী নির্ধারণ করা হলো:

### Mode 01 (Funny Dubbing)
- [ ] মূল ভিডিও আপলোডের পর ফাইল সাইজ, সোর্স রেজোলিউশন ও ডিউরেশন অক্ষুণ্ণ থাকছে।
- [ ] অনুমতিপ্রাপ্ত ফুটেজের লোগো/টেক্সট মুছতে OpenCV ফলব্যাক কাজ করছে; LaMa সক্রিয় থাকলে ৪ জিবি VRAM গেট পাস করছে।
- [ ] জেমিনি `VERIFIED_FREE` থাকলে স্ক্রিপ্ট তৈরি হচ্ছে; অন্যথায় লোকাল স্ক্রিপ্ট ইঞ্জিনে গ্রেসফুল ফলব্যাক হচ্ছে।
- [ ] নির্বাচিত প্রতিটি ভাষার জন্য পৃথক ভয়েস প্রিভিউ শোনা যাচ্ছে এবং ব্যবহারকারীর অনুমোদন ছাড়া ফাইনাল রেন্ডার হচ্ছে না।
- [ ] নির্বাচিত সুনির্দিষ্ট ভাষায় (১টি, ২টি বা ৩টি) আলাদা H.264 MP4 ভিডিও ফাইল এক্সপোর্ট হচ্ছে।

### Mode 02 (Cartoon Re-Creation)
- [ ] অরিজিনাল ভিডিওর দৃশ্য, সিকোয়েন্স ও সংলাপের মূল ভাবার্থ বজায় রেখে রূপান্তর হচ্ছে।
- [ ] Real Voice এবং AI Voice — উভয় ক্ষেত্রেই ফাইনাল রেন্ডারের আগে প্লেব্যাক প্রিভিউ ও ইউজার অ্যাপ্রুভাল কাজ করছে।
- [ ] কার্টুন ফ্রেম ও অডিও আলাদা ক্যাশে থাকছে এবং ১-ক্লিকে Real Voice থেকে AI Voice-এ ডেল্টা অডিও সোয়াপ হচ্ছে।

### Mode 03 (AI Autonomous Content Creator)
- [ ] টপিক ইনপুটের পর এআই স্ক্রিপ্ট ও ভয়েস তৈরি করছে।
- [ ] লোকাল ভিজ্যুয়াল ইঞ্জিন না থাকলে সিস্টেম ক্র্যাশ না করে পরিষ্কারভাবে 'UNAVAILABLE' দেখাচ্ছে।
- [ ] রেন্ডারের পূর্বে ভয়েস প্রিভিউ ও অ্যাপ্রুভাল বাধ্যতামূলকভাবে কাজ করছে।

---

*PRD Version: 2.2 | Approved & Architecture-Aligned with architecture.md v2.2, agent.md v2.4 & prompt.md*
