# Knight idle-loop videos

Drop per-knight MP4 idle loops here. `VideoAvatar.tsx` loads them automatically
and falls back to the procedural figure for any knight whose file is missing.

## Naming (required)

Use the **exact lowercase keys** broadcast by `go_router` (`knightRoster` in
`control_plane/go_router/main.go`):

```
public/videos/anya_idle.mp4
public/videos/merlin_idle.mp4
public/videos/codex_idle.mp4
public/videos/hashimoto_idle.mp4
public/videos/boris_idle.mp4
public/videos/helios_idle.mp4
```

Pattern: `public/videos/<knight>_idle.mp4`. Served at `/videos/<knight>_idle.mp4`
(Vite serves `public/` at the site root). Add files anytime — no rebuild of the
component needed; a page refresh picks them up.

## Encoding recommendations

- **Container/codec:** MP4 / H.264 (`yuv420p`) + AAC — widest browser support.
- **Muted autoplay:** the element is `muted` + `playsInline`, so it autoplays on
  desktop and iOS. Keep loops short (3–8 s) and seamless.
- **Size:** ~512×512 to ~720×720 is plenty for the on-canvas panel; keep files
  small to respect the scarcity budget.

Example re-encode with ffmpeg:

```bash
ffmpeg -i source.mov -c:v libx264 -pix_fmt yuv420p -an -vf "scale=640:640" codex_idle.mp4
```

## Hologram-on-black (optional)

If your loops have a pure-black background and you want a floating-hologram look
(black pixels become invisible), set the material in `VideoAvatar.tsx` to
additive blending:

```tsx
<meshBasicMaterial map={texture} side={THREE.DoubleSide} toneMapped={false}
  blending={THREE.AdditiveBlending} transparent depthWrite={false} />
```

Leave it as the default opaque map for normal (non-black-background) footage.
