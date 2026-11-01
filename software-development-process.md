# 🛠️ Software Development Process & Technical Execution Plan
### Project: AI Funny Dubbing & Video Production Studio (AI-VPS)
**Document Version:** 1.0  
**Target Environment:** Local Windows PC (`http://localhost:7860` / `8000`)  
**Core Framework:** Python 3.10+ (FastAPI Backend) + HTML5/Tailwind/Vanilla JS Desktop UI + SQLite (Zero-Dependency)

---

## ১. আর্কিটেকচার ডায়াগ্রাম ও ওয়ার্কফ্লো (System Flow)

```mermaid
flowchart TD
    User([User in Browser]) <-->|Localhost:7860| WebUI[Web Dashboard UI]
    WebUI <-->|REST API / WebSockets| APIServer[FastAPI Server Engine]
    
    subgraph Data & Persistence [Zero-Dependency Local Storage]
        DB[(studio.db - SQLite)]
        ProjectsCache[projects/[id]/ cache storage]
    end
    
    subgraph Core Execution Engine
        Queue[Strict Sequential Job Queue - FIFO]
        ProviderMgr[Smart AI Provider Manager]
        Checkpointer[Step-wise Checkpoint & Auto-Resume]
    end
    
    subgraph Local AI Engines [Priority 1 - Free & Offline]
        Demucs[Demucs v4 - Audio Stem Splitter]
        Whisper[OpenAI Whisper - Local STT]
        EdgeTTS[Edge-TTS - Free Neural Voice Engine]
        Inpainter[LaMa / OpenCV Inpainter]
        LipSync[Wav2Lip Engine]
    end
    
    subgraph External Cloud AI [Priority 2 - Free API]
        Gemini[Google Free Tier - Configurable Model & Dynamic Quota Observer]
    end

    APIServer <--> Queue
    Queue --> Checkpointer
    Queue --> ProviderMgr
    ProviderMgr --> Demucs
    ProviderMgr --> Whisper
    ProviderMgr --> EdgeTTS
    ProviderMgr --> LipSync
    ProviderMgr --> Inpainter
    ProviderMgr --> Gemini
    
    Checkpointer <--> DB
    Queue <--> ProjectsCache
```

---

## ২. মডুলার প্রজেক্ট স্ট্রাকচার (Target Project Tree)

সফটওয়্যারটির আর্কিটেকচার সম্পূর্ণ মডুলার ও ক্লিন হবে যাতে ভবিষ্যতে যেকোনো সময় `.exe` বানাতে কোনো বাধা না আসে:

```text
funny-videos/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI এন্ট্রি পয়েন্ট ও লোকালহোস্ট সার্ভার
│   ├── config.py                   # পোর্ট, পাথ ও সেটিংস কনফিগারেশন
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py              # SQLite কানেকশন ও সেশন ম্যানেজার
│   │   └── models.py               # প্রজেক্ট, স্ক্রিপ্ট, কিউ ও সেটিংস টেবিল স্কিমা
│   ├── core/
│   │   ├── queue_manager.py        # Strict Sequential FIFO Job Queue
│   │   ├── checkpointer.py         # Step Checkpoint, Pause & Auto-Resume
│   │   └── resource_monitor.py     # VRAM/RAM মনিটর ও মেমরি সেভার
│   ├── providers/
│   │   ├── base.py                 # বেস এআই প্রোভাইডার ক্লাস
│   │   ├── manager.py              # Smart Provider Manager (Free-First Router)
│   │   ├── gemini_provider.py      # Google Free API / OAuth হ্যান্ডলার
│   │   └── local_tts_provider.py   # Edge-TTS ইন্টিগ্রেশন (বাংলা, হিন্দি, ইংলিশ)
│   ├── engines/
│   │   ├── audio_separator.py      # Demucs v4 লোকাল স্টেম সেপারেশন
│   │   ├── transcriber.py          # Whisper অফলাইন স্পিচ-টু-টেক্সট
│   │   ├── inpainter.py            # লোগো/ওয়াটারমার্ক ক্লিন করার ইঞ্জিন
│   │   ├── timing_sync.py          # Audio Speed Stretch & Alignment ইঞ্জিন
│   │   └── compositor.py           # FFmpeg দিয়ে ফাইনাল ভিডিও রেন্ডারিং
│   ├── modes/
│   │   ├── mode01_dubbing.py       # Mode 01: Funny Video Dubbing পাইপলাইন
│   │   ├── mode02_cartoon.py       # Mode 02: Cartoon Re-creation পাইপলাইন
│   │   └── mode03_autonomous.py    # Mode 03: Autonomous Creator পাইপলাইন
│   └── ui/
│       ├── static/                 # CSS/JS ও আইকন এসেটস
│       └── templates/              # রেসপনসিভ ব্রাউজার ড্যাশবোর্ড
├── storage/
│   ├── studio.db                   # SQLite ডাটাবেজ
│   ├── projects/                   # প্রজেক্ট অনুযায়ী অরিজিনাল ও ক্যাশ ফাইল
│   └── training_profiles/          # কমেডি রেফারেন্স প্রোফাইল
├── run.bat                         # ডাবল-ক্লিকে চালানোর স্ক্রিপ্ট
├── requirements.txt                # পাইথন প্যাকেজ তালিকা
└── README.md
```

---

## ৩. ফেজ-বাই-ফেজ ডেভেলপমেন্ট প্রসেস (Development Phases)

### 🚀 ফেজ ০: ফাউন্ডেশন ও কোর আর্কিটেকচার (Foundation Layer)
1. **ভার্চুয়াল এনভায়রনমেন্ট ও ডিপেন্ডেন্সি সেটআপ:** FastAPI, Uvicorn, SQLite, Aiofiles ইত্যাদি সেটআপ।
2. **লোকালহোস্ট অটো-লঞ্চার:** `main.py` রান করলে ফ্রি পোর্ট (7860/8000) চেক করে স্বয়ংক্রিয়ভাবে ব্রাউজারে ড্যাশবোর্ড ওপেন করবে।
3. **SQLite ডাটাবেজ স্কিমা ডিজাইন:** 
   * `projects` টেবিল (আইডি, মোড, ইনপুট ভিডিও পাথ, নির্বাচিত ভাষা, স্টেটাস)।
   * `checkpoints` টেবিল (প্রতিটি স্টেপের ক্যাশ পাথ ও কমপ্লিশন স্টেট)।
   * `settings` টেবিল (API Keys, থ্রেশহোল্ড, প্রেফারেন্স)।

---

### 🚀 ফেজ ১: সেন্ট্রাল এআই প্রোভাইডার ও সিকিউরিটি লেয়ার (Smart Provider Manager)
1. **API Key & Google Account Settings:** 
   * সেটিংস পেজে ফ্রি Gemini API Key পেস্ট ও ভ্যালিডেশন সিস্টেম।
   * **Configurable Model ID:** কোনো হার্ডকোডেড মডেল আইডি নয়; সেটিংস থেকে অ্যাক্টিভ ফ্রি মডেল (যেমন: Gemini 2.0 Flash) বেছে নেওয়া যাবে।
2. **Dynamic Quota Observer & Free-First Router:** 
   * স্ক্রিপ্ট ও বিশ্লেষণের জন্য ফ্রি জেমিনিকে কল করা।
   * নির্দিষ্ট RPM নয়; রেসপন্স হেডার ও ৪২৯ স্ট্যাটাস ট্র্যাকিং।
   * ফ্রি কোটা ওভার হলে কাজ সাথে সাথে মেমরি সেভ করে টাস্ককে `PAUSED (Quota Exceeded)` স্টেটে পাঠানো এবং চেকপয়েন্ট সেভ রাখা।
3. **Zero-Cost Guardrail:** কোনো অবস্থাতেই পেইড এপিআই বা আন-অথরাইজড ক্রেডিট ট্রানজ্যাকশন ব্লক রাখা।

---

### 🚀 ফেজ ২: টাস্ক কিউ ও অটো-রিজিউম চেকার (Sequential Queue & Engine)
1. **Strict FIFO Queue:** 
   * ব্যাকগ্রাউন্ডে একটি সিঙ্গেল ওয়ার্কার থ্রেড চলবে।
   * প্রসেসিং পাইপলাইন: একটি ভারী কাজ শেষে `gc.collect()` এবং `torch.cuda.empty_cache()` দিয়ে মেমরি ক্লিয়ার করে পরবর্তী কাজ ধরবে।
2. **Auto-Resume Logic:**
   * যদি `Hindi Voice` জেনারেট হওয়ার সময় প্রসেস বন্ধ হয়, পুনরায় চালু করলে সিস্টেম ডেটাবেজ চেক করে সরাসরি সেই পয়েন্ট থেকেই অডিও জেনারেট করবে।

---

### 🚀 ফেজ ৩: Mode 01 (Funny Video Dubbing Studio) ইমপ্লিমেন্টেশন
1. **Video Inpainting:** লোগো বা পুরানো টেক্সট মুছে ক্লিন মাস্টার ভিডিও তৈরি।
2. **Demucs Stem Separation & Master Audio Preservation:** ভোকাল রিমুভ করে ব্যাকগ্রাউন্ড অ্যাকমপ্যানিমেন্ট অডিও সেভ করা। একই সাথে মূল ভিডিওর আসল অডিও মাস্টার কপি হিসেবে সংরক্ষণ করা এবং ম্যানুয়াল ব্যালেন্সিং অপশন রাখা।
3. **Video Context Analysis & Multi-Script Generation:** কনফিগার করা জেমিনি ফ্রি মডেল দিয়ে ৩-৫টি স্ক্রিপ্ট তৈরি ও অটোমেটিক সেরা স্ক্রিপ্ট নির্বাচন।
4. **Edge-TTS Character Voice Casting:** বিভিন্ন চরিত্রের জন্য আলাদা পিচ/টোনসহ নিউরাল ভয়েস তৈরি।
5. **Interactive Voice Approval UI:** 
   * ব্রাউজারে অডিও প্লেয়ার; ইউজার বাংলায় ডায়ালগ শুনবেন, ডায়ালগ এডিট করতে পারবেন এবং "Approve" বাটনে ক্লিক করবেন।
6. **Audio Speed Stretch & Sync:** অরিজিনাল ভিডিওর টাইমিং অনুযায়ী অডিওর কথা বলার গতি নিখুঁতভাবে স্ট্রেচ/কম্প্রেস করা।
7. **FFmpeg Final Render:** নির্বাচিত ভাষাগুলোর জন্য আলাদা আলাদা হাই-কোয়ালিটি MP4 এক্সপোর্ট।

---

### 🚀 ফেজ ৪: Mode 02 (Cartoon Re-Creation Studio) ইমপ্লিমেন্টেশন
1. **Whisper STT:** মূল ভিডিওর সংলাপ অরিজিনাল টাইমিং সহ এক্সট্রাক্ট করা।
2. **Meaning-preserving Script Adapter:** আসল সংলাপের অর্থ বজায় রেখে কার্টুন স্ক্রিপ্ট অ্যাডাপ্টেশন।
3. **Visual Cartoonizer Pipeline:** কার্টুন ফ্রেম প্রসেসিং।
4. **ভয়েস অপশন হ্যান্ডলার (User Choice):**
   * **Real Voice:** অরিজিনাল অডিওকে কার্টুন ফ্রেমে জুড়ে দেওয়া।
   * **AI Voice:** সম্পূর্ণ নতুন AI ভয়েস দিয়ে রিক্রিয়েট করা।
5. **Delta Re-rendering (One-Click Voice Swap):** রেন্ডার করা ভিডিও ফ্রেমে এক ক্লিকে অডিও ট্র্যাক বদলানোর সিস্টেম।

---

### 🚀 ফেজ ৫: টেস্টিং, ভ্যালিডেশন ও হ্যান্ডঅফ
1. লোকালহোস্টে বাস্তব ভিডিও আপলোড করে অ্যান্ড-টু-অ্যান্ড টেস্ট।
2. কোটা লিমিট টেস্ট (পজ ও রিজিউম ঠিকমতো হচ্ছে কিনা)।
3. মেমরি সেফটি টেস্ট (টাস্ক চলাকালীন পিসি হ্যাং করে কিনা)।
4. উইন্ডোজ ডাবল-ক্লিক `run.bat` ফাইল ভ্যালিডেশন।
