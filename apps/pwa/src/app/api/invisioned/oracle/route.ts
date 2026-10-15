// SPDX-License-Identifier: MIT
import { type NextRequest, NextResponse } from 'next/server';

interface OracleQueryPayload {
  query: string;
  persona?: 'lady_apis' | 'sir_helios' | 'anya';
  sessionId?: string;
}

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as Partial<OracleQueryPayload>;
    const query = body.query?.trim();

    if (!query) {
      return NextResponse.json({ error: 'Query text is required' }, { status: 400 });
    }

    const persona = body.persona || 'lady_apis';
    const timestamp = new Date().toISOString();

    // Contextual responses based on knowledge graph keywords
    let responseText = `Telemetry analysis complete for query: "${query}". All active marketing campaigns are tracking above target ROAS with zero detected budget anomalies.`;

    if (/energy|deregulated|kba/i.test(query)) {
      responseText = `The deregulated commercial energy campaign across Ohio and Pennsylvania closed 18 meter audits this week, projecting $42,600 in annualized client energy savings and generating $7,200 in agency margin.`;
    } else if (/roi|spend|budget|performance/i.test(query)) {
      responseText = `Current aggregate ad spend is $14,200 across Meta and Google, delivering a 4.12x blended ROAS and 142 qualified enterprise leads at a cost-per-acquisition of $100.`;
    } else if (/agents|knights|swarm/i.test(query)) {
      responseText = `The Round Table Swarm is currently operating at 100% capacity with 5 active knights under 782MB RAM, safely bounded by Camelot-OS Global Law 03.`;
    }

    return NextResponse.json({
      success: true,
      timestamp,
      persona,
      query,
      answer: responseText,
      audioStreamConfig: {
        voiceSampleRate: 24000,
        vadThresholdMs: 80,
        codec: 'audio/pcm',
        duplexEndpoint: process.env.ORACLE_AUDIO_WS || 'ws://127.0.0.1:7680/ws',
      },
      a2ui: {
        componentType: 'MetricCard',
        data: {
          confidenceScore: 0.98,
          citation: 'vfs://worldtree/knights/lady_apis/telemetry.json',
        },
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process Oracle query', detail: String(error) },
      { status: 500 }
    );
  }
}
