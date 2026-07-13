# Anya VRM Model Contract

The Cockpit VRM runtime is implemented but intentionally does not bundle a third-party character model that would replace Anya's identity.

Provide a licensed VRM 1.0 model and set:

```text
NEXT_PUBLIC_ANYA_VRM_URL=/models/anya.vrm
```

Production target:

- Full-body humanoid VRM 1.0
- Under 6 MB after mesh and texture compression
- Standard blink, look, and `aa` expression presets
- Cleared commercial redistribution rights
- Identity aligned with `public/anya-fullbody.png`

Without this variable, the transparent Arthurian raster remains the offline and low-resource production asset. The Three.js and `three-vrm` chunk is not loaded.
