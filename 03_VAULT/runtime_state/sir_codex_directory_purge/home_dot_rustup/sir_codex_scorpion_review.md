# Scorpion Sting Forensic Review

- Root: `C:\Users\vizio\.rustup`
- Generated: `2026-05-24T21:56:00.962543+00:00`
- Scanned files: `81284`
- Scanned dirs: `2082`
- Total scanned: `2.0 GB`
- Candidate footprint: `490.6 MB`

| Action | Entropy | Size | Reason | Path |
|---|---:|---:|---|---|
| purge | 95 | 5.6 MB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/lib/std-0cebe7c42cd80226.pdb` |
| purge | 95 | 4.4 MB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/ld64.lld.pdb` |
| purge | 95 | 4.4 MB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/lld-link.pdb` |
| purge | 95 | 4.4 MB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/wasm-ld.pdb` |
| purge | 95 | 3.5 MB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/bin/rustc_main-1ce660e6f7b09dfc.pdb` |
| purge | 95 | 820.0 KB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/lib/std-0cebe7c42cd80226.dll` |
| purge | 95 | 318.5 KB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/ld64.lld.exe` |
| purge | 95 | 318.5 KB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/lld-link.exe` |
| purge | 95 | 318.5 KB | duplicate_binary | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/gcc-ld/wasm-ld.exe` |
| review | 55 | 184.3 MB | large_binary_review | `toolchains/stable-x86_64-pc-windows-msvc/bin/rustc_driver-0f1b6065992ac7c3.dll` |
| archive | 40 | 174.1 MB | large_file_review | `tmp/0wte7zdee7tit4ah_file` |
| review | 55 | 108.1 MB | large_binary_review | `toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin/rust-lld.exe` |
