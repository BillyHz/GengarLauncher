# Migrating HexLauncher to Tauri

## Why Tauri?

Tauri produces a much smaller, faster, and more modern binary than PyInstaller:

| Metric | PyInstaller (current) | Tauri |
|---|---|---|
| Binary size | ~25-30 MB | ~3-5 MB |
| Startup time | ~1-2 s | <0.5 s |
| UI framework | CustomTkinter | HTML/CSS/JS |
| Native plugins | Limited | Extensive |
| Installer | None | MSI / DEB / DMG |
| Auto-update | Manual | Built-in |
| RAM usage | ~80 MB | ~30 MB |

## Prerequisites

1. **Rust toolchain** — https://rustup.rs
2. **Node.js + npm** — https://nodejs.org
3. **WebView2** — Pre-installed on Windows 10/11

## What migrates

### Backend (Rust)
- Launch Minecraft via `std::process::Command`
- Download files via `reqwest`
- File system access via `std::fs`
- Mod loading (Fabric / Forge / NeoForge)
- JDK download & extraction
- Progress reporting via Tauri events

### Frontend (HTML / CSS / JS)
- Launcher UI (header, version selector, mods panel)
- Cyberpunk cyan theme
- Animated transitions
- Drag-and-drop mod support
- Optional: Modrinth / CurseForge mod browser

### Bridge (Tauri commands)
- `launch_game(version, username, loader)`
- `fetch_versions()`
- `install_mod(loader, version, mod_id)`
- `open_mods_folder(loader, version)`
- `download_jdk(progress_event)`

## Timeline

| Phase | Time |
|---|---|
| Rust + Tauri scaffold | 1 h |
| Backend port (Python → Rust) | 4-6 h |
| Frontend UI (HTML/CSS/JS) | 3-4 h |
| Testing & polish | 2-3 h |
| **Total** | **10-14 h** |

## When to migrate

✅ **Migrate when:**
- You want a professional-grade installer
- You want a smaller, faster binary
- You want features like auto-update, mod store, etc.
- You're ready to learn Rust basics

🟡 **Stay with PyInstaller when:**
- You want quick iteration
- You're not ready to learn Rust
- 30 MB binary is acceptable
- The current UI is sufficient

## How to migrate

If you decide to migrate, I can:
1. Set up the Tauri scaffold
2. Port the backend logic
3. Build the frontend UI
4. Package and test

This is a multi-day project that we'd do in separate sessions.

## Recommended path

For now, I'll set up PyInstaller so you can ship a `.exe` immediately. We can decide on Tauri after you've tested the `.exe` and have a feel for what needs to improve.
