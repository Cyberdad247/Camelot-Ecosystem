import { MidasLeadCapture } from '@/components/MidasLeadCapture';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Inbound Intake Funnel | Invisioned Marketing Inc.',
  description: 'AI-powered B2B client acquisition, high-converting lead funnel, and marketing ROI acceleration.',
};

export const dynamic = 'force-dynamic';

export default function LeadsPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0E] p-6 max-w-7xl mx-auto font-mono">
      <MidasLeadCapture />
    </div>
  );
}
