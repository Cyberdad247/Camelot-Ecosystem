import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "I2L Phygital",
  description: "Bridging physical and digital experiences",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
