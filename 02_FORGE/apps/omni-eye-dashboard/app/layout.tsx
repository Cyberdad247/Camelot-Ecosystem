import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title:       'Omni-Eye | Website Builder Cartridge',
  description: 'Camelot-OS website builder — Ouroboros SSM inference to live deploy',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden">{children}</body>
    </html>
  );
}
