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
  // Graceful fallback for serverless/local environments
  const isVercel = Boolean(process.env.VERCEL || process.env.AWS_LAMBDA_FUNCTION_NAME);
  if (isVercel) {
    return path.join('/tmp', 'invisioned_leads.jsonl');
  }
  return path.join(process.cwd(), '..', '..', '03_VAULT', 'runtime_state', 'invisioned_leads.jsonl');
}

/**
 * Dispatches instant notification webhook (Resend / Email / Slack / Webhook)
 * Ensures zero-blocking: errors in webhook dispatch do NOT abort the lead commitment.
 */
async function dispatchLeadNotification(record: Record<string, unknown>): Promise<{ delivered: boolean; detail?: string }> {
  const resendApiKey = process.env.RESEND_API_KEY;
  const notifyEmail = process.env.LEAD_NOTIFY_EMAIL || 'vizion@invisionedmarketing.agency';

  if (!resendApiKey) {
    // Stored in mock/offline log if API key not injected
    return { delivered: false, detail: 'RESEND_API_KEY omitted, queued in non-volatile ledger' };
  }

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${resendApiKey}`,
      },
      body: JSON.stringify({
        from: 'Midas Funnel <leads@invisionedmarketing.agency>',
        to: [notifyEmail],
        subject: `⚡ [HIGH PRIORITY] New Invisioned Marketing Lead: ${record.name} (${record.company})`,
        html: `
          <div style="font-family: monospace; background: #0B0B0E; color: #F8FAFC; padding: 24px; border: 2px solid #D4AF37;">
            <h2 style="color: #D4AF37; margin-top: 0;">⚡ INVISIONED MARKETING // NEW INBOUND LEAD</h2>
            <p><strong>Name:</strong> ${record.name}</p>
            <p><strong>Email:</strong> <a href="mailto:${record.email}" style="color: #D4AF37;">${record.email}</a></p>
            <p><strong>Company:</strong> ${record.company}</p>
            <p><strong>Est. Monthly Ad Spend:</strong> <span style="color: #10B981; font-weight: bold;">${record.monthlyAdSpend}</span></p>
            <p><strong>Primary Goal:</strong> ${record.goal}</p>
            <p><strong>Lead ID:</strong> <code>${record.leadId}</code></p>
            <p><strong>Timestamp:</strong> ${record.timestamp}</p>
            <hr style="border: 1px solid #242430; margin: 20px 0;" />
            <p style="font-size: 11px; color: #94A3B8;">Action Required: Engage lead within 5 minutes for maximum conversion velocity.</p>
          </div>
        `,
      }),
    });

    if (res.ok) {
      return { delivered: true };
    }
    const errText = await res.text();
    return { delivered: false, detail: `Resend HTTP ${res.status}: ${errText}` };
  } catch (err) {
    return { delivered: false, detail: String(err) };
  }
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

    // 1. Commit to persistent vault ledger (serverless & local compatible)
    const targetPath = getLeadsLedgerPath();
    const parentDir = path.dirname(targetPath);
    await fs.mkdir(parentDir, { recursive: true });
    await fs.appendFile(targetPath, JSON.stringify(record) + '\n', 'utf-8');

    // 2. Dispatch Bio-Kinetic 5-Minute Lead Notification Webhook
    const webhookStatus = await dispatchLeadNotification(record);

    return NextResponse.json({
      success: true,
      leadId,
      timestamp,
      webhook: webhookStatus,
      message: 'Lead safely committed and notification dispatched.',
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
