import type { Metadata, Viewport } from "next";
import { PwaRuntime } from "@/components/pwa-runtime";
import "./globals.css";

export const metadata: Metadata = {
  applicationName: "Camelot-OS Anya Cockpit",
  title: {
    default: "Anya | Camelot-OS",
    template: "%s | Anya",
  },
  description: "Mobile-first sovereign Agent OS interface for Camelot cartridges",
  manifest: "/manifest.json",
  icons: {
    icon: "/icon.svg",
    apple: "/icon-192.png",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Anya",
  },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#0b1112",
  colorScheme: "dark",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#workspace">Skip to workspace</a>
        {children}
        <PwaRuntime />
      </body>
    </html>
  );
}
