"use client";

import { useEffect, useRef, useState } from "react";
import { Activity, Network, ShieldCheck, Zap } from "lucide-react";

interface Node3D {
  id: string;
  name: string;
  role: string;
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  color: string;
}

export function JarvisGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredNode, setHoveredNode] = useState<Node3D | null>(null);
  const [activeTab, setActiveTab] = useState<"graph" | "triplets">("graph");

  // Normalized Graphify SVO Triplets representing the Assimilation Protocol
  const triplets = [
    { head: "WASI 2.0 Control Plane", relation: "implements", tail: "WebAssembly Component Model" },
    { head: "SIR_CORVUS", relation: "guards", tail: "Firecracker KVM microVMs" },
    { head: "virtio-vsock (AF_VSOCK)", relation: "streams", tail: "Host-Guest Telemetry" },
    { head: "Ouroboros SSM", relation: "drives", tail: "1.58-bit Local Reasoning" },
    { head: "Aegis Shield", relation: "redacts", tail: "Secured Sinks & Patterns" },
    { head: "APEE v7.0 Triage", relation: "governs", tail: "Iron Gate v2 Approvals" },
    { head: "MemCastle Vault", relation: "stores", tail: "Semantic Recall Triplets" },
  ];

  // Knights & Subsystems Roster
  const initialNodes: Node3D[] = [
    { id: "codex", name: "SIR_CODEX", role: "WASI 2.0 Warden", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#FFD700" },
    { id: "borris", name: "SIR_BORRIS", role: "Ledger/PBFT Warden", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#7B2CBF" },
    { id: "corvus", name: "SIR_CORVUS", role: "Firecracker execution", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#FF3366" },
    { id: "merlin", name: "MERLIN_Ω", role: "APEE v7.0 Advisor", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#00E5FF" },
    { id: "anya", name: "ANYA_Ω", role: "PWA Cockpit Presence", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#FFD700" },
    { id: "mnemosyne", name: "LADY_MNEMOSYNE", role: "Cloud Brain Synchronizer", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#7B2CBF" },
    { id: "edge", name: "KINETIC_EDGE", role: "Squire swarm cells", x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, color: "#00E5FF" },
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;
    let width = canvas.clientWidth;
    let height = canvas.clientHeight;
    canvas.width = width;
    canvas.height = height;

    // Distribute nodes in a 3D sphere layout
    const nodes = initialNodes.map((node, index) => {
      const phi = Math.acos(-1 + (2 * index) / initialNodes.length);
      const theta = Math.sqrt(initialNodes.length * Math.PI) * phi;
      const radius = Math.min(width, height) * 0.35;
      return {
        ...node,
        x: radius * Math.cos(theta) * Math.sin(phi),
        y: radius * Math.sin(theta) * Math.sin(phi),
        z: radius * Math.cos(phi),
      };
    });

    let angleX = 0.005;
    let angleY = 0.008;

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width;
      canvas.height = height;
    };
    window.addEventListener("resize", handleResize);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Rotate nodes around X and Y axes
      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);
      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);

      nodes.forEach((node) => {
        // Rotate Y
        const x1 = node.x * cosY - node.z * sinY;
        const z1 = node.z * cosY + node.x * sinY;
        // Rotate X
        const y2 = node.y * cosX - z1 * sinX;
        const z2 = z1 * cosX + node.y * sinX;

        node.x = x1;
        node.y = y2;
        node.z = z2;
      });

      // Sort by Z for proper 3D rendering order (back-to-front)
      const sortedNodes = [...nodes].sort((a, b) => a.z - b.z);

      const centerX = width / 2;
      const centerY = height / 2;

      // Draw edges / links
      ctx.lineWidth = 1;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const n1 = nodes[i];
          const n2 = nodes[j];

          // Edge depth styling
          const zDepth = (n1.z + n2.z) / 2;
          const alpha = Math.max(0.05, 0.45 + zDepth / 400);

          const grad = ctx.createLinearGradient(
            n1.x + centerX,
            n1.y + centerY,
            n2.x + centerX,
            n2.y + centerY
          );
          grad.addColorStop(0, `${n1.color}${Math.floor(alpha * 255).toString(16).padStart(2, "0")}`);
          grad.addColorStop(1, `${n2.color}${Math.floor(alpha * 255).toString(16).padStart(2, "0")}`);

          ctx.strokeStyle = grad;
          ctx.beginPath();
          ctx.moveTo(n1.x + centerX, n1.y + centerY);
          ctx.lineTo(n2.x + centerX, n2.y + centerY);
          ctx.stroke();
        }
      }

      // Draw nodes
      sortedNodes.forEach((node) => {
        const x = node.x + centerX;
        const y = node.y + centerY;
        // Project size based on Z depth
        const size = Math.max(4, 8 + node.z / 30);
        const alpha = Math.max(0.2, 0.8 + node.z / 300);

        // Outer glow ring
        ctx.beginPath();
        ctx.arc(x, y, size * 1.8, 0, Math.PI * 2);
        ctx.fillStyle = `${node.color}15`;
        ctx.fill();

        // Node center
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.shadowColor = node.color;
        ctx.shadowBlur = 10;
        ctx.globalAlpha = alpha;
        ctx.fill();
        ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 0;

        // Label for closer nodes
        if (node.z > -10) {
          ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
          ctx.font = "10px Outfit, Inter, sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(node.name, x, y - size - 6);
        }
      });

      animationId = requestAnimationFrame(draw);
    };

    draw();

    // Mouse movement to check hover and skew rotation speed
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left - width / 2;
      const mouseY = e.clientY - rect.top - height / 2;

      // Adjust rotation speed based on cursor
      angleY = mouseX * 0.00005;
      angleX = mouseY * 0.00005;

      // Check node hover
      let foundHover: Node3D | null = null;
      for (const node of nodes) {
        const nx = node.x + width / 2;
        const ny = node.y + height / 2;
        const dx = e.clientX - rect.left - nx;
        const dy = e.clientY - rect.top - ny;
        if (Math.sqrt(dx * dx + dy * dy) < 18) {
          foundHover = node;
          break;
        }
      }
      setHoveredNode(foundHover);
    };
    canvas.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (canvas) canvas.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <section className="surface jarvis-projection-surface" aria-labelledby="jarvis-projection-title">
      <div className="surface-heading">
        <div>
          <p className="eyebrow">Jarvis OS Matrix</p>
          <h2 id="jarvis-projection-title">Assimilation Projection</h2>
        </div>
        <div className="tab-buttons">
          <button className={activeTab === "graph" ? "active" : ""} onClick={() => setActiveTab("graph")}><Network /> Graph</button>
          <button className={activeTab === "triplets" ? "active" : ""} onClick={() => setActiveTab("triplets")}><Activity /> Triplets</button>
        </div>
      </div>

      <div className="jarvis-container">
        {activeTab === "graph" ? (
          <div className="canvas-wrapper">
            <canvas ref={canvasRef} />
            {hoveredNode && (
              <div className="graph-tooltip">
                <Zap />
                <div>
                  <strong>{hoveredNode.name}</strong>
                  <small>{hoveredNode.role}</small>
                </div>
              </div>
            )}
            <div className="system-indicator">
              <span className="pulse-ping" />
              <span>3D Lattice Projections Running</span>
            </div>
          </div>
        ) : (
          <div className="triplets-list">
            <div className="triplets-scroller">
              {triplets.map((t, idx) => (
                <div className="triplet-card" key={idx}>
                  <span className="triplet-head">{t.head}</span>
                  <span className="triplet-relation">--[{t.relation}]--&gt;</span>
                  <span className="triplet-tail">{t.tail}</span>
                </div>
              ))}
            </div>
            <div className="triplets-footer">
              <ShieldCheck />
              <span>MemCastle Semantic Indices Verified</span>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .jarvis-projection-surface {
          grid-column: span 2;
          display: flex;
          flex-direction: column;
          min-height: 400px;
        }
        .tab-buttons {
          display: flex;
          gap: 6px;
          background: rgba(255, 255, 255, 0.05);
          padding: 3px;
          border-radius: 6px;
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .tab-buttons button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
          color: rgba(255, 255, 255, 0.6);
          background: transparent;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .tab-buttons button.active {
          color: #fff;
          background: rgba(212, 175, 55, 0.15);
          border: 1px solid rgba(212, 175, 55, 0.25);
        }
        .jarvis-container {
          flex: 1;
          position: relative;
          min-height: 320px;
          display: flex;
          flex-direction: column;
        }
        .canvas-wrapper {
          flex: 1;
          position: relative;
          width: 100%;
          height: 100%;
          cursor: crosshair;
        }
        canvas {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }
        .graph-tooltip {
          position: absolute;
          bottom: 16px;
          left: 16px;
          background: rgba(11, 11, 15, 0.95);
          border: 1px solid rgba(212, 175, 55, 0.35);
          padding: 8px 12px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          gap: 10px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
          animation: tooltip-fade 0.2s ease-out;
        }
        .graph-tooltip :global(svg) {
          color: #FFD700;
          width: 16px;
          height: 16px;
        }
        .graph-tooltip div {
          display: flex;
          flex-direction: column;
        }
        .graph-tooltip strong {
          font-size: 12px;
          color: #fff;
        }
        .graph-tooltip small {
          font-size: 10px;
          color: rgba(255, 255, 255, 0.6);
        }
        .system-indicator {
          position: absolute;
          top: 16px;
          right: 16px;
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 10px;
          color: rgba(255, 255, 255, 0.5);
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 4px 8px;
          border-radius: 4px;
        }
        .pulse-ping {
          width: 6px;
          height: 6px;
          background: #7B2CBF;
          border-radius: 50%;
          animation: pulse 1.5s infinite;
        }
        .triplets-list {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 16px;
        }
        .triplets-scroller {
          max-height: 240px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .triplet-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 10px 14px;
          border-radius: 6px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-family: monospace;
          font-size: 11px;
        }
        .triplet-head {
          color: #FFD700;
        }
        .triplet-relation {
          color: rgba(255, 255, 255, 0.4);
        }
        .triplet-tail {
          color: #00E5FF;
        }
        .triplets-footer {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 10px;
          color: rgba(255, 255, 255, 0.5);
          padding-top: 10px;
          border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        .triplets-footer :global(svg) {
          width: 14px;
          height: 14px;
          color: #7B2CBF;
        }
        @keyframes tooltip-fade {
          from { opacity: 0; transform: translateY(5px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0% { transform: scale(0.9); opacity: 0.5; }
          50% { transform: scale(1.15); opacity: 1; }
          100% { transform: scale(0.9); opacity: 0.5; }
        }
      `}</style>
    </section>
  );
}
