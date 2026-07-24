# Building HexLauncher.exe

## Prerequisites

- Python 3.14 (already installed)
- PyInstaller: `py -3.14 -m pip install pyinstaller`
- All project dependencies: `py -3.14 -m pip install -r requirements.txt`

## Quick build

```bash
py -3.14 build.py
```

Or on Windows, just double-click `build.bat`.

## Output

The compiled executable is at:
```
dist/HexLauncher.exe
```

## Distribution

The `.exe` is fully standalone — users do NOT need Python installed.

On first run, the launcher creates these folders next to the `.exe`:
- `HexFiles/` — Minecraft installation
- `HexMods/` — Mod library (organized by loader + version)
- `HexJDK/` — Java runtime

## Notes

- Binary size: ~25-30 MB (UPX-compressed)
- Startup: ~1-2 seconds
- Tested on Windows 10/11

## Rebuilding

After code changes:
```bash
py -3.14 build.py
```

PyInstaller caches dependencies, so rebuilds are fast (~10 seconds).

## Troubleshooting

**"Module not found" at runtime**
Add the missing module to `hiddenimports` in `hexlauncher.spec`.

**Icon not showing**
Ensure `Hex.ico` is in the project root and referenced in the spec.

**Antivirus flags the `.exe` (Windows Defender, etc.)**

This is endemic to PyInstaller — see [`ANTIVIRUS.md`](./ANTIVIRUS.md) for
the full guide. Quick fixes:

1. **Distribute via GitHub Releases** — usually whitelisted faster
2. **Report false positive to Microsoft**: https://www.microsoft.com/en-us/wdsi/filesubmission
3. **Run `sign.bat`** to self-sign (reduces some flags, doesn't bypass SmartScreen)
4. **For real protection** — get a free OSS cert from Certum or migrate to Nuitka

**`.exe` is too large**
- Install UPX: https://upx.github.io (already enabled in spec)
- Strip more modules in `excludes`
- Consider migrating to Tauri (see `MIGRATION.md`)
