import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { Providers } from "@/components/providers";

export const metadata: Metadata = {
  title: {
    default: "ATLAS X QFS",
    template: "%s | ATLAS X QFS"
  },
  description: "The decentralized substrate for AI-driven economic coherence.",
  keywords: ["ATLAS", "QFS", "Decentralized", "Web3", "Governance", "Token Economy", "Coherence"],
  authors: [
    {
      name: "ATLAS Team",
      url: "https://atlas-qfs.network",
    },
  ],
  creator: "ATLAS Team",
  icons: {
    icon: "./favicon.ico",
  }, openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://atlas-qfs.network",
    title: "ATLAS X QFS",
    description: "The decentralized substrate for AI-driven economic coherence.",
    siteName: "ATLAS Protocol",
  },
  twitter: {
    card: "summary_large_image",
    title: "ATLAS X QFS",
    description: "The decentralized substrate for AI-driven economic coherence.",
    creator: "@ATLAS_QFS",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className="antialiased bg-background text-foreground font-sans"
      >
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
