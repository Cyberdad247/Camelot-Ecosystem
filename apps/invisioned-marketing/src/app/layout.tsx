import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Invisioned Marketing Inc. — Sovereign Digital Factory',
  description: 'Autonomous multi-agent marketing agency, lead generation, and dynamic client fulfillment engine.',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0B0B0E] text-slate-100 min-h-screen antialiased selection:bg-[#D4AF37]/30 selection:text-[#D4AF37]">
        {children}
      </body>
    </html>
  );
}
