---
schema: "TOON_v3.3"
virtualization: "Copy-on-Write (CoW) MicroVMs"
---
# [SWARM SCALING MATRIX]
* **Local Edge (Cybertronia):** Max 5 concurrent Firecracker/Wasmtime microVMs (Î” â‰¤ 0.12 MiB footprint).
* **Burst CloudBrain (VPS):** Dynamic scaling for DAG compilation and heavy OSINT scans.
* **Routing Rule:** If AST patch requires compilation > 500MB RAM or Î” > 0.12 MiB, intercept via multivoice_router.go and transmit to VPS 100.110.180.18:8091.
