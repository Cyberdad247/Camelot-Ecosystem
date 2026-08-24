import { AccessToken } from 'livekit-server-sdk';
// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { NextResponse } from 'next/server';

export async function POST() {
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const livekitUrl = process.env.LIVEKIT_URL;

  if (!apiKey || !apiSecret || !livekitUrl) {
    return NextResponse.json({ error: 'LiveKit not configured' }, { status: 500 });
  }

  const roomName = `tasha-${crypto.randomUUID().slice(0, 8)}`;
  const participantIdentity = `visitor-${crypto.randomUUID().slice(0, 8)}`;

  const token = new AccessToken(apiKey, apiSecret, {
    identity: participantIdentity,
    ttl: '10m',
  });
  token.addGrant({
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canSubscribe: true,
  });

  const jwt = await token.toJwt();

  return NextResponse.json({
    token: jwt,
    url: livekitUrl,
    room: roomName,
    identity: participantIdentity,
  });
}
