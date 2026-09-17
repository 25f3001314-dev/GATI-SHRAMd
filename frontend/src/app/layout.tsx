import type { Metadata } from "next";
import { GeistSans, GeistMono } from "geist/font";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gati Shram | Mobility Intelligence",
  description: "Predictive mobility intelligence built from governed, aggregated signals.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${GeistSans.variable} ${GeistMono.variable}`}>{children}</body>
    </html>
  );
}
