# Deployment notes (placeholder)

- Vercel deployment is deferred until the remote auth/trust/network
  operator threat model is explicitly approved (design §17).
- If a future dedicated host is required, extract console components
  into `packages/operator-console-ui/` and import — never copy.
