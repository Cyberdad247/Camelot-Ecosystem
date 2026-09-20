import React from 'react';
import type { Metadata } from 'next';
import { SeoAgoStructuredData } from '../snippets/seo-ago-metadata';

export const metadata: Metadata = {
  title: "Lisa's Custom Keychains | Handcrafted Custom Keychains & Jewelry",
  description:
    'Custom hand-woven keychains, charms, and sports team spirit gifts lovingly made one knot at a time. Design your personalized keychain in our interactive studio.',
  metadataBase: new URL('https://lisascustomkeychains.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: "Lisa's Custom Keychains | Handcrafted Custom Keychains & Jewelry",
    description: 'Personalized threads, letter beads, and accent charms. Hand-woven with love.',
    url: 'https://lisascustomkeychains.com',
    siteName: "Lisa's Custom Keychains",
    images: [
      {
        url: 'https://i.postimg.cc/cvyv100W/Untitled_design_(2).png',
        width: 1200,
        height: 630,
        alt: "Lisa's Custom Keychains Hero",
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "Lisa's Custom Keychains | Handcrafted Custom Keychains",
    description: 'Every knot tells a story. Custom hand-woven keychains and gifts.',
    images: ['https://i.postimg.cc/cvyv100W/Untitled_design_(2).png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Inject Agentic Graph Optimization (A.G.O.) JSON-LD */}
        <SeoAgoStructuredData />
      </head>
      <body>{children}</body>
    </html>
  );
}
