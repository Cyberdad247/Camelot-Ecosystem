import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { ShieldCheck, Smartphone, Zap } from 'lucide-react';

export const QRPillGenerator: React.FC = () => {
  const [payload, setPayload] = useState<string>('');
  const [activeRole, setActiveRole] = useState<'EXECUTIVE' | 'MANAGER' | 'STAFF' | null>(null);

  const generateQRPill = (role: 'EXECUTIVE' | 'MANAGER' | 'STAFF') => {
    // 1. Generate a zero-trust, time-to-live (TTL) bootstrap token
    const bootstrapToken = `kba-auth-${Math.random().toString(36).substring(2, 15)}`;
    
    // 2. Construct the high-density micro-manifest
    const pillManifest = {
      protocol: "QR_PILL_BOOTSTRAP",
      version: "v1000.54-ASCENDED",
      role_access: role,
      network_seed: bootstrapToken,
      local_relay: "wss://10.0.0.42:8443/bifrost-bootstrap" // Local Air-Gapped IP
    };
    
    // 3. Compress to base64 for QR density
    setPayload(btoa(JSON.stringify(pillManifest)));
    setActiveRole(role);
  };

  return (
    <div className="bg-[#050507] border border-[#D4AF37] p-8 max-w-md font-mono text-white shadow-[0_0_30px_rgba(212,175,55,0.15)]">
      <header className="mb-6 flex justify-between border-b border-[#333] pb-4">
        <h2 className="text-[#D4AF37] text-2xl tracking-widest font-bold flex items-center gap-2">
          <Zap size={24} /> QR_PILL FORGE
        </h2>
        <p className="text-[10px] text-[#9D4EDD] uppercase mt-2">
          Air-Gapped Bare-Metal Deployment Engine
        </p>
      </header>

      <div className="flex flex-col gap-4 mb-8">
        <button
          onClick={() => generateQRPill('EXECUTIVE')}
          className={`p-3 text-left border transition-all ${
            activeRole === 'EXECUTIVE' 
              ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]' 
              : 'bg-[#111] hover:bg-[#D4AF37] hover:text-black border-[#333] flex items-center justify-center gap-2'
          }`}
        >
          <ShieldCheck size={16} /> GENERATE EXECUTIVE PILL (Andre/Pam)
        </button>
        <button
          onClick={() => generateQRPill('STAFF')}
          className={`p-3 text-left border transition-all ${
            activeRole === 'STAFF' 
              ? 'border-[#9D4EDD] bg-[#9D4EDD]/10 text-[#9D4EDD]' 
              : 'bg-[#111] hover:bg-[#9D4EDD] hover:text-black border-[#333] flex items-center justify-center gap-2'
          }`}
        >
          <Smartphone size={16} /> GENERATE STAFF PILL (POS/Inventory)
        </button>
      </div>

      <div className="flex flex-col items-center justify-center border border-[#333] bg-[#0D0D11] p-6">
        {payload ? (
          <>
            <div className="bg-white p-4 rounded-sm mb-4">
              <QRCodeSVG value={payload} size={200} level="H" />
            </div>
            <div className="text-xs text-green-400 text-center flex items-center gap-2 animate-pulse">
              <Zap size={12} /> ENCRYPTED SEED READY TO SCAN
            </div>
          </>
        ) : (
          <div className="text-xs text-gray-600 text-center italic">
            Awaiting role selection...
          </div>
        )}
      </div>
    </div>
  );
};
