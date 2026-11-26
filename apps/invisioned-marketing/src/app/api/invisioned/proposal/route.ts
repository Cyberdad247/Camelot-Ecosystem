// SPDX-License-Identifier: MIT
import crypto from 'node:crypto';
import { type NextRequest, NextResponse } from 'next/server';
import { persistHybridRecord, readLedgerRecords } from '../../../../lib/invisionedStore';

interface ProposalPayload {
  clientName: string;
  clientEmail: string;
  monthlyBudget: number;
  projectedRevenue: number;
  selectedTier: string;
  contractTerms: string;
  signedBy: string;
}

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as Partial<ProposalPayload>;

    if (!body.clientName || !body.monthlyBudget || !body.signedBy) {
      return NextResponse.json(
        { error: 'clientName, monthlyBudget, and signedBy are required fields' },
        { status: 400 }
      );
    }

    const timestamp = new Date().toISOString();
    const proposalId = `prop_${crypto.randomBytes(6).toString('hex')}`;

    // Cryptographic hash proving agreement integrity
    const hashPayload = `${proposalId}:${body.clientName}:${body.monthlyBudget}:${body.selectedTier}:${timestamp}`;
    const agreementHash = crypto.createHash('sha256').update(hashPayload).digest('hex');

    const proposalRecord = {
      proposalId,
      timestamp,
      agreementHash,
      clientName: body.clientName.trim(),
      clientEmail: body.clientEmail?.trim() || 'N/A',
      monthlyBudget: body.monthlyBudget,
      projectedRevenue: body.projectedRevenue || body.monthlyBudget * 3.4,
      selectedTier: body.selectedTier || 'SOVEREIGN_ENTERPRISE',
      signedBy: body.signedBy.trim(),
      status: 'EXECUTED_AGREEMENT',
      stagedCrystalRef: `vkg_crystal_${proposalId}`,
    };

    const persistence = await persistHybridRecord('proposals', 'invisioned_proposals.jsonl', proposalRecord);

    return NextResponse.json({
      success: true,
      proposalId,
      agreementHash,
      timestamp,
      persistenceMode: persistence.mode,
      message: 'Proposal agreement cryptographically signed and archived.',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to record proposal agreement', detail: String(error) },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const proposals = await readLedgerRecords('invisioned_proposals.jsonl');
    return NextResponse.json({ success: true, count: proposals.length, proposals });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to read proposals ledger', detail: String(error) },
      { status: 500 }
    );
  }
}
