"""
Unit tests for Windows Launcher and Tauri Packaging Prototype (Phase 13).
Validates run_studio.bat, src-tauri configuration, CSP rules, and Decision Gate documentation.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def test_run_studio_bat_launcher():
    """Verify run_studio.bat exists and configures single-port 127.0.0.1:8000 server."""
    bat_path = BASE_DIR / "run_studio.bat"
    assert bat_path.exists(), "run_studio.bat must exist at project root"

    content = bat_path.read_text(encoding="utf-8")
    assert "127.0.0.1:8000" in content, "Must target single port 127.0.0.1:8000"
    assert "uvicorn app.main:app" in content, "Must launch uvicorn backend"
    assert "requirements.txt" in content, "Must check or install dependencies"
    assert "PYTHON_EXE" in content, "Must detect Python executable"


def test_tauri_conf_json_validity():
    """Verify src-tauri/tauri.conf.json is valid and adheres to security constraints."""
    conf_path = BASE_DIR / "src-tauri" / "tauri.conf.json"
    assert conf_path.exists(), "tauri.conf.json must exist"

    with open(conf_path, "r", encoding="utf-8") as f:
        conf = json.load(f)

    assert conf["productName"] in ["Muazu Studio", "AI-VPS Studio"]
    assert conf["version"] == "2.2.0"
    assert conf["build"]["devUrl"] == "http://127.0.0.1:8000"
    assert conf["build"]["frontendDist"] == "../frontend/dist"

    csp = conf["app"]["security"]["csp"]
    assert "127.0.0.1:8000" in csp, "CSP must allow backend single port"
    assert "tauri://localhost" in csp, "CSP must allow tauri origin"


def test_tauri_rust_source_and_cargo():
    """Verify Rust package structure in src-tauri."""
    cargo_path = BASE_DIR / "src-tauri" / "Cargo.toml"
    main_rs_path = BASE_DIR / "src-tauri" / "src" / "main.rs"

    assert cargo_path.exists(), "Cargo.toml must exist"
    assert main_rs_path.exists(), "main.rs must exist"

    cargo_text = cargo_path.read_text(encoding="utf-8")
    assert 'name = "ai-vps-studio"' in cargo_text
    assert "tauri" in cargo_text

    main_text = main_rs_path.read_text(encoding="utf-8")
    assert "check_backend_status" in main_text


def test_tauri_decision_gate_documentation():
    """Verify DECISION_GATE.md documents Option A vs Option B with concrete recommendation."""
    doc_path = BASE_DIR / "src-tauri" / "DECISION_GATE.md"
    assert doc_path.exists(), "DECISION_GATE.md must exist"

    doc_text = doc_path.read_text(encoding="utf-8")
    assert "Option A: Standalone Embedded Python" in doc_text
    assert "Option B: PyInstaller Packaging" in doc_text
    assert "Final Recommendation" in doc_text
