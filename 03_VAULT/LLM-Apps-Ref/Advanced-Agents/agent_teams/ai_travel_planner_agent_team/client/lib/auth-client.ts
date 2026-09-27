// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || '',
  redirects: {
    afterSignIn: '/plan',
    afterSignOut: '/auth',
  },
  fetchOptions: {
    credentials: 'include',
  },
});
