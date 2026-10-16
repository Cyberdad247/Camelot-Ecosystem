// SPDX-License-Identifier: MIT
import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = 'https://www.invisionedmarketing.agency';

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/_next/'],
      },
      // Explicitly allow leading AI search engines (Perplexity, GPTBot, ClaudeBot, Google-Extended)
      // for Generative Engine Optimization (GEO)
      {
        userAgent: ['GPTBot', 'ChatGPT-User', 'ClaudeBot', 'PerplexityBot', 'Google-Extended', 'Amazonbot'],
        allow: ['/', '/#audit', '/#oracle', '/#proposal'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
