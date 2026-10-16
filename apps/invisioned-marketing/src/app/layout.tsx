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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0B0B0E] text-slate-100 min-h-screen antialiased selection:bg-[#D4AF37]/30 selection:text-[#D4AF37]">
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
