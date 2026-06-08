// E. Deploy Route Handler — POST /api/deploy
// Accepts AST snapshot from the client, scaffolds a static site, deploys via Vercel CLI.

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { deploy, DeployError } from '@/lib/deploy';

// ---------------------------------------------------------------------------
// Request schema — mirrors ASTNode but validated at the boundary
// ---------------------------------------------------------------------------

const ASTNodeSchema = z.object({
  id:    z.uuid(),
  pid:   z.uuid().nullable(),
  tag:   z.string().min(1),
  props: z.record(z.string(), z.unknown()),
});

const DeployBodySchema = z.object({
  nodes:     z.array(ASTNodeSchema).min(1, 'At least one node is required'),
  bg:        z.string().regex(/^#[0-9a-fA-F]{6}$/).optional().default('#ffffff'),
  siteName:  z.string().min(1).max(52).optional().default('camelot-site'),
});

type DeployBody = z.infer<typeof DeployBodySchema>;

// ---------------------------------------------------------------------------
// POST /api/deploy
// ---------------------------------------------------------------------------

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: DeployBody;

  try {
    const raw = await req.json() as unknown;
    const parsed = DeployBodySchema.safeParse(raw);
    if (!parsed.success) {
      const issues = parsed.error.issues
        .map(i => `${i.path.join('.')}: ${i.message}`)
        .join('; ');
      return NextResponse.json({ error: `Validation failed: ${issues}` }, { status: 400 });
    }
    body = parsed.data;
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  try {
    const result = await deploy({
      nodes:    body.nodes,
      bg:       body.bg,
      siteName: body.siteName,
    });

    return NextResponse.json(result, { status: 200 });
  } catch (e) {
    if (e instanceof DeployError) {
      const status = e.stage === 'generate' ? 422 : 502;
      return NextResponse.json({ error: e.message, stage: e.stage }, { status });
    }
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
