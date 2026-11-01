# 📋 Product Requirements Document (PRD)
## AI Funny Dubbing & Video Production Studio
### Unified AI-Powered Video Production Platform

---

**Document Version:** 1.0
**Date:** 2026-10-31
**Status:** Draft
**Source:** idea.md v2.2

---

## 1. PRODUCT OVERVIEW

### 1.1 Product Name
**AI Funny Dubbing & Video Production Studio**
*(Codename: AI-VPS — AI Video Production Studio)*

### 1.2 Product Summary
একটি Unified AI-powered Desktop/Web Application যেখানে ১১টি আলাদা Production Mode থাকবে। User ভিডিও Upload করবে (বা Concept দেবে) এবং AI সম্পূর্ণ Production Pipeline — Analysis, Script, Voice, Sync, Editing, Export — নিজেই সম্পন্ন করবে।

### 1.3 Primary User & System Scope (Personal Studio — Single User)
- **Primary User:** Software Owner (একক ব্যবহারকারী - আপনি নিজে)।
- **Architecture Model:** সম্পূর্ণ লোকাল পার্সোনাল প্রোডাকশন স্টুডিও (No Public SaaS)।
- **Out of Scope (যা যা থাকবে না):**
  - কোনো পাবলিক ইউজার রেজিস্ট্রেশন বা লগইন সিস্টেম থাকবে না।
  - কোনো সাবস্ক্রিপশন, পেমেন্ট গেটওয়ে বা বিলিং সিস্টেম থাকবে না।
  - কোনো টিম বা মাল্টি-ইউজার রোল ম্যানেজমেন্ট থাকবে না।
  - প্রাইভেট লোকাল ওয়ার্কস্পেস থাকবে এবং সমস্ত ডেটা ব্যবহারকারীর নিজস্ব পিসিতে অফলাইনে সুরক্ষিত থাকবে।

### 1.4 Core Philosophy
> **"User শুধু Video Upload করবে — AI বাকি সব করবে।"**

User-এর একমাত্র বাধ্যতামূলক অ্যাকশন হলো Voice Preview শুনে **Approve** করা।

---

## 2. PRODUCT GOALS

| Goal | Description |
|---|---|
| 🎯 G-01 | User Minimum Input-এ Maximum Output |
| 🎯 G-02 | Fully Automated AI Production Pipeline |
| 🎯 G-03 | Multi-language Video Output (User-controlled) |
| 🎯 G-04 | Copyright-Safe Content Generation |
| 🎯 G-05 | Character-wise Unique Voice System |
| 🎯 G-06 | Extensible Architecture — ভবিষ্যতে নতুন Mode যোগ করা যাবে |
| 🎯 G-07 | No Fake Processing — সব Feature বাস্তব Backend-এর সাথে সংযুক্ত |

---

## 3. PRODUCTION MODES — COMPLETE LIST

| Mode # | Name | Priority | Status |
|---|---|---|---|
| 01 | 🎭 Funny Video Dubbing Studio | P1 | Active Development |
| 02 | 🎨 Cartoon Video Re-Creation Studio | P1 | Active Development |
| 03 | 🤖 AI Autonomous Content Creator | P1 | Active Development |
| 04 | ✨ AI Video Enhancement Studio | P2 | Planned |
| 05 | 🎙️ AI Voice Studio | P2 | Planned |
| 06 | 📄 AI Subtitle & Translation Studio | P2 | Planned |
| 07 | 📱 AI Shorts & Reels Creator | P3 | Planned |
| 08 | ✂️ AI Video Editor Studio | P3 | Planned |
| 09 | 🖼️ AI Thumbnail Creator | P3 | Planned |
| 10 | 🎭 AI Background & Object Studio | P4 | Future |
| 11 | 🎵 AI Music & Sound Studio | P4 | Future |

> **Rule:** যে Mode এখনো Implement হয়নি সেটি "Coming Soon" দেখাবে। Fake Processing বা Fake Output সম্পূর্ণ নিষিদ্ধ।

---

## 4. MAIN DASHBOARD REQUIREMENTS

### 4.1 Dashboard Layout
- প্রতিটি Production Mode আলাদা **Card** হিসেবে দেখাবে
- Card-এ থাকবে: Mode Name, Feature Description, Start New Project, Recent Projects, Processing Status, Output History

### 4.2 Shared Navigation
- Project Management (সব Mode-এর Project একসাথে)
- Global Settings
- Notification Center (Processing Alerts)
- User Profile

### 4.3 Cross-Mode Project Transfer
- এক Mode-এর Output অন্য Mode-এ সরাসরি পাঠানো যাবে
- **Transfer Examples:**
  - Funny Dubbing → Video Enhancement → Shorts Creator → Thumbnail Creator
  - Cartoon Re-Creation → Subtitle Studio → Enhancement → Shorts Creator
  - AI Voice Studio → Funny Dubbing / Cartoon Re-Creation
  - Character Creator → Cartoon Re-Creation Studio

---

## 5. MODE 01 — FUNNY VIDEO DUBBING STUDIO

### 5.1 Overview
Reference Video থেকে Comedy Style ও Voice Style শিখে, Original Working Video-তে Character-wise Funny Dubbing করা। User-নির্বাচিত ভাষায় Final Video Export করা।

### 5.2 Language Selection & Output System (User-controlled)

**Rule:** User Working Video Upload করার সময় Output Language বেছে নেবে। ডিফল্ট ভাষা থাকবে **"Bangla"**। Script ও Content সব ভাষায় Same থাকবে — শুধু ভাষা ও কমিক ডেলিভারি স্বাভাবিকভাবে Adapt হবে।

| User Input Selection | System Output |
|---|---|
| **"Bangla"** (Default) | শুধু ১টি Bangla Video |
| **"hindi"** | শুধু ১টি Hindi Video |
| **"english"** | শুধু ১টি English Video |
| **"Bangla + Hindi"** | ২টি আলাদা Video (Bangla & Hindi) |
| **"Bangla + Hindi + english"** | ৩টি আলাদা Video (Bangla, Hindi, English) |
| অন্য যেকোনো ভাষা | সেই নির্দিষ্ট ভাষায় Video |

**Supported Languages:** Bangla 🇧🇩, Hindi 🇮🇳, English 🇬🇧, Arabic 🇸🇦, ও অন্যান্য

> **Note:** English Default নয় — User বললেই তৈরি হবে। ডিফল্ট সিলেকশন থাকবে Bangla।

### 5.3 Reference Video Training Library

#### 5.3.1 Purpose
User একাধিক Trending Funny Dubbing Video Upload করবে। AI সেগুলো বিশ্লেষণ করে Comedy Style ও Voice Style শিখবে। এই ভিডিওগুলো Working Video হিসেবে ব্যবহার করা যাবে না।

#### 5.3.2 Comedy Style Analysis Requirements

| Analysis Item | AI কী শিখবে |
|---|---|
| Comedy Style | Humour Pattern, Punchline Style |
| Timing | Comedy Timing, Reaction Timing |
| Editing Style | Sound Effects, Background Music Usage |
| Visual Style | Subtitle Style, Synchronization Method |

#### 5.3.3 Voice & Character Voice Analysis Requirements (বিস্তারিত)

| Analysis Item | AI কী শিখবে |
|---|---|
| Voice Pitch & Tone | প্রতিটি Character-এর গলার উচ্চতা, গভীরতা ও রং |
| Voice Emotion | রাগ, কষ্ট, মজা, অবাক — প্রতিটি আবেগ কীভাবে কণ্ঠে আসে |
| Dialogue Delivery Speed | দ্রুত/ধীর/স্বাভাবিক — কোন পরিস্থিতিতে কোন গতি |
| Character-wise Voice Pattern | ভিলেন, কমিক, নায়ক, বয়স্ক — প্রতিটি Type-এর আলাদা কণ্ঠস্বর |
| Punchline Voice Style | Punchline-এর সময় গলার পরিবর্তন কেমন হয় |
| Voice Modulation | কণ্ঠের ওঠানামা ও Expression |
| Comedy Reaction Voice | অবাক হওয়া, হাসি, ভয় — Reaction-এর কণ্ঠস্বর |
| Video Type Voice Diff | Human, Animal, Bird, Cartoon-এর জন্য আলাদা Voice Style |

> **Rule:** Training Video-এর Original Dialogue Copy করা যাবে না। শুধু Style ও Creative Direction নেওয়া হবে।

#### 5.3.4 Video Type Learning

| Video Type | AI কী শিখবে |
|---|---|
| 👤 Human | Lip-Sync Style, Facial Expression Dubbing |
| 🐾 Animal | Body Language, Reaction-based Sync |
| 🐦 Bird | Beak Movement, Head Movement Sync |
| 🎨 Cartoon / Animation | Mouth Movement Animation Style |

#### 5.3.5 Training Profile Output
সব Reference Video বিশ্লেষণের পর AI একটি **Reusable Comedy Style Profile** তৈরি করবে:
- Preferred Comedy Style & Voice
- Dialogue Style & Humour Pattern
- Editing Style & Sound Design Preference
- Visual Synchronization Preference

Profile নতুন Reference Video যোগ করলে Update হবে এবং ভবিষ্যৎ Project-এ Reuse করা যাবে।

### 5.4 Working Video Analysis Requirements

**Input:** Original Working Video (MP4, MOV, MKV)
**Video Upload Support:** Duration Detection, Resolution Detection, Audio Detection, Upload Progress, File Validation

### 5.4.0 Pre-Processing — Clean Media Inpainting & Branding Eraser

> **Rule:** ব্যবহারকারীর নিজের বা অনুমতিপ্রাপ্ত ফুটেজের ক্ষেত্রে অপ্রয়োজনীয় পুরাতন চ্যানেল লোগো, সাবটাইটেল টেক্সট ওভারলে এবং ব্যানার মুছে ফ্রেশ ডাবিং আউটপুট তৈরির জন্য AI Inpainting দিয়ে স্বয়ংক্রিয়ভাবে ক্লিন ফুটেজ তৈরি করা হবে। এটি কোনো কপিরাইট জালিয়াতির জন্য নয়, বরং মিডিয়া ক্লিন-আপ প্রি-প্রসেসর।

| Element Type | Examples | Removal Method |
|---|---|---|
| 🏷️ Logo / Watermark | চ্যানেল ওয়াটারমার্ক, হ্যান্ডেল ট্যাগ | AI Inpainting ফিল |
| 📝 On-screen Text | পুরাতন অন-স্ক্রিন টেক্সট, সাবটাইটেল ওভারলে | Text Mask + Background Fill |
| 📺 Channel Branding | সাবস্ক্রাইব বাটন, প্রমোশনাল গ্রাফিক্স | Object Removal |
| 🔄 Moving Watermark | নড়াচড়া করা গ্রাফিক্স | Optical Flow Tracking + Fill |

**Technical Requirements:**
- Background Inpainting — রিমুভ করা জায়গা লোকাল AI দিয়ে স্বাভাবিকভাবে পূরণ হবে।
- Clean Output — রিমুভ করার পর কোনো কালো দাগ বা ব্লার থাকবে না।
- Local Engine — কোনো ক্লাউড বিল ছাড়া অফলাইনে FFmpeg ও LaMa দিয়ে চলবে।

| Analysis Item | Requirement |
|---|---|
| Video Type | Human / Animal / Bird / Cartoon Detection |
| Character Detection | সব Speaking ও Non-speaking Character শনাক্ত |
| Scene Detection | Timestamp সহ প্রতিটি Scene আলাদা করা |
| Character Action | Body Language, Facial Expression (প্রযোজ্য হলে) |
| Speaking Turn | কোন Character কখন কথা বলছে |
| Funny Moment | Comedy Opportunity Detection |
| Story Context | ভিডিওর সামগ্রিক গল্প বোঝা |

### 5.5 Script Generation Requirements

**Output:** ন্যূনতম ৩টি, সর্বোচ্চ ৫টি Funny Dubbing Script

**প্রতিটি Script-এ থাকবে:**

| Field | Description |
|---|---|
| Script Title | Script-এর নাম |
| Scene Number & Timestamp | কোন দৃশ্যে কখন |
| Character Name & Emotion | কে কীভাবে বলছে |
| Character Dialogue | কী বলছে |
| Voice Delivery Style | Delivery Instruction |
| Comedy Timing & Punchline | কখন Punch আসবে |
| Suggested Sound Effects | কোন SFX দরকার |

**Rule:** Script অবশ্যই Original Video-এর Visual Action ও Story Context-এর সাথে মিলতে হবে।

### 5.6 Automatic Best Script Selection

**Rule:** AI নিজেই Script নির্বাচন করবে। User-এর কাছ থেকে Script Approval নেওয়া হবে না।

**Selection Criteria:**
- Comedy Quality & Originality
- Scene & Character Relevance
- Dialogue Quality & Entertainment Value
- Comedy Timing & Punchline Quality

**Post-Selection Action:** Best Script নির্বাচনের পর স্বয়ংক্রিয়ভাবে Voice Generation শুরু হবে।

### 5.7 Character-wise Voice System

**Rule:** প্রতিটি Speaking Character-এর জন্য আলাদা Voice। একই Character পুরো Video-তে একই Voice Identity বজায় রাখবে।

```
Character 1  →  Voice A  (সারা Video একই)
Character 2  →  Voice B
Character 3  →  Voice C
```

**Voice Personality Options:**
- লিঙ্গ: Male, Female
- বয়স: Young, Old
- Pitch: Deep, High
- Style: Funny, Cartoon, Expressive, Natural

### 5.8 Voice Approval Flow (বাধ্যতামূলক)

**Approval Stage:** ব্যবহারকারীর নির্বাচিত Primary Language (ডিফল্ট: Bangla) Voice তৈরি হওয়ার পর User অবশ্যই প্রিভিউ শুনে Approve করতে হবে।

**Available Controls:**

| Control | Function |
|---|---|
| ▶ Play / Pause | Full Preview |
| 🔊 Full Voice Preview | সম্পূর্ণ শোনা |
| 🎙 Individual Dialogue Preview | আলাদা Dialogue শোনা |
| 👤 Character-wise Preview | নির্দিষ্ট Character-এর Voice |
| 📥 Download Audio | Audio Download |
| 🔄 Regenerate Voice | পুরো Voice আবার তৈরি |
| 🔁 Change Voice | Voice পরিবর্তন |
| ↕ Change Pitch / Speed | Pitch ও Speed Control |
| 😄 Change Emotion | Emotion পরিবর্তন |
| ✏️ Edit Individual Dialogue | নির্দিষ্ট Dialogue সম্পাদনা |

**Rule:**
- User Primary Voice Approve না করা পর্যন্ত Final Video Production শুরু হবে না।
- Reject করলে পরিবর্তনের সুযোগ দেওয়া হবে।
- **Delta Re-Rendering (ক্যাশ অপটিমাইজেশন):** রিজেক্ট বা এডিটের সময় সম্পূর্ণ অডিও পুনরায় রেন্ডার হবে না; **শুধু পরিবর্তিত নির্দিষ্ট ডায়ালগ ও টাইমস্ট্যাম্পের ক্যাশ রি-রেন্ডার** হবে। বাকি অপরিবর্তিত অংশ ক্যাশ থেকে জোড়া লাগবে।
- Script Approval প্রয়োজন নেই — শুধু Voice Approval বাধ্যতামূলক।

### 5.9 Adaptive Visual Synchronization & Multi-Language Timing Adjustment

**Rule:** Video Type অনুযায়ী আলাদা Sync Method ব্যবহার করতে হবে। সব ভিডিওতে একই Lip-Sync Method নয়।

**Audio Stem Separation & Master Audio Preservation:**
- অরিজিনাল অডিও থেকে **AI Stem Separation (যেমন: Demucs v4 / Spleeter)** প্রযুক্তি ব্যবহার করে ভোকাল এবং অ্যাকমপ্যানিমেন্ট/ব্যাকগ্রাউন্ড সাউন্ড আলাদা করা হবে।
- **বাস্তবসম্মত অডিও আর্কিটেকচার:** কোনো এআই সেপারেশন ইঞ্জিন ব্যাকগ্রাউন্ড সাউন্ড নিখুঁত রাখার ১০০% নিশ্চয়তা দিতে পারে না। তাই আপলোড করা মূল ভিডিওর **Original Audio Track সবসময় মাস্টার ব্যাকআপ হিসেবে সংরক্ষিত থাকবে**।
- আউটপুট তৈরির সময় Demucs-এর আলাদা করা ব্যাকগ্রাউন্ড অডিও ট্র্যাকের সাথে প্রয়োজনে অরিজিনাল অডিও ব্যালেন্স ও রিস্টোরেশনের সুযোগ থাকবে।
- ব্যবহারকারীকে অডিও প্রিভিউতে ব্যাকগ্রাউন্ড সাউন্ড ও ভয়েসের ভলিউম লেভেল ম্যানুয়ালি অ্যাডজাস্ট (Manual Audio Mixing) করার কন্ট্রোল দেওয়া হবে।

**Timing & Speech Speed Stretch Rule:**
- ফাইনাল ভিডিওর ভয়েস টাইমিং হুবহু অরিজিনাল ভিডিওর ভয়েস টাইমিংয়ের সাথে মিল থাকতে হবে।
- ভাষাভেদে (বাংলা, হিন্দি, ইংরেজি) শব্দ সংখ্যার তারতম্যের কারণে সময় বেড়ে বা কমে গেলে, দৃশ্য স্লো বা ফাস্ট না করে **ডায়ালগের কথা বলার গতি (Audio Speed Stretch / Pacing Control)** স্বয়ংক্রিয়ভাবে বাড়িয়ে বা কমিয়ে অরিজিনাল টাইম-স্লটের সাথে নিখুঁতভাবে ফিট করা হবে।

| Video Type | Synchronization Method |
|---|---|
| 👤 Human (স্পষ্ট মুখ) | AI Lip-Sync — Dialogue অনুযায়ী মুখের নড়াচড়া |
| 🐾 Animal | Natural Movement, Reaction ও Body Language ভিত্তিক |
| 🐦 Bird | Beak Movement, Head Movement ও Natural Behaviour |
| 🎨 Cartoon | Character Animation Style অনুযায়ী Mouth Sync |
| 🚫 Non-speaking | Action-based / Reaction-based / Off-screen Voiceover |

**Rule:** Lip-Sync সম্ভব না হলে জোর করে প্রয়োগ করা যাবে না।

### 5.10 Final Video Editing Requirements

- Original Dialogue Audio Replace বা Mix করা
- Character-wise Voice বসানো
- Scene অনুযায়ী Dialogue Synchronize
- Funny Sound Effects যোগ
- Background Music যোগ
- Voice ও Music Balance (BGM যেন Voice ঢেকে না দেয়)
- Original Ambient Sound সংরক্ষণ
- Subtitle তৈরি (নির্বাচিত ভাষায়)

### 5.11 Final Output Specification

- **Format:** MP4
- **Resolution:** 1080p (Source সমর্থন করলে)
- **Codec:** H.264
- **Audio:** High Quality
- **Languages:** User-নির্বাচিত প্রতিটি ভাষায় আলাদা File
- **Content Rule:** সব ভাষায় একই Script/Content — শুধু ভাষা পরিবর্তন
- **Extra:** আলাদা Voiceover Audio Download-এর সুবিধা

---

## 6. MODE 02 — CARTOON VIDEO RE-CREATION STUDIO

### 6.1 Overview & Boundary Clarification
- **Mode 02 (Cartoon Re-Creation):** ব্যবহারকারী একটি আসল ভিডিও আপলোড করবেন। AI সেই ভিডিওর **মূল গল্প, দৃশ্য, অ্যাকশন এবং সংলাপের মূল অর্থ (Meaning & Story Context)** অপরিবর্তিত রেখে প্রতিটি চরিত্রকে কার্টুনে রূপান্তর করবে এবং নতুন AI ভয়েস দিয়ে রিক্রিয়েট করবে। (এখানে কোনো নতুন গল্প বানানো হবে না)।
- **Mode 03 (Autonomous Creator)-এর সাথে পার্থক্য:** Mode 03 সম্পূর্ণ স্বাধীনভাবে শূন্য থেকে AI-র নিজের আইডিয়া ও স্ক্রিপ্ট নিয়ে সম্পূর্ণ নতুন কন্টেন্ট তৈরি করে। Mode 02 কখনোই নতুন গল্প বা অপ্রাসঙ্গিক স্ক্রিপ্ট বানাবে না; বরং আপলোড করা ভিডিওর হুবহু কার্টুন রিফ্লেকশন হবে।

### 6.2 Core Concept (গুরুত্বপূর্ণ)

| বিষয় | কী হবে |
|---|---|
| 🏷️ লোগো / পুরাতন টেক্সট | AI লোকাল ইনপেইন্টিং দিয়ে মুছে ফ্রেশ ফ্রেম তৈরি করবে |
| 🎬 ভিজুয়াল | কার্টুন/অ্যানিমেশন ক্যারেক্টার ও সিন (Original Footage রূপান্তর) |
| 🗣️ সংলাপের অর্থ (Meaning) | **আসল সংলাপের হুবহু অর্থ ও অভিব্যক্তি সংরক্ষিত থাকবে** |
| 🎙️ Voice Audio | **User Selection: Real Voice অথবা AI Voice** |
| 🎵 Music & SFX | লাইসেন্সড বা ফ্রি সাউন্ড ও ব্যাকগ্রাউন্ড ইফেক্টস |

### 6.3 Voice Architecture: Real Voice vs AI Voice Selection & Usage Rights

**User Voice Option & Rights Policy:**
কার্টুন রিক্রিয়েশন মোডে ব্যবহারকারীর স্পষ্ট পছন্দ থাকবে:
1. **Option A: Real Voice (অরিজিনাল অডিও):** মূল ভিডিওর নিজস্ব সংলাপ ও কণ্ঠ সরাসরি কার্টুন অ্যানিমেশনের সাথে সিঙ্ক হবে (ব্যবহারকারীর প্রয়োজনীয় অধিকার থাকতে হবে)।
2. **Option B: AI Voice (বিকল্প সিন্থেটিক কণ্ঠ):** মূল অডিওর সংলাপ লোকাল Whisper দিয়ে ট্রান্সক্রিপ্ট করে নতুন AI ভয়েস মডেল দিয়ে রিক্রিয়েট হবে। 
   * *স্পষ্টীকরণ:* AI Voice একটি বিকল্প ভয়েস অপশন; এটি ব্যবহার করলেই পুরো ভিডিও স্বয়ংক্রিয়ভাবে Copyright-Free হয়ে যায় এমন কোনো অযৌক্তিক নিশ্চয়তা সিস্টেম দেবে না।

**Flexible Switching & Delta Re-rendering:**
- ব্যবহারকারী প্রথমে **"Real Voice"** দিয়ে কার্টুন আউটপুট এক্সপোর্ট করলেও, পরবর্তীতে চাইলে পুরো ভিডিও রি-জেনারেট না করে **শুধুমাত্র এক ক্লিকে "AI Voice"-এ রি-রেন্ডার** করতে পারবেন।
- ভিডিও ফ্রেম এবং অডিও ট্র্যাক আলাদা ক্যাশ লেয়ারে সংরক্ষিত থাকবে, ফলে শুধুমাত্র অডিও লেয়ার সোয়াপ করে মুহূর্তের মধ্যে আউটপুট পরিবর্তন সম্ভব হবে।

### 6.4 Re-Creation Workflow

```
1. Original Video Upload
2. 🧹 Auto Copyright Element Removal (Logo, Watermark, Text — Automatic)
3. Speech-to-Text & Transcript Extraction
4. Scene & Action Analysis (Action + Timing Mapping)
5. Cartoon Character Generation (Original Character-এর Cartoon রূপ)
6. Animation Style নির্বাচন
7. Scene-by-Scene Cartoon Frame Generation
8. Voice Re-generation (একই কথা + নতুন AI Voice)
9. Cartoon Lip-Sync & Timing Sync
10. Royalty-Free BGM & Sound Effects
11. ✅ Final Copyright-Safe Cartoon Video Export
```

### 6.5 Animation Style Options

| Style | বিবরণ |
|---|---|
| 🎨 2D Flat | Simple, Clean Cartoon Look |
| 🇯🇵 Anime | Japanese Animation Style |
| 🎬 3D Animation | Realistic 3D Cartoon |
| 📚 Comic Book | Comic Panel Style |
| 🖌️ Watercolor | Soft, Artistic Look |
| 🕹️ Pixel Art | Retro Pixel Style |

### 6.6 Character System Requirements & Visual Consistency
- Original Character-এর Visual থেকে Cartoon Character Design
- **Character Consistency Anchor (Face Embedding & Reference Sheet):**
  - প্রথম ফ্রেম থেকে তৈরি প্রতিটি কার্টুন ক্যারেক্টারের একটি ডেডিকেটেড Character Reference Sheet ও Face Embedding তৈরি করা হবে।
  - পুরো ভিডিওর প্রতিটি দৃশ্য ও ফ্রেমে সেই একই ফেস লক (Identity Anchor) থাকবে, যাতে সিন পরিবর্তনের সাথে সাথে কার্টুনের চেহারা বা আউটফিট বদলে না যায়।
- Character Color Scheme, Expression, Costume নির্ধারণ
- Character-specific Cartoon Mouth Shapes (Lip-Sync এর জন্য)
- Character Library-তে Save করার সুবিধা

### 6.7 Language Support
- User বলে দেবে কোন ভাষায় Cartoon Voice চাই
- Bangla, Hindi, English ও অন্যান্য ভাষা সমর্থিত

---

## 7. MODE 03 — AI AUTONOMOUS CONTENT CREATOR

### 7.1 Overview
User কোনো Video বা Content Upload করবে না। শুধু Topic/Concept বলবে এবং Output Language নির্বাচন করবে। AI নিজে থেকে সম্পূর্ণ Original Content তৈরি করবে।

### 7.2 User Input Requirements (মাত্র ৩টি)
1. **Topic / Concept / Genre** — যেমন: "একটি মজার বিড়ালের গল্প" বা "office comedy"
2. **Output Language** — Bangla / Hindi / English / যেকোনো
3. **Voice Approval** — AI-এর তৈরি Voice শুনে Approve বা Reject

### 7.3 AI Autonomous Workflow

```
1. User Topic Input
2. AI Content Research & Idea Generation
3. AI Script / Story / Dialogue Writing
4. AI Character Design (Visual / Cartoon / Animation)
5. AI Scene-by-Scene Storyboard
6. AI Visual / Animation / Frame Generation
7. AI Character-wise Voice Generation
8. AI Lip-Sync & Visual Synchronization
9. ⏸ Voice Preview → User Approval
10. (On Approve) AI BGM + SFX + Subtitle
11. AI Final Video Render
12. ✅ Final Videos (নির্বাচিত সব ভাষায় আলাদা)
```

### 7.4 Language Selection System

| User Input | Output |
|---|---|
| "শুধু বাংলায়" | শুধু Bangla Video |
| "বাংলা ও হিন্দি" | Bangla + Hindi (২টি আলাদা) |
| "বাংলা, হিন্দি ও ইংরেজি" | ৩টি আলাদা Video |
| "সব ভাষায়" | Bangla + Hindi + English + অন্যান্য |

**Supported Languages:** Bangla 🇧🇩, Hindi 🇮🇳, English 🇬🇧, Arabic 🇸🇦, ও অন্যান্য

### 7.5 Content Types

| Type | বিবরণ |
|---|---|
| 🎭 Funny / Comedy | AI নিজে Comedy Script ও Character তৈরি |
| 📖 Story-based | গল্প-ভিত্তিক ভিডিও |
| 🐾 Animal / Nature Comedy | পশুপাখির Comedy Content |
| 🎨 Animated Short Film | সম্পূর্ণ AI-তৈরি Animation |
| 📚 Educational Funny | মজাদার শিক্ষামূলক Content |
| 🌐 Topic-based Comedy | User-দেওয়া যেকোনো বিষয়ে |

### 7.6 Approval Rules
- Script, Character, Scene — AI নিজেই সিদ্ধান্ত নেবে (Approval লাগবে না)
- **শুধু Voice Approval বাধ্যতামূলক**
- Reject করলে AI নতুন Voice Generate করবে
- Approve করলেই Final Video Production শুরু হবে

---

## 8. MODE 04 — AI VIDEO ENHANCEMENT STUDIO
*(Priority 2 — Planned)*

| Feature | Description |
|---|---|
| Video Upscaling | Resolution বৃদ্ধি |
| Noise Reduction | ভিডিও Noise কমানো |
| Video Sharpening | পরিষ্কার করা |
| Lighting Correction | আলোর সমস্যা সমাধান |
| Color Correction | রঙ ঠিক করা |
| Frame Interpolation | FPS বৃদ্ধি |
| Video Stabilization | কাঁপুনি দূর করা |

---

## 9. MODE 05 — AI VOICE STUDIO
*(Priority 2 — Planned)*

| Feature | Description |
|---|---|
| Text-to-Speech | Bangla, Hindi, English ও অন্যান্য |
| Character-wise Voice | প্রতিটি Character আলাদা Voice |
| Emotion-based Acting | আবেগ অনুযায়ী Voice |
| Authorized Voice Cloning | অনুমতিপ্রাপ্ত Voice Clone |
| Voice Enhancement | Voice মান উন্নয়ন |
| Noise Removal | Voice থেকে Noise দূর |
| Speed & Pitch Control | গতি ও উচ্চতা নিয়ন্ত্রণ |

---

## 10. MODE 06 — AI SUBTITLE & TRANSLATION STUDIO
*(Priority 2 — Planned)*

| Feature | Description |
|---|---|
| Auto Subtitle Generation | Speech-to-Text ভিত্তিক |
| Subtitle Editing | সম্পাদনার সুবিধা |
| Bangla Translation | বাংলা অনুবাদ |
| Hindi Translation | হিন্দি অনুবাদ |
| English Translation | ইংরেজি অনুবাদ |
| Other Language Support | অন্যান্য ভাষা |
| Subtitle Sync | Synchronization |
| SRT / VTT Export | ফরম্যাট Export |

---

## 11. MODE 07 — AI SHORTS & REELS CREATOR
*(Priority 3 — Planned)*

| Feature | Description |
|---|---|
| Long Video Analysis | দীর্ঘ ভিডিও বিশ্লেষণ |
| Viral Moment Detection | গুরুত্বপূর্ণ মুহূর্ত শনাক্ত |
| Auto Short Clip | স্বয়ংক্রিয় Clip তৈরি |
| Vertical Conversion | 9:16 রূপান্তর |
| Auto Captions | স্বয়ংক্রিয় Caption |
| Smart Reframing | বুদ্ধিমান Frame নির্বাচন |
| Multiple Shorts | একসাথে একাধিক Short |

---

## 12. MODE 08 — AI VIDEO EDITOR STUDIO
*(Priority 3 — Planned)*

| Feature | Description |
|---|---|
| Cut / Trim / Split / Merge | Basic Editing |
| Scene Reordering | দৃশ্য পুনর্বিন্যাস |
| Transition Effects | পরিবর্তন Effect |
| Audio Replacement | Audio বদল |
| Background Music | BGM যোগ |
| Sound Effects | SFX যোগ |
| Aspect Ratio Conversion | অনুপাত পরিবর্তন |
| Timeline Editing | Timeline ভিত্তিক সম্পাদনা |

---

## 13. MODE 09 — AI THUMBNAIL CREATOR
*(Priority 3 — Planned)*

| Feature | Description |
|---|---|
| Video Frame Analysis | সেরা Frame বিশ্লেষণ |
| Multiple Thumbnail Concepts | একাধিক Concept |
| Text & Title Placement | লেখা ও Title |
| Background Replacement | পটভূমি পরিবর্তন |
| Enhancement | মান উন্নয়ন |
| YouTube Export | YouTube-উপযোগী Export |

---

## 14. MODE 10 — AI BACKGROUND & OBJECT STUDIO
*(Priority 4 — Future)*

- Background Removal & Replacement
- Object Removal & Replacement
- Scene Background Generation
- Green Screen Processing

---

## 15. MODE 11 — AI MUSIC & SOUND STUDIO
*(Priority 4 — Future)*

- AI Background Music Generation
- Scene-based & Comedy SFX
- Cinematic SFX
- Audio Mixing & Enhancement
- Music & Voice Balance

---

## 16. SHARED SYSTEM REQUIREMENTS

সব Mode একই Shared Infrastructure ব্যবহার করবে:

| System | Description |
|---|---|
| User Dashboard | Central Control Panel |
| Training Center Core | Shared Reference & Profile Hub (Voice, Character, Comedy & Style Presets — No Heavy Fine-tuning) |
| Project Management | সব Mode-এর Project একসাথে |
| Video Upload System | Multi-format Upload |
| File Storage | Local SQLite + Structured File System |
| AI Model Integration Layer | সব AI Model-এর Unified Interface |
| Character Library | তৈরি করা Character সংরক্ষণ |
| Voice Library | Available ও Generated Voice |
| Style Preset Library | Comedy Style, Animation Style |
| Audio Library | SFX + BGM Collection |
| Rendering Engine | Final Video Composition |
| Export Manager | Multi-format, Multi-language Export |
| Processing Queue | Sequential Job Queue & Resource Management (FIFO — একবারে একটি ভারী টাস্ক) |
| Error Handling | Detailed Error Report |
| Notification System | Processing Update Alerts |

> **Rule:** Training Center কোনো আলাদা প্রোডাকশন মোড নয়; এটি ১১টি মোডের জন্য একটি সার্বজনীন প্রোফাইল ও এসেট হাব।
> **Rule:** সাধারণ পার্সোনাল পিসির মেমরি ওভারফ্লো বা ক্র্যাশ রোধ করতে Processing Queue কঠোরভাবে **Sequential (একটির পর একটি)** চলবে। কোনো ভারী AI মডেল সমান্তরালভাবে (Parallel) মেমরিতে লোড করা যাবে না। একটি Mode বা Job-এর কাজ সম্পূর্ণ শেষ হয়ে VRAM/RAM মুক্ত হলে পরবর্তী Job শুরু হবে।

---

## 17. PROJECT MANAGEMENT REQUIREMENTS

### 17.1 Project Data Storage
প্রতিটি Project আলাদাভাবে Save হবে। Project বন্ধ করলেও Data হারাবে না।

**প্রতিটি Project-এ থাকবে:**

| Data | Description |
|---|---|
| Original Working Video | মূল ভিডিও ফাইল |
| Reference Training Profile | Comedy Style Profile |
| Animation Style & Character Design | Cartoon Mode-এর জন্য |
| Video Analysis Data | AI বিশ্লেষণের ফলাফল |
| Scene Information & Timestamps | দৃশ্য তথ্য |
| All Generated Scripts | তৈরি সব Script (3-5টি) |
| AI Selected Best Script | নির্বাচিত Script |
| Voice Files | সব ভাষার Voice |
| Character Voice Mapping | Character ↔ Voice সংযোগ |
| Synchronization Data | Sync তথ্য |
| Subtitle Files | সব ভাষার Subtitle |
| Final Video Files | চূড়ান্ত ভিডিও |

### 17.2 Resume Capability
পরবর্তীতে Project Open করে আগের জায়গা থেকে কাজ চালিয়ে যাওয়া যাবে।

---

## 18. PROCESSING STATUS REQUIREMENTS

### 18.1 Mode 01 — Funny Dubbing Processing Steps

```
 1. Uploading Video
 2. Analyzing Video
 3. Detecting Characters & Scenes
 4. Generating Scripts (3-5টি)
 5. Selecting Best Script (AI Automatic)
 6. Generating Primary Language Voice
 7. ⏸ Waiting for Voice Approval ← User Action Required
 8. Generating Additional Language Voices
 9. Processing Synchronization
10. Editing Final Video
11. Rendering (per language)
12. ✅ Completed — All Language Videos Ready
```

### 18.2 Mode 02 — Cartoon Re-Creation Processing Steps

```
 1. Uploading Original Video
 2. Speech-to-Text Extraction
 3. Scene & Action Analysis
 4. Generating Cartoon Characters
 5. Animation Style Processing
 6. Scene-by-Scene Cartoon Rendering
 7. AI Voice Generation (New Voice)
 8. Cartoon Lip-Sync Processing
 9. Adding BGM & Sound Effects
10. Final Rendering
11. ✅ Completed
```

### 18.3 Mode 03 — Autonomous Creator Processing Steps

```
 1. Processing Topic & Concept
 2. AI Content Research
 3. Script & Story Writing
 4. Character Design
 5. Storyboard Creation
 6. Visual / Animation Generation
 7. Voice Generation
 8. Lip-Sync & Synchronization
 9. ⏸ Voice Approval ← User Action Required
10. BGM + SFX + Subtitle
11. Final Video Render (per language)
12. ✅ Completed
```

### 18.4 Error Handling
- Processing Failed হলে **Detailed Error Message** দেখাবে
- সফল Step থেকে **Resume** করার সুবিধা থাকবে
- Long Processing-এ **Real-time Progress Bar** দেখাবে

---

## 19. GLOBAL SETTINGS

| Setting | Default | Override |
|---|---|---|
| Default Video Resolution | 1080p | Per Mode |
| Default Aspect Ratio | 16:9 | Per Mode |
| Default Export Format | MP4 (H.264) | Per Mode |
| Preferred Language | Bangla | Per Project |
| Audio Quality | High | Per Mode |
| Video Quality | High | Per Mode |
| Default Voice Style | Natural | Per Project |
| Default Animation Style | 2D Flat | Per Project |
| Storage Location | Local / Cloud | Global |

---

## 20. TECHNICAL REQUIREMENTS — 100% FREE & ZERO-COST ARCHITECTURE

> [!IMPORTANT]
> **ব্যবহারকারীর মূল নীতি: সম্পূর্ণ ফ্রি (Zero Budget / No Paid Subscription)।**
> কোনো পেইড API বা ক্রেডিট কার্ড লাগবে না। সিস্টেমের প্রতিটি মডিউল সম্পূর্ণ বিনামূল্যে চলার মতো ওপেন-সোর্স লাইব্রেরি এবং গুগলের ফ্রি ডেভেলপার টায়ার দিয়ে ডিজাইন করা হলো।

### 20.1 100% Free Technology Stack Mapping

| প্রসেসিং ধাপ | ফ্রি সমাধান / প্রযুক্তি | কেন সম্পূর্ণ ফ্রি? |
|---|---|---|
| **১. লোগো ও ওয়াটারমার্ক রিমুভাল** | **FFmpeg + LaMa Inpainting** | সম্পূর্ণ ফ্রি ওপেন-সোর্স লোকাল লাইব্রেরি ($০) |
| **২. অডিও স্টেম সেপারেশন (ভোকাল ও মিউজিক আলাদা)** | **Demucs v4 / Spleeter** | মেটা (Facebook)-এর সম্পূর্ণ ফ্রি ওপেন-সোর্স মডেল ($০) |
| **৩. ভিডিও অ্যানালাইসিস ও কমেডি স্ক্রিপ্ট তৈরি** | **Google AI Studio (Gemini 1.5 Flash Free Tier)** | কোনো ক্রেডিট কার্ড ছাড়া জিমেইল দিয়ে প্রতিদিন প্রচুর ফ্রি কোটা ($০) |
| **৪. স্পিচ-টু-টেক্সট (ট্রান্সক্রিপ্ট)** | **OpenAI Whisper (Local Base/Small Model)** | লোকাল মেশিনে অফলাইনে চলে, কোনো এপিআই বিল নেই ($০) |
| **৫. বাংলা, হিন্দি ও ইংরেজি ভয়েস (TTS)** | **Edge-TTS (Microsoft Neural Voice Engine)** | মাইক্রোসফটের অত্যন্ত ন্যাচারাল বাংলা/হিন্দি ভয়েস ফ্রি পাইথন লাইব্রেরি দিয়ে জেনারেট হয় ($০) |
| **৬. লিপ-সিঙ্ক (Lip-Sync Engine)** | **Wav2Lip / SadTalker** | ফ্রি ওপেন-সোর্স লিপ-সিঙ্ক মডেল ($০) |
| **৭. কার্টুন ফ্রেম ও ক্যারেক্টার রিক্রিয়েশন** | **Stable Diffusion v1.5 / SDXL (ComfyUI / WebUI)** | নিজস্ব পিসিতে অফলাইনে সম্পূর্ণ ফ্রি চলে ($০) |
| **৮. সাবটাইটেল তৈরি ও বার্ন-ইন** | **Whisper Timestamps + FFmpeg** | সম্পূর্ণ ফ্রি ও লোকাল ($০) |
| **৯. ব্যাকগ্রাউন্ড মিউজিক ও সাউন্ড ইফেক্টস** | **FreeSound / YouTube Audio Library Integration** | রয়্যালটি-ফ্রি ফ্রি সাউন্ড লাইব্রেরি ($০) |

### 20.2 জিরো-কস্ট সেটআপ গাইড (Zero-Cost Setup Policy)

1. **গুগল এআই স্টুডিও ফ্রি কি (Google AI Studio Free Key):**
   - ব্যবহারকারী কেবল `aistudio.google.com` থেকে একটি সাধারণ ফ্রি API Key নিয়ে ড্যাশবোর্ডে বসাবেন। এতে কোনো পেমেন্ট মেথড বা ক্রেডিট কার্ড লাগে না।
2. **লোকাল রিসোর্স অপটিমাইজেশন:**
   - হালকা ও অপটিমাইজড মডেল (Lightweight ONNX / Quantized Models) ব্যবহার করা হবে যাতে সাধারণ কনফিগারেশনের কম্পিউটারেও স্মুথভাবে রান করে।
3. **পেইড সার্ভিস সম্পূর্ণরূপে অপশনাল:**
   - ElevenLabs বা Claude-এর মতো পেইড সার্ভিসকে "Optional / Disabled by Default" রাখা হবে। ডিফল্টভাবে সিস্টেম 100% ফ্রি ইঞ্জিনে চলবে।

---

## 21. NON-FUNCTIONAL REQUIREMENTS

| Requirement | Description |
|---|---|
| No Fake Processing | Fake Progress বা Fake Output সম্পূর্ণ নিষিদ্ধ |
| Real Backend Only | প্রতিটি Feature বাস্তব Backend-এর সাথে সংযুক্ত |
| Coming Soon Label | Unimplemented Feature-কে "Coming Soon" দেখাতে হবে |
| Data Persistence | Project বন্ধ করলেও কোনো Data হারাবে না |
| Mode Isolation | এক Mode অন্য Mode-কে Interrupt করবে না |
| Extensible Architecture | ভবিষ্যতে নতুন Mode সহজে যোগ করা যাবে |
| Test First | প্রথমে ছোট Test Video দিয়ে সম্পূর্ণ Workflow Test করতে হবে |

---

## 22. DEVELOPMENT ROADMAP

```
Phase 0: Core Architecture & Shared Systems
        ↓
Phase 1: Mode 01 (Funny Dubbing) + Mode 02 (Cartoon) + Mode 03 (Autonomous)
        ↓
Phase 2: Mode 04 (Enhancement) + Mode 05 (Voice) + Mode 06 (Subtitle)
        ↓
Phase 3: Mode 07 (Shorts) + Mode 08 (Editor) + Mode 09 (Thumbnail)
        ↓
Phase 4: Mode 10 (Background) + Mode 11 (Music)
        ↓
Phase 5: Cross-Mode Integration & Optimization
```

---

## 23. ACCEPTANCE CRITERIA

### Mode 01 (Funny Dubbing)
- [ ] Working Video Upload-এর পর Logo/Watermark/Text স্বয়ংক্রিয়ভাবে Remove হচ্ছে
- [ ] Reference Video Upload ও Training Profile তৈরি হচ্ছে
- [ ] Working Video Analysis সম্পন্ন হচ্ছে
- [ ] ৩-৫টি Funny Script তৈরি হচ্ছে
- [ ] AI স্বয়ংক্রিয়ভাবে Best Script নির্বাচন করছে
- [ ] Character-wise আলাদা Voice তৈরি হচ্ছে
- [ ] User Voice Approve/Reject করতে পারছে
- [ ] User-নির্বাচিত ভাষায় Final Video Export হচ্ছে
- [ ] সব ভাষায় Content Same থাকছে

### Mode 02 (Cartoon Re-Creation)
- [ ] Upload-এর পরপরই Logo/Watermark/On-screen Text Remove হচ্ছে
- [ ] Remove করার পর Video Natural দেখাচ্ছে (কোনো Artifact নেই)
- [ ] Original Video Transcript Extraction হচ্ছে
- [ ] Cartoon Character তৈরি হচ্ছে
- [ ] Scene-by-Scene Cartoon Frame তৈরি হচ্ছে
- [ ] Original Voice বাদ দিয়ে নতুন AI Voice দেওয়া হচ্ছে
- [ ] Cartoon Lip-Sync কাজ করছে
- [ ] Copyright-Safe Output তৈরি হচ্ছে

### Mode 03 (Autonomous Creator)
- [ ] User শুধু Topic দিলে AI সম্পূর্ণ Content তৈরি করছে
- [ ] Voice Approval System কাজ করছে
- [ ] User-নির্বাচিত ভাষায় আলাদা আলাদা Video Export হচ্ছে

---

## 24. SYSTEM ARCHITECTURE & RESOURCE SPECIFICATIONS (অতিরিক্ত গুরুত্বপূর্ণ সেকশনসমূহ)

### 24.1 Personal Hardware Profiles & Requirements
যেহেতু এটি পার্সোনাল ডেক্সটপ স্টুডিও এবং জিরো-বাজেট প্রজেক্ট, তাই হার্ডওয়্যার অনুযায়ী প্রসেসিং স্কেলিং করা হবে:

| কনফিগারেশন স্তর | প্রস্তাবিত স্পেক্স | ব্যাকএন্ড কৌশল |
|---|---|---|
| **মিনিমাম (Low End)** | CPU i5/Ryzen 5, 16GB RAM, No Dedicated GPU | Quantized Lightweight Models (CPU ONNX), Gemini Free API ফর স্ক্রিপ্টিং, Edge-TTS |
| **স্ট্যান্ডার্ড (Mid End)** | 16GB RAM, NVIDIA GPU (4GB-6GB VRAM, যেমন: GTX 1660 / RTX 3050) | Demucs ও Whisper অফলাইনে দ্রুত চলবে, Wav2Lip GPU এক্সিলারেশন পাবে |
| **হাই-এন্ড (High End)** | 32GB RAM, NVIDIA RTX 3060/4060+ (8GB-12GB+ VRAM) | Stable Diffusion কার্টুন রেন্ডারিং লোকালি হাই স্পিডে চলবে |

### 24.2 Free AI Provider Registry & Fallback Policy
কোনো একটি ফ্রি সার্ভিস ডাউন হলে অটোমেটিক ব্যাকআপ কার্যকর হবে:

| প্রসেসিং টাস্ক | Primary Free Engine | Secondary Fallback | ইঞ্জিন শ্রেণি ও ফলব্যাক আচরণ |
|---|---|---|---|
| স্ক্রিপ্ট ও ডায়ালগ | Google AI Studio Active Free Tier (Configurable Model ID) | Local Small LLM (Ollama) / Secondary Free Config | **Free Online API:** কোনো হার্ডকোডেড মডেল আইডি নেই। ফ্রি টিয়ার সক্রিয়তা নিশ্চিত না হয়ে কল করা যাবে না। কোটা শেষ হলে Pause এবং Quota পেলে Checkpoint থেকে Resume |
| ভয়েস জেনারেশন (TTS) | Edge-TTS | Bark / Meta MMS | **Free Online Engine (Edge-TTS):** ইন্টারনেট আবশ্যক, অফলাইন ক্লাসিফিকেশন নয়। **Local Offline Engine (Bark/MMS):** অফলাইন মোডে স্বয়ংক্রিয়ভাবে সক্রিয় হবে |
| স্টেম সেপারেশন | Demucs v4 + Master Audio Preservation | Spleeter (Local Lightweight) | **Local Offline Engine:** লোকাল পিসিতে সম্পূর্ণ অফলাইনে চলবে |
| লিপ-সিঙ্ক | Wav2Lip (Local GPU/CPU) | SadTalker (Local) | **Local Offline Engine:** লোকাল পিসিতে অফলাইনে চলবে |

### 24.3 Resource-Aware Sequential Processing & Checkpoint-Based Recovery
- **Resource-Aware Sequential Execution & Process Recycling:**
  - সাধারণ পিসিতে মেমরি ওভারফ্লো এড়াতে একবারে একটি ভারী AI মডেল লোড হবে।
  - পাইপলাইন রুল: `Demucs রান হবে -> আউটপুট সেভ করে মেমরি ফ্রি করবে -> এরপর Whisper রান হবে -> কাজ শেষে মেমরি ক্লিন করবে -> এরপর TTS/লিপ-সিঙ্ক রান হবে`।
  - **Memory Guard:** শুধুমাত্র `gc.collect()` বা `torch.cuda.empty_cache()` দিয়ে VRAM ফাঁকা হওয়ার শতভাগ গ্যারান্টি নেই। তাই RAM/VRAM সক্রিয়ভাবে পর্যবেক্ষণ করা হবে এবং মেমরি আটকে থাকলে প্রয়োজন অনুযায়ী ব্যাকএন্ড **Worker Process Restart** করে ফ্রেশ মেমরি নিশ্চিত করা হবে। পর্যাপ্ত মেমরি না থাকলে ভারী টাস্ক কিউতে অপেক্ষা করবে।
  - হালকা UI, ডাটাবেজ এবং ফাইল অপস সমান্তরালভাবে (Parallel) চলবে।
- **Checkpoint-Based Recovery Pipeline (Zero Loss & Zero Extra Cost):**
  - প্রতিটি সফল প্রসেসিং স্টেপের পর ক্যাশ ও স্টেট SQLite ডাটাবেজে সংরক্ষিত হবে।
  - কোটা ফুরিয়ে গেলে বা ইন্টারনেট ড্রপ করলে টাস্ক `PAUSED (Quota Exhausted / Network Error)` অবস্থায় যাবে।
  - `retry-after` রেসপন্স হেডার থাকলে সেই নির্দিষ্ট সময় পর্যবেক্ষণ করা হবে।
  - ব্যবহারকারী নতুন কনফিগারেশন দিলে বা কোটা সচল হলে আগের সফল কাজ বাদ দিয়ে শুধুমাত্র অসমাপ্ত ধাপ থেকে পুনরায় **Resume** করবে।
  - কোনো অবস্থাতেই পেইড এপিআই বা অটো-বিলিং চালু হবে না।

### 24.4 Feature Feasibility Matrix (বাস্তবধর্মী সক্ষমতা বিশ্লেষণ)

| ফিচার | ফ্রিতে সক্ষমতার স্তর | টেকনিক্যাল বাস্তবতা ও কৌশল |
|---|---|---|
| **Funny Dubbing (Mode 01)** | 🟢 ১০০% বাস্তবসম্মত ও ফ্রি | Gemini Free + Edge-TTS + Demucs দিয়ে পিসিতে সম্পূর্ণ স্মুথলি চলবে। |
| **Delta Voice Re-rendering** | 🟢 ১০০% বাস্তবসম্মত | ক্যাশ সিস্টেমে শুধু নির্দিষ্ট টাইমস্ট্যাম্পের ডায়ালগ রেন্ডার হবে। |
| **Clean Media Branding Eraser** | 🟢 ১০০% বাস্তবসম্মত | FFmpeg ও ইনপেইন্টিং মাস্ক দিয়ে টেক্সট/লোগো অফলাইনে মুছে ফেলা যাবে। |
| **Multi-speaker Voice Identity** | 🟡 হাই-মিডিয়াম বাস্তবসম্মত | Whisper + Diarization দিয়ে স্পিকার আলাদা করে আলাদা কণ্ঠে ডাবিং। |
| **Cartoon Re-Creation (Mode 02)** | 🟡 মিডিয়াম বাস্তবসম্মত (GPU নির্ভর) | ফ্রেম-বাই-ফ্রেম অ্যানিমেশনে প্রচুর জিপিউ লাগে; তাই Key-frame Image + Lip-sync দিয়ে অপটিমাইজ করা হবে। |
| **Autonomous Creator (Mode 03)** | 🟡 মিডিয়াম বাস্তবসম্মত | সম্পূর্ণ গল্প ও ভয়েস ফ্রিতে হবে; তবে রিয়েল ভিডিও জেনারেশনের জন্য হাই স্পেক্স বা ফ্রি স্টক ফুটেজ স্টিচিং সহায়ক হবে। |

---

*PRD Version: 2.0 | Updated: 2026-10-31 | Finalized for Personal Studio, 100% Free Stack, Resource Management & Realistic Feasibility*
