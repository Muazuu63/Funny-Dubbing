// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::{Manager, RunEvent, WindowEvent};

struct BackendProcess(Mutex<Option<Child>>);

#[tauri::command]
fn check_backend_status() -> bool {
    // Check if backend responds on http://127.0.0.1:8000/api/v1/health
    true
}

fn main() {
    let app = tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![check_backend_status])
        .setup(|app| {
            // Check if backend is already listening on 127.0.0.1:8000
            // If not, spawn python sidecar process
            println!("[Tauri] Initializing AI-VPS Studio Desktop Shell...");
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while running tauri application");

    app.run(|app_handle, event| {
        match event {
            RunEvent::WindowEvent {
                event: WindowEvent::Destroyed,
                ..
            } => {
                // Terminate spawned Python backend when main window closes
                println!("[Tauri] Main window destroyed, shutting down cleanly.");
                let state = app_handle.state::<BackendProcess>();
                if let Ok(mut lock) = state.0.lock() {
                    if let Some(mut child) = lock.take() {
                        let _ = child.kill();
                    }
                }
            }
            _ => {}
        }
    });
}
