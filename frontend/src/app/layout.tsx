import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VidyaSearch — Search Engine for Indian College Resources",
  description: "Crawl, index, and search through NPTEL, SWAYAM, IITs, NITs, course notes, and Indian academic materials with BM25 and PageRank.",
  keywords: ["search engine", "NPTEL", "SWAYAM", "IIT", "NIT", "college resources", "BM25", "PageRank", "GATE syllabus", "lecture notes"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${plusJakartaSans.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
