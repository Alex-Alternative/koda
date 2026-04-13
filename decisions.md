# Decisions Log — Koda

| Date | Decision | Why | Alternatives Rejected |
|------|----------|-----|----------------------|
| — | Python + pystray + tkinter | Proven stack for Windows tray apps with overlay UI | Electron (too heavy), C# (less AI-friendly) |
| — | Subprocess isolation for hotkey service | Prevents GIL starvation when Whisper model runs | Single process (causes input lag) |
| — | GitHub releases for auto-update (no infra) | Zero server cost; works for private distribution | Custom update server |
| — | PyInstaller + Inno Setup for distribution | Produces single .exe installer; proven on v4.x | Raw Python (requires user to have Python installed) |
| — | No NVIDIA GPU dependency | Machine has Intel UHD 770 only — CUDA unavailable | GPU-accelerated Whisper (not viable here) |
| — | Run from source only during dev | Avoids reinstalling .exe on every change | Building exe for every test (slow) |
