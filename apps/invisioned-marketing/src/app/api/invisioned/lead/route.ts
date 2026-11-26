// SPDX-License-Identifier: MIT
import { promises as fs } from 'node:fs';
import crypto from 'node:crypto';
import { type NextRequest, NextResponse } from 'next/server';
import { escapeHtml, persistHybridRecord, readLedgerRecords } from '../../../../lib/invisionedStore';

interface InvisionedLeadPayload {
  name: string;
  email: string;
  company?: string;
  monthlyAdSpend?: string;
  goal?: string;
  notes?: string;
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
        subject: `⚡ [HIGH PRIORITY] New Invisioned Marketing Lead: ${escapeHtml(record.name)} (${escapeHtml(record.company)})`,
        html: `
          <div style="font-family: monospace; background: #0B0B0E; color: #F8FAFC; padding: 24px; border: 2px solid #D4AF37;">
            <h2 style="color: #D4AF37; margin-top: 0;">⚡ INVISIONED MARKETING // NEW INBOUND LEAD</h2>
            <p><strong>Name:</strong> ${escapeHtml(record.name)}</p>
            <p><strong>Email:</strong> <a href="mailto:${escapeHtml(record.email)}" style="color: #D4AF37;">${escapeHtml(record.email)}</a></p>
            <p><strong>Company:</strong> ${escapeHtml(record.company)}</p>
            <p><strong>Est. Monthly Ad Spend:</strong> <span style="color: #10B981; font-weight: bold;">${escapeHtml(record.monthlyAdSpend)}</span></p>
            <p><strong>Primary Goal:</strong> ${escapeHtml(record.goal)}</p>
            <p><strong>Lead ID:</strong> <code>${escapeHtml(record.leadId)}</code></p>
            <p><strong>Timestamp:</strong> ${escapeHtml(record.timestamp)}</p>
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

    // 1. Commit to hybrid persistence (cloud bridge + non-volatile JSONL fallback)
    const persistence = await persistHybridRecord('leads', 'invisioned_leads.jsonl', record);
    const targetPath = persistence.ledgerPath;

    // 2. Dispatch Midas Loop Autonomous Qualification (Knight Strategos)
    const midasQualification = {
      lead_id: leadId,
      company: record.company,
      contact_name: record.name,
      contact_email: record.email,
      monthly_ad_spend: record.monthlyAdSpend,
      primary_goal: record.goal,
      qualification_score:
        record.monthlyAdSpend.includes('$') || record.monthlyAdSpend.includes('k') ? 95 : 85,
      selected_branch:
        record.monthlyAdSpend.includes('$') || record.monthlyAdSpend.includes('k')
          ? 'Aggressive'
          : 'Balanced',
      assigned_knights: ['KNIGHT_STRATEGOS', 'SIR_VISAGE', 'SIR_FORGE'],
      qualified_at: timestamp,
      status: 'QUALIFIED',
    };

    const qualifiedPath = targetPath.replace('invisioned_leads.jsonl', 'midas_qualified_leads.jsonl');
    await fs.appendFile(qualifiedPath, JSON.stringify(midasQualification) + '\n', 'utf-8');

    // 3. Dispatch Bio-Kinetic 5-Minute Lead Notification Webhook
    const webhookStatus = await dispatchLeadNotification(record);

    return NextResponse.json({
      success: true,
      leadId,
      timestamp,
      persistenceMode: persistence.mode,
      qualification: midasQualification,
      webhook: webhookStatus,
      message: 'Lead safely committed, Midas Loop qualified, and notification dispatched.',
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
    const leads = await readLedgerRecords('invisioned_leads.jsonl');
    return NextResponse.json({ success: true, count: leads.length, leads });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to read leads ledger', detail: String(error) },
      { status: 500 }
    );
  }
}
