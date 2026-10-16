import type { Metadata, Viewport } from 'next';
import { ServiceWorkerRegister } from '../components/ServiceWorkerRegister';
import './globals.css';

export const metadata: Metadata = {
  title: 'Invisioned Marketing Inc. — Sovereign Digital Factory',
  description: 'Autonomous multi-agent marketing agency, lead generation, and dynamic client fulfillment engine.',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Invisioned',
  },
  icons: {
    icon: '/icon.svg',
    apple: '/icon.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#0B0B0E',
  width: 'device-width',
  initialScale: 1,
  colorScheme: 'dark',
};

const JSON_LD_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'MarketingAgency',
  name: 'Invisioned Marketing Inc.',
  url: 'https://www.invisionedmarketing.agency',
  logo: 'https://www.invisionedmarketing.agency/icon.svg',
  description: 'Autonomous AI digital marketing agency specializing in Paid Media ROAS optimization, Conversion Rate Optimization, and multi-agent creative swarms.',
  sameAs: [
    'https://twitter.com/invisioned_mktg',
    'https://www.linkedin.com/company/invisioned-marketing',
  ],
  areaServed: {
    '@type': 'AdministrativeArea',
    name: 'Worldwide',
  },
  knowsAbout: [
    'Generative Engine Optimization (GEO)',
    'Search Engine Optimization (SEO)',
    'Meta Ads ROAS Optimization',
    'Google Ads Performance Max',
    'Conversion Rate Optimization (CRO)',
    'Multi-Agent Autonomous Systems',
  ],
  offers: {
    '@type': 'Offer',
    name: 'Autonomous AI Agency Retainer',
    priceCurrency: 'USD',
    price: '7500.00',
    description: 'Autonomous 24/7 creative swarm execution and multi-channel paid acquisition management.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD_SCHEMA) }}
        />
      </head>
      <body className="bg-[#0B0B0E] text-slate-100 min-h-screen antialiased selection:bg-[#D4AF37]/30 selection:text-[#D4AF37]">
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
