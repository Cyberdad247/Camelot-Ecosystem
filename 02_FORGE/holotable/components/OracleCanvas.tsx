"use client";

import { useEffect, useState, useCallback } from "react";
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Connection,
} from "reactflow";
import "reactflow/dist/style.css";
import { api, OracleState } from "@/lib/api";
import { Zap, Hexagon, Database } from "lucide-react";

// Mock Layout Logic
const CENTER_X = 250;
const CENTER_Y = 250;
const RADIUS = 150;

export default function OracleCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [state, setState] = useState<OracleState | null>(null);

  const refreshGraph = useCallback(async () => {
    const data = await api.getWorldState();
    if (!data) return;
    setState(data);

    // 1. Create Core Node (Tension / Epoch)
    const newNodes: Node[] = [
      {
        id: "CORE",
        position: { x: CENTER_X, y: CENTER_Y },
        data: { label: `EPOCH: ${data.epoch}` },
        style: {
          background: "#a855f7",
          color: "#fff",
          border: "2px solid #fff",
          width: 100,
          fontSize: "0.8rem",
          fontWeight: "bold",
          textAlign: "center",
          boxShadow: "0 0 20px #a855f7",
        },
        type: "default",
      },
    ];

    const newEdges: Edge[] = [];

    // 2. Create Faction Nodes in a Circle
    data.factions.forEach((f, i) => {
      const angle = (i / data.factions.length) * 2 * Math.PI;
      const x = CENTER_X + RADIUS * Math.cos(angle);
      const y = CENTER_Y + RADIUS * Math.sin(angle);

      const nodeId = `faction-${i}`;
      newNodes.push({
        id: nodeId,
        position: { x, y },
        data: { label: f.name },
        style: {
          background: "#1e293b",
          color: "#e2e8f0",
          border: "1px solid #06b6d4",
          padding: "10px",
          borderRadius: "8px",
          minWidth: "120px",
          textAlign: "center",
        },
      });

      // Connect to Core
      newEdges.push({
        id: `e-core-${nodeId}`,
        source: "CORE",
        target: nodeId,
        animated: true,
        style: { stroke: "#eab308" },
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [setNodes, setEdges]);

  useEffect(() => {
    refreshGraph();
    const interval = setInterval(refreshGraph, 5000);
    return () => clearInterval(interval);
  }, [refreshGraph]);

  return (
    <div className="glass-panel p-4 rounded-xl h-[400px] flex flex-col relative overflow-hidden">
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
        <h2 className="text-xl font-mono font-bold text-secondary flex items-center gap-2">
          <Hexagon className="w-5 h-5" /> ORACLE VIZ
        </h2>
        {state && (
          <div className="text-xs font-mono text-slate-300">
            TENSION:{" "}
            <span className="text-red-400">
              {(state.global_tension * 100).toFixed(0)}%
            </span>{" "}
            <br />
            RESOURCES: {Object.keys(state.resources).length}
          </div>
        )}
      </div>

      <div className="w-full h-full bg-slate-950/50 rounded-lg">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#334155" gap={16} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
