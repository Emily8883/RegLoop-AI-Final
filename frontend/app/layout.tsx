import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RegLoop AI - Compliance Dashboard",
  description: "Closed-Loop Regulatory Execution Platform. Visualize, track, and manage regulatory obligations with advanced compliance analytics.",
  keywords: ["compliance", "regulatory", "obligations", "dashboard", "RegLoop"],
  authors: [{ name: "RegLoop AI" }],
  creator: "RegLoop AI",
  openGraph: {
    type: "website",
    locale: "en_US",
    title: "RegLoop AI - Compliance Dashboard",
    description: "Professional compliance management platform for regulatory obligations",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-screen flex flex-col bg-background text-foreground overflow-x-hidden">
        {children}
      </body>
    </html>
  );
}
