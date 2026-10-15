import { OmniFulfillmentCanvas } from '@/components/OmniFulfillmentCanvas';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Omni-Fulfillment Canvas | Invisioned Marketing Inc.',
  description: 'Visual DAG node campaign assembly line and robotic agency execution kitchen.',
};

export default function CanvasPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0E] p-6 max-w-7xl mx-auto font-mono">
      <OmniFulfillmentCanvas />
    </div>
  );
}
