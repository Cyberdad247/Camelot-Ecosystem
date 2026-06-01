# Scorpion Sting Forensic Review

- Root: `C:\Users\vizio\.docker`
- Generated: `2026-05-24T21:56:02.022687+00:00`
- Scanned files: `255`
- Scanned dirs: `68`
- Total scanned: `18.5 GB`
- Candidate footprint: `18.3 GB`

| Action | Entropy | Size | Reason | Path |
|---|---:|---:|---|---|
| purge | 70 | 2.5 MB | dormant_log | `cloud/logs/cloud-daemon-2025-08-19T20-41-15.492.log` |
| purge | 70 | 23.1 KB | dormant_log | `cloud/logs/cloud-daemon.log` |
| purge | 70 | 1.6 KB | dormant_log | `cloud/logs/mutagen-daemon.log` |
| archive | 40 | 11.1 GB | large_file_review | `models/blobs/sha256/cba351b0548ef26e896c3a3063a969c3cc1f1dcfb8c8335b123908337fd75eba` |
| archive | 40 | 2.3 GB | large_file_review | `models/blobs/sha256/09b370de51ad3bde8c3aea3559a769a59e7772e813667ddbafc96ab2dc1adaa7` |
| archive | 40 | 1.9 GB | large_file_review | `models/blobs/sha256/91651317fc958f8e6b4f1414cd71e2529ad335b4a6af9c3add2f5f09c822fba0` |
| archive | 40 | 1.8 GB | large_file_review | `models/blobs/sha256/8334b850b7bd46238c16b0c550df2138f0889bf433809008cc17a8b05761863e` |
| review | 55 | 637.7 MB | large_binary_review | `bin/inference/cublasLt64_12.dll` |
| archive | 40 | 261.5 MB | large_file_review | `models/blobs/sha256/2780dda2bd2b39f03f67394fe7f29e3824bb23dd40ed70bfde55528c7c12888a` |
| archive | 40 | 258.1 MB | large_file_review | `models/blobs/sha256/bf6f20a603055433b4b998119e17928fc4a89b35c42855dd7eada105058cae0a` |
| review | 55 | 153.4 MB | large_binary_review | `bin/inference/ggml-cuda.dll` |
