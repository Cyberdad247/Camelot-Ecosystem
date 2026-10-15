import { InteractiveB2BProposal } from '@/components/InteractiveB2BProposal';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Interactive B2B Proposal | Invisioned Marketing Inc.',
  description: 'Cryptographically signed agency agreements, ROI modeling, and performance retainers.',
};

export default function ProposalPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0E] p-6 max-w-7xl mx-auto font-mono">
      <InteractiveB2BProposal />
    </div>
  );
}
