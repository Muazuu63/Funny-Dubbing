# Tauri Packaging Decision Gate: Embedded Python vs PyInstaller

**Document Version:** 1.0  
**Phase:** 13 (Packaging Prototype & Decision Gate)  
**Target Architecture:** AI-VPS Studio v2.2 (Single-User Local Desktop Application)  
**Date:** 2026-11-02  

---

## 1. Executive Summary

AI-VPS Studio utilizes a high-performance, single-port (`127.0.0.1:8000`) architecture combining a lightweight Vite + React + Tailwind frontend with an asynchronous Python FastAPI + SQLite WAL backend. 

To package the studio into a native Windows `.msi` / `.exe` installer using **Tauri v2 (Rust Core + System WebView2)**, a definitive technical decision is required between two distribution strategies for the Python backend:

- **Option A:** Standalone Embedded Python Runtime (`python-3.11.x-embed-amd64`)
- **Option B:** PyInstaller / Nuitka Single-File / Directory Packaging

---

## 2. Comparative Matrix

| Evaluation Criteria | Option A: Standalone Embedded Python | Option B: PyInstaller Packaging |
| :--- | :--- | :--- |
| **Windows Defender / Antivirus** | **Near 0% False Positives.** Uses official signed Python binaries from Python Software Foundation. | **High False Positive Risk.** PyInstaller bootloaders frequently trigger heuristic antivirus warnings. |
| **Heavy AI Wheels (PyTorch, OpenCV)** | **100% Native Compatibility.** Loads C-extensions, CUDA/DirectML DLLs, and Onnx runtime directly from `site-packages`. | **Fragile Hooking.** Requires complex `--hidden-import` and `.spec` manifests; dynamic imports often break. |
| **Cold Startup Latency** | **Instant (200-400ms).** Directly executes `python.exe -m uvicorn app.main:app`. | **High Overhead (2-5 seconds).** Single-file `.exe` must unpack temp archives to `%TEMP%` on every launch. |
| **Subprocess Process Tree Cleanup** | **Clean.** Windows Job Objects can strictly track and kill Python child process trees (`taskkill /F /T`). | **Complex.** PyInstaller child wrappers can create orphan processes upon abrupt parent crash. |
| **Model & Preset Patching** | **Modular & Updatable.** Users can update models in `models/` or presets in `presets/` without re-downloading entire installer. | **Rigid.** Re-packaging requires compiling the entire monolith binary. |
| **Distribution Installer Size** | ~120 MB (Compressed Embedded Python + Core Dependencies). Heavy AI weights downloaded on-demand. | ~180-250 MB (Bundled PyInstaller executable). |

---

## 3. Detailed Architectural Evaluation

### 3.1 Option A: Standalone Embedded Python Runtime (Recommended)

In this approach, the Tauri installer bundles:
1. `src-tauri/` compiled Rust binary (`AI-VPS-Studio.exe` ~8 MB).
2. `runtime/python/` (Official PSF Windows 64-bit embedded package with `python311._pth` configured).
3. `runtime/bin/` (Static `ffmpeg.exe` and `ffprobe.exe`).
4. `app/` and `frontend/dist/` (Application source and compiled frontend).

**Startup Flow:**
```
[User Clicks AI-VPS-Studio.exe]
       │
       ▼
[Tauri Rust Core]
       ├── 1. Verify port 127.0.0.1:8000
       ├── 2. Spawn sidecar: ./runtime/python/python.exe -m uvicorn app.main:app
       ├── 3. Poll /api/v1/health until HTTP 200 OK
       └── 4. Open Tauri WebView2 pointing to http://127.0.0.1:8000
```

**Key Advantages:**
- Completely eliminates Antivirus heuristic blocks on Windows 10/11.
- Allows seamless drop-in of optional AI modules (Demucs, Whisper, Telea OpenCV) without re-linking binaries.
- Dual Durability SQLite (`PRAGMA synchronous=FULL;`) behaves deterministically with native file locks.

### 3.2 Option B: PyInstaller Single-Binary Architecture

In this approach, `pyinstaller --onedir` or `--onefile` compiles the FastAPI backend into `backend.exe`.

**Identified Risks & Drawbacks:**
- Frequent heuristic detections by Windows SmartScreen and 3rd-party antivirus software, requiring code-signing certificates costing $300-$500/year (violating Zero Extra Cost policy).
- Packaging OpenCV and PyTorch requires hundreds of hidden DLL exclusions.
- Temporary unpack directory cleanup issues on Windows crash recovery (Case K reconciliation).

---

## 4. Final Recommendation & Phase 2 Roadmap

**Selected Architecture: Option A (Standalone Embedded Python Runtime)**

### Phase 2 Implementation Roadmap:
1. **CI/CD Pipeline:** Configure GitHub Actions to download `python-3.11.9-embed-amd64.zip`, inject `pip`, install `requirements.txt`, and bundle alongside `src-tauri`.
2. **Sidecar Launcher:** Rust `tauri::command` manages child process PID and attaches to Windows Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
3. **FFmpeg Bundling:** Pre-packaged FFmpeg static binary placed in `resources/bin/`.
