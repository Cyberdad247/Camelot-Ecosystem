import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Excalibur Resonance',
  description: 'Camelot Agent-OS interface',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#020203] text-slate-200 antialiased">
        {children}
        <footer className="mt-8 text-center text-xs text-slate-400">
          Made by Invisioned Marketing inc.
        </footer>
      </body>
    </html>
  );
}
