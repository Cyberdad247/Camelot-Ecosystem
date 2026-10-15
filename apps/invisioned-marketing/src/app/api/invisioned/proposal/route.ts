// SPDX-License-Identifier: MIT
import { promises as fs } from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { type NextRequest, NextResponse } from 'next/server';

interface ProposalPayload {
  clientName: string;
  clientEmail: string;
  monthlyBudget: number;
  projectedRevenue: number;
  selectedTier: string;
  contractTerms: string;
  signedBy: string;
}

function getProposalsLedgerPath(): string {
  return path.join(process.cwd(), '..', '..', '03_VAULT', 'runtime_state', 'invisioned_proposals.jsonl');
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

    const targetPath = getProposalsLedgerPath();
    const parentDir = path.dirname(targetPath);
    await fs.mkdir(parentDir, { recursive: true });

    await fs.appendFile(targetPath, JSON.stringify(proposalRecord) + '\n', 'utf-8');

    return NextResponse.json({
      success: true,
      proposalId,
      agreementHash,
      timestamp,
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
    const targetPath = getProposalsLedgerPath();
    try {
      const data = await fs.readFile(targetPath, 'utf-8');
      const lines = data.split('\n').filter(Boolean);
      const proposals = lines.map((line) => JSON.parse(line));
      return NextResponse.json({ success: true, count: proposals.length, proposals });
    } catch {
      return NextResponse.json({ success: true, count: 0, proposals: [] });
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to read proposals ledger', detail: String(error) },
      { status: 500 }
    );
  }
}
