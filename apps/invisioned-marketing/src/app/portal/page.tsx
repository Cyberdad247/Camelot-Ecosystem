import { ClientOraclePortal } from '@/components/ClientOraclePortal';
import { HolographicClientOracle } from '@/components/HolographicClientOracle';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'VIP Client Lounge & Voice Oracle | Invisioned Marketing Inc.',
  description: 'Real-time campaign telemetry, GraphRAG analytics, and conversational 2.5D AI Oracle.',
};

export const dynamic = 'force-dynamic';

export default function PortalPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0E] p-6 max-w-7xl mx-auto font-mono space-y-8">
      <div className="border border-[#D4AF37]/30 bg-[#121217] p-4 text-xs flex justify-between items-center text-[#D4AF37]">
        <span>⚡ VIP CLIENT TELEMETRY ENCLAVE</span>
        <span className="text-emerald-400 font-bold">LIVE A2UI LINK ACTIVE</span>
      </div>
      <HolographicClientOracle />
      <ClientOraclePortal />
    </div>
  );
}
