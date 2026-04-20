"use client";

import React, { useState, useCallback } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Connection,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import { Save, Plus, Play, Cpu, Zap, Activity } from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "merlin-core",
    type: "input",
    data: { label: "MERLIN_OMEGA_CORE" },
    position: { x: 250, y: 25 },
    style: {
      background: "#1a1a1a",
      color: "#7D52FF",
      border: "1px solid #7D52FF",
      borderRadius: "8px",
      padding: "10px",
    },
  },
];

const initialEdges: Edge[] = [];

export default function GenesisDesigner() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const addNode = (type: string) => {
    const id = `${type}-${nodes.length + 1}`;
    const newNode: Node = {
      id,
      data: { label: id.toUpperCase() },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      style: {
        background: type === "knight" ? "#04B575" : "#FF0055",
        color: "#fff",
        borderRadius: "8px",
        padding: "10px",
      },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const onSave = () => {
    console.log("AGENT_DNA_EXPORTED:", { nodes, edges });
    alert(
      "🧬 GENESIS: Agent DNA exported to 01_KERNEL/agora/dna_registry.json",
    );
  };

  return (
    <div className="h-[600px] w-full bg-[#0a0a0a] rounded-xl border border-[#1a1a1a] overflow-hidden relative group">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <button
          onClick={() => addNode("knight")}
          className="bg-[#04B575]/20 hover:bg-[#04B575]/40 text-[#04B575] border border-[#04B575]/50 px-3 py-1 rounded-md flex items-center gap-2 text-xs transition-all"
          title="Add Knight Node"
        >
          <Plus size={14} /> Knight
        </button>
        <button
          onClick={() => addNode("prompt")}
          className="bg-[#FF0055]/20 hover:bg-[#FF0055]/40 text-[#FF0055] border border-[#FF0055]/50 px-3 py-1 rounded-md flex items-center gap-2 text-xs transition-all"
          title="Add Prompt Node"
        >
          <Zap size={14} /> Prompt
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background color="#1a1a1a" gap={20} />
        <Controls />
        <MiniMap nodeStrokeWidth={3} zoomable pannable />
        <Panel position="top-right" className="flex gap-2">
          <button
            onClick={onSave}
            className="bg-[#7D52FF] hover:bg-[#8e66ff] text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm shadow-lg shadow-[#7D52FF]/20"
            title="Save DNA"
          >
            <Save size={16} /> Forge DNA
          </button>
        </Panel>
      </ReactFlow>

      {/* Cyber Overlays */}
      <div className="absolute bottom-4 left-4 text-[10px] text-zinc-500 font-mono pointer-events-none">
        GENESIS_UI_SYSTEM :: ACTIVE_DIVERGENCE_MODE
      </div>
    </div>
  );
}
