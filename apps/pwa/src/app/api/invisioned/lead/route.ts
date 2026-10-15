// SPDX-License-Identifier: MIT
import { promises as fs } from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { type NextRequest, NextResponse } from 'next/server';

interface InvisionedLeadPayload {
  name: string;
  email: string;
  company?: string;
  monthlyAdSpend?: string;
  goal?: string;
  notes?: string;
}

function getLeadsLedgerPath(): string {
  return path.join(process.cwd(), '..', '..', '03_VAULT', 'runtime_state', 'invisioned_leads.jsonl');
}

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as Partial<InvisionedLeadPayload>;

    if (!body.email || typeof body.email !== 'string' || !body.email.includes('@')) {
      return NextResponse.json(
        { error: 'Valid business email is required' },
        { status: 400 }
      );
    }

    const leadId = `lead_${crypto.randomBytes(6).toString('hex')}`;
    const timestamp = new Date().toISOString();

    const record = {
      leadId,
      timestamp,
      name: body.name?.trim() || 'Anonymous Lead',
      email: body.email.trim().toLowerCase(),
      company: body.company?.trim() || 'N/A',
      monthlyAdSpend: body.monthlyAdSpend || 'Unspecified',
      goal: body.goal || 'General Inbound',
      notes: body.notes || '',
      status: 'NEW',
      provenance: 'MIDAS_LEAD_CAPTURE_v1',
    };

    const targetPath = getLeadsLedgerPath();
    const parentDir = path.dirname(targetPath);
    await fs.mkdir(parentDir, { recursive: true });

    await fs.appendFile(targetPath, JSON.stringify(record) + '\n', 'utf-8');

    return NextResponse.json({
      success: true,
      leadId,
      timestamp,
      message: 'Lead safely committed to non-volatile vault ledger.',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to persist lead record', detail: String(error) },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const targetPath = getLeadsLedgerPath();
    try {
      const data = await fs.readFile(targetPath, 'utf-8');
      const lines = data.split('\n').filter(Boolean);
      const leads = lines.map((line) => JSON.parse(line));
      return NextResponse.json({ success: true, count: leads.length, leads });
    } catch {
      return NextResponse.json({ success: true, count: 0, leads: [] });
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to read leads ledger', detail: String(error) },
      { status: 500 }
    );
  }
}
