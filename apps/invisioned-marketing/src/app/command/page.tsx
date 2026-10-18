import { SovereignCommandDashboard } from '@/components/SovereignCommandDashboard';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Swarm Command Nexus | Invisioned Marketing Inc.',
  description: 'Real-time multi-agent execution telemetry, node resource governance, and task dispatch.',
};

export const dynamic = 'force-dynamic';

export default function CommandPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0E] p-6 max-w-7xl mx-auto font-mono">
      <SovereignCommandDashboard />
    </div>
  );
}
